"""
VSP-specific extraction module for processing VSP vision insurance documents.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
import fitz # PyMuPDF for classification

from app.core.extractors.base_extractor import BaseExtractor
# Import the Pydantic template for structure validation/guidance
from app.core.templates.vsp_template import VSPTemplate, LensCategory, LensSubcategory, LensOption, EligibilityInfo, PlanDetails, FrameAllowance
# Import the detailed VSP lens structure mapping
import app.config.vsp_lens_mapping as vsp_mapping
# Keep ProviderMappings for potential future standardization, though less critical now
from app.core.models.provider_mappings import ProviderMappings

logger = logging.getLogger(__name__)


class VSPExtractor(BaseExtractor):
    """
    Extractor specifically designed for VSP vision insurance documents.
    Implements extraction logic based on VSP_EXTRACTOR_DESIGN.md.
    Handles Patient Record and Lens Enhancement documents.
    """

    def __init__(self):
        """Initialize the VSP extractor."""
        super().__init__("VSP")
        # Load the hierarchical lens structure
        self.lens_structure_template = vsp_mapping.VSP_LENS_STRUCTURE
        # Keep mappings for potential standardization if needed later
        self.mappings = ProviderMappings.get_provider_mapping("vsp")
        # Use the Pydantic model as a reference for the final structure
        self.output_template = VSPTemplate

    async def extract(self, document_text: str, document_path: str) -> Dict[str, Any]:
        """
        Extract structured data from a VSP document by classifying it and
        delegating to specific processing methods.

        Args:
            document_text: The extracted text from the document (may not be needed if path is used).
            document_path: Path to the original document file.

        Returns:
            A dictionary of extracted VSP information conforming to VSPTemplate.
        """
        logger.info(f"Starting VSP extraction for: {document_path}")
        self.reset() # Clear previous extraction data

        try:
            # 1. Classify Document Type(s)
            # We need the path to open the PDF for reliable classification
            doc_types = self._classify_document(document_path)
            logger.info(f"Classified document types: {doc_types}")

            patient_record_data = {}
            lens_enhancement_data = {}

            # 2. Process based on classification
            if "patient_record" in doc_types:
                patient_record_data = await self._process_patient_record(document_path)

            if "lens_enhancement" in doc_types:
                lens_enhancement_data = await self._process_lens_enhancement(document_path)

            # Handle case where classification failed or document is unusable
            if not patient_record_data and not lens_enhancement_data:
                 logger.warning(f"Could not extract significant data from {document_path}")
                 # Return a minimal structure or raise an error? For now, return minimal.
                 return self.get_result() # Will be mostly empty

            # 3. Merge and Format Results
            final_data = self._merge_and_format_results(
                patient_record_data,
                lens_enhancement_data,
                doc_types # Pass doc_types to set document_type/title correctly
            )
            self.extracted_data.update(final_data)

            # Store raw text sample for debugging if needed (optional)
            # self.extracted_data["raw_data"] = {"text_sample": document_text[:1000] + "..."}

            logger.info(f"Successfully extracted data for: {document_path}")
            return self.get_result()

        except Exception as e:
            logger.error(f"Error during VSP extraction for {document_path}: {e}", exc_info=True)
            # Return partial data if any, or an empty dict with error info?
            self.extracted_data["error"] = str(e)
            return self.get_result() # Return whatever was extracted before the error

    async def extract_from_multiple_files(self, document_paths: List[str], filenames: List[str]) -> Dict[str, Any]:
        """
        Extract structured data from multiple VSP documents.
        
        Args:
            document_paths: List of paths to the document files
            filenames: List of original filenames
            
        Returns:
            A dictionary of extracted VSP information conforming to VSPTemplate.
        """
        logger.info(f"Starting VSP extraction from multiple files: {filenames}")
        self.reset()  # Clear previous extraction data
        
        try:
            patient_record_data = {}
            lens_enhancement_data = {}
            all_doc_types = []
            
            # Process each document
            for doc_path, filename in zip(document_paths, filenames):
                logger.info(f"Processing document: {filename} at {doc_path}")
                
                # Classify this document
                doc_types = self._classify_document(doc_path)
                all_doc_types.extend(doc_types)
                logger.info(f"Classified {filename} as: {doc_types}")
                
                # Process based on classification
                if "patient_record" in doc_types:
                    logger.info(f"Processing patient record from {filename}")
                    patient_record_data = await self._process_patient_record(doc_path)
                
                if "lens_enhancement" in doc_types:
                    logger.info(f"Processing lens enhancement from {filename}")
                    lens_enhancement_data = await self._process_lens_enhancement(doc_path)
            
            # Handle case where classification failed or documents are unusable
            if not patient_record_data and not lens_enhancement_data:
                logger.warning(f"Could not extract significant data from any of the provided documents")
                return self.get_result()  # Will be mostly empty
            
            # Merge and Format Results
            final_data = self._merge_and_format_results(
                patient_record_data,
                lens_enhancement_data,
                list(set(all_doc_types))  # Remove duplicates
            )
            
            self.extracted_data.update(final_data)
            
            logger.info("VSP multi-file extraction completed successfully")
            return self.get_result()
            
        except Exception as e:
            logger.error(f"Error during VSP multi-file extraction: {e}", exc_info=True)
            # Return whatever data we managed to extract
            return self.get_result()

    def _classify_document(self, document_path: str) -> List[str]:
        """
        Detect the type(s) of VSP document (Patient Record, Lens Enhancement, Combined).

        Args:
            document_path: Path to the VSP document.

        Returns:
            List containing identified document types (e.g., ["patient_record", "lens_enhancement"]).
        """
        doc_types = []
        try:
            doc = fitz.open(document_path)
            # Check first few pages for keywords
            text_sample = ""
            for page_num in range(min(3, len(doc))): # Check first 3 pages
                 text_sample += doc[page_num].get_text("text", flags=fitz.TEXTFLAGS_TEXT)

            doc.close()

            # Use keywords from design plan and samples
            is_patient_record = "VSP PATIENT RECORD REPORT" in text_sample
            is_lens_enhancement = "VSP Lens Enhancement Charges" in text_sample

            if is_patient_record:
                doc_types.append("patient_record")
            if is_lens_enhancement:
                doc_types.append("lens_enhancement")

            # If neither specific header found, maybe try broader checks?
            if not doc_types and "VSP" in text_sample:
                 # Could be an unknown format, or maybe default to one?
                 # For now, return empty if specific headers aren't found.
                 logger.warning(f"Could not definitively classify VSP document: {document_path}")

        except Exception as e:
            logger.error(f"Error classifying VSP document {document_path}: {e}", exc_info=True)
            # Return empty list on error

        return doc_types


    async def _process_patient_record(self, document_path: str) -> Dict[str, Any]:
        """
        Extracts data specifically from VSP Patient Record sections.
        Placeholder - logic to be implemented based on design plan.

        Args:
            document_path: Path to the document file.

        Returns:
            Dictionary containing structured Patient Record data.
        """
        logger.info(f"Processing Patient Record data from: {document_path}")
        extracted_record_data = {}

        # Example placeholder structure
        extracted_record_data = {
            "patient_info": {"id_number": None, "patient_name": "[REDACTED]"},
            "eligibility_info": {"exam": None, "lens": None, "frame": None, "contacts": None},
            "plan_details": {
                "plan_name": None,
                "copays": {},
                "frame_allowance": {}
            },
            "covered_items_codes": [] # List of codes identified as fully covered
        }

        try:
            doc = fitz.open(document_path)
            text = ""
            for page in doc:
                text += page.get_text("text", flags=fitz.TEXTFLAGS_TEXT | fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE)
            doc.close()

            # Preprocess text slightly (e.g., normalize whitespace)
            text = re.sub(r'\s+', ' ', text).strip()

            # --- Extract Data ---
            plan_info = await self._extract_plan_info(text) # Extracts name, id, patient name
            exam_benefits = await self.extract_exam_benefits(text) # Extracts exam copay
            material_benefits = await self.extract_material_benefits(text) # Extracts frame allowance
            contact_benefits = await self.extract_contact_benefits(text) # Extracts contacts allowance/copay
            eligibility_info = self._extract_eligibility(text) # Extracts boolean flags

            # Populate the result dictionary
            extracted_record_data["patient_info"] = {
                "id_number": plan_info.get("id_number"),
                "patient_name": plan_info.get("patient_name", "[REDACTED]")
            }
            extracted_record_data["eligibility_info"] = eligibility_info

            # Combine copays
            copays = {}
            if "exam_copay" in exam_benefits:
                copays["exam"] = exam_benefits["exam_copay"]
            if "contacts_exam_copay" in contact_benefits:
                copays["contacts_exam"] = contact_benefits["contacts_exam_copay"]
            # Add other copays if found (e.g., lens, frame from vsp3)
            lens_copay_match = re.search(r"Lens\s+\$(\d+(?:\.\d+)?)", text)
            if lens_copay_match:
                 try: copays["lens"] = float(lens_copay_match.group(1))
                 except ValueError: pass
            frame_copay_match = re.search(r"Frame\s+\$(\d+(?:\.\d+)?)", text)
            if frame_copay_match:
                 try: copays["frame"] = float(frame_copay_match.group(1))
                 except ValueError: pass


            extracted_record_data["plan_details"] = {
                "plan_name": plan_info.get("plan_name"),
                "copays": copays if copays else None,
                "frame_allowance": material_benefits.get("frame_allowance"),
                # Add contacts allowance if needed in this structure level
                "contacts_allowance": contact_benefits.get("contacts_allowance")
            }

            # --- Identify Fully Covered Lens Items from Patient Record ---
            covered_codes_found = []
            # Find the Lens Enhancement Details section first
            details_section_match = re.search(r"LENS ENHANCEMENT DETAILS \(SEE.*?Covered\s+(Covered with Additional Copay.*?)\Z", text, re.IGNORECASE | re.DOTALL)
            if details_section_match:
                 details_text = details_section_match.group(1)
                 # Now look for specific keywords known to be under "Covered" in vsp3.pdf structure
                 if re.search(r"Polycarbonate", details_text, re.IGNORECASE):
                     logger.debug("Found 'Polycarbonate' potentially covered in Patient Record.")
                     # Add all polycarbonate codes as potentially covered based on this plan type
                     poly_codes = [opt['code'] for cat in self.lens_structure_template if cat['category'] == 'LENSES'
                                   for subcat in cat['subcategories'] if subcat['name'] == 'Polycarbonate'
                                   for opt in subcat['options']]
                     covered_codes_found.extend(poly_codes)

                 if re.search(r"UV Protection", details_text, re.IGNORECASE):
                     logger.debug("Found 'UV Protection' potentially covered in Patient Record.")
                     covered_codes_found.extend(['SV', 'BV']) # Add both codes

                 if re.search(r"Scratch Resistant Coatings", details_text, re.IGNORECASE):
                     logger.debug("Found 'Scratch Resistant Coatings' potentially covered in Patient Record.")
                     covered_codes_found.extend(['QQ', 'QS']) # Add both codes

                 if re.search(r"Rimless Drill", details_text, re.IGNORECASE):
                     logger.debug("Found 'Rimless Drill' potentially covered in Patient Record.")
                     covered_codes_found.append('SW')

                 # Add other checks based on vsp3.pdf structure if needed

            extracted_record_data["covered_items_codes"] = list(set(covered_codes_found)) # Ensure uniqueness
            logger.info(f"Identified covered codes from Patient Record: {extracted_record_data['covered_items_codes']}")


        except Exception as e:
            logger.error(f"Error processing patient record from {document_path}: {e}", exc_info=True)
            # Return potentially partial data or empty dict on error
            return extracted_record_data

        return extracted_record_data


    async def _process_lens_enhancement(self, document_path: str) -> Dict[str, Any]:
        """
        Extracts data specifically from VSP Lens Enhancement sections.
        Uses fitz get_text("words") for positional analysis.
        """
        logger.info(f"Processing Lens Enhancement data from: {document_path}")
        extracted_lens_data = {"lens_categories": []}

        import copy
        import fitz # PyMuPDF

        try:
            doc = fitz.open(document_path)
            all_words = []
            for page_num, page in enumerate(doc):
                # Extract words with coordinates: (x0, y0, x1, y1, "word", block_no, line_no, word_no)
                page_words = page.get_text("words")
                # Add page number to each word tuple
                all_words.extend([(page_num,) + word for word in page_words])
            doc.close()

            if not all_words:
                logger.warning(f"No text words found in lens enhancement document: {document_path}")
                return {"lens_categories": []}

            # Create a deep copy of the template to populate
            processed_categories = copy.deepcopy(self.lens_structure_template)
            found_pricing = False

            for category in processed_categories:
                logger.debug(f"Processing Category: {category['category']}")
                for subcategory in category["subcategories"]:
                    subcategory_name = subcategory['name']
                    logger.debug(f"  Processing Subcategory: {subcategory_name}")

                    # --- Try to find section-level pricing string ---
                    section_pricing_string = self._find_section_pricing_string(all_words, subcategory_name)
                    if section_pricing_string:
                        logger.debug(f"    Found section-level pricing for '{subcategory_name}': {section_pricing_string}")
                    # ---

                    for option in subcategory["options"]:
                        code = option["code"]
                        description = option["description"]
                        logger.debug(f"    Processing Option: {code} - {description}")

                        # Find costs using word information
                        extracted_costs = self._find_costs_for_option_words(all_words, code, description)

                        if extracted_costs:
                            option.update(extracted_costs)
                            found_pricing = True
                            logger.debug(f"      Found costs: {extracted_costs}")
                        else:
                            logger.debug(f"      No specific costs found for {code}. Setting costs to None.")
                            # Explicitly set costs to None initially if not found
                            option["single_cost"] = None
                            option["multi_cost"] = None
                            if "cost_description" in option:
                                del option["cost_description"]

                            # Apply section-level pricing string if found and specific costs are missing
                            if section_pricing_string:
                                logger.debug(f"      Applying section-level pricing '{section_pricing_string}' to {code}")
                                option["cost_description"] = section_pricing_string
                                # Ensure numeric costs are still None if only description applies
                                option["single_cost"] = None
                                option["multi_cost"] = None


            if not found_pricing:
                 logger.warning(f"Could not extract any lens pricing from {document_path}")

            extracted_lens_data["lens_categories"] = processed_categories

        except Exception as e:
            logger.error(f"Error processing lens enhancement from {document_path}: {e}", exc_info=True)
            return {"lens_categories": []}

        return extracted_lens_data

    def _find_costs_for_option_words(self, words: List[Tuple], code: str, description: str) -> Optional[Dict[str, Any]]:
        """
        Finds pricing information using text words with coordinates.
        Searches for the code word, then looks for costs ($ or strings) in subsequent words on the same line.
        """
        code_word_index = -1
        code_word_details = None

        # Find the word matching the code (case-insensitive), allowing for asterisks
        for i, word_details in enumerate(words):
            word_text_cleaned = word_details[5].strip().upper().replace('*', '') # Clean text for comparison
            code_upper = code.upper()

            # Check for exact match (cleaned), or code followed/preceded by '*' in original
            original_word_text = word_details[5].strip()
            if (word_text_cleaned == code_upper or
                original_word_text == code_upper + '*' or
                original_word_text == '*' + code_upper):

                 # Basic check: does the next word look like '-'? (Or is it part of hyphenated word?)
                 is_hyphenated = '-' in original_word_text and original_word_text.upper().startswith(code_upper + '-')
                 next_is_hyphen = i + 1 < len(words) and words[i+1][5] == '-'

                 if next_is_hyphen or is_hyphenated or code in ["NA", "OA", "CM"]: # Assume NA, OA, CM don't need hyphen check
                     code_word_index = i
                     code_word_details = word_details
                     logger.debug(f"      Found potential code word '{original_word_text}' at index {i}")
                     break


        if code_word_index == -1:
            logger.debug(f"      Could not find word for code {code}.")
            return None

        page_num, x0, y0, x1, y1, _, _, _, _ = code_word_details # Coordinates of the code word

        # Search subsequent words on the same line for costs
        cost_words_on_line = []
        y_tolerance = 5 # Vertical tolerance for words on the same line
        max_words_to_check = 30 # Limit search distance

        for i in range(code_word_index + 1, min(code_word_index + max_words_to_check, len(words))):
            word_details = words[i]
            # Check page and vertical position
            if word_details[0] == page_num and abs(word_details[2] - y0) < y_tolerance:
                cost_words_on_line.append(word_details[5]) # Add the word text
            elif word_details[0] != page_num or word_details[2] > y1 + y_tolerance:
                 # Stop if we move to the next page or significantly below the current line
                 break

        combined_cost_text = " ".join(cost_words_on_line)
        logger.debug(f"      Text on same line after code {code}: '{combined_cost_text[:100]}...'")

        # --- Try to extract numeric costs ---
        single_cost = None
        multi_cost = None
        extracted_numeric = False

        # Look for two dollar amounts first
        two_costs_match = re.search(r"\$(\d+(?:\.\d+)?)\s+\$(\d+(?:\.\d+)?)", combined_cost_text)
        if two_costs_match:
            single_cost = self._parse_price_value(two_costs_match.group(1))
            multi_cost = self._parse_price_value(two_costs_match.group(2))
            if single_cost is not None:
                extracted_numeric = True
                logger.debug(f"      Numeric costs found (2 values): S={single_cost}, M={multi_cost}")
        else:
            # Look for a single dollar amount
            one_cost_match = re.search(r"\$(\d+(?:\.\d+)?)", combined_cost_text)
            if one_cost_match:
                single_cost = self._parse_price_value(one_cost_match.group(1))
                if single_cost is not None:
                    extracted_numeric = True
                    logger.debug(f"      Numeric cost found (1 value): S={single_cost}")

        if extracted_numeric:
            costs = {"single_cost": single_cost}
            if multi_cost is not None:
                costs["multi_cost"] = multi_cost
            return costs

        # --- If no numeric costs, look for pricing strings ---
        # Check the combined text on the line AND potentially text near the code word itself
        pricing_strings = [
            "Covered With Additional Copay, 80% of U&C to Max",
            "Covered With Additional Copay, 80% of U&C",
            "Covered With Additional Copay",
            "Covered",
        ]
        # Check text immediately following code word + cost words
        search_text_for_strings = words[code_word_index][5] + " " + combined_cost_text
        for price_str in pricing_strings:
            if price_str in search_text_for_strings:
                 # Basic check: ensure we didn't *also* find a numeric price on the line
                 if re.search(r"\$(\d+(?:\.\d+)?)", combined_cost_text):
                     logger.debug(f"      Found string '{price_str}' for {code}, but also numeric price. Preferring numeric.")
                     # If numeric extraction failed parsing but pattern matched, maybe reconsider? For now, prefer numeric if pattern matches.
                     return None # Let potential numeric extraction (even if parsing failed) take precedence
                 else:
                     logger.debug(f"      String match found for {code}: '{price_str}'")
                     return {"cost_description": price_str}

        # --- If same-line search failed, check line below for specific cases (like Custom Progressives) ---
        logger.debug(f"      No cost found on same line for {code}. Checking line below.")
        words_below = []
        found_line_below = False
        for i in range(code_word_index + 1, min(code_word_index + max_words_to_check, len(words))):
            word_details = words[i]
            # Check page
            if word_details[0] != page_num:
                continue

            # Check if it's on the line below (y0 > y1 of code word)
            # and horizontally aligned or slightly indented (x0 >= code_word's x0 - tolerance)
            x_tolerance = 20
            # Ensure y-coordinates are compared correctly (word_details[2] is y0, word_details[4] is y1)
            if word_details[2] > y1 and abs(word_details[1] - x0) < x_tolerance:
                 words_below.append(word_details[5])
                 found_line_below = True
            # Stop searching below if we hit a word significantly lower or on the next page
            elif found_line_below and (word_details[2] > y1 + (y1 - y0) + y_tolerance or word_details[0] != page_num):
                 break

        if words_below:
            combined_below_text = " ".join(words_below)
            logger.debug(f"      Text on line below code {code}: '{combined_below_text[:100]}...'")
            # Look for a single dollar amount on the line below
            one_cost_match_below = re.search(r"\$(\d+(?:\.\d+)?)", combined_below_text)
            if one_cost_match_below:
                single_cost_below = self._parse_price_value(one_cost_match_below.group(1))
                if single_cost_below is not None:
                    logger.debug(f"      Numeric cost found on line below: S={single_cost_below}")
                    # Assume single cost only for line below cases unless proven otherwise
                    return {"single_cost": single_cost_below}

        logger.debug(f"      No pricing found for {code} using word analysis (including line below).")
        return None


    def _parse_price_value(self, price_str: Optional[str]) -> Optional[Union[int, float]]:
        """ Parses a string price into int or float. """
        if price_str is None:
            return None
        try:
            price = float(price_str)
            return int(price) if price.is_integer() else price
        except (ValueError, TypeError):
            return None


    # Optional: Helper to clean empty entries if needed
    # def _clean_empty_lens_entries(self, categories): ...


    def _merge_and_format_results(self, record_data: Dict, lens_data: Dict, doc_types: List[str]) -> Dict[str, Any]:
        """
        Merges data from Patient Record and Lens Enhancement processing
        and formats it according to the VSPTemplate.
        Placeholder - logic to be implemented based on design plan.

        Args:
            record_data: Data extracted from patient record sections.
            lens_data: Data extracted from lens enhancement sections.
            doc_types: List of identified document types.

        Returns:
            A single dictionary conforming to the VSPTemplate structure.
        """
        logger.info("Merging and formatting VSP results...")
        final_result = {}

        # Determine document type/title
        if "patient_record" in doc_types and "lens_enhancement" in doc_types:
            final_result["document_type"] = "vsp_combined"
            final_result["document_title"] = "VSP Combined Insurance Benefits"
        elif "patient_record" in doc_types:
            final_result["document_type"] = "vsp_patient_record"
            final_result["document_title"] = "VSP Patient Record Report"
        elif "lens_enhancement" in doc_types:
            final_result["document_type"] = "vsp_lens_enhancement_charges"
            final_result["document_title"] = "VSP Lens Enhancement Charges"
        else:
             final_result["document_type"] = "vsp_unknown"
             final_result["document_title"] = "VSP Document (Unknown Type)"


        from datetime import datetime
        import copy

        # Start with a base structure (can use Pydantic model defaults if desired)
        # Keep the document_type and document_title already determined
        base_result = {
            "document_type": final_result.get("document_type", "vsp_unknown"),
            "document_title": final_result.get("document_title", "VSP Document"),
            "patient_info": None,
            "eligibility_info": None,
            "plan_details": None,
            "lens_categories": None,
            "custom_id": None, # Assuming this might come from record_data or elsewhere
            "metadata": None,
        }
        final_result = base_result # Use this merged dict going forward

        # Merge Patient Record Data
        if record_data:
            final_result["patient_info"] = record_data.get("patient_info")
            final_result["eligibility_info"] = record_data.get("eligibility_info")
            final_result["plan_details"] = record_data.get("plan_details")
            # Assuming custom_id might be part of patient_info or record_data directly
            # Use Auth# (id_number) if no other custom ID found
            patient_info_dict = final_result["patient_info"] or {}
            final_result["custom_id"] = record_data.get("custom_id", patient_info_dict.get("id_number"))

        # Merge Lens Enhancement Data (make a copy to avoid modifying original)
        if lens_data and "lens_categories" in lens_data:
            final_result["lens_categories"] = copy.deepcopy(lens_data.get("lens_categories", [])) # Ensure it's a list

            # --- Apply Override Logic ---
            # Check if record_data exists and has the covered codes list
            if record_data and "covered_items_codes" in record_data:
                covered_codes = record_data["covered_items_codes"]
                if covered_codes and final_result["lens_categories"]: # Check if list is not empty
                    logger.info(f"Applying overrides for covered codes identified in Patient Record: {covered_codes}")
                    for category in final_result["lens_categories"]:
                        if category and "subcategories" in category:
                            for subcategory in category["subcategories"]:
                                if subcategory and "options" in subcategory:
                                    for option in subcategory["options"]:
                                        if option and option.get("code") in covered_codes:
                                            logger.debug(f"Overriding cost for covered code: {option.get('code')}")
                                            option["single_cost"] = 0
                                            option["multi_cost"] = 0
                                            option["cost_description"] = "Covered" # Explicitly mark as covered based on Patient Record

        # Add Metadata
        final_result["metadata"] = {
            "processingDate": datetime.now().isoformat()
        }

        # --- Final Formatting/Cleanup ---
        # Ensure structure matches VSPTemplate as closely as possible
        # Ensure required top-level keys exist even if empty
        for key in ["patient_info", "eligibility_info", "plan_details", "lens_categories", "metadata"]:
             if key not in final_result or final_result[key] is None:
                 # Initialize with empty dict/list based on expected type
                 # Check the Pydantic model for default types if available
                 final_result[key] = [] if key == "lens_categories" else {}

        # Note: Pydantic validation could be added here for stricter checking
        # try:
        #     VSPTemplate(**final_result)
        #     logger.info("Final result structure validated against VSPTemplate.")
        # except Exception as validation_error:
        #     logger.error(f"Final result validation failed: {validation_error}", exc_info=True)

        logger.info("Finished merging and formatting VSP results.")

        return final_result


    # --- Keep and Refine Old Methods (excluding frequency) for _process_patient_record ---

    async def _extract_plan_info(self, text: str) -> Dict[str, Any]:
        """ Extracts plan name and effective date. (Refined from original) """
        plan_info = {}
        # Extract plan name (Consider refining regex based on samples)
        # Example: "BenefitVSP Choice Plan Client Name..." (vsp1.pdf)
        plan_name_match = re.search(r"(?:Benefit|Client Name:|Plan Name)\s*(VSP\s+[A-Za-z0-9\s]+?)(?:\s+Client Name|\n|$)", text, re.IGNORECASE)
        if plan_name_match:
            plan_info["plan_name"] = plan_name_match.group(1).strip()
            self.set_confidence("plan_details.plan_name", 0.9) # Confidence tracking needs review

        # Extract effective date (Auth Eff Date)
        date_match = re.search(r"Auth\s+Eff\s+Date\s+(\d{1,2}/\d{1,2}/\d{2,4})", text, re.IGNORECASE)
        if date_match:
             # This might not be the 'plan' effective date, but authorization date. Revisit if needed.
             # plan_info["effective_date"] = date_match.group(1)
             # self.set_confidence("effective_date", 0.9)
             pass # Skipping for now as it's not in final template

        # Extract Auth# as id_number
        auth_match = re.search(r"Auth#\s*(\d+)", text)
        if auth_match:
            plan_info["id_number"] = auth_match.group(1)
            self.set_confidence("patient_info.id_number", 0.95)

        # Extract Patient Name (and redact)
        name_match = re.search(r"Patient\s+Name\s+([A-Z\s,']+)", text, re.IGNORECASE)
        if name_match:
            plan_info["patient_name"] = "[REDACTED]"
            self.set_confidence("patient_info.patient_name", 0.95)

        return plan_info

    async def extract_exam_benefits(self, text: str) -> Dict[str, Any]:
        """ Extracts exam copay. (Refined from original, frequency removed) """
        exam_benefits = {}
        # Look for exam copay (Consider specific "Exam Copay" line like in vsp1.pdf)
        exam_copay_patterns = [
            r"Exam\s+Copay\s*\$(\d+(?:\.\d+)?)", # More specific
            r"(?:WellVision\s+Exam|Eye\s+Exam).*?(?:copay|copayment)?\s*(?:of)?\s*\$(\d+(?:\.\d+)?)",
        ]
        for pattern in exam_copay_patterns:
            copay_match = re.search(pattern, text, re.IGNORECASE)
            if copay_match:
                # Store as float/int
                try:
                    cost = float(copay_match.group(1))
                    exam_benefits["exam_copay"] = int(cost) if cost.is_integer() else cost
                    self.set_confidence("plan_details.copays.exam", 0.85) # Adjust path
                    break
                except ValueError:
                    logger.warning(f"Could not parse exam copay value: {copay_match.group(1)}")
        return exam_benefits

    async def extract_material_benefits(self, text: str) -> Dict[str, Any]:
        """ Extracts frame allowance and lens copay. (Refined from original, frequency removed) """
        material_benefits = {}
        frame_allowance_details = {}

        # Extract materials copay (Less common? Check samples)
        # materials_copay_pattern = r"(?:Materials|Prescription\s+Glasses)\s+(?:Copay|Copayment)(?:\s+of)?\s*\$(\d+)"
        # materials_match = re.search(materials_copay_pattern, text, re.IGNORECASE)
        # if materials_match:
        #     material_benefits["materials_copay"] = f"${materials_match.group(1)}" # Store as number
        #     self.set_confidence("materials_copay", 0.85)

        # Extract frame allowance (More complex based on vsp1.pdf)
        # Look for base allowance
        allowance_match = re.search(r"Frame\s+Allowance.*?\$(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if allowance_match:
             try:
                 # This might be a base or specific type, need context
                 # For now, store generically, refine later if needed
                 base_allowance = float(allowance_match.group(1))
                 # material_benefits["frame_allowance_base"] = int(base_allowance) if base_allowance.is_integer() else base_allowance
                 # self.set_confidence("plan_details.frame_allowance.base", 0.8)
             except ValueError:
                 logger.warning(f"Could not parse frame allowance value: {allowance_match.group(1)}")

        # Look for Altair/Marchon specific allowance (vsp1.pdf line 49)
        altair_match = re.search(r"Altair\s+Eyewear/Marchon\s+frames.*?\$(\d+(?:\.\d+)?)", text, re.IGNORECASE)
        if altair_match:
            try:
                cost = float(altair_match.group(1))
                frame_allowance_details["altair_marchon"] = int(cost) if cost.is_integer() else cost
                self.set_confidence("plan_details.frame_allowance.altair_marchon", 0.9)
            except ValueError:
                 logger.warning(f"Could not parse Altair/Marchon allowance: {altair_match.group(1)}")

        # Look for non-Altair/Marchon allowance (vsp1.pdf line 50)
        # Use a very specific pattern including the line code WFA76
        non_altair_match = re.search(r"WFA76\s+\$(\d+(?:\.\d+)?)\s+for\s+non-Altair\s+Eyewear/Marchon\s+frames", text, re.IGNORECASE)
        if non_altair_match:
             try:
                # Ensure we are capturing the correct value associated with this line
                cost_str = non_altair_match.group(1)
                cost = float(cost_str)
                frame_allowance_details["non_altair_marchon"] = int(cost) if cost.is_integer() else cost
                self.set_confidence("plan_details.frame_allowance.non_altair_marchon", 0.9)
                logger.debug(f"Extracted non-Altair allowance: {cost}")
             except ValueError:
                 logger.warning(f"Could not parse non-Altair/Marchon allowance: {non_altair_match.group(1)}")
             except IndexError:
                 logger.warning(f"Regex pattern for non-Altair allowance matched but failed to capture group.")


        # Look for promotion (vsp1.pdf line 48)
        promo_match = re.search(r"Extra\s+\$(\d+(?:\.\d+)?)\s+promotion", text, re.IGNORECASE)
        if promo_match:
            try:
                cost = float(promo_match.group(1))
                frame_allowance_details["promotion"] = int(cost) if cost.is_integer() else cost
                self.set_confidence("plan_details.frame_allowance.promotion", 0.9)
            except ValueError:
                 logger.warning(f"Could not parse frame promotion: {promo_match.group(1)}")

        if frame_allowance_details:
             material_benefits["frame_allowance"] = frame_allowance_details


        # Extract lens-specific copay (Less common? Check samples)
        # lens_copay_pattern = r"(?:Lenses|Single\svision\slenses).*?(?:copay|copayment)(?:\s+of)?\s*\$(\d+)"
        # lens_copay_match = re.search(lens_copay_pattern, text, re.IGNORECASE)
        # if lens_copay_match:
        #     material_benefits["lens_copay"] = f"${lens_copay_match.group(1)}" # Store as number
        #     self.set_confidence("lens_copay", 0.8)

        return material_benefits

    async def extract_contact_benefits(self, text: str) -> Dict[str, Any]:
        """ Extracts contact lens allowance and exam copay. (Refined from original, frequency removed) """
        contact_benefits = {}

        # Extract contact lens allowance/materials (vsp1.pdf line 54)
        contacts_allowance_pattern = r"CL\s+Materials\s*\$(\d+(?:\.\d+)?)"
        contacts_match = re.search(contacts_allowance_pattern, text, re.IGNORECASE)
        if contacts_match:
            try:
                cost = float(contacts_match.group(1))
                contact_benefits["contacts_allowance"] = int(cost) if cost.is_integer() else cost
                self.set_confidence("plan_details.contacts_allowance", 0.85) # Adjust path if needed
            except ValueError:
                 logger.warning(f"Could not parse contacts allowance: {contacts_match.group(1)}")

        # Extract contact lens exam copay (vsp1.pdf line 53)
        contacts_copay_pattern = r"CL\s+Exam\s+Services.*?Charge.*?\$(\d+(?:\.\d+)?)\s+copay"
        contacts_copay_match = re.search(contacts_copay_pattern, text, re.IGNORECASE)
        if contacts_copay_match:
            try:
                cost = float(contacts_copay_match.group(1))
                contact_benefits["contacts_exam_copay"] = int(cost) if cost.is_integer() else cost
                self.set_confidence("plan_details.copays.contacts_exam", 0.8) # Adjust path
            except ValueError:
                 logger.warning(f"Could not parse contacts exam copay: {contacts_copay_match.group(1)}")

        return contact_benefits

    # Note: _extract_lens_options is removed as its logic will be part of _process_lens_enhancement

    # --- Helper for Eligibility ---
    def _extract_eligibility(self, text: str) -> Dict[str, Optional[bool]]:
        """ Extracts eligibility flags based on PATIENT COVERAGE section """
        eligibility = {"exam": None, "lens": None, "frame": None, "contact_lens_exam": None, "contacts": None}
        # Find the eligibility line (e.g., "EligibilityExam/ProfSvcs YESLens YESFrame YES...")
        eligibility_section_match = re.search(r"Eligibility\s*(.*?)(?:Service Freq|$)", text, re.IGNORECASE | re.DOTALL)
        if eligibility_section_match:
            eligibility_text = eligibility_section_match.group(1).replace("\n", " ").replace(" ", "")

            # Check for YES/NO for each category
            if "Exam/ProfSvcsYES" in eligibility_text: eligibility["exam"] = True
            elif "Exam/ProfSvcsNO" in eligibility_text: eligibility["exam"] = False

            if "LensYES" in eligibility_text: eligibility["lens"] = True
            elif "LensNO" in eligibility_text: eligibility["lens"] = False

            # Treat presence of Frame info as True unless explicitly NO
            if "FrameNO" in eligibility_text:
                eligibility["frame"] = False
            elif re.search(r"Frame", eligibility_text, re.IGNORECASE): # Check if Frame is mentioned at all
                 eligibility["frame"] = True # Assume eligible if mentioned and not NO

            if "ContactLensExamYES" in eligibility_text: eligibility["contact_lens_exam"] = True
            elif "ContactLensExamNO" in eligibility_text: eligibility["contact_lens_exam"] = False

            if "ContactsYES" in eligibility_text: eligibility["contacts"] = True
            elif "ContactsNO" in eligibility_text: eligibility["contacts"] = False

            # Set confidence based on whether we found the section
            self.set_confidence("eligibility_info", 0.9)
        else:
            logger.warning("Could not find Eligibility section in patient record text.")
            self.set_confidence("eligibility_info", 0.1)

        return eligibility

    def _find_section_pricing_string(self, words: List[Tuple], subcategory_name: str) -> Optional[str]:
        """
        Finds a section-level pricing string (Covered, etc.) near a subcategory name.
        """
        header_word_index = -1
        header_word_details = None
        name_words = subcategory_name.split()
        if not name_words: return None

        # Find the first word of the subcategory name
        for i, word_details in enumerate(words):
            word_text = word_details[5].strip()
            # Simple match on first word for now, might need refinement
            if word_text.lower() == name_words[0].lower():
                 # Check if subsequent words match the rest of the name (basic check)
                 match = True
                 for j, name_part in enumerate(name_words[1:]):
                     if i + 1 + j >= len(words) or words[i+1+j][5].strip().lower() != name_part.lower():
                         match = False
                         break
                 if match:
                     header_word_index = i
                     header_word_details = word_details
                     logger.debug(f"      Found potential header '{subcategory_name}' at index {i}")
                     break

        if header_word_index == -1:
            logger.debug(f"      Could not find header word for subcategory '{subcategory_name}'.")
            return None

        page_num, x0, y0, x1, y1, _, _, _, _ = header_word_details

        # Search subsequent words on the same line or line below for pricing strings
        search_words = []
        y_tolerance = 15 # Allow slightly more vertical distance for section headers
        max_words_to_check = 40

        for i in range(header_word_index + len(name_words), min(header_word_index + max_words_to_check, len(words))):
            word_details = words[i]
            # Check page and vertical position (allow same line or one line below)
            if word_details[0] == page_num and (abs(word_details[2] - y0) < y_tolerance or (word_details[2] > y1 and word_details[2] < y1 + (y1-y0) + y_tolerance)):
                search_words.append(word_details[5])
            elif word_details[0] != page_num or word_details[2] > y1 + (y1-y0) + y_tolerance*2: # Stop if too far down
                 break

        combined_search_text = " ".join(search_words)
        logger.debug(f"      Text near header '{subcategory_name}': '{combined_search_text[:100]}...'")

        pricing_strings = [
            "Covered With Additional Copay, 80% of U&C to Max",
            "Covered With Additional Copay, 80% of U&C",
            "Covered With Additional Copay",
            "Covered",
        ]

        for price_str in pricing_strings:
            if price_str in combined_search_text:
                # Ensure a numeric price isn't closer/part of the string itself
                if not re.search(r"\$(\d+(?:\.\d+)?)", combined_search_text):
                    logger.debug(f"      Section string match found for '{subcategory_name}': '{price_str}'")
                    return price_str
                else:
                    logger.debug(f"      Found section string '{price_str}' but also numeric price nearby. Ignoring string for section level.")


        logger.debug(f"      No section pricing string found for '{subcategory_name}'.")
        return None


    # --- Implementations for BaseExtractor Abstract Methods ---
    # These are required by the base class but our primary logic is in
    # _process_patient_record and _process_lens_enhancement.
    # We provide minimal implementations here.

    # Note: We already implemented extract_exam_benefits

    async def extract_frame_benefits(self, document_text: str) -> str:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_frame_benefits called (placeholder)")
        # Logic is handled within _process_patient_record -> extract_material_benefits
        # BaseExtractor expects a string return, but our data is structured.
        # Return empty string or perhaps a summary if needed?
        return "" # Or potentially extract just the allowance string if required by caller

    async def extract_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_lens_benefits called (placeholder)")
        # Logic is handled within _process_patient_record and _process_lens_enhancement
        return {}

    async def extract_progressive_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_progressive_lens_benefits called (placeholder)")
        # Logic is handled within _process_lens_enhancement
        return {}

    async def extract_lens_options(self, document_text: str) -> Dict[str, Any]:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_lens_options called (placeholder)")
        # Logic is handled within _process_lens_enhancement
        return {}

    async def extract_contact_lens_fit(self, document_text: str) -> Dict[str, Any]:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_contact_lens_fit called (placeholder)")
        # Logic is handled within _process_patient_record -> extract_contact_benefits
        return {}

    async def extract_contact_lenses(self, document_text: str) -> Dict[str, Any]:
        """ Placeholder implementation for abstract method. """
        logger.debug("VSPExtractor.extract_contact_lenses called (placeholder)")
        # Logic is handled within _process_patient_record -> extract_contact_benefits
        return {}

    # BaseExtractor methods like preprocess_text, get_result, set_confidence are inherited