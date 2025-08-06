# Vision Extractor Service - Refactoring Plan

## Executive Summary

This document outlines a comprehensive step-by-step refactoring plan for the Vision Extractor Service codebase. The plan addresses code duplication, configuration management, architectural coupling, and testing structure issues identified through detailed codebase analysis.

## Current State Analysis

### Key Issues Identified
1. **High Code Duplication**: Each extractor implements similar methods independently
2. **Scattered Configuration**: Provider mappings distributed across multiple files
3. **Tight Coupling**: Components directly depend on concrete implementations
4. **Inconsistent Data Models**: Different templates with overlapping responsibilities
5. **Fragmented Testing**: Tests scattered between directories and root level
6. **Pattern Library Limitations**: Basic functionality with limited reusability

### Priority Matrix
| Area | Impact | Effort | Priority |
|------|--------|--------|----------|
| Extractor Duplication | High | Medium | **HIGH** |
| Configuration Management | High | Low | **HIGH** |
| Data Model Consistency | Medium | Medium | **MEDIUM** |
| Component Coupling | High | High | **MEDIUM** |
| Testing Structure | Medium | Low | **MEDIUM** |

## Implementation Phases

### Phase 1: Foundation Cleanup (Week 1-2)
**Objective**: Clean up project structure and centralize configuration

#### Step 1.1: Consolidate Test Files
```bash
# Move all root-level test files to tests/ directory
tests/
├── unit/
│   ├── extractors/
│   │   ├── test_davis_extractor.py  # from test_davis_simplified.py
│   │   ├── test_eyemed_extractor.py # from test_eyemed.py
│   │   ├── test_vsp_extractor.py    # from test_vsp_extractor.py
│   │   └── test_spectera_extractor.py # from test_spectera_simplified.py
│   ├── patterns/
│   │   ├── test_pattern_base.py     # from test_pattern_base.py
│   │   └── test_regex_patterns.py   # from test_regex.py
│   └── core/
├── integration/
│   └── test_full_pipeline.py       # from test_simplified_plan.py
└── fixtures/
    └── sample_documents/
```

**Actions:**
1. Create proper test directory structure
2. Move and rename test files following naming conventions
3. Update imports and paths in moved files
4. Remove root-level test files
5. Update GitHub Actions/CI to use new test structure

#### Step 1.2: Centralize Configuration Management
```python
# New structure: app/config/providers/
app/config/
├── __init__.py
├── settings.py                    # Enhanced settings
├── providers/
│   ├── __init__.py
│   ├── base_provider_config.py
│   ├── vsp_config.py             # from vsp_lens_mapping.py
│   ├── davis_config.py           # from davis_mapping.py
│   ├── eyemed_config.py
│   ├── spectera_config.py        # from spectera_lens_mapping.py
│   └── versant_config.py
└── factory.py                    # Configuration factory
```

**Actions:**
1. Create `BaseProviderConfig` abstract class
2. Convert existing mapping files to provider config classes
3. Implement `ConfigurationFactory` for dynamic provider config loading
4. Create `ProviderConfigRegistry` for centralized config management
5. Update all extractors to use centralized configuration
6. Remove old mapping files

#### Step 1.3: Remove Legacy Files
**Actions:**
1. Archive or remove `fixed_eyemed.py` (appears to be development artifact)
2. Clean up `debug_output/` directory structure
3. Consolidate any scattered configuration remnants

### Phase 2: Extractor Architecture Refactoring (Week 3-4)
**Objective**: Eliminate code duplication and improve extractor architecture

#### Step 2.1: Create Shared Extraction Engine
```python
# app/core/extraction/
app/core/extraction/
├── __init__.py
├── engine.py              # Main extraction engine
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py
│   ├── regex_strategy.py
│   ├── table_strategy.py
│   ├── fuzzy_strategy.py
│   └── section_strategy.py
└── context.py             # Extraction context management
```

**New ExtractionEngine Implementation:**
```python
class ExtractionEngine:
    def __init__(self, provider_config: ProviderConfig):
        self.config = provider_config
        self.strategies = self._load_strategies()
    
    async def extract_field(self, field_type: str, document_text: str) -> ExtractionResult:
        strategy_config = self.config.get_extraction_strategy(field_type)
        strategy = self.strategies[strategy_config.type]
        return await strategy.extract(document_text, strategy_config)
    
    async def extract_all_fields(self, document_text: str) -> Dict[str, ExtractionResult]:
        results = {}
        for field_type in self.config.supported_fields:
            results[field_type] = await self.extract_field(field_type, document_text)
        return results
```

**Actions:**
1. Implement base `ExtractionStrategy` interface
2. Create concrete strategy implementations for each extraction type
3. Implement `ExtractionEngine` with strategy pattern
4. Create `ExtractionContext` for managing extraction state
5. Refactor `BaseExtractor` to use extraction engine

#### Step 2.2: Refactor Individual Extractors
**Template for New Extractor Structure:**
```python
class ProviderExtractor(BaseExtractor):
    def __init__(self, provider_config: ProviderConfig):
        super().__init__()
        self.config = provider_config
        self.engine = ExtractionEngine(provider_config)
        self.adapter = self._create_adapter()
    
    async def extract(self, document_text: str, **kwargs) -> Dict[str, Any]:
        # Common extraction workflow
        raw_results = await self.engine.extract_all_fields(document_text)
        standardized_data = self.adapter.adapt_to_standard(raw_results)
        return self._format_output(standardized_data)
    
    def _create_adapter(self) -> ProviderAdapter:
        return AdapterFactory.create(self.config.provider_type)
```

**Actions:**
1. Refactor `VSPExtractor` to use extraction engine
2. Refactor `EyeMedExtractor` to use extraction engine
3. Refactor `DavisTabularExtractor` to use extraction engine
4. Refactor `SpecteraExtractor` to use extraction engine
5. Refactor `VersantTabularExtractor` to use extraction engine
6. Remove duplicated extraction logic from individual extractors
7. Update unit tests for each extractor

#### Step 2.3: Enhance BaseExtractor
**Actions:**
1. Move common extraction logic to `BaseExtractor`
2. Implement template method pattern for extraction workflow
3. Add common validation and error handling
4. Standardize logging across all extractors

### Phase 3: Data Model Unification (Week 5-6)
**Objective**: Create consistent data models and reduce mapping complexity

#### Step 3.1: Design Unified Data Models
```python
# app/core/models/unified/
app/core/models/unified/
├── __init__.py
├── base_models.py         # Base classes for all models
├── extraction_result.py   # Standardized extraction result
├── eligibility_models.py  # Unified eligibility data structures
├── benefit_models.py      # Unified benefit data structures
└── metadata_models.py     # Extraction metadata models
```

**Standard Model Structure:**
```python
class StandardExtractionResult(BaseModel):
    provider: str
    extraction_id: str
    timestamp: datetime
    confidence: float
    patient_info: Optional[PatientInfo]
    eligibility: EligibilityData
    benefits: BenefitData
    metadata: ExtractionMetadata
    raw_data: Optional[Dict[str, Any]]  # Provider-specific raw data
```

**Actions:**
1. Design unified base models for all data types
2. Create standard field mappings between provider-specific and unified models
3. Implement validation schemas for unified models
4. Create migration utilities for existing data structures

#### Step 3.2: Implement Provider Adapters
```python
# app/core/adapters/
app/core/adapters/
├── __init__.py
├── base_adapter.py
├── vsp_adapter.py
├── eyemed_adapter.py
├── davis_adapter.py
├── spectera_adapter.py
└── factory.py
```

**Adapter Pattern Implementation:**
```python
class ProviderAdapter(ABC):
    @abstractmethod
    def adapt_to_standard(self, provider_data: Dict[str, Any]) -> StandardExtractionResult:
        pass
    
    @abstractmethod
    def adapt_from_standard(self, standard_data: StandardExtractionResult) -> Dict[str, Any]:
        pass

class VSPAdapter(ProviderAdapter):
    def adapt_to_standard(self, vsp_data: Dict[str, Any]) -> StandardExtractionResult:
        return StandardExtractionResult(
            provider="VSP",
            eligibility=self._map_vsp_eligibility(vsp_data.get("eligibility", {})),
            benefits=self._map_vsp_benefits(vsp_data.get("vision_benefits", {})),
            # ... additional mapping logic
        )
```

**Actions:**
1. Implement base adapter interface
2. Create concrete adapters for each provider
3. Implement bidirectional mapping (to/from standard format)
4. Add adapter factory for dynamic adapter creation
5. Update extractors to use adapters for output formatting

#### Step 3.3: Replace Legacy Templates
**Actions:**
1. Update all extractors to output unified models
2. Deprecate provider-specific templates (`VSPTemplate`, `EyeMedTemplate`, etc.)
3. Update API responses to use unified format
4. Maintain backward compatibility with version-aware response formatting
5. Update all tests to expect unified model outputs

### Phase 4: Dependency Injection and Decoupling (Week 7-8)
**Objective**: Reduce coupling and improve testability

#### Step 4.1: Implement Dependency Injection Container
```python
# app/core/container/
app/core/container/
├── __init__.py
├── container.py           # Main DI container
├── providers.py           # Service providers
└── bindings.py           # Service bindings configuration
```

**DI Container Implementation:**
```python
class DIContainer:
    def __init__(self):
        self._bindings = {}
        self._instances = {}
    
    def bind(self, interface: Type, implementation: Type, singleton: bool = False):
        self._bindings[interface] = {
            'implementation': implementation,
            'singleton': singleton
        }
    
    def get(self, interface: Type):
        if interface in self._instances:
            return self._instances[interface]
        
        binding = self._bindings.get(interface)
        if not binding:
            raise ValueError(f"No binding found for {interface}")
        
        instance = binding['implementation']()
        if binding['singleton']:
            self._instances[interface] = instance
        
        return instance

# Configuration
container = DIContainer()
container.bind(IExtractionEngine, ExtractionEngine, singleton=True)
container.bind(IPatternManager, PatternManager, singleton=True)
container.bind(IConfigurationFactory, ConfigurationFactory, singleton=True)
```

**Actions:**
1. Implement lightweight DI container
2. Define interfaces for all major components
3. Configure service bindings for production and testing
4. Update extractors to receive dependencies via constructor injection
5. Update API endpoints to use DI container for service resolution

#### Step 4.2: Refactor DocumentProcessor
**Current Issue:** `DocumentProcessor` directly instantiates all extractors
```python
# Current tightly coupled approach
extractors = {
    ProviderType.VSP: VSPExtractor(),
    ProviderType.EYEMED: EyeMedExtractor(),
    # ...
}
```

**New Approach:**
```python
class DocumentProcessor:
    def __init__(self, extractor_factory: IExtractorFactory):
        self._extractor_factory = extractor_factory
    
    async def process_document(self, provider_type: ProviderType, document_data: bytes) -> ExtractionResult:
        extractor = self._extractor_factory.create_extractor(provider_type)
        return await extractor.extract(document_data)

class ExtractorFactory(IExtractorFactory):
    def __init__(self, container: DIContainer):
        self._container = container
    
    def create_extractor(self, provider_type: ProviderType) -> BaseExtractor:
        config = self._container.get(IConfigurationFactory).get_provider_config(provider_type)
        return self._container.get(BaseExtractor, provider_type=provider_type)
```

**Actions:**
1. Create `IExtractorFactory` interface and implementation
2. Refactor `DocumentProcessor` to use factory injection
3. Update API endpoints to use dependency injection
4. Remove direct extractor instantiations throughout codebase

#### Step 4.3: Enhance Pattern Library with DI
**Actions:**
1. Convert pattern managers to use dependency injection
2. Make pattern libraries configurable via DI container
3. Enable easy swapping of pattern implementations for testing
4. Improve pattern library testability with mock injection

### Phase 5: Enhanced Testing Infrastructure (Week 9)
**Objective**: Improve test coverage and organization

#### Step 5.1: Implement Test Infrastructure
```python
# tests/infrastructure/
tests/infrastructure/
├── __init__.py
├── fixtures.py            # Test data fixtures
├── mocks.py              # Mock implementations
├── builders.py           # Test data builders
└── test_container.py     # DI container for testing
```

**Test Infrastructure Features:**
```python
class TestDataBuilder:
    @staticmethod
    def sample_vsp_document() -> bytes:
        # Return sample VSP document bytes
        pass
    
    @staticmethod
    def expected_vsp_result() -> StandardExtractionResult:
        # Return expected extraction result
        pass

class MockExtractorFactory(IExtractorFactory):
    def __init__(self, mock_extractors: Dict[ProviderType, BaseExtractor]):
        self._mock_extractors = mock_extractors
    
    def create_extractor(self, provider_type: ProviderType) -> BaseExtractor:
        return self._mock_extractors[provider_type]
```

**Actions:**
1. Create comprehensive test data builders
2. Implement mock versions of all major interfaces
3. Set up test-specific DI container configuration
4. Create reusable test fixtures for common scenarios

#### Step 5.2: Improve Test Coverage
**Target Test Structure:**
```
tests/
├── unit/
│   ├── extractors/        # Individual extractor tests
│   ├── adapters/          # Adapter functionality tests
│   ├── models/           # Model validation tests
│   ├── patterns/         # Pattern library tests
│   └── core/             # Core component tests
├── integration/
│   ├── api/              # API endpoint tests
│   ├── extraction/       # End-to-end extraction tests
│   └── pipeline/         # Full processing pipeline tests
├── fixtures/
│   ├── documents/        # Sample test documents
│   └── expected_results/ # Expected extraction outputs
└── infrastructure/       # Test utilities and mocks
```

**Actions:**
1. Add comprehensive unit tests for all new components
2. Create integration tests for extraction workflows
3. Implement property-based testing for data models
4. Add performance tests for extraction pipeline
5. Set up test coverage reporting and monitoring

### Phase 6: API and Security Enhancements (Week 10)
**Objective**: Improve API design and security posture

#### Step 6.1: API Restructuring
**New API Structure:**
```
/api/v1/
├── extract/
│   ├── single           # Single document extraction
│   ├── batch            # Batch processing
│   └── validate         # Document validation
├── providers/
│   ├── supported        # List supported providers
│   └── {provider}/info  # Provider-specific information
├── health/
│   ├── status           # Service health
│   └── metrics          # Performance metrics
└── admin/
    ├── config           # Configuration management
    └── cache            # Cache management
```

**Actions:**
1. Implement versioned API endpoints
2. Add batch processing capabilities
3. Create provider information endpoints
4. Implement comprehensive health checks
5. Add API documentation with OpenAPI/Swagger

#### Step 6.2: Security Enhancements
**Security Improvements:**
```python
# Enhanced security features
class SecurityMiddleware:
    async def __call__(self, request: Request, call_next):
        # Rate limiting
        # Input sanitization
        # Audit logging
        # Request validation
        pass

class PHIRedactor:
    def __init__(self, patterns: List[RedactionPattern]):
        self.patterns = patterns
    
    def redact_document(self, text: str) -> RedactionResult:
        # Enhanced PHI detection and redaction
        pass
```

**Actions:**
1. Implement proper rate limiting middleware
2. Add comprehensive input validation and sanitization
3. Enhance PHI detection and redaction capabilities
4. Implement audit logging for all operations
5. Add request/response encryption for sensitive data
6. Implement proper secrets management

## Implementation Guidelines

### Code Quality Standards
1. **Type Hints**: All new code must include comprehensive type hints
2. **Documentation**: Every public method must have docstrings
3. **Error Handling**: Implement consistent error handling patterns
4. **Logging**: Use structured logging throughout the application
5. **Testing**: Minimum 80% test coverage for all new code

### Performance Considerations
1. **Async/Await**: Maintain async patterns for all I/O operations
2. **Memory Management**: Ensure efficient memory usage for document processing
3. **Caching**: Implement appropriate caching for configuration and patterns
4. **Monitoring**: Add performance monitoring and metrics collection

### Migration Strategy
1. **Backward Compatibility**: Maintain API compatibility during transition
2. **Feature Flags**: Use feature flags to enable new functionality gradually
3. **Database Migration**: Plan for any data structure changes
4. **Deployment Strategy**: Implement blue-green deployment for zero downtime

## Success Metrics

### Technical Metrics
- **Code Duplication**: Reduce from ~40% to <10%
- **Test Coverage**: Increase from ~60% to >90%
- **Cyclomatic Complexity**: Reduce average complexity by 30%
- **Configuration Files**: Reduce from 8 scattered files to 1 centralized system

### Performance Metrics
- **Extraction Speed**: Maintain or improve current processing times
- **Memory Usage**: Reduce memory footprint by 20%
- **Error Rate**: Reduce extraction errors by 50%
- **Maintainability**: Reduce time to add new provider by 60%

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | Week 1-2 | Clean project structure, centralized config |
| Phase 2 | Week 3-4 | Refactored extractors, extraction engine |
| Phase 3 | Week 5-6 | Unified data models, provider adapters |
| Phase 4 | Week 7-8 | Dependency injection, decoupled components |
| Phase 5 | Week 9 | Enhanced testing infrastructure |
| Phase 6 | Week 10 | API improvements, security enhancements |

**Total Estimated Timeline: 10 weeks**

## Risk Mitigation

### Technical Risks
1. **Breaking Changes**: Maintain backward compatibility through versioning
2. **Performance Regression**: Implement performance monitoring and rollback plan
3. **Data Loss**: Ensure thorough testing of data transformation logic
4. **Integration Issues**: Implement comprehensive integration testing

### Process Risks
1. **Timeline Delays**: Prioritize high-impact, low-effort improvements first
2. **Resource Constraints**: Plan for incremental delivery and partial implementations
3. **Stakeholder Alignment**: Regular demos and progress updates

## Conclusion

This refactoring plan addresses the major architectural issues in the Vision Extractor Service while maintaining system functionality and improving code quality. The phased approach ensures manageable implementation with clear milestones and deliverables.

The successful completion of this refactoring will result in:
- More maintainable and testable codebase
- Easier addition of new insurance providers
- Improved performance and reliability
- Better security and compliance posture
- Enhanced developer experience and productivity