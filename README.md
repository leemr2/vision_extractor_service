# Vision Insurance Extractor

A microservice for extracting structured benefit information from vision insurance documents.

## Overview

The Vision Insurance Extractor is a specialized API service that processes vision insurance PDFs and extracts structured benefit information. It supports multiple insurance providers including VSP, EyeMed, Davis Vision, Spectera, Superior Vision, and Versant Health.

This service accepts PDF uploads, processes them in-memory (with no persistent storage of the original document), and returns standardized JSON representations of the benefits data. It includes comprehensive PHI (Protected Health Information) redaction to ensure compliance with privacy requirements.

## Features

- **Multi-Provider Support**: Processes documents from VSP, EyeMed, Davis Vision, Spectera, Superior Vision, and Versant Health
- **Advanced Pattern Library**: Sophisticated pattern recognition system with multiple extraction strategies (regex, fuzzy matching, table-based, section-based) and confidence scoring
- **In-Memory Processing**: Handles documents securely without persistent storage
- **PHI Redaction**: Automatically detects and redacts patient identifiable information
- **Term Recognition**: Identifies and standardizes vision insurance terminology while preserving original document structure
- **Intelligent OCR**: Uses OCR for image-based PDFs or low-quality text extraction
- **Interactive Test Interface**: Web-based testing interface with drag-and-drop file upload and real-time results
- **RESTful API**: Simple API for document submission and JSON response
- **Containerized Deployment**: Packaged as a Docker container for easy deployment
- **Debug Tools**: Comprehensive debugging and testing utilities for development

## Supported Providers

### EyeMed

The service extracts comprehensive data from EyeMed vision insurance documents using an advanced pattern library system:

- **Member and Plan Information**: Intelligent extraction with pattern-based recognition
- **Eligibility Detection**: Advanced eligibility pattern matching for all benefit types
- **Exam Benefits**: Comprehensive exam benefit extraction including retinal imaging
- **Frame Allowances**: Frame benefit detection with allowance and discount extraction
- **Progressive Lens Tiers**: Sophisticated multi-tier progressive lens extraction (Standard, Premium, Tier 1-5, including "Tier 5 Innovations")
- **Lens Options**: Advanced pattern-based extraction for anti-reflective coatings, tints, photochromic options
- **Contact Lens Benefits**: Comprehensive contact lens coverage including conventional, disposable, and medically necessary options

**Key Features:**
- **Pattern Library Architecture**: Uses sophisticated pattern recognition with multiple extraction strategies
- **Confidence Scoring**: Built-in confidence assessment for extraction quality
- **Dynamic Pattern Generation**: Automatic pattern generation from term variations
- **Fallback Mechanisms**: Multiple pattern variations with automatic fallbacks

For detailed EyeMed extraction workflow, refer to [EyeMed Extraction Documentation](docs/eyemed_architecture/).

### VSP

VSP processing includes advanced dual-document handling capabilities:

- **Dual-Document Processing**: Handles both "Patient Record Report" and "Lens Enhancement Charges" documents
- **Combined Document Support**: Can process documents containing both sections in a single file
- **Comprehensive Lens Mapping**: Uses sophisticated code-based lens enhancement mapping system
- **Advanced Pricing Logic**: Handles complex pricing strategies including "Covered", percentage-based calculations, and maximum amounts

### Davis Vision, Spectera, and Superior Vision

Each provider has specialized extraction logic to handle their specific document formats and terminology:

- **Davis Vision**: Advanced tabular data extraction with sophisticated table parsing
- **Spectera**: Provider-specific pattern recognition and benefit extraction
- **Superior Vision**: Comprehensive benefit extraction using tabular processing methods

### Versant Health

Versant Health is the parent company of Davis Vision and Superior Vision. The service supports extraction from Versant Health insurance documents using a unified extractor architecture:

**Key features of the Versant Health extraction:**
- **Unified Template System**: Uses the `VersantUnifiedTemplate` that inherits from `DavisTemplate`
- **Multi-Provider Support**: Single extractor handles Davis Vision, Superior Vision, and Versant Health documents
- **Advanced Tabular Processing**: Sophisticated sequential parsing with multiple fallback strategies
- **Intelligent Provider Detection**: Automatically recognizes provider branding while handling dual-branded documents
- **Comprehensive Benefit Mapping**: Extracts detailed benefits data including:
  - Exam benefits with frequency and copay information
  - Spectacle lens benefits (single vision, bifocal, trifocal, lenticular)
  - Advanced lens options (AR coatings, progressive lenses, high-index materials, photochromic options)
  - Frame benefits (premier, designer, fashion, non-plan frames)
  - Contact lens benefits and fitting fees
- **Complex Value Parsing**: Handles various pricing formats including dollar amounts, "No Copay", and allowance values

## Installation

### Prerequisites

- Python 3.9+
- Docker (for containerized deployment)
- Tesseract OCR engine (for OCR capabilities)
- Access to the container registry (for production deployment)

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/leemr2/vision_extractor_service.git
   cd vision_extractor_service
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:

   **For Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr
   ```
   
   **For Windows:**
   - Download and install from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Add the Tesseract installation directory to your PATH
   
   **For macOS:**
   ```bash
   brew install tesseract
   ```

5. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

6. Run the development server:

   ```bash
   ./scripts/run_dev.sh
   # Or directly with: uvicorn app.main:app --reload
   ```

### Docker Deployment

1. Build the Docker image:

   ```bash
   docker build -t vision-extractor-service:latest .
   ```

2. Run the container:

   ```bash
   docker run -p 8000:8000 -e API_KEY=your_api_key vision-extractor-service:latest
   ```

## API Usage

### Authentication

All API requests require authentication using an API key:

```
Authorization: Bearer YOUR_API_KEY
```

### Extracting Benefits

**Endpoint:** `POST /api/extract`

**Request:**

- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF file upload
  - `provider_hint` (optional): Provider name hint (e.g., "eyemed", "versant", "vsp", "davis", "spectera")
  - `patient_id` (optional): Patient identifier for output naming
  - `vsp_file2` (optional): Second PDF file for VSP dual-document processing

**Response Example (EyeMed):**

```json
{
  "provider": "eyemed",
  "extraction_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "provider": "EyeMed",
    "patient_info": {
      "member_id": "ABC123456",
      "member_name": "[REDACTED]",
      "network": "Insight",
      "group": "Group123"
    },
    "eligibility_info": {
      "exam": {
        "is_eligible": true,
        "eligible_as_of": "01/01/2023",
        "frequency": "Once every 12 months"
      },
      "frame": {
        "is_eligible": true,
        "eligible_as_of": "01/01/2023",
        "frequency": "Once every 24 months"
      }
    },
    "vision_benefits": {
      "exam_services": {
        "exam": {
          "provider_name": "EyeMed",
          "cost_type": "copay",
          "cost_value": "$10",
          "cost_details": "For routine eye exam"
        }
      },
      "frame": {
        "provider_name": "EyeMed",
        "cost_type": "allowance",
        "allowance": "$150",
        "discount_percentage": "20%"
      }
    }
  },
  "confidence": 0.92,
  "processing_time": 1.25
}
```

### Interactive Test Interface

**Endpoint:** `GET /api/test-interface`

The service includes a comprehensive web-based test interface for development and testing:

**Features:**
- **Drag-and-Drop File Upload**: Modern file upload interface
- **Multi-Provider Support**: Dropdown selection for all supported providers
- **VSP Dual-File Mode**: Special handling for VSP's two-document requirement
- **Real-Time Results**: JSON output display with formatting
- **Result Persistence**: Automatic saving to `test_files/results/`

**Usage:**
1. Navigate to `/api/test-interface` in your browser
2. Select the provider from the dropdown
3. Upload PDF file(s) using drag-and-drop or file browser
4. View extraction results in real-time
5. Results are automatically saved with timestamp

### Health Check

**Endpoint:** `GET /health`

Returns service health status.

## Development

### Project Structure

```
/vision-extractor-service/
├── app/                     # Application code
│   ├── api/                 # API endpoints
│   │   ├── extract.py       # Main extraction endpoint
│   │   ├── test_interface.py # Interactive test interface
│   │   └── health.py        # Health check endpoint
│   ├── core/                # Business logic
│   │   ├── extractors/      # Provider-specific extractors
│   │   │   ├── eyemed_extractor.py      # EyeMed-specific extraction
│   │   │   ├── versant_tabular_extractor.py # Unified Versant Health extraction
│   │   │   ├── davis_tabular_extractor.py   # Davis Vision tabular extraction
│   │   │   ├── vsp_extractor.py         # VSP dual-document extraction
│   │   │   └── spectera_extractor.py    # Spectera extraction
│   │   ├── pattern_library/ # Advanced pattern recognition system
│   │   │   ├── base/        # Base pattern classes
│   │   │   ├── providers/   # Provider-specific patterns
│   │   │   │   └── eyemed/  # EyeMed pattern implementations
│   │   │   ├── utils/       # Pattern utilities
│   │   │   └── manager.py   # Pattern orchestration
│   │   ├── preprocessing/   # Document preprocessing
│   │   ├── templates/       # Output data templates
│   │   │   ├── eyemed_template.py       # EyeMed output structure
│   │   │   ├── versant_unified_template.py # Versant Health unified template
│   │   │   └── vsp_template.py          # VSP output structure
│   │   ├── utils/           # Utility functions
│   │   └── models/          # Data models
│   ├── config/              # Configuration
│   │   ├── provider_patterns.py    # Provider recognition patterns
│   │   ├── davis_mapping.py         # Davis Vision benefit mappings
│   │   ├── vsp_lens_mapping.py      # VSP lens code mappings
│   │   └── term_dictionary.py       # Vision insurance terminology
│   └── templates/           # HTML templates
│       └── test_interface.html      # Test interface UI
├── docs/                    # Documentation
│   ├── eyemed_architecture/ # EyeMed implementation documentation
│   ├── davis_architecture/  # Davis extraction planning
│   └── VSP_EXTRACTOR_DESIGN.md # VSP extractor design documentation
├── tests/                   # Test suite
│   ├── samples/             # Sample documents for testing
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── test_files/              # Test result storage
│   └── results/             # Extraction results from testing
├── debug_output/            # Debug information storage
└── scripts/                 # Utility scripts
    ├── run_dev.sh           # Development server script
    ├── run_tests.sh         # Test runner script
    └── build_docker.sh      # Docker build script
```

### Running Tests

The service includes multiple testing approaches:

#### Automated Test Suite
```bash
./scripts/run_tests.sh
# Or directly: pytest
```

#### Interactive Test Interface
Access the web-based test interface:
```bash
# Start the development server
./scripts/run_dev.sh
# Navigate to: http://localhost:8000/api/test-interface
```

#### Provider-Specific Testing
Test individual providers with dedicated scripts:
```bash
# Test EyeMed extraction
python test_eyemed.py [path/to/eyemed.pdf]

# Test VSP extraction
python test_vsp_extractor.py

# Test Davis Vision extraction
python test_davis_simplified.py

# Test Spectera extraction
python test_spectera_simplified.py
```

#### Pattern Library Testing
Test the pattern recognition system:
```bash
# Test pattern base functionality
python test_pattern_base.py

# Debug pattern library
python debug_patterns.py
```

For detailed EyeMed testing instructions, see [TESTING_EYEMED.md](TESTING_EYEMED.md).

### Adding a New Insurance Provider

1. **Create Provider Extractor**: Add a new extractor class in `app/core/extractors/`
2. **Pattern Library Integration**: 
   - Create provider-specific patterns in `app/core/pattern_library/providers/[provider]/`
   - Implement pattern groups for eligibility, benefits, lens options, etc.
   - Register patterns with the pattern manager
3. **Provider Recognition**: Add provider detection patterns to `app/config/provider_patterns.py`
4. **Output Template**: Create a template for structured output in `app/core/templates/`
5. **Configuration**: Add provider-specific mappings and terminology to `app/config/`
6. **Schema Validation**: Add validation rules in `app/core/validators/`
7. **Testing**: 
   - Create provider-specific test scripts
   - Add sample documents to `tests/samples/[provider]/`
   - Update the interactive test interface

### Pattern Library Development

The advanced pattern library system supports multiple extraction strategies:

#### Pattern Types
- **RegexPattern**: Traditional regex-based extraction
- **FuzzyPattern**: Fuzzy string matching for variations
- **TablePattern**: Structured table data extraction
- **SectionPattern**: Section-based document parsing

#### Pattern Development Workflow
1. **Pattern Definition**: Create pattern classes with confidence scoring
2. **Testing**: Use `debug_patterns.py` to test pattern recognition
3. **Integration**: Register patterns with the pattern manager
4. **Validation**: Test with real documents using the test interface

#### Example Pattern Implementation
```python
# Example pattern for progressive lens extraction
PROGRESSIVE_PATTERNS = PatternGroup(
    name="progressive_lenses",
    patterns=[
        RegexPattern(
            name="progressive_standard",
            pattern_type=PatternType.EXACT,
            target_field="progressive.standard",
            confidence=ConfidenceLevel.HIGH,
            patterns=[r"Progressive.*Standard.*\$(\d+)"]
        )
    ]
)
```

### Debug and Development Tools

The service includes comprehensive debugging capabilities:

#### Debug Output
- **Debug Logging**: Detailed logging for extraction processes
- **Debug Output Directory**: `debug_output/` contains extracted text and processing logs
- **Pattern Debug**: `debug_patterns.py` for testing pattern recognition

#### Development Utilities
- **Text Extraction**: Raw text extraction utilities for document analysis
- **Pattern Testing**: Isolated pattern testing without full document processing
- **Result Validation**: Validation tools for output structure verification

## Security Considerations

- **In-Memory Processing**: No input files are saved to disk; all processing happens in memory
- **PHI Redaction**: Automatically detects and redacts patient identifiable information
- **API Authentication**: API authentication is required for all endpoints
- **No Persistent Storage**: No database or persistent storage is used for documents
- **Secure Testing**: Test interface results are stored locally and not transmitted
- **Input Validation**: Comprehensive input validation for all file uploads

## License



## Contributors



## Support

For issues, questions, or feedback, please [create an issue](https://github.com/yourusername/vision-extractor-service/issues) on GitHub.