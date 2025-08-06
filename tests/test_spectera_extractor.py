"""
Unit tests for the Spectera document extractor
"""

import asyncio
import json
import os
import unittest
from pathlib import Path

from app.core.extractors.spectera_extractor import SpecteraExtractor


class TestSpecteraExtractor(unittest.TestCase):
    """Test suite for Spectera document extraction"""

    def setUp(self):
        """Set up test environment"""
        self.extractor = SpecteraExtractor()
        self.samples_dir = Path(__file__).parent / "samples" / "Spectera"
        self.results_dir = Path(__file__).parent / "samples" / "Spectera" / "results"
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def test_extract_spectera_document(self):
        """Test extraction of Spectera document"""
        # Get sample PDF paths
        sample_docs = [f for f in os.listdir(self.samples_dir) if f.endswith('.pdf')]
        
        for doc_file in sample_docs:
            # Skip running tests on all documents to save time during development
            # Uncomment this if you want to test specific files only
            # if doc_file not in ['spectera.pdf', 'spectera2.pdf']:
            #     continue
                
            with self.subTest(doc_file=doc_file):
                pdf_path = os.path.join(self.samples_dir, doc_file)
                
                # Extract data from the PDF
                result = asyncio.run(self.extractor.extract("", pdf_path))
                
                # Save the result for manual review
                result_path = os.path.join(self.results_dir, f"{doc_file.replace('.pdf', '')}_result.json")
                with open(result_path, 'w') as f:
                    json.dump(result, f, indent=2)
                
                # Basic assertions to ensure the extraction completed successfully
                self.assertIsNotNone(result)
                self.assertEqual(result["provider"], "Spectera")
                self.assertIn("vision_benefits", result)
                
                # Check that key sections were extracted
                vision_benefits = result["vision_benefits"]
                self.assertIn("professional_services", vision_benefits)
                self.assertIn("frames", vision_benefits)
                
                # Check confidence scores - failures here might indicate extraction issues
                self.assertGreaterEqual(result.get("confidence", 0), 0.5,
                                      f"Low overall confidence score for {doc_file}")
    
    def test_compare_to_expected_output(self):
        """Compare extraction results to expected output template"""
        # Path to the expected output template
        expected_output_path = os.path.join(self.samples_dir, "spectera-json.json")
        
        # Skip if the expected output file doesn't exist
        if not os.path.exists(expected_output_path):
            self.skipTest("Expected output file not found")
        
        # Load the expected structure (not the values, just the structure)
        with open(expected_output_path, 'r') as f:
            expected = json.load(f)
        
        # Get sample PDF path - use the first sample
        sample_path = os.path.join(self.samples_dir, "spectera.pdf")
        
        # Extract data from the sample
        result = asyncio.run(self.extractor.extract("", sample_path))
        
        # Check structure compatibility 
        self._assert_structure_compatibility(result, expected)
    
    def _assert_structure_compatibility(self, result, expected, path=""):
        """
        Recursively check that the result structure is compatible with the expected structure
        
        Args:
            result: Extraction result
            expected: Expected structure
            path: Current path in the structure (for error messages)
        """
        # Check top-level keys
        expected_keys = set(expected.keys())
        result_keys = set(result.keys())
        
        # Additional keys in result are OK (e.g., confidence scores)
        # but we should have at least the keys defined in the expected structure
        missing_keys = expected_keys - result_keys
        if missing_keys:
            self.fail(f"Missing expected keys at {path}: {missing_keys}")
        
        # Recursively check nested structures
        for key in expected_keys:
            if key not in result:
                continue
                
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(expected[key], dict) and isinstance(result[key], dict):
                # If both are dicts, check recursively
                self._assert_structure_compatibility(result[key], expected[key], current_path)
                
            elif isinstance(expected[key], list) and isinstance(result[key], list):
                # If both are lists and expected list has items, check the first item's structure
                if expected[key] and result[key]:
                    # For lists, we just check that the structure of the first item matches
                    # since we're validating structure, not content
                    if isinstance(expected[key][0], dict) and isinstance(result[key][0], dict):
                        self._assert_structure_compatibility(result[key][0], expected[key][0], 
                                                         f"{current_path}[0]")


if __name__ == "__main__":
    unittest.main() 