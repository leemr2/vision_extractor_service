# Vision Extractor Pattern Library

This pattern library provides a flexible, extensible system for extracting structured information from vision insurance documents. It's designed to overcome the limitations of rigid pattern matching by providing multiple strategies for identifying and extracting benefit information.

## Key Features

- **Multiple pattern types**: Regular expressions, fuzzy matching, table-based extraction, and section-based extraction
- **Fallback patterns**: Each field can have multiple pattern variations with automatic fallbacks
- **Confidence scoring**: Results include confidence scores to indicate extraction quality
- **Provider-specific patterns**: Easily add patterns for new insurance providers
- **Dynamic pattern generation**: Create patterns programmatically from term variations

## Architecture

The pattern library is organized as follows:

```
app/core/pattern_library/
├── base/
│   ├── __init__.py
│   └── pattern_base.py       # Base classes for patterns
├── providers/
│   ├── __init__.py
│   ├── eyemed/               # EyeMed-specific patterns
│   │   ├── __init__.py
│   │   ├── exam.py
│   │   ├── progressive.py
│   │   └── lens_options.py
│   └── [other providers]/    # Add patterns for other providers
├── utils/
│   ├── __init__.py
│   └── pattern_generator.py  # Utilities for generating patterns
└── manager.py                # Pattern manager for orchestration
```

## How to Use

### Basic Usage

```python
from app.core.pattern_library.manager import PatternManager
from app.core.pattern_library.providers.eyemed import EYEMED_PATTERNS

# Initialize the pattern manager
pattern_manager = PatternManager(provider="eyemed")

# Register patterns
for category, patterns in EYEMED_PATTERNS.items():
    for pattern_group in patterns:
        pattern_manager.register_pattern_group(pattern_group)

# Extract a specific field
exam_result = pattern_manager.extract(document_text, "exam_services.exam")
if exam_result:
    print(f"Exam cost: {exam_result['value']} (confidence: {exam_result['confidence']})")

# Extract all fields
all_results = pattern_manager.extract_all(document_text)
```

## Extending for New Providers

### 1. Create Provider Directory Structure

```
app/core/pattern_library/providers/[provider_name]/
├── __init__.py
├── exam.py
├── frames.py
├── lenses.py
└── [other benefit categories].py
```

### 2. Define Pattern Groups

```python
# In app/core/pattern_library/providers/[provider_name]/exam.py
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup, TablePattern
)

EXAM_COST_PATTERNS = PatternGroup(
    name="exam_cost",
    patterns=[
        RegexPattern(
            name="standard_exam_pattern",
            description="Standard pattern for exam cost",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Eye Exam(?:[^$]*?)(\$\d+(?:\.\d+)?)",
                r"Routine Exam\s+(\$\d+(?:\.\d+)?)",
            ]
        ),
        # Add more patterns...
    ]
)
```

### 3. Create an Export in __init__.py

```python
# In app/core/pattern_library/providers/[provider_name]/__init__.py
from app.core.pattern_library.providers.[provider_name].exam import (
    EXAM_COST_PATTERNS,
    RETINAL_IMAGING_PATTERNS
)
# Import other pattern groups...

# Group all patterns for easy reference
PROVIDER_PATTERNS = {
    "exam": [
        EXAM_COST_PATTERNS,
        RETINAL_IMAGING_PATTERNS
    ],
    # Add other categories...
}
```

### 4. Use Utility Functions for Common Patterns

```python
from app.core.pattern_library.utils import (
    generate_cost_patterns,
    create_pattern_group_from_variations,
    get_term_variations_from_dictionary
)

# Generate patterns using term variations
term_variations = get_term_variations_from_dictionary("exam", "standard_exam")
EXAM_COST_PATTERNS = create_pattern_group_from_variations(
    group_name="exam_cost",
    term_variations=term_variations,
    target_field="exam_services.exam"
)
```

### 5. Update the Extractor

```python
from app.core.pattern_library.manager import PatternManager
from app.core.pattern_library.providers.[provider_name] import PROVIDER_PATTERNS

class ProviderExtractor(BaseExtractor):
    def __init__(self):
        super().__init__(provider_name="[Provider Name]")
        # Initialize the pattern manager
        self.pattern_manager = PatternManager(provider="[provider_name]")
        self._register_patterns()
    
    def _register_patterns(self):
        # Register all pattern groups
        for category, patterns in PROVIDER_PATTERNS.items():
            for pattern_group in patterns:
                self.pattern_manager.register_pattern_group(pattern_group)
    
    # Update the extraction methods to use the pattern manager
    # ...
```

## Best Practices

1. **Start with the most common formats** and add specific pattern variations as needed
2. **Use section patterns** when a document has clear sections to narrow down the extraction scope
3. **Include table patterns** for tabular data formats
4. **Leverage the term dictionary** for consistent terminology across providers
5. **Adjust confidence scores** based on pattern specificity and reliability
6. **Add detailed logging** to help with troubleshooting and pattern refinement

By using this pattern library, extractors can handle a wider variety of document formats and be more resilient to formatting changes in insurance documents. 