# EyeMed Extractor Testing Guide

This guide explains how to use the test scripts to validate the EyeMed extractor functionality.

## Overview

The EyeMed extractor converts vision benefits documents into structured JSON data. The extractor focuses on capturing cost values in the following formats:

1. Set dollar copay (e.g., "$25 copay")
2. Percentage off retail over a dollar allowance (e.g., "20% off balance over $150")
3. Percentage off retail less a dollar allowance (e.g., "20% off retail price less $120 allowance")
4. Percentage off retail (e.g., "20% off retail")

The test scripts help you verify that the extractor works correctly with different kinds of EyeMed documents.

## Prerequisites

- Python 3.7 or higher
- Required Python packages:
  - pydantic
  - pytesseract (for image-based PDFs)
  - PyMuPDF (for PDF processing)

Install the required packages:

```bash
pip install pydantic pytesseract pymupdf
```

For PDF processing, you also need to have Tesseract OCR installed:
- Windows: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Mac: `brew install tesseract`
- Linux: `apt-get install tesseract-ocr`

## Using the Test Script

The `test_eyemed_simplified.py` script provides several ways to test the EyeMed extractor:

### 1. Testing with Synthetic Data

To test with built-in synthetic data:

```bash
python test_eyemed_simplified.py --synthetic
```

or simply:

```bash
python test_eyemed_simplified.py
```

This will process the synthetic data and save the results to `eyemed_result.json`.

### 2. Testing with Your Own Files

To test with your own EyeMed benefit document (text or PDF):

```bash
python test_eyemed_simplified.py --file path/to/your/document.pdf
```

### 3. Batch Processing Multiple Files

To process multiple files at once:

```bash
python test_eyemed_simplified.py --batch path/to/files_directory
```

By default, this will:
- Process all .txt and .pdf files in the specified directory
- Save results in a "results" subfolder within the input directory
- Run in quiet mode (minimal console output)

You can customize the batch processing:

```bash
# Process only PDF files
python test_eyemed_simplified.py --batch path/to/files_directory --pattern "*.pdf"

# Use a specific output directory
python test_eyemed_simplified.py --batch path/to/files_directory --outdir path/to/output

# Show detailed results for each file
python test_eyemed_simplified.py --batch path/to/files_directory --pattern "*.txt" --quiet=false
```

### 4. Customizing Output

You can specify a custom output file:

```bash
python test_eyemed_simplified.py --file path/to/document.pdf --output my_results.json
```

### 5. Quiet Mode

To suppress detailed console output and only save the JSON:

```bash
python test_eyemed_simplified.py --file path/to/document.pdf --quiet
```

## Command-Line Options

```
usage: test_eyemed_simplified.py [-h] [-s | -f FILE | -b BATCH] [-p PATTERN] [-d OUTDIR] [-o OUTPUT] [-q]

Test the EyeMed extractor with different inputs

options:
  -h, --help            show this help message and exit
  -s, --synthetic       Use synthetic test data (default if no input specified)
  -f FILE, --file FILE  Path to an EyeMed benefits document (text or PDF)
  -b BATCH, --batch BATCH
                        Process all files in the specified directory
  -p PATTERN, --pattern PATTERN
                        File pattern for batch processing (comma-separated, default: *.txt,*.pdf)
  -d OUTDIR, --outdir OUTDIR
                        Output directory for batch results (default: inputdir/results)
  -o OUTPUT, --output OUTPUT
                        Path to save the JSON output (default: eyemed_result.json)
  -q, --quiet           Suppress detailed console output
```

## Output Structure

The JSON output follows this structure:

```json
{
  "provider": "EyeMed",
  "patient_info": {
    "member_id": "ABC123456",
    "member_name": "ID",
    "network": "Insight",
    "group": "Group123",
    "benefit_level": "Enhanced EYE EXAM"
  },
  "eligibility_info": {
    "exam": {
      "eligible_as_of": "01/01/2023",
      "frequency": "Once every 12 months"
    },
    ...
  },
  "vision_benefits": {
    "exam_services": {
      "exam": "$10",
      "retinal_imaging": "Up to $39"
    },
    "frame": "$0 copay; 20% off balance over $150",
    "lenses": {
      "single_vision": "$25 copay",
      ...
    },
    "progressive_lenses": {
      "standard": "$90",
      ...
    },
    "lens_options": {
      "anti_reflective_coating": {
        "standard": "$45",
        ...
      },
      ...
    },
    ...
  },
  "confidence": 0.83,
  "confidence_scores": {
    ...
  }
}
```

## Troubleshooting

1. **PDF Processing Issues**
   - Make sure PyMuPDF (fitz) is installed
   - Check that the PDF is not password-protected or corrupted

2. **Text Extraction Issues**
   - If the extractor isn't finding certain fields, check if your document format differs from the expected format
   - Try pre-processing your document text to match the expected format

3. **Low Confidence Scores**
   - A low confidence score indicates the extractor is uncertain about some fields
   - Examine the specific confidence scores to identify which fields have issues

## Adding New Test Files

To build your own test suite, create a directory of test files and process them in batch:

```bash
for file in test_files/*.pdf; do
  python test_eyemed_simplified.py --file "$file" --output "results/$(basename "$file" .pdf).json"
done
``` 