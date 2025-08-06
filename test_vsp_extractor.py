#!/usr/bin/env python
"""
Test script for the VSP Extractor

This script allows testing the VSP extractor by processing a pair of
VSP documents: a Patient Record PDF and a Lens Enhancement PDF.
"""

import os
import sys
import json
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, # Changed level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default output path for VSP results
DEFAULT_OUTPUT_PATH = r"C:\Users\drlee\Vision Extractor service\tests\samples\VSP\results"

# Add the project root to the Python path if needed
# Assumes the script is run from the project root or a similar context
project_root = Path(__file__).parent.parent.parent # Adjust based on actual script location
if str(project_root) not in sys.path:
    # Find the 'app' directory dynamically if possible, otherwise assume structure
    if (project_root / "app").exists():
         sys.path.insert(0, str(project_root))
    else:
         # Fallback assuming script is run from project root
         if (Path.cwd() / "app").exists():
              sys.path.insert(0, str(Path.cwd()))
         else:
              logger.warning("Could not reliably determine project root. Ensure 'app' is in PYTHONPATH.")


try:
    from app.core.extractors.vsp_extractor import VSPExtractor
except ImportError as e:
    logger.error(f"Failed to import VSPExtractor. Ensure the project structure is correct and in PYTHONPATH: {e}")
    sys.exit(1)

async def test_vsp_pair(record_pdf_path: str, lens_pdf_path: str, output_file: Optional[str] = None) -> None:
    """
    Test the VSP extractor by processing a pair of PDF documents.

    Args:
        record_pdf_path: Path to the VSP Patient Record PDF file.
        lens_pdf_path: Path to the VSP Lens Enhancement PDF file.
        output_file: Optional path to save the results JSON file.
    """
    logger.info(f"Testing with Record PDF: {record_pdf_path}")
    logger.info(f"Testing with Lens PDF:   {lens_pdf_path}")

    if not Path(record_pdf_path).exists():
        logger.error(f"Record PDF not found: {record_pdf_path}")
        return
    if not Path(lens_pdf_path).exists():
        logger.error(f"Lens PDF not found: {lens_pdf_path}")
        return

    try:
        # Initialize the extractor
        extractor = VSPExtractor()

        # Manually process each document type using internal methods
        # This bypasses the single-file logic in the main `extract` method
        # but allows testing the core components with paired inputs.
        logger.info("Processing Patient Record PDF...")
        record_data = await extractor._process_patient_record(record_pdf_path)
        logger.info("Processing Lens Enhancement PDF...")
        lens_data = await extractor._process_lens_enhancement(lens_pdf_path)

        # Manually merge the results
        logger.info("Merging results...")
        # We know we provided both types, so classify accordingly for merging
        doc_types = ["patient_record", "lens_enhancement"]
        final_results = extractor._merge_and_format_results(record_data, lens_data, doc_types)

        # Log some key results (adjust based on VSPTemplate structure)
        logger.info(f"Document Type: {final_results.get('document_type')}")
        patient_info = final_results.get('patient_info', {})
        logger.info(f"Patient Info: ID={patient_info.get('id_number')}, Name={patient_info.get('patient_name')}")

        eligibility_info = final_results.get('eligibility_info', {})
        logger.info("Eligibility Information:")
        for key, value in eligibility_info.items():
            logger.info(f"  {key}: {value}")

        plan_details = final_results.get('plan_details', {})
        logger.info("Plan Details:")
        logger.info(f"  Plan Name: {plan_details.get('plan_name')}")
        logger.info(f"  Copays: {plan_details.get('copays')}")
        logger.info(f"  Frame Allowance: {plan_details.get('frame_allowance')}")
        logger.info(f"  Contacts Allowance: {plan_details.get('contacts_allowance')}")

        # Optionally log lens categories count or specific items
        lens_categories = final_results.get('lens_categories', [])
        logger.info(f"Extracted {len(lens_categories)} lens categories.")

        # Save the results to a file
        if not output_file:
            output_path = Path(DEFAULT_OUTPUT_PATH)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            # Create a base name from the record PDF
            base_name = Path(record_pdf_path).stem
            output_file = output_path / f"{base_name}_combined_result.json"

        output_file_path = Path(output_file)
        output_file_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists

        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False)
        logger.info(f"Combined results saved to {output_file_path}")

    except Exception as e:
        logger.error(f"Error processing VSP pair ({record_pdf_path}, {lens_pdf_path}): {e}")
        import traceback
        traceback.print_exc()

def main() -> None:
    """
    Main function to parse arguments and run the VSP pair test.
    """
    parser = argparse.ArgumentParser(description="Test VSP extraction with a pair of PDF documents.")

    parser.add_argument("--record-pdf", required=True, help="Path to the VSP Patient Record PDF file.")
    parser.add_argument("--lens-pdf", required=True, help="Path to the VSP Lens Enhancement PDF file.")
    parser.add_argument("-o", "--output", help=f"Output JSON file path (default: derived name in {DEFAULT_OUTPUT_PATH})")

    args = parser.parse_args()

    try:
        asyncio.run(test_vsp_pair(args.record_pdf, args.lens_pdf, args.output))
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()