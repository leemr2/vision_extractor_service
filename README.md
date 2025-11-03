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

### ⚠️ Required Environment Variables

**IMPORTANT:** As of Phase 1 security improvements, the service requires proper environment configuration to start. The following environment variables are **required**:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | **YES** | None | API authentication key (minimum 32 characters recommended) |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:8000` | Comma-separated list of allowed CORS origins |
| `DEBUG` | No | `False` | Enable debug mode for development |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `MAX_DOCUMENT_SIZE_MB` | No | `10` | Maximum document size in megabytes (enforced at API level) |
| `RATE_LIMIT_PER_MINUTE` | No | `10` | Maximum API requests per minute per IP address |
| `RATE_LIMIT_ENABLED` | No | `True` | Enable/disable rate limiting |

**The service will not start without a valid API_KEY configured.**

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

5. **Generate a secure API key:**

   ```bash
   # Using Python (recommended)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Or using OpenSSL
   openssl rand -base64 32
   
   # On Windows PowerShell
   [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
   ```

6. **Set up environment variables:**

   Create a `.env` file in the project root:

   ```bash
   # .env
   # API Authentication (REQUIRED)
   API_KEY=your_generated_secure_api_key_here
   
   # CORS Configuration (comma-separated list of allowed origins)
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   
   # Debug Mode (set to True for development)
   DEBUG=True
   
   # Logging Level
   LOG_LEVEL=INFO
   
   # Document Processing Limits
   MAX_DOCUMENT_SIZE_MB=10
   
   # Rate Limiting (requests per minute per IP)
   RATE_LIMIT_PER_MINUTE=10
   RATE_LIMIT_ENABLED=True
   ```

   **⚠️ IMPORTANT:** 
   - Never commit your `.env` file to version control
   - Use a strong, randomly generated API key (minimum 32 characters)
   - Never use `test_api_key` or similar weak values in production

7. Run the development server:

   ```bash
   # On Unix/macOS
   ./scripts/run_dev.sh
   
   # Or directly with uvicorn
   uvicorn app.main:app --reload
   
   # On Windows (using venv)
   .\venv\Scripts\python.exe -m app.main
   ```

### Docker Deployment

1. **Generate a secure API key** (see step 5 in Local Development Setup above)

2. Build the Docker image:

   ```bash
   docker build -t vision-extractor-service:latest .
   ```

3. Run the container with environment variables:

   ```bash
   # Using environment variables directly
   docker run -p 8000:8000 \
     -e API_KEY=your_generated_secure_api_key_here \
     -e CORS_ORIGINS=http://localhost:3000,http://localhost:8000 \
     -e DEBUG=False \
     vision-extractor-service:latest
   ```

4. Or use Docker Compose with environment file:

   Create a `docker-compose.yml`:
   ```yaml
   version: '3.8'
   
   services:
     vision-extractor:
       build: .
       ports:
         - "8000:8000"
       env_file:
         - .env
       environment:
         - API_KEY=${API_KEY}
         - CORS_ORIGINS=${CORS_ORIGINS}
         - DEBUG=${DEBUG}
         - LOG_LEVEL=${LOG_LEVEL}
   ```

   Then run:
   ```bash
   docker-compose up
   ```

   **⚠️ Security Note:** 
   - Never hardcode API keys in Dockerfiles or docker-compose.yml
   - Use environment variables or secrets management
   - Ensure `.env` is in your `.gitignore`

## API Usage

### Authentication

**All API requests require authentication** using the API key configured in your environment variables.

Include the API key in the `Authorization` header using Bearer token format:

```
Authorization: Bearer YOUR_API_KEY
```

**Example using cURL:**
```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Authorization: Bearer your_api_key_here" \
  -F "file=@sample.pdf" \
  -F "provider_hint=eyemed"
```

**Example using Python requests:**
```python
import requests

headers = {
    'Authorization': 'Bearer your_api_key_here'
}

files = {
    'file': ('sample.pdf', open('sample.pdf', 'rb'), 'application/pdf')
}

data = {
    'provider_hint': 'eyemed'
}

response = requests.post(
    'http://localhost:8000/api/extract',
    headers=headers,
    files=files,
    data=data
)
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid API key
- `400 Bad Request`: Invalid request parameters
- `413 Payload Too Large`: File exceeds maximum size limit (default 10MB)
- `429 Too Many Requests`: Rate limit exceeded (default 10 requests/minute)
- `500 Internal Server Error`: Processing error

**Rate Limiting:**
- The API enforces rate limits to prevent abuse (default: 10 requests per minute per IP address)
- Rate limit information is included in response headers: `X-RateLimit-Limit`
- Adjust `RATE_LIMIT_PER_MINUTE` in environment variables to customize limits

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

### Data Protection
- **In-Memory Processing**: No input files are saved to disk; all processing happens in memory
- **PHI Redaction**: Automatically detects and redacts patient identifiable information (SSN, DOB, etc.)
- **No Persistent Storage**: No database or persistent storage is used for documents
- **Secure Testing**: Test interface results are stored locally and not transmitted
- **Input Validation**: Comprehensive input validation for all file uploads

### Authentication & Authorization
- **Required API Key**: API authentication is mandatory for all endpoints (enforced since Phase 1)
- **Bearer Token Authentication**: Standard OAuth 2.0 Bearer token format
- **Secure Key Generation**: Cryptographically secure random key generation required
- **Environment-Based Configuration**: API keys must be configured via environment variables

### Network Security
- **CORS Protection**: Configurable CORS origins (defaults to localhost for development)
- **HTTPS Recommended**: Always use HTTPS in production environments
- **Rate Limiting**: Enforced at API level (10 requests/minute per IP by default, configurable)
- **Security Headers**: Comprehensive security headers on all responses:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Content-Security-Policy: default-src 'self'`

### Configuration Security
- **No Default Keys**: Service will not start without proper API_KEY configuration
- **Validation on Startup**: Configuration is validated when the service starts
- **Environment Variables**: Sensitive configuration is never hardcoded
- **Production Warnings**: Automatic warnings for insecure configurations in production mode

### Best Practices
1. **Generate Strong API Keys**: Use cryptographically secure random generators (minimum 32 characters)
2. **Rotate Keys Regularly**: Implement a key rotation schedule for production
3. **Use Environment Files**: Never commit `.env` files or hardcode secrets
4. **Restrict CORS Origins**: Set specific allowed origins in production (avoid wildcards)
5. **Enable Logging**: Monitor authentication failures and suspicious activity
6. **Keep Dependencies Updated**: Regularly update dependencies for security patches

Security Improvements (Completed)
✅ Mandatory API key authentication  
✅ Secure configuration defaults  
✅ Improved error handling (no bare except blocks)  
✅ Input validation enforcement  
✅ CORS origin restrictions  
✅ Configuration validation on startup  

Security Hardening (Completed)
✅ Rate limiting with configurable thresholds (slowapi integration)  
✅ Document size limit enforcement (validated before processing)  
✅ Security headers middleware (comprehensive HTTP security headers)  
✅ Improved temp file handling (automatic cleanup with context managers)  
✅ Resource leak prevention (proper file descriptor management)  

**Security Enhancements Details:**
- **Rate Limiting**: Prevents DoS attacks by limiting requests to 10/minute per IP (configurable)
- **File Size Validation**: Enforces maximum document size at API level before processing
- **Security Headers**: Industry-standard security headers on all responses
- **Automatic Cleanup**: Context managers ensure temp files are always deleted
- **Error Isolation**: Specific exception handling prevents resource leaks

See `CODE_QUALITY_ANALYSIS.md` for detailed security improvements and future roadmap.

## License



## Contributors



## Support

For issues, questions, or feedback, please [create an issue](https://github.com/yourusername/vision-extractor-service/issues) on GitHub.