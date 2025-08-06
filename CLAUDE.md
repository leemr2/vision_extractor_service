# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Service
- **Development server**: `./scripts/run_dev.sh` or `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- **Docker build**: `docker build -t vision-extractor-service:latest .`
- **Docker compose**: `docker-compose up`

### Testing
- **Run all tests**: `./scripts/run_tests.sh` or `pytest --cov=app tests/ --cov-report=term-missing`
- **Test EyeMed extraction**: `python test_eyemed.py [path/to/eyemed.pdf]`
- **Test VSP extraction**: `python test_vsp_extractor.py`
- **Test Davis Vision**: `python test_davis_simplified.py`
- **Test Spectera**: `python test_spectera_simplified.py`
- **Pattern library testing**: `python test_pattern_base.py`
- **Debug patterns**: `python debug_patterns.py`

### Interactive Testing
- Access web-based test interface at: `/api/test-interface`
- Supports drag-and-drop file upload, provider selection, and real-time results

## High-Level Architecture

### Core Processing Flow
1. **Document Upload** → FastAPI endpoint (`/api/extract`)
2. **Text Extraction** → PDF processing with OCR fallback
3. **Provider Detection** → Pattern-based provider identification
4. **PHI Redaction** → Automatic patient information removal
5. **Provider-Specific Extraction** → Specialized extractors per insurance provider
6. **Data Validation** → Schema validation against templates
7. **JSON Response** → Standardized output format

### Provider-Specific Extractors
Located in `app/core/extractors/`:
- **EyeMedExtractor**: Advanced pattern library system with confidence scoring
- **VSPExtractor**: Dual-document processing (Patient Record + Lens Enhancement)
- **VersantTabularExtractor**: Unified extractor for Davis/Superior/Versant using tabular parsing
- **SpecteraExtractor**: Provider-specific pattern recognition
- **BaseExtractor**: Abstract base class defining common interface

### Pattern Library System (`app/core/pattern_library/`)
Advanced extraction system supporting:
- **Multiple Pattern Types**: Regex, fuzzy matching, table-based, section-based
- **Confidence Scoring**: Built-in quality assessment
- **Dynamic Pattern Generation**: Automatic pattern variations
- **Fallback Mechanisms**: Multiple extraction strategies
- **Provider-Specific Patterns**: Organized by insurance provider

### Key Components
- **PatternManager**: Orchestrates pattern-based extraction
- **Document Classifier**: Detects insurance provider from document content
- **Schema Validator**: Validates extracted data against provider templates
- **Security Module**: PHI redaction and input validation

### VSP Dual-Document Processing
VSP requires processing two documents together:
- Primary document: Patient Record Report
- Secondary document: Lens Enhancement Charges
- Combined processing through `process_vsp_documents()` function

### Template System (`app/core/templates/`)
Standardized output structures for each provider:
- **EyeMedTemplate**: Complex benefit structure with progressive lens tiers
- **VSPTemplate**: Dual-document benefit mapping
- **VersantUnifiedTemplate**: Shared template for Davis/Superior/Versant
- **SpecteraTemplate**: Provider-specific benefit structure

### Configuration (`app/config/`)
- **provider_patterns.py**: Provider detection patterns
- **davis_mapping.py**: Davis Vision benefit mappings
- **vsp_lens_mapping.py**: VSP lens code mappings
- **term_dictionary.py**: Vision insurance terminology

## Important Implementation Notes

### Security Requirements
- All processing is in-memory with no persistent storage
- Automatic PHI redaction for patient information
- API key authentication required for all extraction endpoints
- Temporary files are automatically cleaned up

### Adding New Providers
1. Create extractor class inheriting from `BaseExtractor`
2. Implement provider-specific patterns in `pattern_library/providers/[provider]/`
3. Add provider detection patterns to `provider_patterns.py`
4. Create output template in `templates/`
5. Add provider configuration mappings
6. Register extractor in `processor.py:get_extractor()`

### Testing Strategy
- Interactive web interface for manual testing
- Provider-specific test scripts for isolated testing
- Integration tests for full API workflow
- Pattern library unit tests for extraction accuracy
- Results automatically saved to `test_files/results/`