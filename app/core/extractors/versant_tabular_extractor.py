"""
Unified Versant Health tabular document extraction logic.
Handles Davis Vision, Superior Vision, and Versant Health documents in tabular format.
"""
import re
import logging
import os
from typing import Dict, Any, Optional, List, Tuple
import fitz  # PyMuPDF

from app.core.extractors.base_extractor import BaseExtractor
from app.core.templates.davis_template import DavisTemplate, BenefitValue, BenefitItem, ExamBenefits, SpectacleLensBenefits, SpectacleLensOptionsBenefits, FrameBenefits
from app.config import davis_mapping
from app.config.term_dictionary import find_standard_term, get_provider_specific_term, VISION_INSURANCE_TERMS

logger = logging.getLogger(__name__)

class VersantTabularExtractor(BaseExtractor):
    """
    Unified extractor for all Versant Health products (Davis Vision, Superior Vision, Versant Health).
    Extracts benefit information from PDF documents in tabular format.
    """

    def __init__(self, provider_name: str = "Versant Health"):
        """
        Initialize the Versant Health extractor.
        
        Args:
            provider_name: The specific provider name (Davis Vision, Superior Vision, or Versant Health)
        """
        super().__init__(provider_name)
        self.provider_name = provider_name
        self.output_template = DavisTemplate

    async def extract(self, document_text: str, document_path: str) -> Dict[str, Any]:
        """
        Extract structured benefit information from Versant Health family documents in tabular format.

        Args:
            document_text: Raw text extracted previously (may not be used if processing path directly).
            document_path: Path to the original PDF document file.

        Returns:
            Dictionary containing structured benefit information for the specific provider.
        """
        logger.info(f"Starting {self.provider_name} extraction for: {document_path}")
        full_text = ""
        
        try:
            # 1. Load PDF & Extract Text
            doc = fitz.open(document_path)
            for page_num, page in enumerate(doc):
                # Extract text using layout mode for preserving tabular structure
                full_text += page.get_text("text") + "\n\n"

            doc.close()

            # 2. Parse the tabular data
            rows = await self._parse_table_rows(full_text)
            logger.info(f"Extracted {len(rows)} rows from tabular data")
            
            # 3. Create template with extracted data
            template_data = {
                'plan_name': self.provider_name,
                'document_type': "Vision Benefits",
                'provider': self.provider_name,
            }
            
            # Organize rows by benefit category
            benefit_categories = {}
            for row in rows:
                category = row.get('Category')
                if category:
                    if category not in benefit_categories:
                        benefit_categories[category] = []
                    benefit_categories[category].append(row)
            
            # Process Exam benefits
            if 'Exam' in benefit_categories:
                exam_benefits = ExamBenefits()
                for row in benefit_categories['Exam']:
                    description = row.get('Description', '').strip()
                    if 'routine eye exam' in description.lower() or 'eye examination' in description.lower() or 'exam' in description.lower():
                        parsed_value = await self._parse_value(row.get('Copay'))
                        frequency = f"Every {row.get('FrequencyMonths', '12')} Months" if row.get('FrequencyMonths') else None
                        
                        exam_benefits.routine_exam = BenefitItem(
                            description=description,
                            frequency=frequency,
                            copay=parsed_value,
                            available="Yes" if row.get('Available', True) else "No"
                        )
                
                template_data['exam_benefits'] = exam_benefits
            
            # Process SpectacleLens benefits
            if 'SpectacleLens' in benefit_categories:
                spectacle_lens_benefits = SpectacleLensBenefits()
                for row in benefit_categories['SpectacleLens']:
                    description = row.get('Description', '').strip()
                    parsed_value = await self._parse_value(row.get('Copay'))
                    frequency = f"Every {row.get('FrequencyMonths', '12')} Months" if row.get('FrequencyMonths') else None
                    
                    if 'bifocal' in description.lower():
                        spectacle_lens_benefits.bifocal_spectacle_lens = BenefitItem(
                            description=description,
                            frequency=frequency,
                            copay=parsed_value,
                            available="Yes" if row.get('Available', True) else "No"
                        )
                    elif 'single vision - lenticular myodisc' in description.lower():
                        spectacle_lens_benefits.single_vision_lenticular_myodisc = BenefitItem(
                            description=description,
                            frequency=frequency,
                            copay=parsed_value,
                            available="Yes" if row.get('Available', True) else "No"
                        )
                    elif 'single vision' in description.lower() and 'lenticular' not in description.lower():
                        spectacle_lens_benefits.single_vision_spectacle_lens = BenefitItem(
                            description=description,
                            frequency=frequency,
                            copay=parsed_value,
                            available="Yes" if row.get('Available', True) else "No"
                        )
                    elif 'trifocal' in description.lower():
                        spectacle_lens_benefits.trifocal_spectacle_lens = BenefitItem(
                            description=description,
                            frequency=frequency,
                            copay=parsed_value,
                            available="Yes" if row.get('Available', True) else "No"
                        )
                    elif 'spectacle lens (plan)' in description.lower() or 'spectacle lenses' in description.lower():
                        # Generic spectacle lens - add to all types that don't have a value yet
                        if not spectacle_lens_benefits.single_vision_spectacle_lens:
                            spectacle_lens_benefits.single_vision_spectacle_lens = BenefitItem(
                                description=description,
                                frequency=frequency,
                                copay=parsed_value,
                                available="Yes" if row.get('Available', True) else "No"
                            )
                        
                        if not spectacle_lens_benefits.bifocal_spectacle_lens:
                            spectacle_lens_benefits.bifocal_spectacle_lens = BenefitItem(
                                description=description,
                                frequency=frequency,
                                copay=parsed_value,
                                available="Yes" if row.get('Available', True) else "No"
                            )
                        
                        if not spectacle_lens_benefits.trifocal_spectacle_lens:
                            spectacle_lens_benefits.trifocal_spectacle_lens = BenefitItem(
                                description=description,
                                frequency=frequency,
                                copay=parsed_value,
                                available="Yes" if row.get('Available', True) else "No"
                            )
                
                template_data['spectacle_lens_benefits'] = spectacle_lens_benefits
            
            # Process SpectacleLensOptions benefits
            if 'SpectacleLensOptions' in benefit_categories:
                options_benefits = SpectacleLensOptionsBenefits()
                
                # Map of description keywords to model field names with flexible patterns
                options_mapping = {
                    # Anti-reflective coatings - multiple pattern variations
                    'ar coating standard': 'ar_coating_standard',
                    'anti-reflective standard': 'ar_coating_standard',
                    'ar standard': 'ar_coating_standard',
                    'standard ar': 'ar_coating_standard',
                    'standard ar coating': 'ar_coating_standard',
                    'anti-reflective coating standard': 'ar_coating_standard',
                    
                    'ar coating premium': 'ar_coating_premium',
                    'anti-reflective premium': 'ar_coating_premium',
                    'ar premium': 'ar_coating_premium',
                    'premium ar': 'ar_coating_premium',
                    'premium ar coating': 'ar_coating_premium',
                    'anti-reflective coating premium': 'ar_coating_premium',
                    
                    'ar coating ultra': 'ar_coating_ultra',
                    'anti-reflective ultra': 'ar_coating_ultra',
                    'ar ultra': 'ar_coating_ultra',
                    'ultra ar': 'ar_coating_ultra',
                    'ultra ar coating': 'ar_coating_ultra',
                    'anti-reflective coating ultra': 'ar_coating_ultra',
                    
                    'ar coating ultimate': 'ar_coating_ultimate',
                    'anti-reflective ultimate': 'ar_coating_ultimate',
                    'ar ultimate': 'ar_coating_ultimate',
                    'ultimate ar': 'ar_coating_ultimate',
                    'ultimate ar coating': 'ar_coating_ultimate',
                    'anti-reflective coating ultimate': 'ar_coating_ultimate',
                    
                    # Progressive lenses
                    'progressive standard': 'progressive_standard',
                    'progressive premium': 'progressive_premium',
                    'progressive ultra': 'progressive_ultra',
                    'progressive ultimate': 'progressive_ultimate',
                    
                    # Polycarbonate options
                    'polycarbonate - single vision': 'polycarbonate_single_vision',
                    'polycarbonate provided': 'polycarbonate_provided',
                    'hd polycarbonate - single vision': 'hd_polycarbonate_single_vision',
                    'hd polycarbonate - multifocal': 'hd_polycarbonate_multifocal',
                    
                    # High index lenses
                    'highindex 1.67 - single vision': 'high_index_167_single_vision',
                    'highindex 1.74 - single vision': 'high_index_174_single_vision',
                    'highindex 1.74 - multifocal': 'high_index_174_multifocal',
                    
                    # Tints and photochromic options
                    'tint': 'tint',
                    'tint solid': 'tint_solid',
                    'tint gradient': 'tint_gradient',
                    'tint gg': 'tint_gg',
                    'single vision - tint photogrey': 'single_vision_tint_photogrey',
                    'multivision - tint photogrey': 'multivision_tint_photogrey',
                    'single vision - tint plastic - photosensitive': 'single_vision_tint_plastic_photosensitive',
                    'multivision - tint plastic - photosensitive': 'multivision_tint_plastic_photosensitive',
                    
                    # Other lens options
                    'blue light filtering - ebs': 'blue_light_filtering_ebs',
                    'blue light filtering': 'blue_light_filtering_ebs',
                    'polarized': 'polarized',
                    'intermediate vision': 'intermediate_vision',
                    'ultraviolet coating': 'ultraviolet_coating',
                    'scratch resistant coating': 'scratch_resistant_coating',
                    'scratch resistant coating premium': 'scratch_resistant_coating_premium',
                    'single vision - scratch resistant coating protection': 'single_vision_scratch_resistant_coating_protection',
                    'multivision - scratch resistant coating protection': 'multivision_scratch_resistant_coating_protection',
                    'mirror - solid, single & double gradient': 'mirror_solid_single_double_gradient',
                    
                    # Edge and special processing options
                    'edge polish': 'edge_polish',
                    'high luster edge polish': 'high_luster_edge_polish',
                    'roll polish': 'roll_polish',
                    'roll edge': 'roll_edge',
                    'rimless drill': 'rimless_drill',
                    'slab off': 'slab_off',
                    'blended segment': 'blended_segment',
                    'oversized lenses': 'oversized_lenses',
                }
                
                for row in benefit_categories['SpectacleLensOptions']:
                    description = row.get('Description', '').strip().lower()
                    parsed_value = await self._parse_value(row.get('Copay'))
                    frequency = f"Every {row.get('FrequencyMonths', '12')} Months" if row.get('FrequencyMonths') else None
                    
                    matched = False
                    # Try to find a match in our mapping
                    for key, field_name in options_mapping.items():
                        if key in description:
                            # Create a BenefitItem for this option
                            benefit_item = BenefitItem(
                                description=row.get('Description'),
                                frequency=frequency,
                                copay=parsed_value,
                                available="Yes" if row.get('Available', True) else "No"
                            )
                            
                            # Set the field on the options_benefits object
                            setattr(options_benefits, field_name, benefit_item)
                            matched = True
                            logger.info(f"Matched SpectacleLensOptions: '{key}' -> {field_name} with value {parsed_value}")
                            break
                    
                    # Enhanced fallback matching for AR coatings
                    if not matched and 'ar' in description and 'coating' in description:
                        logger.info(f"Attempting fallback AR matching for: '{description}'")
                        if 'standard' in description:
                            field_name = 'ar_coating_standard'
                            matched = True
                        elif 'premium' in description:
                            field_name = 'ar_coating_premium'
                            matched = True
                        elif 'ultra' in description:
                            field_name = 'ar_coating_ultra'
                            matched = True
                        elif 'ultimate' in description:
                            field_name = 'ar_coating_ultimate'
                            matched = True
                        
                        if matched:
                            benefit_item = BenefitItem(
                                description=row.get('Description'),
                                frequency=frequency,
                                copay=parsed_value,
                                available="Yes" if row.get('Available', True) else "No"
                            )
                            setattr(options_benefits, field_name, benefit_item)
                            logger.info(f"Fallback matched AR coating: '{description}' -> {field_name} with value {parsed_value}")
                    
                    # Log unmatched items for debugging
                    if not matched:
                        logger.warning(f"Unmatched SpectacleLensOptions item: '{description}' with copay '{row.get('Copay')}'")
                
                template_data['spectacle_lens_options_benefits'] = options_benefits
            
            # Process Frame benefits
            if 'Frame' in benefit_categories:
                frame_benefits = FrameBenefits()
                for row in benefit_categories['Frame']:
                    description = row.get('Description', '').strip()
                    parsed_value = await self._parse_value(row.get('Copay'))
                    frequency = f"Every {row.get('FrequencyMonths', '12')} Months" if row.get('FrequencyMonths') else None
                    
                    # Create the benefit item - for some frames like Non-Plan frames, there might be an 
                    # allowed amount instead of a copay
                    benefit_item = BenefitItem(
                        description=description,
                        frequency=frequency,
                        copay=parsed_value,
                        amount_allowed_per_period=await self._parse_value(row.get('AllowedPerPeriod')),
                        available="Yes" if row.get('Available', True) else "No"
                    )
                    
                    # Check specific frame types
                    if 'premier frame' in description.lower():
                        frame_benefits.premier_frame = benefit_item
                    elif 'designer frame' in description.lower():
                        frame_benefits.designer_frame = benefit_item
                    elif 'fashion frame' in description.lower():
                        frame_benefits.fashion_frame = benefit_item
                    elif 'frame (non plan)' in description.lower():
                        frame_benefits.frame_non_plan = benefit_item
                
                template_data['frame_benefits'] = frame_benefits
            
            # Create the final template
            result = self.output_template(**template_data)
            self.extracted_data = result.to_template_json()
            logger.info(f"Successfully created template for {self.provider_name}: {document_path}")
            return self.extracted_data

        except Exception as e:
            logger.error(f"Error during {self.provider_name} extraction for {document_path}: {str(e)}", exc_info=True)
            # Return a complete template structure even in case of error
            error_result = self.output_template(
                provider=self.provider_name,
                document_type="Vision Benefits",
                plan_name=self.provider_name,
                error=f"Extraction failed: {str(e)}"
            )
            return error_result.to_template_json()

    async def _parse_table_rows(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse the tabular data into a structured list of rows using a strict sequential parsing approach.
        
        Args:
            text: Raw text containing tabular data
            
        Returns:
            List of dictionaries representing each row with its values
        """
        rows = []
        
        # Define category types that match the benefit headers in the template
        category_types = ["Exam", "SpectacleLens", "SpectacleLensOptions", "Frame", "ContactLens"]
        
        # Find the table section that begins with "Plan Covered Benefits"
        plan_benefits_idx = text.find("Plan Covered Benefits")
        if plan_benefits_idx == -1:
            logger.warning("Could not find 'Plan Covered Benefits' section in document")
            # Try alternative starting points
            alt_start_points = ["Vision Care Services", "In-Network Coverage", "Benefits", "Category"]
            for start_point in alt_start_points:
                idx = text.find(start_point)
                if idx != -1:
                    logger.info(f"Using alternative section start point: '{start_point}'")
                    plan_benefits_idx = idx
                    break
                    
        if plan_benefits_idx == -1:
            logger.warning("Could not find any benefits section marker in document")
            return rows
        
        # Extract text after the marker
        table_text = text[plan_benefits_idx:]
        
        # Split into lines for processing
        lines = table_text.split('\n')
        
        # Improved parsing approach - handles multiple items per category
        logger.info("Using improved parsing approach for document rows")
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line is exactly one of our category types
            if line in category_types:
                category = line
                logger.info(f"Found category: {category}")
                
                # Process all items under this category until we hit the next category
                j = i + 1
                items_processed = 0
                max_items_per_category = 20  # Prevent infinite loops
                
                while j < len(lines) and items_processed < max_items_per_category:
                    current_line = lines[j].strip()
                    
                    # If we hit another category, stop processing this one
                    if current_line in category_types:
                        break
                    
                    # Skip empty lines
                    if not current_line:
                        j += 1
                        continue
                    
                    # Check if this looks like a description line
                    # (not a frequency, copay, or other metadata line)
                    if (not re.match(r'Every \d+ Months', current_line) and 
                        not re.match(r'\$\d+(?:\.\d+)?', current_line) and
                        not re.match(r'No Copay', current_line) and
                        current_line not in ['Yes', 'No'] and
                        not current_line.isdigit()):
                        
                        description = current_line
                        logger.info(f"Processing item under {category}: {description}")
                        
                        # Look for frequency in the next few lines
                        frequency_months = "12"  # Default
                        for k in range(j + 1, min(j + 4, len(lines))):
                            freq_line = lines[k].strip()
                            if "Every" in freq_line and "Months" in freq_line:
                                freq_match = re.search(r"Every (\d+) Months", freq_line)
                                if freq_match:
                                    frequency_months = freq_match.group(1)
                                    break
                        
                        # Get copay - try next few lines
                        copay = "--"  # Default
                        for k in range(j + 1, min(j + 5, len(lines))):
                            copay_line = lines[k].strip()
                            
                            if "$" in copay_line:
                                copay_match = re.search(r"\$(\d+(?:\.\d+)?)", copay_line)
                                if copay_match:
                                    copay = f"${copay_match.group(1)}"
                                    break
                            elif "No Copay" in copay_line:
                                copay = "No Copay"
                                break
                        
                        # Check for availability
                        available = True  # Default to True
                        for k in range(j + 1, min(j + 6, len(lines))):
                            avail_line = lines[k].strip()
                            if avail_line == "No":
                                available = False
                                break
                            elif avail_line == "Yes":
                                available = True
                                break
                        
                        # Look for allowed amount
                        allowed_per_period = None
                        for k in range(j + 1, min(j + 6, len(lines))):
                            allowed_line = lines[k].strip()
                            # Check for a numeric value in a cell that would typically be the Allowed Per Period column
                            if allowed_line.isdigit() and len(allowed_line) <= 5:
                                allowed_per_period = allowed_line
                                break
                        
                        # Create the row
                        row = {
                            'Category': category,
                            'Description': description,
                            'Copay': copay,
                            'Available': available,
                            'FrequencyMonths': frequency_months
                        }
                        
                        if allowed_per_period:
                            row['AllowedPerPeriod'] = allowed_per_period
                        
                        rows.append(row)
                        items_processed += 1
                        logger.info(f"Added row: {row}")
                    
                    j += 1
                
                # Move to the next category (or continue from where we left off)
                i = j
            else:
                i += 1
        
        # If we found rows, return them
        if rows:
            logger.info(f"Successfully parsed {len(rows)} rows using strict sequential parsing")
            return rows
        
        # If strict parsing didn't work, fall back to alternative methods
        logger.info("Strict parsing found no rows, attempting looser pattern-based parsing")
        
        # Find all category indexes
        category_indexes = []
        for i, line in enumerate(lines):
            if line.strip() in category_types:
                category_indexes.append((i, line.strip()))
        
        if category_indexes:
            # Process each category section
            for idx, (line_idx, category) in enumerate(category_indexes):
                next_section = line_idx + 20  # Default look-ahead
                if idx < len(category_indexes) - 1:
                    next_section = category_indexes[idx+1][0]
                
                # Extract text between this category and the next
                section_lines = lines[line_idx:next_section]
                
                # Try to find description (usually the line after category)
                description = ""
                for j in range(1, min(3, len(section_lines))):
                    if section_lines[j].strip() and section_lines[j].strip() not in category_types:
                        description = section_lines[j].strip()
                        break
                
                if not description:
                    continue
                
                # Try to find frequency
                frequency_months = "12"  # Default
                for line in section_lines:
                    freq_match = re.search(r"Every (\d+) Months", line)
                    if freq_match:
                        frequency_months = freq_match.group(1)
                        break
                
                # Try to find copay
                copay = "--"  # Default
                for line in section_lines:
                    if "$" in line:
                        copay_match = re.search(r"\$(\d+(?:\.\d+)?)", line)
                        if copay_match:
                            copay = f"${copay_match.group(1)}"
                            break
                    elif "No Copay" in line:
                        copay = "No Copay"
                        break
                
                # Try to find allowed amount
                allowed_per_period = None
                for line in section_lines:
                    allowed_match = re.search(r"(\d+)", line)
                    if allowed_match and len(line.strip()) <= 5:  # Simple numeric values are likely allowances
                        allowed_per_period = allowed_match.group(1)
                        break
                
                # Check for availability
                available = True  # Default to True
                for line in section_lines:
                    if line.strip() == "No":
                        available = False
                        break
                    elif line.strip() == "Yes":
                        available = True
                        break
                
                # Create and add row
                row = {
                    'Category': category,
                    'Description': description,
                    'FrequencyMonths': frequency_months,
                    'Copay': copay,
                    'Available': available
                }
                
                if allowed_per_period:
                    row['AllowedPerPeriod'] = allowed_per_period
                
                rows.append(row)
        
        logger.info(f"Parsed {len(rows)} rows from table")
        return rows
    
    async def _parse_value(self, value_str: Optional[str]) -> BenefitValue:
        """Parse extracted value string into appropriate format."""
        
        if value_str is None or value_str == "--":
            return None
            
        # Normalize the string: trim whitespace and convert to lowercase
        value_str = value_str.strip().lower()
        
        # Handle "No Copay" as $0
        if value_str == "no copay":
            return 0
            
        # Handle dollar values
        if '$' in value_str:
            try:
                # Remove $ and convert to float or int
                numeric_part = value_str.replace('$', '').replace(',', '')
                if '.' in numeric_part:
                    result = float(numeric_part)
                    return result
                else:
                    result = int(numeric_part)
                    return result
            except ValueError:
                logger.warning(f"Could not parse monetary value: {value_str}")
                return value_str
                
        # Handle other cases
        return value_str
        
    # Implement required abstract methods from BaseExtractor
    
    async def extract_exam_benefits(self, document_text: str) -> Dict[str, Any]:
        """Extract examination benefit information."""
        # In tabular format, we'd need to parse the table and find exam info
        rows = await self._parse_table_rows(document_text)
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'Exam' and 'routine exam' in description:
                copay_value = await self._parse_value(row.get('Copay'))
                return {"cost": copay_value}
                
        return {"cost": None}
    
    async def extract_frame_benefits(self, document_text: str) -> Dict[str, Any]:
        """Extract frame benefit information."""
        rows = await self._parse_table_rows(document_text)
        result = {}
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'Frame':
                copay_value = await self._parse_value(row.get('Copay'))
                allowed_value = await self._parse_value(row.get('AllowedPerPeriod'))
                
                # Determine which value to use (copay or allowed amount)
                # For frames like Frame (Non Plan), the benefit is typically an allowance amount
                # rather than a copay
                value = copay_value if copay_value is not None else allowed_value
                
                if 'premier frame' in description:
                    result['premier'] = value
                elif 'designer frame' in description:
                    result['designer'] = value
                elif 'fashion frame' in description:
                    result['fashion'] = value
                elif 'frame (non plan)' in description:
                    result['non_plan'] = value
                else:
                    # Generic frame
                    result['generic'] = value
                    
        return result
    
    async def extract_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """Extract lens benefit information."""
        rows = await self._parse_table_rows(document_text)
        result = {}
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'SpectacleLens':
                copay_value = await self._parse_value(row.get('Copay'))
                
                if 'bifocal - spectacle lens' in description:
                    result['bifocal'] = copay_value
                elif 'single vision - lenticular myodisc' in description:
                    result['single_vision_lenticular_myodisc'] = copay_value
                elif 'single vision - spectacle lens' in description:
                    result['single_vision'] = copay_value
                elif 'trifocal - spectacle lens' in description:
                    result['trifocal'] = copay_value
                elif 'spectacle lens (plan)' in description or 'spectacle lenses' in description:
                    # Generic spectacle lens
                    result['generic'] = copay_value
                    
        return result
    
    async def extract_progressive_lens_benefits(self, document_text: str) -> Dict[str, Any]:
        """Extract progressive lens benefit information."""
        rows = await self._parse_table_rows(document_text)
        result = {}
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'SpectacleLensOptions':
                if 'progressive standard' in description:
                    result['standard'] = await self._parse_value(row.get('Copay'))
                elif 'progressive premium' in description:
                    result['premium'] = await self._parse_value(row.get('Copay'))
                elif 'progressive ultra' in description:
                    result['ultra'] = await self._parse_value(row.get('Copay'))
                elif 'progressive ultimate' in description:
                    result['ultimate'] = await self._parse_value(row.get('Copay'))
                    
        return result
    
    async def extract_lens_options(self, document_text: str) -> Dict[str, Any]:
        """Extract lens options information."""
        rows = await self._parse_table_rows(document_text)
        result = {}
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'SpectacleLensOptions':
                copay_value = await self._parse_value(row.get('Copay'))
                
                # AR Coatings
                if 'ar coating standard' in description:
                    result['anti_reflective_standard'] = copay_value
                elif 'ar coating premium' in description:
                    result['anti_reflective_premium'] = copay_value
                elif 'ar coating ultra' in description:
                    result['anti_reflective_ultra'] = copay_value
                elif 'ar coating ultimate' in description:
                    result['anti_reflective_ultimate'] = copay_value
                    
                # Polarized
                elif 'polarized' in description:
                    result['polarized'] = copay_value
                    
                # Photochromic
                elif 'tint plastic - photosensitive' in description:
                    result['photochromic'] = copay_value
                    
                # UV
                elif 'ultraviolet coating' in description:
                    result['uv_coating'] = copay_value
                    
        return result
    
    async def extract_contact_lens_fit(self, document_text: str) -> Dict[str, Any]:
        """Extract contact lens fitting benefit information."""
        rows = await self._parse_table_rows(document_text)
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'ContactLens' and 'fitting' in description:
                copay_value = await self._parse_value(row.get('Copay'))
                return {"cost": copay_value}
                
        return {"cost": None}
    
    async def extract_contact_lenses(self, document_text: str) -> Dict[str, Any]:
        """Extract contact lenses benefit information."""
        rows = await self._parse_table_rows(document_text)
        result = {}
        
        for row in rows:
            category = row.get('Category')
            description = row.get('Description', '').lower() if row.get('Description') else ''
            
            if category == 'ContactLens':
                # Skip fitting entries which are handled in extract_contact_lens_fit
                if 'fitting' in description:
                    continue
                    
                copay_value = await self._parse_value(row.get('Copay'))
                allowed_value = await self._parse_value(row.get('AllowedPerPeriod'))
                
                # Use allowed amount if copay is not present (like for Non Plan contacts)
                value = copay_value if copay_value is not None else allowed_value
                
                if 'contact lens (non plan)' in description:
                    result['non_plan'] = value
                elif 'standard' in description or 'conventional' in description:
                    result['standard'] = value
                elif 'disposable' in description:
                    result['disposable'] = value
                elif 'medically necessary' in description:
                    result['medically_necessary'] = value
                else:
                    # Generic contact lens entry
                    result['generic'] = value
                    
        return result


# Convenience classes for backwards compatibility and clarity
class DavisTabularExtractor(VersantTabularExtractor):
    """Davis Vision extractor - uses unified Versant tabular extractor."""
    
    def __init__(self):
        super().__init__("Davis Vision")


class SuperiorExtractor(VersantTabularExtractor):
    """Superior Vision extractor - uses unified Versant tabular extractor."""
    
    def __init__(self):
        super().__init__("Superior Vision")


class VersantExtractor(VersantTabularExtractor):
    """Versant Health extractor - uses unified Versant tabular extractor."""
    
    def __init__(self):
        super().__init__("Versant Health")