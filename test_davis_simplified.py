#!/usr/bin/env python
"""
Test script for the simplified Davis Vision extractor

This script provides testing options:
1. Test with a single PDF file
2. Batch test with multiple PDF files
3. Uses the Davis tabular extractor
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
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_INPUT_PATH = r"tests/samples/Davis"
DEFAULT_OUTPUT_PATH = r"tests/samples/Davis/results"

# Add the project root to the Python path if needed
script_dir = Path(__file__).parent
project_root = script_dir # Assuming script is in project root
if str(project_root) not in sys.path:
    # If script is moved elsewhere, adjust project_root calculation
    # e.g., project_root = script_dir.parent if script is in tests/
    sys.path.append(str(project_root))
    logger.info(f"Added {project_root} to sys.path")

# Ensure extractor can be imported
try:
    from app.core.extractors.versant_tabular_extractor import DavisTabularExtractor
except ImportError as e:
    logger.error(f"Failed to import Davis tabular extractor: {e}")
    logger.error("Ensure the script is run from the project root or the project root is in PYTHONPATH.")
    sys.exit(1)

async def test_with_file(file_path: str, output_file: Optional[str] = None) -> None:
    """
    Test the Davis tabular extractor with a single PDF file

    Args:
        file_path: Path to the PDF file
        output_file: Optional path to save the results
    """
    logger.info(f"Testing with file: {file_path} (Using Tabular extractor)")
    pdf_path = Path(file_path)
    if not pdf_path.exists() or not pdf_path.is_file():
        logger.error(f"File not found or is not a file: {file_path}")
        return

    try:
        # Initialize the tabular extractor
        extractor = DavisTabularExtractor()
        logger.info("Using Davis Tabular Extractor")

        # Process the document - extractor handles PDF reading internally
        # Pass document_path, document_text can be empty or None
        results = await extractor.extract(document_text="", document_path=str(pdf_path))

        # Log the extraction results based on new DavisTemplate structure
        logger.info(f"Provider: {results.get('provider', 'N/A')}")
        logger.info(f"Document Type: {results.get('document_type', 'N/A')}")
        logger.info(f"Plan Name: {results.get('plan_name', 'N/A')}")

        # Log Exam Benefits
        exam_benefits = results.get('Exam', {})
        if exam_benefits:
            logger.info("Exam Benefits:")
            routine_exam = exam_benefits.get('Routine Exam', {})
            if routine_exam:
                logger.info(f"  Routine Exam:")
                for key, value in routine_exam.items():
                    logger.info(f"    {key}: {value}")
        else:
            logger.info("Exam Benefits: Not found")

        # Log Frame Benefits
        frame_benefits = results.get('Frame', {})
        if frame_benefits:
            logger.info("Frame Benefits:")
            frame_details = frame_benefits.get('Frame', {})
            if frame_details:
                logger.info(f"  Frame Details:")
                for key, value in frame_details.items():
                    logger.info(f"    {key}: {value}")
        else:
            logger.info("Frame Benefits: Not found")

        # Log Spectacle Lens Benefits
        spectacle_lens = results.get('SpectacleLens', {})
        if spectacle_lens:
            logger.info("Spectacle Lens Benefits:")
            for lens_type, details in spectacle_lens.items():
                if details and isinstance(details, dict):
                    logger.info(f"  {lens_type}:")
                    for key, value in details.items():
                        logger.info(f"    {key}: {value}")
                else:
                    logger.info(f"  {lens_type}: Not found or invalid format")
        else:
            logger.info("Spectacle Lens Benefits: Not found")

        # Log Spectacle Lens Options
        lens_options = results.get('SpectacleLensOptions', {})
        if lens_options:
            logger.info("Spectacle Lens Options:")
            
            # Progressive lenses options
            progressive_options = [key for key in lens_options.keys() if 'Progressive' in key]
            if progressive_options:
                logger.info("  Progressive Lens Options:")
                for option in progressive_options:
                    details = lens_options.get(option, {})
                    if details:
                        logger.info(f"    {option}:")
                        if isinstance(details, dict):
                            for key, value in details.items():
                                logger.info(f"      {key}: {value}")
                        else:
                            # Handle the case where details is a string
                            logger.info(f"      Value: {details}")
            
            # AR Coating options
            ar_options = [key for key in lens_options.keys() if 'AR Coating' in key]
            if ar_options:
                logger.info("  Anti-Reflective Coating Options:")
                for option in ar_options:
                    details = lens_options.get(option, {})
                    if details:
                        logger.info(f"    {option}:")
                        if isinstance(details, dict):
                            for key, value in details.items():
                                logger.info(f"      {key}: {value}")
                        else:
                            # Handle the case where details is a string
                            logger.info(f"      Value: {details}")
            
            # Photochromic options
            photo_options = [key for key in lens_options.keys() if 'Photosensitive' in key or 'Photogrey' in key]
            if photo_options:
                logger.info("  Photochromic Options:")
                for option in photo_options:
                    details = lens_options.get(option, {})
                    if details:
                        logger.info(f"    {option}:")
                        if isinstance(details, dict):
                            for key, value in details.items():
                                logger.info(f"      {key}: {value}")
                        else:
                            # Handle the case where details is a string
                            logger.info(f"      Value: {details}")
            
            # Polarized options
            if 'Polarized' in lens_options:
                details = lens_options.get('Polarized', {})
                if details:
                    logger.info("  Polarized Lenses:")
                    if isinstance(details, dict):
                        for key, value in details.items():
                            logger.info(f"    {key}: {value}")
                    else:
                        # Handle the case where details is a string
                        logger.info(f"    Value: {details}")
            
            # UV Coating
            if 'Ultraviolet Coating' in lens_options:
                details = lens_options.get('Ultraviolet Coating', {})
                if details:
                    logger.info("  Ultraviolet Coating:")
                    if isinstance(details, dict):
                        for key, value in details.items():
                            logger.info(f"    {key}: {value}")
                    else:
                        # Handle the case where details is a string
                        logger.info(f"    Value: {details}")
        else:
            logger.info("Spectacle Lens Options: Not found")

        # If there was an error during extraction
        if 'error' in results and results['error']:
            logger.error(f"Extraction Error: {results['error']}")

        # Save the results to a file
        if not output_file:
            output_path = Path(DEFAULT_OUTPUT_PATH)
            if not output_path.exists():
                logger.info(f"Creating output directory: {output_path}")
                output_path.mkdir(parents=True, exist_ok=True)
            output_file_path = output_path / f"{pdf_path.stem}_tabular_result.json"
        else:
            output_file_path = Path(output_file)
            # Ensure parent directory exists if a specific file path is given
            if not output_file_path.parent.exists():
                 logger.info(f"Creating output directory: {output_file_path.parent}")
                 output_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file_path}")

    except ImportError as e:
         logger.error(f"Import error during extraction (likely fitz/PyMuPDF): {e}. Please ensure PyMuPDF is installed.")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        import traceback
        traceback.print_exc()

async def batch_test(directory: str, output_dir: Optional[str] = None) -> None:
    """
    Test the Davis tabular extractor with multiple PDF files in a directory

    Args:
        directory: Directory containing PDF files
        output_dir: Optional directory to save results
    """
    logger.info(f"Batch testing with files in: {directory} (Using Tabular extractor)")
    input_path = Path(directory)
    if not input_path.is_dir():
        logger.error(f"Input directory not found or is not a directory: {directory}")
        return

    # Use default output directory if not specified
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_PATH

    output_path = Path(output_dir)
    if not output_path.exists():
        logger.info(f"Creating output directory: {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list(input_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files to process")

    for pdf_file in pdf_files:
        # Construct output file path within the designated output directory
        output_file = output_path / f"{pdf_file.stem}_tabular_result.json"
        await test_with_file(str(pdf_file), str(output_file))

def main() -> None:
    """
    Main function to parse arguments and run the appropriate test
    """
    parser = argparse.ArgumentParser(description="Test Davis Vision extraction with PDF files")

    # Create a mutually exclusive group for test types
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Path to a specific PDF file to test.")
    group.add_argument("-b", "--batch", nargs='?', const=DEFAULT_INPUT_PATH,
                       help=f"Directory containing PDF files for batch testing (default: {DEFAULT_INPUT_PATH} if specified without path).")

    # Add output file/directory option
    parser.add_argument("-o", "--output",
                        help=f"Output file (for --file) or directory (for --batch). Default for batch: {DEFAULT_OUTPUT_PATH}")

    args = parser.parse_args()

    try:
        if args.file:
            # If --output is not given with --file, output file is generated automatically in DEFAULT_OUTPUT_PATH
            output_location = args.output # Can be None
            asyncio.run(test_with_file(args.file, output_location))
        elif args.batch is not None: # Check if --batch was specified (even without a value)
            input_directory = args.batch
            # If --output is not given with --batch, output dir defaults to DEFAULT_OUTPUT_PATH
            output_location = args.output if args.output else DEFAULT_OUTPUT_PATH
            asyncio.run(batch_test(input_directory, output_location))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()