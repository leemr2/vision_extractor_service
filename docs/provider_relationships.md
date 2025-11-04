# Insurance Provider Relationships

This document outlines the relationships between the various vision insurance providers supported by the Vision Insurance Extractor service.

## Provider Overview

The Vision Insurance Extractor service supports the following providers:

1. VSP (Vision Service Plan)
2. EyeMed
3. Davis Vision
4. Spectera (UnitedHealthcare Vision)
5. Superior Vision
6. Versant Health

## Corporate Relationships

### Versant Health

Versant Health is the parent company that combines Davis Vision and Superior Vision. In 2017, Davis Vision and Superior Vision merged to form Versant Health. As a result, newer benefit documents may display "Versant Health" branding while still containing references to either Davis Vision or Superior Vision.

Important points about Versant Health:

- Documents may contain both Versant Health and Davis Vision/Superior Vision branding
- The benefit structure is compatible with the Davis Vision tabular format
- Extraction leverages the Davis Vision tabular extractor for processing
- The system correctly identifies Versant Health documents regardless of dual branding

### Implementation Details

The Versant Health implementation:

1. Uses the `VersantExtractor` class that inherits from the `DavisTabularExtractor`
2. Leverages the `DavisTemplate` structure through the `VersantTemplate` extension
3. Contains specific provider detection patterns to recognize Versant Health branding
4. Modifies output to correctly identify the provider as "Versant Health"

## Provider Selection

The system requires users to specify the provider type when submitting documents. Provider-specific patterns defined in `app/config/provider_patterns.py` are maintained for potential future debugging or audit purposes, but are not used for automatic detection.

**Note**: Provider types must be user-defined because benefit pages often do not contain provider names or branding. The user selection ensures accurate extraction regardless of document content.

For Versant Health, the stored patterns include:
```python
r"Versant Health",
r"Versant\s+Health",
r"www\.versanthealth\.com",
r"Davis Vision.*Versant Health",
r"Superior Vision.*Versant Health",
r"Versant Health.*Davis Vision",
r"Versant Health.*Superior Vision",
```

## Extraction Workflow

When a document is identified as a Versant Health document:

1. The `VersantExtractor` is instantiated
2. The document is processed using the Davis Vision tabular extraction logic
3. The output is formatted according to the Versant Health template
4. Provider and plan names are set as "Versant Health"

This approach ensures consistent extraction results while maintaining the distinct identity of Versant Health documents.

## Future Considerations

As Versant Health continues to evolve its document formats, we may need to adjust our extraction logic. Key points to monitor:

- Changes to tabular format structure in future documents
- Potential rebranding efforts
- Introduction of new benefit types or structures
- Complete phasing out of Davis Vision or Superior Vision branding

The modular design of our extractors allows us to adapt to these changes as needed. 