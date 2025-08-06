# Simplified EyeMed Vision Benefits Extractor

This document explains the simplified EyeMed vision benefits extractor, which has been updated to provide a streamlined output structure with enhanced privacy protection.

## Key Features

- **PHI Protection**: Removes all member information to protect PHI
- **Simplified Eligibility**: Only includes boolean flags for eligibility (no dates or frequency)
- **Consistent Cost Values**: Extracts vision benefits cost values in standardized formats
- **PDF Focus**: Optimized for PDF processing (not scanned images)
- **Progressive Lenses and Anti-Reflective Coatings**: Properly extracts these important benefits

## Output Structure

The extractor produces a JSON structure with the following key sections:

1. **Provider Information**: Identifies the document as EyeMed
2. **Eligibility Information**: Boolean flags for each service type
   - `exam_eligible`: true/false
   - `lenses_eligible`: true/false
   - `frame_eligible`: true/false
   - `contact_lenses_eligible`: true/false
3. **Vision Benefits**: Detailed cost values for each service category, including:
   - Exam services
   - Frame
   - Lenses (single vision, bifocal, trifocal, lenticular)
   - Progressive lenses (standard and premium tiers)
   - Lens options, including anti-reflective coating
   - Contact lens fit and follow-up
   - Contact lenses
4. **Confidence Score**: Overall confidence in the extraction (0.0 to 1.0)

## Cost Value Formats

The extractor captures cost values in the following formats:

1. **Set Dollar Copay**: `$10 copay`
2. **Percentage Off Retail Over Dollar Allowance**: `20% off balance over $150`
3. **Percentage Off Retail Less Dollar Allowance**: `20% off retail price less $120 allowance`
4. **Percentage Off Retail**: `20% off retail`

## Testing the Extractor

A comprehensive test script `test_eyemed_simplified.py` is provided to verify extraction results with different inputs:

### Test with Synthetic Data

```bash
python test_eyemed_simplified.py --synthetic
```

This runs the extractor on a synthetic EyeMed benefits document built into the script.

### Test with a Specific PDF File

```bash
python test_eyemed_simplified.py --file path/to/eyemed_document.pdf
```

This processes a specific PDF file and outputs the results to a JSON file.

### Batch Test with Multiple PDF Files

```bash
python test_eyemed_simplified.py --batch path/to/pdf/directory
```

This processes all PDF files in the specified directory and outputs results for each file.

### Specifying Output Location

```bash
python test_eyemed_simplified.py --file path/to/eyemed_document.pdf --output custom_output.json
```

Or for batch processing:

```bash
python test_eyemed_simplified.py --batch path/to/pdf/directory --output path/to/results
```

## Implementation Details

The simplified extractor is implemented in:

- `app/core/templates/eyemed_template.py`: Defines the output data structure
- `app/core/extractors/eyemed_extractor.py`: Implements the extraction logic

Key changes include:

1. Removed `PatientInfo` class from the template to protect PHI
2. Simplified `EligibilityInfo` to only include boolean flags
3. Enhanced extraction patterns for frame, progressive lenses, and anti-reflective coatings
4. Added confidence score calculation
5. Optimized text preprocessing for PDF documents

## Troubleshooting

If you encounter issues with extraction:

1. Check that the PDF document is text-based (not a scanned image)
2. Verify that the document follows EyeMed's standard format
3. Review the confidence score - lower scores may indicate issues with extraction
4. Examine the test output for specific fields that may be missing or incorrect

For scanned document support, additional OCR setup would be required. 