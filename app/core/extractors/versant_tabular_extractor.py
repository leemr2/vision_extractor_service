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
from app.core.templates.davis_template import DavisTemplate, BenefitValue, SimplifiedBenefitItem, ExamBenefits, SpectacleLensBenefits, SpectacleLensOptionsBenefits, FrameBenefits, ContactLensBenefits
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
        rows = []
        
        try:
            # 1. Load PDF & Try table detection first
            doc = fitz.open(document_path)
            parsing_method_used = None
            
            # Try PyMuPDF table detection first (PRIMARY METHOD)
            logger.info("=" * 60)
            logger.info("PARSING METHOD 1: Attempting PyMuPDF table detection...")
            logger.info("=" * 60)
            rows = await self._extract_tables_from_pdf(doc)
            
            if rows and len(rows) > 0:
                parsing_method_used = "PyMuPDF Table Detection"
                logger.info(f"✓ SUCCESS: PyMuPDF table detection extracted {len(rows)} rows")
            else:
                logger.info("✗ FALLBACK: Table detection found no rows, falling back to text extraction")
                logger.info("=" * 60)
                logger.info("PARSING METHOD 2: Text-based line-by-line parsing...")
                logger.info("=" * 60)
                
                # Fall back to text-based extraction if table detection fails
                for page_num, page in enumerate(doc):
                    # Extract text using layout mode for preserving tabular structure
                    full_text += page.get_text("text") + "\n\n"
                
                # 2. Parse the tabular data using improved text-based parser (FALLBACK METHOD)
                rows = await self._parse_table_rows(full_text)
                
                if rows and len(rows) > 0:
                    parsing_method_used = "Text-based Line Parser"
                    logger.info(f"✓ SUCCESS: Text-based parser extracted {len(rows)} rows")
                else:
                    parsing_method_used = "None (extraction failed)"
                    logger.warning(f"✗ FAILURE: All parsing methods failed to extract rows")
            
            doc.close()
            
            logger.info("=" * 60)
            logger.info(f"FINAL RESULT: Extracted {len(rows)} rows using: {parsing_method_used}")
            logger.info("=" * 60)
            
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

                        exam_benefits.routine_exam = SimplifiedBenefitItem(
                            description=description,
                            copay=parsed_value
                        )

                template_data['exam_benefits'] = exam_benefits
            
            # Process SpectacleLens benefits
            if 'SpectacleLens' in benefit_categories:
                spectacle_lens_benefits = SpectacleLensBenefits()
                for row in benefit_categories['SpectacleLens']:
                    description = row.get('Description', '').strip()
                    parsed_value = await self._parse_value(row.get('Copay'))

                    if 'bifocal' in description.lower():
                        spectacle_lens_benefits.bifocal_spectacle_lens = SimplifiedBenefitItem(
                            description=description,
                            copay=parsed_value
                        )
                    elif 'single vision - lenticular myodisc' in description.lower():
                        spectacle_lens_benefits.single_vision_lenticular_myodisc = SimplifiedBenefitItem(
                            description=description,
                            copay=parsed_value
                        )
                    elif 'single vision' in description.lower() and 'lenticular' not in description.lower():
                        spectacle_lens_benefits.single_vision_spectacle_lens = SimplifiedBenefitItem(
                            description=description,
                            copay=parsed_value
                        )
                    elif 'trifocal' in description.lower():
                        spectacle_lens_benefits.trifocal_spectacle_lens = SimplifiedBenefitItem(
                            description=description,
                            copay=parsed_value
                        )
                    elif 'spectacle lens (plan)' in description.lower() or 'spectacle lenses' in description.lower():
                        # Generic spectacle lens - add to all types that don't have a value yet
                        if not spectacle_lens_benefits.single_vision_spectacle_lens:
                            spectacle_lens_benefits.single_vision_spectacle_lens = SimplifiedBenefitItem(
                                description=description,
                                copay=parsed_value
                            )

                        if not spectacle_lens_benefits.bifocal_spectacle_lens:
                            spectacle_lens_benefits.bifocal_spectacle_lens = SimplifiedBenefitItem(
                                description=description,
                                copay=parsed_value
                            )

                        if not spectacle_lens_benefits.trifocal_spectacle_lens:
                            spectacle_lens_benefits.trifocal_spectacle_lens = SimplifiedBenefitItem(
                                description=description,
                                copay=parsed_value
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
                    'polycarbonate single vision': 'polycarbonate_single_vision',
                    'polycarbonate - multifocal': 'polycarbonate_multifocal',
                    'polycarbonate multifocal': 'polycarbonate_multifocal',
                    'polycarbonate provided': 'polycarbonate_provided',
                    'hd polycarbonate - single vision': 'hd_polycarbonate_single_vision',
                    'hd polycarbonate - multifocal': 'hd_polycarbonate_multifocal',
                    'hd polycarbonate multifocal': 'hd_polycarbonate_multifocal',
                    
                    # High index lenses
                    'highindex 1.67 - single vision': 'high_index_167_single_vision',
                    'highindex 1.67 - multifocal': 'high_index_167_multifocal',
                    'highindex 1.74 - single vision': 'high_index_174_single_vision',
                    'highindex 1.74 - multifocal': 'high_index_174_multifocal',
                    'high index 1.67 - single vision': 'high_index_167_single_vision',
                    'high index 1.67 - multifocal': 'high_index_167_multifocal',
                    'high index 1.74 - single vision': 'high_index_174_single_vision',
                    'high index 1.74 - multifocal': 'high_index_174_multifocal',
                    
                    # Glass lenses
                    'glass - single vision': 'glass_single_vision',
                    'glass single vision': 'glass_single_vision',
                    'glass - bifocal': 'glass_bifocal',
                    'glass bifocal': 'glass_bifocal',
                    'glass - trifocal': 'glass_trifocal',
                    'glass trifocal': 'glass_trifocal',
                    
                    # Tints and photochromic options
                    'tint': 'tint',
                    'tint solid': 'tint_solid',
                    'tint gradient': 'tint_gradient',
                    'tint gg': 'tint_gg',
                    'single vision - tint photogrey': 'single_vision_tint_photogrey',
                    'multivision - tint photogrey': 'multivision_tint_photogrey',
                    'single vision - tint plastic - photosensitive': 'single_vision_tint_plastic_photosensitive',
                    'multivision - tint plastic - photosensitive': 'multivision_tint_plastic_photosensitive',
                    
                    # Transitions lenses (photochromic brand name)
                    'transitions - single vision': 'transitions_single_vision',
                    'transitions single vision': 'transitions_single_vision',
                    'transitions - multifocal': 'transitions_multifocal',
                    'transitions multifocal': 'transitions_multifocal',
                    
                    # Other lens options
                    'blue light filtering - ebs': 'blue_light_filtering_ebs',
                    'blue light filtering': 'blue_light_filtering_ebs',
                    'polarized': 'polarized',
                    'intermediate vision': 'intermediate_vision',
                    'ultraviolet coating': 'ultraviolet_coating',
                    'uv coating': 'ultraviolet_coating',
                    'uv coat': 'ultraviolet_coating',
                    'scratch resistant coating': 'scratch_resistant_coating',
                    'scratch resistant coating premium': 'scratch_resistant_coating_premium',
                    'coating (non edp)': 'coating_non_edp',
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
                    'specialty lenses': 'specialty_lenses',
                }
                
                for row in benefit_categories['SpectacleLensOptions']:
                    description = row.get('Description', '').strip().lower()
                    parsed_value = await self._parse_value(row.get('Copay'))

                    # Skip spurious rows that are clearly not benefit descriptions
                    if self._is_spurious_row(description):
                        continue

                    matched = False
                    # Try to find a match in our mapping
                    for key, field_name in options_mapping.items():
                        if key in description:
                            # Create a SimplifiedBenefitItem for this option
                            benefit_item = SimplifiedBenefitItem(
                                description=row.get('Description'),
                                copay=parsed_value
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
                            benefit_item = SimplifiedBenefitItem(
                                description=row.get('Description'),
                                copay=parsed_value
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
                    parsed_copay = await self._parse_value(row.get('Copay'))
                    parsed_allowance = await self._parse_value(row.get('AllowedPerPeriod'))

                    # Create SimplifiedBenefitItem with copay and allowance (for Non Plan frames)
                    benefit_item = SimplifiedBenefitItem(
                        description=description,
                        copay=parsed_copay,
                        allowance=parsed_allowance if 'non plan' in description.lower() else None
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

            # Process ContactLens benefits
            if 'ContactLens' in benefit_categories:
                contact_lens_benefits = ContactLensBenefits()
                for row in benefit_categories['ContactLens']:
                    description = row.get('Description', '').strip()
                    parsed_copay = await self._parse_value(row.get('Copay'))
                    parsed_allowance = await self._parse_value(row.get('AllowedPerPeriod'))

                    # Create SimplifiedBenefitItem with copay and allowance (for Non Plan contacts)
                    benefit_item = SimplifiedBenefitItem(
                        description=description,
                        copay=parsed_copay,
                        allowance=parsed_allowance if 'non plan' in description.lower() else None
                    )

                    # Check specific contact lens types
                    if 'contact lens (plan)' in description.lower():
                        contact_lens_benefits.contact_lens_plan = benefit_item
                    elif 'medically necessary' in description.lower() and 'non plan' in description.lower():
                        contact_lens_benefits.medically_necessary_non_plan = benefit_item
                    elif 'specialty' in description.lower() and 'non plan' in description.lower():
                        contact_lens_benefits.contact_lens_specialty_non_plan = benefit_item
                    elif 'contact lens (non plan)' in description.lower() or 'non plan' in description.lower():
                        contact_lens_benefits.contact_lens_non_plan = benefit_item

                template_data['contact_lens_benefits'] = contact_lens_benefits

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

    async def _extract_tables_from_pdf(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF using PyMuPDF's table detection.
        
        Args:
            doc: PyMuPDF document object
            
        Returns:
            List of dictionaries representing each row with its values
        """
        rows = []
        
        # Define category types that match the benefit headers in the template
        category_types = ["Exam", "SpectacleLens", "SpectacleLensOptions", "Frame", "ContactLens"]
        
        try:
            for page_num, page in enumerate(doc):
                logger.info(f"Processing page {page_num + 1} for table detection")
                
                # Find tables on the page
                tables = page.find_tables()
                
                if not tables or len(tables.tables) == 0:
                    logger.info(f"No tables found on page {page_num + 1}")
                    continue
                
                logger.info(f"Found {len(tables.tables)} table(s) on page {page_num + 1}")
                
                for table_idx, table in enumerate(tables.tables):
                    logger.info(f"Processing table {table_idx + 1}")
                    
                    # Extract table data
                    table_data = table.extract()
                    
                    if not table_data or len(table_data) < 2:
                        logger.info(f"Table {table_idx + 1} has insufficient data")
                        continue
                    
                    # Try to identify column headers
                    header_row = None
                    data_start_row = 0
                    
                    # Look for header row (usually contains "Description", "Copay", etc.)
                    for i, row in enumerate(table_data[:5]):  # Check first 5 rows
                        row_text = ' '.join([str(cell).lower() for cell in row if cell])
                        if any(header in row_text for header in ['description', 'copay', 'frequency', 'available']):
                            header_row = [str(cell).strip() if cell else "" for cell in row]
                            data_start_row = i + 1
                            logger.info(f"Found header row at index {i}: {header_row}")
                            break
                    
                    # If no header row found, try to infer columns based on common patterns
                    if header_row is None:
                        logger.info("No explicit header row found, using default column structure")
                        # Common column order: Category/Description, Frequency, Copay, Available, Allowed Per Period
                        header_row = ['Description', 'Frequency', 'Copay', 'Available', 'AllowedPerPeriod']
                        data_start_row = 0
                    
                    # Normalize header names for mapping
                    col_map = {}
                    for idx, header in enumerate(header_row):
                        header_lower = header.lower().strip()
                        if 'description' in header_lower or 'benefit' in header_lower or 'category' in header_lower:
                            col_map['description'] = idx
                        elif 'copay' in header_lower or 'co-pay' in header_lower or 'cost' in header_lower:
                            col_map['copay'] = idx
                        elif 'frequency' in header_lower or 'month' in header_lower:
                            col_map['frequency'] = idx
                        elif 'available' in header_lower or 'covered' in header_lower:
                            col_map['available'] = idx
                        elif 'allowed' in header_lower or 'allowance' in header_lower:
                            col_map['allowed'] = idx
                    
                    logger.info(f"Column mapping: {col_map}")
                    
                    # Current category context
                    current_category = None
                    
                    # Process data rows
                    for row_idx in range(data_start_row, len(table_data)):
                        row = table_data[row_idx]
                        
                        if not row or all(not cell for cell in row):
                            continue  # Skip empty rows
                        
                        # Convert cells to strings
                        row_cells = [str(cell).strip() if cell else "" for cell in row]
                        
                        # Check if this row is a category header
                        first_cell = row_cells[0] if row_cells else ""
                        if first_cell in category_types:
                            current_category = first_cell
                            logger.info(f"Found category: {current_category}")
                            continue
                        
                        # Skip if we don't have a current category
                        if not current_category:
                            # Try to infer category from description
                            if 'exam' in first_cell.lower():
                                current_category = 'Exam'
                            elif 'frame' in first_cell.lower():
                                current_category = 'Frame'
                            elif 'contact' in first_cell.lower():
                                current_category = 'ContactLens'
                            elif any(x in first_cell.lower() for x in ['progressive', 'ar coating', 'polycarbonate', 'tint']):
                                current_category = 'SpectacleLensOptions'
                            elif any(x in first_cell.lower() for x in ['lens', 'bifocal', 'trifocal', 'single vision']):
                                current_category = 'SpectacleLens'
                            else:
                                continue  # Skip rows without category context
                        
                        # Extract data based on column mapping
                        description = row_cells[col_map.get('description', 0)] if len(row_cells) > col_map.get('description', 0) else ""
                        
                        # Skip empty descriptions or category headers
                        if not description or description in category_types:
                            continue
                        
                        # Skip spurious rows (column headers, fragments, etc.)
                        if self._is_spurious_row(description.lower()):
                            logger.debug(f"Skipping spurious row in table detection: '{description}'")
                            continue
                        
                        # Extract other fields
                        copay = ""
                        frequency = "12"  # Default
                        available = True  # Default
                        allowed_per_period = None
                        
                        if 'copay' in col_map and len(row_cells) > col_map['copay']:
                            copay = row_cells[col_map['copay']]
                        
                        if 'frequency' in col_map and len(row_cells) > col_map['frequency']:
                            freq_str = row_cells[col_map['frequency']]
                            freq_match = re.search(r'(\d+)', freq_str)
                            if freq_match:
                                frequency = freq_match.group(1)
                        
                        if 'available' in col_map and len(row_cells) > col_map['available']:
                            avail_str = row_cells[col_map['available']].lower()
                            available = 'yes' in avail_str or 'covered' in avail_str or avail_str == ''
                        
                        if 'allowed' in col_map and len(row_cells) > col_map['allowed']:
                            allowed_str = row_cells[col_map['allowed']]
                            allowed_match = re.search(r'(\d+)', allowed_str)
                            if allowed_match:
                                allowed_per_period = allowed_match.group(1)
                        
                        # Create row dictionary
                        row_dict = {
                            'Category': current_category,
                            'Description': description,
                            'Copay': copay if copay else "--",
                            'Available': available,
                            'FrequencyMonths': frequency
                        }
                        
                        if allowed_per_period:
                            row_dict['AllowedPerPeriod'] = allowed_per_period
                        
                        rows.append(row_dict)
                        logger.info(f"Extracted row via table detection: {row_dict}")
            
            logger.info(f"Table detection extracted {len(rows)} total rows")
            
            # Merge split rows (e.g., "AR Coating" + "Premium" -> "AR Coating Premium")
            if rows:
                rows = self._merge_split_rows(rows)
            
            return rows
            
        except Exception as e:
            logger.warning(f"Table detection failed: {str(e)}", exc_info=True)
            return []

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
                # REMOVED: max_items_per_category limit to capture all items (e.g., 43+ SpectacleLensOptions)
                
                while j < len(lines):
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
        
        # If we found rows, merge any split descriptions and return
        if rows:
            logger.info(f"✓ SUCCESS: Strict sequential parsing extracted {len(rows)} rows")
            rows = self._merge_split_rows(rows)
            return rows
        
        # If strict parsing didn't work, fall back to alternative methods
        logger.info("=" * 60)
        logger.info("PARSING METHOD 2b: Strict parsing found no rows, attempting looser pattern-based parsing")
        logger.info("=" * 60)
        
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
        
        if rows:
            logger.info(f"✓ SUCCESS: Looser pattern-based parsing extracted {len(rows)} rows")
            rows = self._merge_split_rows(rows)
        else:
            logger.info(f"✗ FAILURE: Looser pattern-based parsing found no rows")
        
        return rows
    
    def _merge_split_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge consecutive rows that are parts of the same benefit item.
        
        Some PDF tables split benefit descriptions across multiple lines/rows:
        Row 1: "AR Coating" - $70
        Row 2: "Premium" - $70
        
        This method merges them into:
        Row 1: "AR Coating Premium" - $70
        
        Args:
            rows: List of extracted table rows
            
        Returns:
            List of merged rows
        """
        if not rows:
            return rows
        
        # Qualifier words that indicate a row is part of a split description
        qualifier_words = {
            'premium', 'standard', 'ultra', 'ultimate',
            'single vision', 'multifocal', 'bifocal', 'trifocal',
            'vision',  # For cases like "Glass - Single" + "Vision"
        }
        
        merged_rows = []
        i = 0
        
        while i < len(rows):
            current_row = rows[i].copy()
            current_desc = current_row.get('Description', '').strip().lower()
            current_copay = current_row.get('Copay', '')
            
            # Look ahead to see if next rows should be merged
            merged_count = 0
            j = i + 1
            
            while j < len(rows):
                next_row = rows[j]
                next_desc = next_row.get('Description', '').strip().lower()
                next_copay = next_row.get('Copay', '')
                
                # Check if this row should be merged with current row
                should_merge = False
                
                # Condition 1: Same copay AND next description is a qualifier word
                if (current_copay == next_copay and 
                    next_desc in qualifier_words):
                    should_merge = True
                    logger.debug(f"Merging qualifier: '{current_desc}' + '{next_desc}'")
                
                # Condition 2: Current description ends with dash/hyphen (incomplete)
                # AND next is a qualifier (like "HD Polycarbonate -" + "Multifocal")
                elif (current_copay == next_copay and
                      current_desc.endswith('-') and
                      next_desc in qualifier_words):
                    should_merge = True
                    logger.debug(f"Merging hyphenated: '{current_desc}' + '{next_desc}'")
                
                if should_merge:
                    # Merge the descriptions
                    current_row['Description'] = (
                        current_row.get('Description', '').strip() + ' ' + 
                        next_row.get('Description', '').strip()
                    ).strip()
                    current_desc = current_row.get('Description', '').lower()
                    merged_count += 1
                    j += 1
                else:
                    # No more rows to merge
                    break
            
            # Add the merged row
            merged_rows.append(current_row)
            
            # Skip the rows we merged
            i += merged_count + 1
            
            if merged_count > 0:
                logger.info(f"Merged {merged_count} row(s) into: '{current_row.get('Description')}'")
        
        logger.info(f"Row merging: {len(rows)} rows -> {len(merged_rows)} rows")
        return merged_rows
    
    def _is_spurious_row(self, description: str) -> bool:
        """
        Check if a row is spurious (not a real benefit description).
        
        Args:
            description: Lowercase description text to check
            
        Returns:
            True if the row should be skipped, False otherwise
        """
        if not description:
            return True
        
        # Skip very short strings (likely fragments)
        if len(description) < 3:
            return True
        
        # Skip common column headers and metadata
        spurious_keywords = [
            'category', 'description', 'frequency', 'copay', 'amount',
            'allowed', 'per period', 'available', 'next', 'date',
            'allowance', 'remaining', 'auth', 'required',
            # Skip frequency/period indicators
            '1 per 12', '1 per 24', 'per 12', 'per 24', 'months', 'month',
            '1 every plan', 'every plan', 'year',  # Common frequency fragments
            # Skip status indicators  
            'covered', 'not covered', 'yes', 'no',
            # Skip standalone symbols
            '--', '—', '-', '•', '*',
        ]
        
        # Check if description is exactly a spurious keyword
        if description in spurious_keywords:
            return True
        
        # Skip if description is only "covered" or similar status
        if description in ['covered', 'not covered', 'yes', 'no']:
            return True
        
        # Skip if description matches frequency pattern exactly
        if re.match(r'^(\d+\s*per\s*\d+|months?)$', description):
            return True
        
        # Skip rows that are just fragments from other columns
        # (e.g., "- ebs" without the main description)
        if description.startswith('- ') and len(description) < 10:
            return True
        
        # Skip incomplete lens type descriptions (clear fragments only)
        incomplete_fragments = [
            'coating premium',  # Fragment of "Scratch Resistant Coating Premium"
            'coating',  # Fragment alone (but allow "ultraviolet coating", "scratch resistant coating", etc.)
        ]
        
        # Only skip if it's exactly one of these fragments
        if description in incomplete_fragments:
            return True
        
        # Skip single-word generic material names that need context
        # (e.g., "polycarbonate" alone, but allow "Polycarbonate - Single Vision")
        if description == 'polycarbonate' or description == 'scratch resistant':
            return True
        
        return False
    
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