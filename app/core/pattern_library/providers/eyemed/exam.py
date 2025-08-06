"""
EyeMed-specific patterns for exam benefits
"""
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup, SectionPattern, TablePattern
)

# Define pattern groups for exam section
EXAM_COST_PATTERNS = PatternGroup(
    name="exam_cost",
    patterns=[
        RegexPattern(
            name="standard_exam_pattern",
            description="Standard pattern for exam cost with copay",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Eye\s*)?Exam(?:[^$]*?)(?:Copay|Cost)?:?\s*(\$\d+(?:\.\d+)?)",
                r"(?:Eye\s*)?Exam\s+(\$\d+(?:\.\d+)?\s+copay)",
                r"Exam(?:\s*Services)?:?\s*(\$\d+(?:\.\d+)?)",
            ]
        ),
        RegexPattern(
            name="free_exam_pattern",
            description="Pattern for $0 exam",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Eye\s*)?Exam(?:[^$]*?)(?:Covered|Free|\$0)",
                r"(?:Eye\s*)?Exam\s+\$0(?:\s+copay)?",
            ]
        ),
        TablePattern(
            name="tabular_exam_pattern",
            description="Pattern for exam cost in tabular format",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Exam",
            column_header="Cost"
        ),
        TablePattern(
            name="tabular_exam_innetwork_pattern",
            description="Pattern for exam cost in in-network column",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Exam",
            column_header="In-Network"
        ),
        TablePattern(
            name="tabular_exam_member_cost_pattern",
            description="Pattern for exam cost in member cost column",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Exam",
            column_header="Member Cost"
        ),
        TablePattern(
            name="tabular_exam_in_network_member_cost_pattern",
            description="Pattern for exam cost in in-network member cost column",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Exam",
            column_header="In-Network Member Cost"
        ),
        SectionPattern(
            name="section_exam_pattern",
            description="Section-based pattern for exam cost",
            pattern_type=PatternType.SECTION,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Exam Services",
            value_pattern=r"(?:Eye\s*)?Exam(?:[^$]*?)(\$\d+(?:\.\d+)?)"
        )
    ]
)

RETINAL_IMAGING_PATTERNS = PatternGroup(
    name="retinal_imaging",
    patterns=[
        RegexPattern(
            name="standard_retinal_pattern",
            description="Standard pattern for retinal imaging cost",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.retinal_imaging",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Retinal Imaging[^$]*?(?:Up to\s*)?(\$\d+(?:\.\d+)?)",
                r"Retinal Imaging\s+(?:Up to\s*)?(\$\d+(?:\.\d+)?)",
                r"Retinal (?:Imaging|Screening)[^$]*?(?:Up to\s*)?(\$\d+(?:\.\d+)?)"
            ]
        ),
        RegexPattern(
            name="discount_retinal_pattern",
            description="Pattern for retinal imaging with discount",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.retinal_imaging",
            confidence=ConfidenceLevel.MEDIUM,
            patterns=[
                r"Retinal Imaging[^$]*?((?:\d+)%\s+off)",
                r"Retinal (?:Imaging|Screening)[^$]*?((?:\d+)%\s+discount)"
            ]
        ),
        TablePattern(
            name="tabular_retinal_pattern",
            description="Pattern for retinal imaging in tabular format",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.retinal_imaging",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Retinal Imaging",
            column_header="Cost"
        ),
        TablePattern(
            name="tabular_retinal_innetwork_pattern",
            description="Pattern for retinal imaging in in-network column",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.retinal_imaging",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Retinal Imaging",
            column_header="In-Network"
        ),
        TablePattern(
            name="tabular_retinal_member_cost_pattern",
            description="Pattern for retinal imaging in member cost column",
            pattern_type=PatternType.TABLE,
            target_field="exam_services.retinal_imaging", 
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Retinal Imaging",
            column_header="Member Cost"
        ),
        SectionPattern(
            name="section_retinal_pattern",
            description="Section-based pattern for retinal imaging",
            pattern_type=PatternType.SECTION,
            target_field="exam_services.retinal_imaging",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Exam Services",
            value_pattern=r"Retinal (?:Imaging|Screening)(?:[^$]*?)(?:Up to\s*)?(\$\d+(?:\.\d+)?|(?:\d+)%\s+off)"
        )
    ]
)

# Define pattern for free exams specifically
FREE_EXAM_PATTERNS = PatternGroup(
    name="free_exam",
    patterns=[
        RegexPattern(
            name="zero_dollar_exam",
            description="Pattern for $0 copay exam",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Eye\s*)?Exam(?:[^$]*?)\$0(?:\s+copay)?",
                r"(?:Eye\s*)?Exam\s+\$0",
                r"Exam\s+\$0\s+copay"
            ]
        ),
        RegexPattern(
            name="covered_exam",
            description="Pattern for covered exam",
            pattern_type=PatternType.EXACT,
            target_field="exam_services.exam",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Eye\s*)?Exam(?:[^$]*?)Covered\s+in\s+full",
                r"(?:Eye\s*)?Exam(?:[^$]*?)Covered",
                r"(?:Eye\s*)?Exam(?:[^$]*?)Free"
            ]
        )
    ]
) 