# Testing the EyeMed Extractor

This guide explains how to test the EyeMed extraction functionality locally.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR (required for image-based PDFs):
   - **Windows**: Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`

## Testing Options

There are two ways to test the EyeMed extractor:

### 1. With a PDF File

Use the `test_eyemed.py` script to test the extractor with a real PDF:

```bash
# With default sample PDF
python test_eyemed.py

# With a specific PDF file
python test_eyemed.py path/to/your/eyemed.pdf
```

The script will:
- Extract text from the PDF
- Process the text with the EyeMed extractor
- Print the extraction results
- Save the full results to a JSON file

### 2. With Synthetic Data

Use the `test_eyemed_synthetic.py` script to test with synthetic data:

```bash
python test_eyemed_synthetic.py
```

This is useful for testing the extraction logic without needing a real PDF. The script contains a sample text representation of an EyeMed benefits document.

## Understanding Results

The extraction results include:

- **Provider**: Always "EyeMed"
- **Patient Info**: Member ID, name, network, group, etc.
- **Eligibility Info**: Eligibility status and dates for exams, frames, lenses, etc.
- **Vision Benefits**:
  - Exam services (exam cost, retinal imaging)
  - Frame details (allowance, discount)
  - Lens options (single vision, bifocal, trifocal, etc.)
  - Progressive lens options (standard, premium tiers)
  - Contact lens options (conventional, disposable, medically necessary)

Results are saved to a JSON file for further analysis.

## Troubleshooting

If you encounter issues:

1. Check the extracted text (saved as `.txt`) to verify the PDF content is being properly extracted
2. Examine the JSON output for fields that may be missing or incorrect
3. Ensure Tesseract OCR is properly installed if you're testing image-based PDFs
4. Check the confidence scores in the output to identify potential issues

## Adding New Test Files

To test with a new EyeMed PDF:

1. Add the PDF to the `tests/samples/Eyemed/` directory
2. Run the test script with the path to your PDF:
   ```bash
   python test_eyemed.py tests/samples/Eyemed/your_new_file.pdf
   ``` 