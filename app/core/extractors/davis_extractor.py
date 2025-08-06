"""
Davis Vision specific document extraction logic.
"""
import re
import logging
from typing import Dict, Any, Optional, Union, Type, List
import fitz  # PyMuPDF
import json # Added for debug output
from pydantic import BaseModel
import os

from app.core.extractors.base_extractor import BaseExtractor
from app.core.templates.davis_template import DavisTemplate, BenefitItem, BenefitValue # Import necessary models
from app.config import davis_mapping
from app.config.term_dictionary import find_standard_term, get_provider_specific_term, VISION_INSURANCE_TERMS

logger = logging.getLogger(__name__)

class DavisExtractor(BaseExtractor):
    """
    Extracts benefit information from Davis Vision PDF documents.
    Follows the plan outlined in docs/davis_architecture/davis_extraction_plan.md.
    """

    def __init__(self):
        """Initialize the Davis Vision extractor."""
        super().__init__("Davis Vision") # Match provider name in template
        self.output_template = DavisTemplate

    async def extract(self, document_text: str, document_path: str) -> Dict[str, Any]:
        """
        Extract structured benefit information from Davis Vision documents.

        Args:
            document_text: Raw text extracted previously (may not be used if processing path directly).
            document_path: Path to the original PDF document file.

        Returns:
            Dictionary containing structured Davis Vision benefit information.
        """
        logger.info(f"Starting Davis Vision extraction for: {document_path}")
        full_text = ""
        extracted_data = {}

        try:
            # 1. Load PDF & Extract Text
            doc = fitz.open(document_path)
            for page_num, page in enumerate(doc):
                # Extract text using layout mode for general processing
                full_text += page.get_text("text") + "\n\n"

            doc.close()

            # DEBUG: Save raw text to file for inspection
            debug_filename = os.path.join("debug_output", os.path.basename(document_path) + "_raw_text.txt")
            with open(debug_filename, "w", encoding="utf-8") as f:
                f.write(full_text)
            logger.info(f"Saved raw text to {debug_filename} for debugging")

            # 2. Preprocess Text
            processed_text = await self._preprocess_text(full_text)

            # 3. Initial PHI Redaction (Placeholder)
            processed_text = await self._redact_phi(processed_text, initial=True)

            # Log found section headers for debugging
            section_headers = re.findall(r'SECTION [IVX]+ - [A-Z ]+SECTION', processed_text, re.IGNORECASE)
            logger.info(f"Found section headers in document: {section_headers}")

            # 4. Isolate Sections (Still useful for Coverage/Allowance)
            coverage_text = await self._isolate_section(processed_text, "SECTION II - COVERAGE SECTION", None)
            allowance_text = await self._isolate_section(processed_text, "SECTION III - ALLOWANCE SECTION", None)
            # We might not need isolated options_text if table extraction works, but keep for fallback
            options_text = await self._isolate_section(processed_text, "SECTION IV - OPTIONS SECTION", None)

            # Log the section texts (summary only to avoid flooding logs)
            logger.info(f"Coverage section length: {len(coverage_text)} chars")
            logger.info(f"Allowance section length: {len(allowance_text)} chars")
            logger.info(f"Options section (from text) length: {len(options_text)} chars")

            # 5. Extract Data from Sections
            coverage_info = await self._extract_coverage(coverage_text)
            allowance_info = await self._extract_allowances(allowance_text)
            # Now only pass options_text to _extract_options, as table data is no longer used
            lens_benefits = await self._extract_options(options_text, None, None)

            # Log extraction results at high level
            if lens_benefits:
                logger.info("Lens benefits extraction results summary:")
                # Log progressive lens results
                if lens_benefits.progressive_lenses:
                    prog = lens_benefits.progressive_lenses
                    logger.info(f"  Progressive lenses: standard={prog.standard_tier_pal}, premium={prog.premium_tier_pal}, ultra={prog.ultra_tier_pal}, ultimate={prog.ultimate_tier_pal}")
                # Log AR coating results
                if lens_benefits.anti_reflective_lenses:
                    ar = lens_benefits.anti_reflective_lenses
                    logger.info(f"  AR coatings: standard={ar.standard_tier_ar}, premium={ar.premium_tier_ar}, ultra={ar.ultra_tier_ar}, ultimate={ar.ultimate_tier_ar}")
                # Log photochromic results
                if lens_benefits.photochromic_lenses:
                    photo = lens_benefits.photochromic_lenses
                    logger.info(f"  Photochromic: {photo.plastic_photosensitive}")
                # Log polarized results
                if lens_benefits.polarized_lenses:
                    polar = lens_benefits.polarized_lenses
                    logger.info(f"  Polarized: {polar.polarized}")

            # 6. Combine Extracted Data into a dictionary suitable for template instantiation
            # We use the aliases defined in the models as keys where appropriate
            combined_data = {}
            if coverage_info:
                 combined_data[DavisTemplate.__fields__['coverage'].alias] = coverage_info
            if allowance_info:
                 combined_data[DavisTemplate.__fields__['allowances'].alias] = allowance_info
            if lens_benefits:
                 combined_data['lens_benefits'] = lens_benefits # Assuming 'lens_benefits' is the direct field name

            # Add other potential top-level fields if extracted (e.g., plan_name, custom_id)
            # combined_data['plan_name'] = extracted_plan_name etc.

            # 7. Final PHI Redaction (Targeted)
            # Example: If we extracted subscriber_id into combined_data
            # if 'subscriber_id' in combined_data:
            #    combined_data['subscriber_id'] = "[REDACTED]"
            # Apply to any other PHI fields as needed based on actual extraction results.
            # Since the current template doesn't have explicit PHI fields, this is mostly illustrative.

            # 8. Instantiate Template & Output
            result = self.output_template(**combined_data)
            # Use by_alias=True to ensure output keys match the JSON template structure (using aliases)
            # Use exclude_none=True to avoid cluttering output with fields that weren't found
            # self.extracted_data = result.dict(exclude_none=True, by_alias=True)
            # Use the custom template JSON method to ensure proper format with "none" values
            self.extracted_data = result.to_template_json()
            logger.info(f"Successfully extracted data for: {document_path}")
            return self.extracted_data

        except Exception as e:
            logger.error(f"Error during Davis Vision extraction for {document_path}: {str(e)}", exc_info=True)
            # Return error structure
            error_result = self.output_template(error=f"Extraction failed: {str(e)}")
            # Update error result to also use template JSON format
            return error_result.to_template_json()

    async def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing."""
        # Normalize whitespace, potentially remove headers/footers later if needed
        text = re.sub(r' +', ' ', text) # Replace multiple spaces with single
        text = re.sub(r'\n\s*\n', '\n\n', text) # Normalize multiple newlines
        return text.strip()

    async def _redact_phi(self, text: str, initial: bool = False) -> str:
        """Placeholder for PHI redaction."""
        # In initial pass, could redact names, complex IDs from raw text
        # In final pass (initial=False), would redact specific fields in the structured data
        # For now, just return text
        if initial:
             # Example: Redact typical name patterns if needed before parsing
             # text = re.sub(r'Patient Name:\s*\S+', 'Patient Name: [REDACTED]', text, flags=re.IGNORECASE)
             # text = re.sub(r'Employee ID No.:\s*\S+', 'Employee ID No.: [REDACTED]', text, flags=re.IGNORECASE)
             pass
        # Final redaction would happen on the structured dict before returning
        return text
        
    def _standardize_term(self, term: str, category: str) -> str:
        """
        Use the term dictionary to standardize terms before searching for them.
        
        Args:
            term: The term or variation to standardize
            category: The category in the term dictionary (e.g., 'lens_types', 'pricing_terms')
            
        Returns:
            The standardized term or the original if not found
        """
        return find_standard_term(category, term)
        
    def _get_davis_terms(self, standard_term: str, category: str) -> List[str]:
        """
        Get Davis-specific variations of a standard term from the term dictionary.
        
        Args:
            standard_term: The standardized term to look up
            category: The category in the term dictionary
            
        Returns:
            List of Davis-specific variations for the term, or empty list if not found
        """
        davis_terms = get_provider_specific_term("davis", category, standard_term)
        if not davis_terms:
            return []
        
        # Handle both string and list returns
        if isinstance(davis_terms, str):
            return [davis_terms]
        return davis_terms

    async def _isolate_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """
        Isolate text between start and end markers, regardless of their order in the document.
        
        This improved version handles documents where sections may appear in any order due to
        multi-column layouts being linearized during text extraction.
        """
        try:
            # Find ALL section headers in the document first
            section_headers = re.findall(r'SECTION [IVX]+ - [A-Z ]+SECTION', text, re.IGNORECASE)
            logger.debug(f"Found section headers: {section_headers}")
            
            # Find the start marker
            start_match = re.search(re.escape(start_marker), text, re.IGNORECASE)
            if not start_match:
                logger.warning(f"Could not find section start marker: '{start_marker}'")
                return ""
            
            start_index = start_match.end()
            
            # If there's no end marker specified, take text to the end
            if not end_marker:
                return text[start_index:].strip()
            
            # Create a list of all possible end markers (all other section headers)
            # This allows us to handle sections appearing in any order
            possible_end_markers = []
            for header in section_headers:
                if not re.search(re.escape(start_marker), header, re.IGNORECASE):
                    possible_end_markers.append(header)
            
            # Add the specific end_marker if not already in possible_end_markers
            if end_marker not in possible_end_markers:
                possible_end_markers.append(end_marker)
            
            logger.debug(f"Possible end markers for '{start_marker}': {possible_end_markers}")
            
            # Find the nearest end marker that appears AFTER the start_index
            nearest_end_index = None
            for marker in possible_end_markers:
                marker_match = re.search(re.escape(marker), text[start_index:], re.IGNORECASE)
                if marker_match:
                    end_pos = start_index + marker_match.start()
                    if nearest_end_index is None or end_pos < nearest_end_index:
                        nearest_end_index = end_pos
            
            # If we found any end marker, use it; otherwise take text to the end
            if nearest_end_index:
                return text[start_index:nearest_end_index].strip()
            else:
                logger.warning(f"No end markers found after '{start_marker}'. Taking text until end.")
                return text[start_index:].strip()
                
        except AttributeError as e:
            logger.warning(f"Error finding section: {str(e)}")
            return "" # Return empty string if section not found

    async def _parse_value(self, value_str: Optional[str]) -> BenefitValue:
        """Parse extracted string value into number or specific string."""
        if value_str is None:
            logger.debug("parse_value: input is None, returning 'none'")
            return "none"  # Return "none" string instead of None

        logger.debug(f"parse_value: processing value string: '{value_str}'")
        
        # Normalize the string: trim whitespace and convert to lowercase
        value_str = value_str.strip().lower()
        logger.debug(f"parse_value: after strip and lowercase: '{value_str}'")

        # Handle special text values - expanded for variations of "included"
        included_variations = ["included", "n/a", "paid in full", "paid-in-full", "covered in full", "covered", "no charge"]
        if any(variation in value_str for variation in included_variations):
            logger.debug(f"parse_value: matched included variation in '{value_str}', returning 0")
            return 0
        elif value_str == "":
            logger.debug("parse_value: empty string, returning 'none'")
            return "none"  # Return "none" string for empty strings
            
        # Handle Davis-specific "dollar plus percentage" format
        if "plus" in value_str:
            try:
                logger.debug(f"parse_value: detected Davis-specific 'plus' format: '{value_str}'")
                parts = value_str.split("plus")
                dollar_part = parts[0].strip()
                percentage_part = parts[1].strip()
                
                # Extract dollar amount
                dollar_match = re.search(r'\$(\d+(?:\.\d+)?)', dollar_part)
                if dollar_match:
                    dollar_amount = float(dollar_match.group(1))
                    logger.debug(f"parse_value: extracted dollar amount from 'plus' format: {dollar_amount}")
                    # Return just the dollar amount as that's the copay
                    return dollar_amount
            except Exception as e:
                logger.warning(f"Failed to parse 'plus' format '{value_str}': {str(e)}")
                # Fall back to regular handling below
            
        # Handle dollar values - improved to handle various formats
        if '$' in value_str:
            try:
                logger.debug(f"parse_value: detected dollar value: '{value_str}'")
                
                # Extract only numeric parts by removing dollar sign, commas, and spaces
                dollar_part = value_str
                
                # Extract numeric part
                numeric_part = ''.join(c for c in dollar_part if c.isdigit() or c == '.')
                
                # Make sure there's only one decimal point at most
                if numeric_part.count('.') > 1:
                    first_decimal = numeric_part.find('.')
                    numeric_part = numeric_part[:first_decimal+1] + numeric_part[first_decimal+1:].replace('.', '')
                
                logger.debug(f"parse_value: extracted numeric part: '{numeric_part}'")
                
                # Convert to float or int
                if numeric_part:
                    result = float(numeric_part) if '.' in numeric_part else int(numeric_part)
                    logger.debug(f"parse_value: converted to numeric value: {result}")
                    return result
                else:
                    logger.warning(f"Could not extract numeric value from: {value_str}")
                    return value_str
            except ValueError:
                logger.warning(f"Could not parse monetary value: {value_str}")
                return value_str # Return original string if parsing fails
                
        # Handle numeric values without $ symbol - improved detection
        elif re.match(r'^\d+(?:\.\d+)?$', value_str) or re.match(r'^[0-9,.]+$', value_str):
            try:
                logger.debug(f"parse_value: detected numeric value without $ symbol: '{value_str}'")
                # Remove commas before converting
                clean_value = value_str.replace(',', '')
                result = float(clean_value) if '.' in clean_value else int(clean_value)
                logger.debug(f"parse_value: converted to numeric value: {result}")
                return result
            except ValueError:
                logger.warning(f"Could not parse numeric value: {value_str}")
                return value_str
        else:
            # Could be a percentage or other description
            logger.debug(f"parse_value: returning as string: '{value_str}'")
            return value_str

    async def _extract_coverage(self, section_text: str) -> Optional[Dict[str, Any]]:
        """Extract data from Section II - Coverage."""
        # Define common value pattern for coverage section
        value_pattern = r"(\$?\d+(?:[.,]\d+)*(?:\s+plus\s+\d+%)?|included|covered|[Pp]aid\s+in\s+[Ff]ull|[Nn]o\s+[Cc]harge|N/A)"

        if not section_text:
            return None
        
        # DEBUG: Save coverage section text for inspection
        with open("debug_output/coverage_section.txt", "w", encoding="utf-8") as f:
            f.write(section_text)
        logger.info("Saved coverage section text to debug_output/coverage_section.txt")
        
        data = {}
        # Use mapping to find terms and extract values
        coverage_map = davis_mapping.DAVIS_TERM_MAP.get("coverage", {})
        
        # Add Davis-specific pricing terms from the term dictionary
        davis_pricing_terms = []
        for pricing_entry in VISION_INSURANCE_TERMS.get("pricing_terms", []):
            if "davis" in pricing_entry.get("providers", {}):
                davis_provider_terms = pricing_entry["providers"]["davis"]
                if isinstance(davis_provider_terms, list):
                    davis_pricing_terms.extend(davis_provider_terms)
        
        logger.info(f"Found {len(davis_pricing_terms)} Davis-specific pricing terms in dictionary")
        
        for key, terms in coverage_map.items():
            found_value = None
            # Get additional Davis-specific variations for each term
            additional_terms = []
            
            # Ensure terms is a list of strings, not nested lists
            flattened_terms = []
            for term in terms:
                if isinstance(term, list):
                    flattened_terms.extend(term)
                else:
                    flattened_terms.append(term)
            
            for term in flattened_terms:
                if not isinstance(term, str):
                    continue  # Skip non-string terms
                
                standard_term = self._standardize_term(term, "pricing_terms")
                davis_terms = self._get_davis_terms(standard_term, "pricing_terms")
                if davis_terms:
                    for davis_term in davis_terms:
                        if isinstance(davis_term, str):
                            additional_terms.append(davis_term)
            
            # Combine original terms with Davis-specific variations
            # Use a loop to ensure we only add strings
            all_terms = []
            for term in flattened_terms:
                if isinstance(term, str) and term not in all_terms:
                    all_terms.append(term)
            for term in additional_terms:
                if isinstance(term, str) and term not in all_terms:
                    all_terms.append(term)
            
            logger.debug(f"Coverage search for {key} - Original terms: {flattened_terms}")
            logger.debug(f"Coverage search for {key} - With Davis terms: {all_terms}")
            
            for term in all_terms:
                # Simplified pattern using \s+
                pattern = rf"{re.escape(term)}\s+{value_pattern}"
                
                match = re.search(pattern, section_text, re.IGNORECASE | re.MULTILINE)
                
                logger.debug(f"Coverage search - Key: '{key}', Term: '{term}', Pattern: '{pattern}'")
                
                if match:
                    logger.debug(f"Coverage match for '{term}': '{match.group(1)}'")
                    raw_value = match.group(1)
                    if key == 'eye_examination': # DEBUG specific key
                        logger.info(f"DEBUG Coverage Raw Match (Direct) for '{term}': '{raw_value}'")
                    found_value = await self._parse_value(raw_value)
                    break # Found value for this key, continue to next key
                else:
                    logger.debug(f"No match found for '{term}' using term-value pattern")
                    
                    # Removed linebreak pattern as it's less relevant for layout mode

                    # Fall back to flexible patterns for any numeric value near the term
                    # This might be less necessary with layout mode, but keep as fallback
                    # Adjusted flexible pattern to use the main value_pattern
                    pattern_flexible = rf"{re.escape(term)}.*?{value_pattern}"
                    match_flexible = re.search(pattern_flexible, section_text, re.IGNORECASE | re.MULTILINE)
                    logger.debug(f"Trying flexible pattern: '{pattern_flexible}'")
                    
                    if match_flexible:
                        # Group 1 captures the value in the simplified flexible pattern
                        value_str = match_flexible.group(1)
                        if key == 'eye_examination': # DEBUG specific key
                            logger.info(f"DEBUG Coverage Raw Match (Flexible) for '{term}': '{value_str}'")
                        logger.debug(f"Coverage match (flexible) for '{term}': '{value_str}'")
                        # Add $ symbol if not present but looks like a dollar amount
                        if '$' not in value_str and re.match(r'\s*\d+', value_str):
                            value_str = '$' + value_str
                        found_value = await self._parse_value(value_str)
                        break
            
            if found_value is not None:
                logger.debug(f"Setting {key} = {found_value}")
            else:
                logger.debug(f"No value found for {key}")
            data[key] = found_value

        # Ensure all keys from the model are present, defaulting to None if not found
        return data


    async def _extract_allowances(self, section_text: str) -> Optional[Dict[str, Any]]:
        """Extract data from Section III - Allowances."""
        # Define a value pattern for allowance amounts/descriptions
        # More general than coverage, as it might include text like "Paid in full" or percentages
        allowance_value_pattern = r"(\$?[0-9,.]+(?:\s*plus\s*\d+%)?|Paid\s+in\s+full(?:\s*\(.*?\))?|.*?)"

        if not section_text:
            return None
            
        # DEBUG: Save allowance section text for inspection
        with open("debug_output/allowance_section.txt", "w", encoding="utf-8") as f:
            f.write(section_text)
        logger.info("Saved allowance section text to debug_output/allowance_section.txt")

        data = {}
        allowance_map = davis_mapping.DAVIS_TERM_MAP.get("allowances", {})
        
        # Allowance section has a different structure - it's often in a table
        # The first row contains headers, followed by rows with values
        # Let's try a more targeted approach for this section
        
        for key, terms in allowance_map.items():
            found_detail = None
            for term in terms:
                 # Look for the term and capture any text that follows until another term or end of text
                 # This pattern works better with table structures where values might be separated by cells
                 pattern = rf"{re.escape(term)}\s+{allowance_value_pattern}"
                 match = re.search(pattern, section_text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                 
                 logger.debug(f"Allowance search - Key: '{key}', Term: '{term}', Pattern: '{pattern}'")
                 
                 if match:
                     description = match.group(1).strip()
                     logger.debug(f"Allowance match for '{term}': '{description}'")
                     # Further clean description if needed (e.g., remove extra spaces)
                     description = re.sub(r'\s+', ' ', description)
                     found_detail = AllowanceDetail(description=description)
                     break # Found description for this key
                 else:
                     logger.debug(f"No match found for '{term}' using main pattern")
                     
                     # Try a more general pattern that looks for any non-empty text after the term
                     # Adjusted general pattern: term, minimal non-greedy chars, then value
                     pattern_general = rf"{re.escape(term)}.*?{allowance_value_pattern}"
                     match_general = re.search(pattern_general, section_text, re.IGNORECASE | re.MULTILINE)
                     logger.debug(f"Trying general pattern: '{pattern_general}'")
                     
                     if match_general:
                         description = match_general.group(1).strip()
                         logger.debug(f"Allowance match (general) for '{term}': '{description}'")
                         description = re.sub(r'\s+', ' ', description)
                         found_detail = {"description": description}
                         break
            
            # Use the key directly for assignment
            data[key] = found_detail
            logger.debug(f"Set allowance.{key} = {found_detail.get('description') if found_detail else None}")

        # Return the allowance data as a dictionary
        return data


    async def _extract_options(self, section_text: str, options_table_data: Optional[List[List[str]]], options_header_row_idx: Optional[int]) -> Optional[Dict[str, Any]]:
        """Extract data from Section IV - Options using regex on the section text."""

        lens_benefits_data = {} # Dict to hold lens benefits data
        options_map = davis_mapping.DAVIS_TERM_MAP.get("lens_benefits", {}) # Load term mapping

        # Check if section text is available
        if not section_text:
            logger.warning("No options text provided for regex extraction.")
            return None

        # Since we're simplifying, we'll just use direct mapping without complex model types
        category_model_map: Dict[str, Type[BaseModel]] = {}

        # Get Davis-specific tier structures from the term dictionary
        davis_progressive_tiers = VISION_INSURANCE_TERMS.get("davis_specific_terms", {}).get("progressive_tiers", [])
        davis_ar_tiers = VISION_INSURANCE_TERMS.get("davis_specific_terms", {}).get("ar_coating_tiers", [])
        tier_terms = {}
        for tier_data in davis_progressive_tiers: tier_terms[f"progressive_{tier_data.get('tier')}"] = tier_data.get("description")
        for tier_data in davis_ar_tiers: tier_terms[f"ar_{tier_data.get('tier')}"] = tier_data.get("description")
        logger.info(f"Found {len(tier_terms)} Davis-specific tier terms in dictionary for regex processing")

        # Process options based on mapping structure
        for category_key, category_items in options_map.items():

            if category_key not in category_model_map:
                 logger.warning(f"Skipping category '{category_key}' as it does not map to a known model type.")
                 continue

            # Case A: Category maps to a sub-model (e.g., progressive_lenses)
            if category_key in category_model_map:
                TargetModel = category_model_map[category_key]
                category_data = {} # Holds data for the sub-model instance
                category_fields = category_items # category_items is the dict of field_key: terms

                # Augment search terms with tier descriptions from dictionary if applicable
                if category_key == "progressive_lenses":
                    for field_key, terms in category_fields.items():
                        for tier_key, tier_description in tier_terms.items():
                            if tier_key.startswith("progressive_") and field_key.replace("_pal", "") == tier_key.replace("progressive_", ""):
                                if isinstance(tier_description, str):
                                    current_terms = terms if isinstance(terms, list) else [terms]
                                    if tier_description not in current_terms:
                                        category_fields[field_key] = current_terms + [tier_description]
                elif category_key == "anti_reflective_lenses":
                     for field_key, terms in category_fields.items():
                        for tier_key, tier_description in tier_terms.items():
                            if tier_key.startswith("ar_") and field_key.replace("_ar", "") == tier_key.replace("ar_", ""):
                                if isinstance(tier_description, str):
                                    current_terms = terms if isinstance(terms, list) else [terms]
                                    if tier_description not in current_terms:
                                        category_fields[field_key] = current_terms + [tier_description]

                # --- Loop through fields within the sub-model category --- 
                for field_key, terms in category_fields.items():
                    found_value = None
                    # Determine the appropriate dictionary category (can be reused)
                    dictionary_category = "lens_treatments"
                    if category_key == "progressive_lenses": dictionary_category = "lens_types"
                    elif category_key in ["photochromic_lenses", "polarized_lenses"]: dictionary_category = "lens_treatments"
                    elif category_key == "anti_reflective_lenses": dictionary_category = "lens_treatments"

                    # --- Get all terms (Flatten, Add Davis variations, Deduplicate - Reuse this block) --- 
                    all_terms = []
                    orig_terms = terms if isinstance(terms, list) else [terms]
                    flattened_terms = []
                    for term in orig_terms:
                        if isinstance(term, list): flattened_terms.extend(term)
                        else: flattened_terms.append(term)
                    additional_terms = []
                    for term in flattened_terms:
                        if not isinstance(term, str): continue
                        standard_term = self._standardize_term(term, dictionary_category)
                        davis_terms = self._get_davis_terms(standard_term, dictionary_category)
                        if davis_terms:
                            for davis_term in davis_terms:
                                if isinstance(davis_term, str): additional_terms.append(davis_term)
                    for term in flattened_terms + additional_terms:
                        if isinstance(term, str) and term not in all_terms:
                            all_terms.append(term)

                    logger.debug(f"Options search (regex) for {category_key}.{field_key} - Terms: {all_terms}")

                    # --- Apply Regex Patterns (Direct, Two-Line - Reuse this block) ---
                    for term in all_terms:
                        # ... (regex pattern definitions and search logic from previous version) ...
                        debug_key = "uv_protection" # Specific key to add detailed logging for
                        value_pattern = r"(\$[\d,.]+(?:\s+plus\s+\d+%)?|Included|N/A)"
                        direct_pattern = rf"\b{re.escape(term)}\b\s+{value_pattern}"
                        direct_match = re.search(direct_pattern, section_text, re.IGNORECASE | re.MULTILINE)
                        is_debug_key = (field_key == debug_key) # Check if current field is the one we're debugging
                        if direct_match:
                             raw_val = direct_match.group(1); logger.debug(f"Regex Direct match for '{term}': '{raw_val}'")
                             if is_debug_key: logger.info(f"DEBUG Options Direct Match Found for '{term}': '{raw_val}'")
                             if raw_val.strip().upper() == 'N/A': found_value = 0
                             else: found_value = await self._parse_value(raw_val)
                             break
                        else:
                             if is_debug_key: logger.info(f"DEBUG Options Direct Match Failed for '{term}'")
                             # Two-line search logic...
                             try:
                                 term_pos = -1
                                 term_pattern = r'\b' + r'\s*\n?\s*'.join(re.escape(part) for part in term.split()) + r'\b'
                                 term_match = re.search(term_pattern, section_text, re.IGNORECASE)
                                 if term_match:
                                     term_pos = term_match.end()
                                     if is_debug_key: logger.info(f"DEBUG Options Two-Line Term Match Found for '{term}'")
                                 else:
                                     if is_debug_key: logger.info(f"DEBUG Options Two-Line Term Match Failed for '{term}' using pattern: {term_pattern}")

                                 if term_pos >= 0:
                                     next_newline_pos = section_text.find('\n', term_pos)
                                     if next_newline_pos != -1:
                                         search_start_pos = next_newline_pos + 1
                                         line_end_pos = section_text.find('\n', search_start_pos)
                                         search_area = section_text[search_start_pos : line_end_pos if line_end_pos != -1 else None]
                                         if is_debug_key: logger.info(f"DEBUG Options Two-Line Search Area for '{term}': '{search_area[:50]}...'")
                                         proximity_match = re.search(r'^\s*' + value_pattern, search_area, re.IGNORECASE)
                                         if proximity_match:
                                             raw_val = proximity_match.group(1); logger.debug(f"Regex Two-Line Proximity match for '{term}': '{raw_val}'")
                                             if is_debug_key: logger.info(f"DEBUG Options Two-Line Proximity Match Found for '{term}': '{raw_val}'")
                                             if raw_val.strip().upper() == 'N/A': found_value = 0
                                             else: found_value = await self._parse_value(raw_val)
                                             break
                                         elif is_debug_key:
                                              logger.info(f"DEBUG Options Two-Line Proximity Match Failed for '{term}' in search area.")
                             except Exception as prox_ex:
                                 logger.warning(f"Error during two-line proximity search for '{term}': {prox_ex}")

                        # --- Assign value to sub-model data --- 
                        target_field_info = TargetModel.__fields__.get(field_key)
                        if target_field_info:
                            model_field_name = target_field_info.alias if target_field_info.alias else field_key
                            category_data[model_field_name] = found_value
                            logger.debug(f"Set {category_key}.{model_field_name} (regex) = {found_value}")
                        else:
                             logger.warning(f"Field key '{field_key}' not found in target model '{TargetModel.__name__}'. Storing with original key.")
                             category_data[field_key] = found_value # Corrected indentation

                    # --- Instantiate the sub-model --- 
                    try:
                        category_data_for_instantiation = {f_name: category_data.get(f_info.alias if f_info.alias else f_name)
                                                           for f_name, f_info in TargetModel.__fields__.items()}
                        lens_benefits_data[category_key] = TargetModel(**category_data_for_instantiation)
                    except Exception as model_error:
                        logger.error(f"Error instantiating model {TargetModel.__name__} (regex) for category {category_key}: {model_error}")
                        lens_benefits_data[category_key] = None

                # Simplified Case B: Store basic data for direct fields
                else:
                    # Store empty data for now to avoid complex model logic
                    lens_benefits_data[category_key] = None
                    logger.debug(f"Simplified extraction for category {category_key}")

            # This completes the mapping logic
 
        # --- Final Assembly --- 
        # Return the lens benefits data as a dictionary
        try:
            return lens_benefits_data
        except Exception as final_model_error:
             logger.error(f"Error creating lens benefits data: {final_model_error}")
             return None

    # Implement required abstract methods from BaseExtractor
    
    async def extract_exam_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract examination benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of examination benefits
        """
        # This implementation uses the newer structured approach
        # but meets the interface requirements
        processed_text = await self._preprocess_text(document_text)
        coverage_text = await self._isolate_section(processed_text, "SECTION II - COVERAGE SECTION", "SECTION III - ALLOWANCE SECTION")
        coverage_info = await self._extract_coverage(coverage_text)
        
        # Return the eye_examination field as a simplified dict if available
        if coverage_info and hasattr(coverage_info, "eye_examination"):
            return {"cost": coverage_info.eye_examination}
        return {"cost": None}
    
    async def extract_frame_benefits(self, document_text: str) -> str:
        """
        Extract frame benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            Frame benefit cost value as a string
        """
        processed_text = await self._preprocess_text(document_text)
        coverage_text = await self._isolate_section(processed_text, "SECTION II - COVERAGE SECTION", "SECTION III - ALLOWANCE SECTION")
        coverage_info = await self._extract_coverage(coverage_text)
        
        # Convert the frame cost to string as required by the interface
        if coverage_info and hasattr(coverage_info, "frame"):
            return str(coverage_info.frame) if coverage_info.frame is not None else ""
        return ""
    
    async def extract_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract lens benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of lens benefits
        """
        processed_text = await self._preprocess_text(document_text)
        coverage_text = await self._isolate_section(processed_text, "SECTION II - COVERAGE SECTION", "SECTION III - ALLOWANCE SECTION")
        coverage_info = await self._extract_coverage(coverage_text)
        
        # Return spectacle_lenses info as a dict if available
        if coverage_info and hasattr(coverage_info, "spectacle_lenses"):
            return {"cost": coverage_info.spectacle_lenses}
        return {"cost": None}
    
    async def extract_progressive_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """
        Extract progressive lens benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of progressive lens benefits
        """
        processed_text = await self._preprocess_text(document_text)
        options_text = await self._isolate_section(processed_text, "SECTION IV - OPTIONS SECTION", None)
        # Need to call _extract_options correctly here
        lens_benefits = await self._extract_options(options_text, None, None) 
        
        # Return data from the progressive_lenses section if available
        result = {}
        if lens_benefits and hasattr(lens_benefits, "progressive_lenses") and lens_benefits.progressive_lenses:
            prog = lens_benefits.progressive_lenses
            if hasattr(prog, "standard_progressive"):
                result["standard"] = prog.standard_progressive
            if hasattr(prog, "premium_progressive"):
                result["premium"] = prog.premium_progressive
            if hasattr(prog, "ultra_progressive"):
                result["ultra"] = prog.ultra_progressive
            if hasattr(prog, "ultimate_progressive"):
                result["ultimate"] = prog.ultimate_progressive
        return result
    
    async def extract_lens_options(self, document_text: str) -> Dict[str, Any]:
        """
        Extract lens options information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of lens options
        """
        processed_text = await self._preprocess_text(document_text)
        options_text = await self._isolate_section(processed_text, "SECTION IV - OPTIONS SECTION", None)
        # Need to call _extract_options correctly here
        lens_benefits = await self._extract_options(options_text, None, None) 
        
        # Combine various lens options into a single dictionary
        result = {}
        
        # Add anti-reflective coatings if available
        if lens_benefits and hasattr(lens_benefits, "anti_reflective_lenses") and lens_benefits.anti_reflective_lenses:
            ar = lens_benefits.anti_reflective_lenses
            if hasattr(ar, "standard_tier_ar"):
                result["anti_reflective_standard"] = ar.standard_tier_ar
            if hasattr(ar, "premium_tier_ar"):
                result["anti_reflective_premium"] = ar.premium_tier_ar
            if hasattr(ar, "ultra_tier_ar"):
                result["anti_reflective_ultra"] = ar.ultra_tier_ar
            if hasattr(ar, "ultimate_tier_ar"):
                result["anti_reflective_ultimate"] = ar.ultimate_tier_ar
                
        # Add polarized lenses if available
        if lens_benefits and hasattr(lens_benefits, "polarized_lenses") and lens_benefits.polarized_lenses:
            pol = lens_benefits.polarized_lenses
            if hasattr(pol, "polarized"):
                result["polarized"] = pol.polarized
                
        # Add photochromic lenses if available
        if lens_benefits and hasattr(lens_benefits, "photochromic_lenses") and lens_benefits.photochromic_lenses:
            photo = lens_benefits.photochromic_lenses
            if hasattr(photo, "plastic_photosensitive"):
                result["photochromic"] = photo.plastic_photosensitive
                
        return result
    
    async def extract_contact_lens_fit(self, document_text: str) -> Dict[str, Any]:
        """
        Extract contact lens fit benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of contact lens fit benefits
        """
        # This provider may not have explicit contact lens fit information
        # in the sample documents, so return empty dictionary
        # We might need to look in Section II for this later
        logger.warning("Contact lens fit extraction not fully implemented for Davis Vision based on current structure.")
        return {}
    
    async def extract_contact_lenses(self, document_text: str) -> Dict[str, Any]:
        """
        Extract contact lenses benefit information.
        
        Args:
            document_text: The extracted text from the document
            
        Returns:
            A dictionary of contact lenses benefits
        """
        processed_text = await self._preprocess_text(document_text)
        # Check Section III (Allowances) first
        allowance_text = await self._isolate_section(processed_text, "SECTION III - ALLOWANCE SECTION", "SECTION IV - OPTIONS SECTION")
        allowance_info = await self._extract_allowances(allowance_text)
        
        result = {}
        
        if allowance_info and hasattr(allowance_info, "contact_lens_material") and allowance_info.contact_lens_material:
            if hasattr(allowance_info.contact_lens_material, "description"):
                result["allowance"] = allowance_info.contact_lens_material.description
                logger.debug(f"Found contact lens allowance in Section III: {result['allowance']}")
                # Potentially return here if allowance is the primary goal
                # return result 

        # If not found in allowances, check Section II (Coverage) for specific contact lens copays/details
        if not result:
             coverage_text = await self._isolate_section(processed_text, "SECTION II - COVERAGE SECTION", "SECTION III - ALLOWANCE SECTION")
             coverage_info = await self._extract_coverage(coverage_text)
             if coverage_info:
                 # Check specific fields in coverage data if they exist (e.g., contact_lens_copay)
                 # Example: if 'contact_lens_copay' in coverage_info: result['copay'] = coverage_info['contact_lens_copay']
                 # Check for Evaluation/Fitting copay specifically mentioned in Coverage
                 if 'contact_lens_evaluation_fitting' in coverage_info and coverage_info['contact_lens_evaluation_fitting'] != 'none':
                     result['evaluation_fitting_copay'] = coverage_info['contact_lens_evaluation_fitting']
                     logger.debug(f"Found contact lens eval/fit copay in Section II: {result['evaluation_fitting_copay']}")

        if not result:
             logger.warning("Could not extract specific contact lens benefit details.")

        return result