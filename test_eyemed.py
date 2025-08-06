#!/usr/bin/env python
"""
Simple script to test the EyeMed extractor on a local PDF file.
"""
import asyncio
import json
import sys
from pathlib import Path

from app.core.extractors.eyemed_extractor import EyeMedExtractor
from app.core.utils.pdf_utils import extract_text_from_pdf


async def test_eyemed_extraction(pdf_path):
    """
    Test the EyeMed extractor on a PDF file
    
    Args:
        pdf_path: Path to the PDF file to test
    """
    print(f"Testing EyeMed extraction on: {pdf_path}")
    
    # Create an instance of the EyeMed extractor
    extractor = EyeMedExtractor()
    
    # Read the PDF file
    with open(pdf_path, "rb") as pdf_file:
        # Extract text from the PDF
        text = await extract_text_from_pdf(pdf_file)
        print(f"Extracted {len(text)} characters of text")
        
        # Save the extracted text to a file for debugging
        text_path = pdf_path.with_suffix('.txt')
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
            print(f"Extracted text saved to: {text_path}")
        
        # Process the text with the EyeMed extractor
        try:
            result = await extractor.extract(text, str(pdf_path))
            
            # Print the extraction results
            print("\nExtraction Results:")
            print(f"Provider: {result['metadata']['provider']}")
            print(f"Confidence: {result['metadata']['confidence']:.2f}")
            
            # Print some key extracted fields
            data = result["data"]
            
            if "patient_info" in data:
                print("\nPatient Info:")
                for key, value in data["patient_info"].items():
                    print(f"  {key}: {value}")
            
            if "eligibility_info" in data:
                print("\nEligibility Info:")
                for benefit_type, info in data["eligibility_info"].items():
                    print(f"  {benefit_type}:")
                    if isinstance(info, dict):
                        for key, value in info.items():
                            print(f"    {key}: {value}")
                    else:
                        print(f"    {info}")
            
            if "vision_benefits" in data:
                print("\nVision Benefits:")
                benefits = data["vision_benefits"]
                
                if "exam_services" in benefits:
                    print("  Exam Services:")
                    for exam_type, info in benefits["exam_services"].items():
                        if isinstance(info, dict) and "cost_value" in info:
                            print(f"    {exam_type}: {info.get('cost_value')}")
                        else:
                            print(f"    {exam_type}: {info}")
                
                if "frame" in benefits:
                    print("  Frame:")
                    frame = benefits["frame"]
                    if isinstance(frame, dict):
                        print(f"    Allowance: {frame.get('allowance')}")
                        print(f"    Discount: {frame.get('discount_percentage')}")
                    else:
                        print(f"    {frame}")
            
            # Save full results to JSON file
            output_path = pdf_path.with_suffix('.json')
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
                print(f"\nFull results saved to: {output_path}")
            
            return result
        
        except Exception as e:
            print(f"\nError during extraction: {str(e)}")
            print("\nPrinting the first 500 characters of extracted text for debugging:")
            print(text[:500])
            print("...")
            raise e


if __name__ == "__main__":
    # Get PDF path from command line argument or use default
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
    else:
        # Default to using the sample in the tests directory
        pdf_path = Path("tests/samples/eyemedexmple2.pdf")
    
    # Make sure the file exists
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
    
    # Run the extraction test
    asyncio.run(test_eyemed_extraction(pdf_path)) 