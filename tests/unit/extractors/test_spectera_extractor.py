#!/usr/bin/env python
"""
Test script for the Spectera extractor

This script provides multiple testing options:
1. Test with a single PDF file
2. Batch test with multiple PDF files
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

# Default output path
DEFAULT_OUTPUT_PATH = r"tests/samples/Spectera/results"

# Add the project root to the Python path if needed
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent  # tests/unit/extractors -> tests/unit -> tests -> project_root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.info(f"Added {project_root} to sys.path")

from app.core.extractors.spectera_extractor import SpecteraExtractor

async def test_with_file(file_path: str, output_file: Optional[str] = None) -> None:
    """
    Test the Spectera extractor with a single PDF file
    
    Args:
        file_path: Path to the PDF file
        output_file: Optional path to save the results
    """
    logger.info(f"Testing with file: {file_path}")
    
    try:
        # Initialize the extractor
        extractor = SpecteraExtractor()
        
        # Process the document
        results = await extractor.extract("", file_path)
        
        # Log the extraction results
        logger.info(f"Provider: {results.get('provider')}")
        logger.info(f"Confidence: {results.get('confidence', 0)}")
        
        # Print vision benefits
        vision_benefits = results.get('vision_benefits', {})
        logger.info("Vision Benefits:")
        for category, details in vision_benefits.items():
            logger.info(f"  {category}:")
            if isinstance(details, dict):
                for key, value in details.items():
                    logger.info(f"    {key}: {value}")
            else:
                logger.info(f"    {details}")
        
        # Save the results to a file
        if not output_file:
            output_path = Path(DEFAULT_OUTPUT_PATH)
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{Path(file_path).stem}_result.json"
        else:
            output_file = Path(output_file)
            
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        import traceback
        traceback.print_exc()

async def batch_test(directory: str, output_dir: Optional[str] = None) -> None:
    """
    Test the Spectera extractor with multiple PDF files in a directory
    
    Args:
        directory: Directory containing PDF files
        output_dir: Optional directory to save results
    """
    logger.info(f"Batch testing with files in: {directory}")
    
    # Use default output directory if not specified
    if not output_dir:
        output_dir = DEFAULT_OUTPUT_PATH
    
    output_path = Path(output_dir)
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(Path(directory).glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_file in pdf_files:
        output_file = output_path / f"{pdf_file.stem}_result.json"
        await test_with_file(str(pdf_file), str(output_file))

def main() -> None:
    """
    Main function to parse arguments and run the appropriate test
    """
    parser = argparse.ArgumentParser(description="Test Spectera extraction with various options")
    
    # Create a mutually exclusive group for test types
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Path to a specific PDF file")
    group.add_argument("-b", "--batch", help="Directory containing PDF files for batch testing")
    
    # Add output file/directory option
    parser.add_argument("-o", "--output", help=f"Output file/directory (default: {DEFAULT_OUTPUT_PATH})")
    
    args = parser.parse_args()
    
    try:
        if args.file:
            asyncio.run(test_with_file(args.file, args.output))
        elif args.batch:
            asyncio.run(batch_test(args.batch, args.output))
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 