"""
Spectera-specific document extraction
"""
import re
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from app.core.templates.spectera_template import CostItem, AgeCostItem, FrameItem, EligibilityCategory
import fitz  # PyMuPDF

from app.core.extractors.base_extractor import BaseExtractor
from app.core.templates.spectera_template import SpecteraTemplate
from app.core.pattern_library import spectera_patterns as patterns
from app.config import spectera_lens_mapping as mapping

logger = logging.getLogger(__name__)


class SpecteraExtractor(BaseExtractor):
    """
    Spectera-specific document extractor
    
    Implements the extraction logic for Spectera vision insurance documents
    """
    
    def __init__(self):
        """Initialize the Spectera extractor"""
        super().__init__("Spectera")
        self.output_template = SpecteraTemplate
    
    async def extract(self, document_text: str, document_path: str) -> Dict[str, Any]:
        """
        Extract structured benefit information from Spectera documents
        
        Args:
            document_text: The extracted text from the document
            document_path: Path to the original document file
            
        Returns:
            Dictionary containing structured Spectera benefit information
        """
        logger.info(f"Starting Spectera extraction for: {document_path}")
        
        try:
            # Open the PDF document for preprocessing
            doc = fitz.open(document_path)
            processed_text = ""
            
            # Process each page and extract text
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text("text", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                processed_text += page_text + "\n\n"  # Add page separation
            
            doc.close()
            
            # Preprocess the text
            processed_text = await self.preprocess_text(processed_text)
            
            # Extract different sections of data
            patient_info = await self._extract_patient_info(processed_text)
            eligibility_info = await self._extract_eligibility_info(processed_text)
            
            # Extract vision benefits using the simplified row-based method
            vision_benefits = await self._extract_vision_benefits(processed_text)
            
            # Debug log to verify extraction results
            benefit_count = sum(1 for section in vision_benefits.values() if section)
            logger.debug(f"Extracted {benefit_count} benefit sections from document")
            
            # Create the output template instance to ensure standard format
            result = self.output_template(
                provider="Spectera",
                patient_info=patient_info,
                eligibility_info=eligibility_info,
                vision_benefits=vision_benefits
            )

            # Convert the Pydantic model to a dictionary for the final output
            self.extracted_data = result.dict()
            logger.info(f"Successfully extracted data for: {document_path}")
            
            # Return the Pydantic model converted to dict
            return self.extracted_data
            
        except Exception as e:
            logger.error(f"Error during Spectera extraction: {str(e)}", exc_info=True)
            # Return a basic error structure if extraction fails
            return {
                 "provider": "Spectera",
                 "error": str(e)
            }
    
    async def preprocess_text(self, text: str) -> str:
        """
        Preprocess document text for extraction
        
        Args:
            text: The raw document text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace while preserving table structure
        processed = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove headers and footers by identifying repeating patterns
        lines = processed.split('\n')
        filtered_lines = []
        header_footer_patterns = [
            r'Page \d+ of \d+',
            r'Spectera Vision',
            r'Confidential',
            r'www\.spectera\.com',
            r'\d{1,2}/\d{1,2}/\d{2,4}'  # Date pattern
        ]
        for line in lines:
            # Skip line if ANY pattern matches
            if not any(re.search(pattern, line, re.IGNORECASE) for pattern in header_footer_patterns):
                # Additional check for lines that are just numbers (potential page numbers)
                if not line.strip().isdigit():
                    filtered_lines.append(line)
        
        processed = '\n'.join(filtered_lines)
        return processed

    async def _extract_patient_info(self, text: str) -> Dict[str, Any]:
        """
        Extract patient information from the document
        
        Args:
            text: The preprocessed document text
            
        Returns:
            Dictionary containing patient information
        """
        patient_info = {
            "member_name": "[REDACTED]", # Keep redacted for privacy
            "subscriber_id": "",
            "product_name": ""
        }
        
        # Use regex directly on the text, less dependent on section splitting
        id_match = re.search(r"(?:ID Number|Subscriber ID|Member ID)[:\s]+([A-Za-z0-9\-]+)", text, re.IGNORECASE)
        if id_match:
            patient_info["subscriber_id"] = id_match.group(1).strip()
            
        plan_match = re.search(r"(?:Plan|Product|Product Name)[:\s]+([^\n]+)", text, re.IGNORECASE)
        if plan_match:
            # Clean up potential extra details captured after the name
            product_name = plan_match.group(1).strip()
            # Example cleanup: Stop at "Please Note:" or similar phrases if they get included
            stop_phrases = ["Please Note:", "In Network Coverage"]
            for phrase in stop_phrases:
                if phrase in product_name:
                    product_name = product_name.split(phrase)[0].strip()
            patient_info["product_name"] = product_name

        # Confidence can be based on whether key fields were found
        self.set_confidence("patient_info", 0.9 if patient_info["subscriber_id"] else 0.5)
        return patient_info
    
    async def _extract_eligibility_info(self, text: str) -> Dict[str, Any]:
        """
        Extracts eligibility status (true/false) for Exam, Frame, Lenses
        based on the 'In Network Coverage Frequency' section.
        
        Args:
            text: The preprocessed document text
            
        Returns:
            Dictionary containing eligibility information with categories list
        """
        eligibility_info = {"categories": []}
        required_categories = ["Exam", "Frame", "Lenses"]
        
        # Find the eligibility section between precise boundaries
        section_pattern = re.compile(
            r"(In\s+Network\s+Coverage\s+Frequency\s*\n)(.*?)(?=\s*In\s+Network\s+Coverage\s*\n|\Z)", 
            re.IGNORECASE | re.DOTALL
        )
        section_match = section_pattern.search(text)
        
        if section_match:
            eligibility_section = section_match.group(2)
            logger.debug("Successfully isolated 'In Network Coverage Frequency' section for eligibility check.")
            
            # Process each required category
            for category_name in required_categories:
                is_eligible = False # Default to false
                
                try:
                    # Look for line starting with exact category name
                    # This pattern matches the category name at the beginning of the line,
                    # followed by eligibility text, and then frequency information at the end 
                    line_pattern = re.compile(
                        rf"^[ \t]*{re.escape(category_name)}\s+([^\n]*?(?:Available|Eligible|Not\s*Covered)[^\n]*?)(?:\s+\d+\s+every|\s+Every|\s+Once|$)",
                        re.IGNORECASE | re.MULTILINE
                    )
                    match = line_pattern.search(eligibility_section)
                    
                    if match:
                        eligibility_text = match.group(1).strip()
                        logger.debug(f"Category: {category_name}, Found Eligibility Text: '{eligibility_text}'")
                        
                        # Apply clear eligibility detection rules
                        if eligibility_text.lower() == "available":
                            is_eligible = True
                        elif eligibility_text.lower() == "eligible":
                            is_eligible = True
                        elif "available on" in eligibility_text.lower():
                            is_eligible = False
                        elif "not covered" in eligibility_text.lower():
                            is_eligible = False
                    else:
                        logger.warning(f"Could not find eligibility text for category: {category_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing eligibility for category '{category_name}': {e}")
                
                # Add category with determined eligibility
                eligibility_info["categories"].append(
                    EligibilityCategory(name=category_name, is_eligible=is_eligible)
                )
                
            self.set_confidence("eligibility_info", 0.9)
        else:
            # If section not found, add default categories with is_eligible=False
            for category_name in required_categories:
                eligibility_info["categories"].append(
                    EligibilityCategory(name=category_name, is_eligible=False)
                )
            self.set_confidence("eligibility_info", 0.5)
            logger.warning("'In Network Coverage Frequency' section not found for eligibility extraction.")
            
        return eligibility_info

    async def _extract_benefit_row(self, text: str, row_patterns: List[str]) -> Optional[Tuple[str, str]]:
        """
        Extract a specific benefit row from the text using direct pattern matching.
        
        Args:
            text: The preprocessed document text
            row_patterns: List of patterns to match the row
            
        Returns:
            Tuple of (service_name, patient_responsibility) or None if not found
        """
        # Try to match the row patterns directly
        for pattern in row_patterns:
            # Look for pattern: "Service name: Value" or "Service name..........Value"
            combined_pattern = rf"({pattern})[:\s\.]+([^\n]+)"
            match = re.search(combined_pattern, text, re.IGNORECASE)
            if match:
                service_name = match.group(1).strip()
                value = match.group(2).strip()
                return (service_name, value)
            
            # Try alternative pattern with newline
            alternative_pattern = rf"{pattern}\s*\n\s*([^\n]+)"
            match = re.search(alternative_pattern, text, re.IGNORECASE)
            if match:
                service_name = pattern
                value = match.group(1).strip()
                return (service_name, value)
            
            # Try a more flexible pattern that looks for the service name followed by any non-empty value
            flexible_pattern = rf"{pattern}\s*[:\.]?\s*([^\n]+)"
            match = re.search(flexible_pattern, text, re.IGNORECASE)
            if match:
                service_name = pattern
                value = match.group(1).strip()
                return (service_name, value)
        
        return None

    def _process_responsibility(self, provider_name: str, responsibility: str) -> Union[CostItem, AgeCostItem, FrameItem]:
        """
        Process a patient responsibility value into a simplified Pydantic model instance,
        primarily capturing the raw responsibility string.
        
        Args:
            provider_name: The name of the service or provider. Used to determine model type.
            responsibility: The raw patient responsibility value string captured from the document row.
            
        Returns:
            An instance of CostItem, AgeCostItem, or FrameItem.
        """
        logger.debug(f"Processing responsibility for {provider_name}: '{responsibility}'")
        
        # Clean up the responsibility value
        responsibility_cleaned = responsibility.strip()
        
        # If no value provided, return None
        if not responsibility_cleaned:
            logger.debug(f"No responsibility value found for {provider_name}, setting to None")
            responsibility_cleaned = "None"
        
        # Remove common prefixes
        for prefix in mapping.PREFIX_PATTERNS:
            if responsibility_cleaned.startswith(prefix):
                responsibility_cleaned = responsibility_cleaned[len(prefix):].strip()
                logger.debug(f"Removed prefix '{prefix}', new value: '{responsibility_cleaned}'")
        
        # Handle special cases
        if responsibility_cleaned.lower() in ["covered", "covered-in-full", "included", "no charge", "free", "waived"]:
            responsibility_cleaned = "Covered-in-Full"
            logger.debug(f"Converted to Covered-in-Full for {provider_name}")
        elif responsibility_cleaned.lower() in ["not covered", "not available"]:
            responsibility_cleaned = "Not Covered"
            logger.debug(f"Converted to Not Covered for {provider_name}")
        elif responsibility_cleaned.lower() == "optional":
            responsibility_cleaned = "Optional"
            logger.debug(f"Converted to Optional for {provider_name}")
            
        # Determine model type based on provider_name
        is_poly_adult = "Polycarbonate" in provider_name and ("19+" in responsibility_cleaned or "19+" in provider_name)
        is_frame = provider_name == "Frame"
        
        # Create appropriate model instance
        if is_poly_adult:
            # For adult polycarbonate, use AgeCostItem with age_note
            result_model = AgeCostItem(
                provider_name=provider_name, 
                patient_responsibility=responsibility_cleaned,
                age_note="for Ages 19+"
            )
            # Try to extract more precise age note if present
            age_match = re.search(r'(for\s+Ages?\s+\d+(?:\s*-\s*\d+|\+))', responsibility_cleaned, re.IGNORECASE)
            if age_match:
                result_model.age_note = age_match.group(1).strip()
                logger.debug(f"Updated age note to: {result_model.age_note}")
        elif is_frame:
            # For frame, use FrameItem
            result_model = FrameItem(
                provider_name=provider_name, 
                patient_responsibility=responsibility_cleaned
            )
        else:
            # Default to CostItem
            result_model = CostItem(
                provider_name=provider_name, 
                patient_responsibility=responsibility_cleaned
            )
            
        logger.debug(f"Created {result_model.__class__.__name__} with responsibility: '{result_model.patient_responsibility}'")
        return result_model

    async def _extract_vision_benefits(self, text: str) -> Dict[str, Any]:
        """
        Extract vision benefits using direct row matching.
        
        Args:
            text: The preprocessed document text
            
        Returns:
            Dictionary containing structured vision benefits
        """
        # Initialize result structure based on the template with "None" as default
        professional_services = {
            "exam": CostItem(provider_name="Exam", patient_responsibility="None"),
            "retinal_screening": CostItem(provider_name="Retinal Screening Photography for Diabetics", patient_responsibility="None")
        }
        frames = FrameItem(provider_name="Frame", patient_responsibility="None")
        lenses = {
            "standard_lenses": CostItem(provider_name="Lenses / Standard Lenses", patient_responsibility="None"),
            "blended_bifocals": CostItem(provider_name="Lenses / Blended Bifocals", patient_responsibility="None"),
            "free_form_sv_lenses": CostItem(provider_name="Lenses / Free-form SV Lenses", patient_responsibility="None"),
            "sv_aspheric_lenses": CostItem(provider_name="Lenses / SV Aspheric Lenses", patient_responsibility="None"),
            "mf_aspheric_lenses": CostItem(provider_name="Lenses / MF Aspheric Lenses", patient_responsibility="None"),
            "occupational_double_seg_lenses": CostItem(provider_name="Lenses / Occupational Double Seg Lenses", patient_responsibility="None")
        }
        progressive_lenses = {
            "non_formulary": CostItem(provider_name="Lenses / Progressive Lenses: Non-Formulary", patient_responsibility="None"),
            "tier_1": CostItem(provider_name="Lenses / Progressive Lenses: Tier I", patient_responsibility="None"),
            "tier_2": CostItem(provider_name="Lenses / Progressive Lenses: Tier II", patient_responsibility="None"),
            "tier_3": CostItem(provider_name="Lenses / Progressive Lenses: Tier III", patient_responsibility="None"),
            "tier_4": CostItem(provider_name="Lenses / Progressive Lenses: Tier IV", patient_responsibility="None"),
            "tier_5": CostItem(provider_name="Lenses / Progressive Lenses: Tier V", patient_responsibility="None")
        }
        lens_materials = {
            "high_index_standard": CostItem(provider_name="High Index less than or equal to 1.66", patient_responsibility="None"),
            "high_index_premium": CostItem(provider_name="High Index 1.66 - 1.73", patient_responsibility="None"),
            "high_index_ultra": CostItem(provider_name="High Index, >= 1.74", patient_responsibility="None"),
            "polycarbonate_child": CostItem(provider_name="Polycarbonate Lenses", patient_responsibility="None"),
            "polycarbonate_adult": AgeCostItem(provider_name="Polycarbonate Lenses", patient_responsibility="None", age_note="for Ages 19+")
        }
        lens_options = {
            "anti_reflective_coating": {
                 "non_formulary": CostItem(provider_name="Anti-Reflective Coating: Non-Formulary", patient_responsibility="None"),
                 "tier_1": CostItem(provider_name="Anti-Reflective Coating: Tier I", patient_responsibility="None"),
                 "tier_2": CostItem(provider_name="Anti-Reflective Coating: Tier II", patient_responsibility="None"),
                 "tier_3": CostItem(provider_name="Anti-Reflective Coating: Tier III", patient_responsibility="None"),
                 "tier_4": CostItem(provider_name="Anti-Reflective Coating: Tier IV", patient_responsibility="None")
            },
            "scratch_coating": CostItem(provider_name="Scratch Coating", patient_responsibility="None"),
            "one_year_scratch_warranty": CostItem(provider_name="One Year Scratch Warranty", patient_responsibility="None"),
            "edge_coating": CostItem(provider_name="Edge Coating", patient_responsibility="None"),
            "photochromic": CostItem(provider_name="Photochromic", patient_responsibility="None"),
            "polarized": CostItem(provider_name="Polarized", patient_responsibility="None"),
            "tint": CostItem(provider_name="Tint", patient_responsibility="None"),
            "uv_coating": CostItem(provider_name="UV Coating", patient_responsibility="None"),
            "polished_edges": CostItem(provider_name="Polished Edges / Roll & Polish", patient_responsibility="None"),
            "oversize_lenses": CostItem(provider_name="Oversize Lenses", patient_responsibility="None"),
            "chemistrie_clip": CostItem(provider_name="Chemistrie Clip", patient_responsibility="None"),
            "miscellaneous_lens_options": CostItem(provider_name="Miscellaneous Lens Options", patient_responsibility="None")
        }
        
        # Try to isolate the "In Network Coverage" section for better targeting
        benefits_section_pattern = re.compile(
            r"(In\s+Network\s+Coverage(?!\s+Frequency))(.*?)(?=\s*Out\s+of\s+Network|\Z)",
            re.IGNORECASE | re.DOTALL
        )
        benefits_match = benefits_section_pattern.search(text)
        benefits_text = benefits_match.group(2) if benefits_match else text
        
        # Debug log the section we're working with
        logger.debug(f"Found benefits section: {benefits_text[:200]}...")
        
        # Extract professional services
        exam_result = await self._extract_benefit_row(benefits_text, mapping.ROW_PATTERNS["exam"])
        if exam_result:
            professional_services["exam"] = self._process_responsibility(*exam_result)
            logger.debug(f"Extracted exam value: {exam_result[1]}")
            
        retinal_result = await self._extract_benefit_row(benefits_text, mapping.ROW_PATTERNS["retinal_screening"])
        if retinal_result:
            professional_services["retinal_screening"] = self._process_responsibility(*retinal_result)
            logger.debug(f"Extracted retinal screening value: {retinal_result[1]}")
            
        # Extract frame benefits
        frame_result = await self._extract_benefit_row(benefits_text, mapping.ROW_PATTERNS["frame"])
        if frame_result:
            frames = self._process_responsibility("Frame", frame_result[1])
            logger.debug(f"Extracted frame value: {frame_result[1]}")
            
        # Extract standard lens benefits
        for lens_type, patterns in {
            "standard_lenses": mapping.ROW_PATTERNS["standard_lenses"],
            "blended_bifocals": mapping.ROW_PATTERNS["blended_bifocals"],
            "free_form_sv_lenses": mapping.ROW_PATTERNS["free_form_sv_lenses"],
            "sv_aspheric_lenses": mapping.ROW_PATTERNS["sv_aspheric_lenses"],
            "mf_aspheric_lenses": mapping.ROW_PATTERNS["mf_aspheric_lenses"],
            "occupational_double_seg_lenses": mapping.ROW_PATTERNS["occupational_double_seg_lenses"]
        }.items():
            result = await self._extract_benefit_row(benefits_text, patterns)
            if result:
                lenses[lens_type] = self._process_responsibility(result[0], result[1])
                logger.debug(f"Extracted {lens_type} value: {result[1]}")
                
        # Extract progressive lens benefits
        for prog_type, patterns in {
            "non_formulary": mapping.ROW_PATTERNS["progressive_non_formulary"],
            "tier_1": mapping.ROW_PATTERNS["progressive_tier_1"],
            "tier_2": mapping.ROW_PATTERNS["progressive_tier_2"],
            "tier_3": mapping.ROW_PATTERNS["progressive_tier_3"],
            "tier_4": mapping.ROW_PATTERNS["progressive_tier_4"],
            "tier_5": mapping.ROW_PATTERNS["progressive_tier_5"]
        }.items():
            result = await self._extract_benefit_row(benefits_text, patterns)
            if result:
                progressive_lenses[prog_type] = self._process_responsibility(result[0], result[1])
                logger.debug(f"Extracted {prog_type} value: {result[1]}")
                
        # Extract lens materials
        for material_type, patterns in {
            "high_index_standard": mapping.ROW_PATTERNS["high_index_standard"],
            "high_index_premium": mapping.ROW_PATTERNS["high_index_premium"],
            "high_index_ultra": mapping.ROW_PATTERNS["high_index_ultra"]
        }.items():
            result = await self._extract_benefit_row(benefits_text, patterns)
            if result:
                lens_materials[material_type] = self._process_responsibility(result[0], result[1])
                logger.debug(f"Extracted {material_type} value: {result[1]}")
                
        # Handle polycarbonate lenses specially (check for age-specific pricing)
        poly_child_result = await self._extract_benefit_row(benefits_text, mapping.ROW_PATTERNS["polycarbonate_child"])
        poly_adult_result = await self._extract_benefit_row(benefits_text, mapping.ROW_PATTERNS["polycarbonate_adult"])
        
        # If we have age-specific results, use them
        if poly_child_result:
            lens_materials["polycarbonate_child"] = self._process_responsibility(poly_child_result[0], poly_child_result[1])
            logger.debug(f"Extracted polycarbonate child value: {poly_child_result[1]}")
        
        if poly_adult_result:
            lens_materials["polycarbonate_adult"] = self._process_responsibility(poly_adult_result[0], poly_adult_result[1])
            logger.debug(f"Extracted polycarbonate adult value: {poly_adult_result[1]}")
            
        # If we only found one generic polycarbonate price, try to use it for both
        if not poly_child_result and not poly_adult_result:
            # Try generic pattern
            generic_poly_pattern = [r"(?:Polycarbonate Lenses)"]
            generic_poly_result = await self._extract_benefit_row(benefits_text, generic_poly_pattern)
            if generic_poly_result:
                lens_materials["polycarbonate_child"] = self._process_responsibility(generic_poly_result[0], generic_poly_result[1])
                # For adult, use same value but with age_note
                lens_materials["polycarbonate_adult"] = AgeCostItem(
                    provider_name=generic_poly_result[0],
                    patient_responsibility=generic_poly_result[1],
                    age_note="for Ages 19+"
                )
                logger.debug(f"Extracted generic polycarbonate value: {generic_poly_result[1]}")
                
        # Extract anti-reflective coating options
        ar_coating = lens_options["anti_reflective_coating"]
        for ar_type, patterns in {
            "non_formulary": mapping.ROW_PATTERNS["ar_non_formulary"],
            "tier_1": mapping.ROW_PATTERNS["ar_tier_1"],
            "tier_2": mapping.ROW_PATTERNS["ar_tier_2"],
            "tier_3": mapping.ROW_PATTERNS["ar_tier_3"],
            "tier_4": mapping.ROW_PATTERNS["ar_tier_4"]
        }.items():
            result = await self._extract_benefit_row(benefits_text, patterns)
            if result:
                ar_coating[ar_type] = self._process_responsibility(result[0], result[1])
                logger.debug(f"Extracted {ar_type} value: {result[1]}")
                
        # Extract other lens options
        for option_type, patterns in {
            "scratch_coating": mapping.ROW_PATTERNS["scratch_coating"],
            "one_year_scratch_warranty": mapping.ROW_PATTERNS["one_year_scratch_warranty"],
            "edge_coating": mapping.ROW_PATTERNS["edge_coating"],
            "photochromic": mapping.ROW_PATTERNS["photochromic"],
            "polarized": mapping.ROW_PATTERNS["polarized"],
            "tint": mapping.ROW_PATTERNS["tint"],
            "uv_coating": mapping.ROW_PATTERNS["uv_coating"],
            "polished_edges": mapping.ROW_PATTERNS["polished_edges"],
            "oversize_lenses": mapping.ROW_PATTERNS["oversize_lenses"],
            "chemistrie_clip": mapping.ROW_PATTERNS["chemistrie_clip"],
            "miscellaneous_lens_options": mapping.ROW_PATTERNS["miscellaneous_lens_options"]
        }.items():
            result = await self._extract_benefit_row(benefits_text, patterns)
            if result:
                lens_options[option_type] = self._process_responsibility(result[0], result[1])
                logger.debug(f"Extracted {option_type} value: {result[1]}")
                
        # Combine results into the vision benefits structure
        vision_benefits = {
            "professional_services": professional_services,
            "frames": frames,
            "lenses": lenses,
            "progressive_lenses": progressive_lenses,
            "lens_materials": lens_materials,
            "lens_options": lens_options
        }
        
        # Set confidence based on key fields found
        has_exam = professional_services["exam"].patient_responsibility != "None"
        has_frame = frames.patient_responsibility != "None"
        self.set_confidence("vision_benefits", 0.9 if has_exam and has_frame else 0.6)
        
        return vision_benefits
        
    # Implement the abstract methods from BaseExtractor but delegate to _extract_vision_benefits
    
    async def extract_exam_benefits(self, document_text: str) -> Dict[str, Any]:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["professional_services"]
    
    async def extract_frame_benefits(self, document_text: str) -> Any:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["frames"]
    
    async def extract_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["lenses"]
    
    async def extract_progressive_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["progressive_lenses"]
    
    async def extract_lens_materials(self, document_text: str) -> Dict[str, Any]:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["lens_materials"]
    
    async def extract_lens_options(self, document_text: str) -> Dict[str, Any]:
        vision_benefits = await self._extract_vision_benefits(document_text)
        return vision_benefits["lens_options"]
    
    async def extract_contact_lens_fit(self, document_text: str) -> Dict[str, Any]:
        # Not included in the final output as per requirements, return empty dict
        return {}
    
    async def extract_contact_lenses(self, document_text: str) -> Dict[str, Any]:
        # Not included in the final output as per requirements, return empty dict
        return {}

