"""
EyeMed-specific patterns for eligibility determination
"""
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup, SectionPattern, TablePattern
)

# Define pattern groups for exam eligibility
EXAM_ELIGIBILITY_PATTERNS = PatternGroup(
    name="exam_eligibility",
    patterns=[
        RegexPattern(
            name="member_is_eligible_column_exam",
            description="Pattern for 'Member is Eligible?' column with 'Yes' for exam",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.exam_eligible",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Exam\s+Yes\s+",
                r"Exam\s+Yes(?:\s+|$)",
            ]
        ),
        TablePattern(
            name="tabular_exam_eligible",
            description="Tabular pattern for exam eligibility",
            pattern_type=PatternType.TABLE,
            target_field="eligibility_info.exam_eligible",
            confidence=ConfidenceLevel.HIGH,
            row_header="Exam",
            column_header="Member is Eligible?"
        ),
        RegexPattern(
            name="member_eligible_as_of_exam",
            description="Pattern for 'Member Eligible As Of' date for exam",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.exam_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            patterns=[
                r"Exam(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{4})",
                r"Exam(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{2})",
            ]
        ),
        SectionPattern(
            name="section_exam_eligible",
            description="Section-based pattern for exam eligibility",
            pattern_type=PatternType.SECTION,
            target_field="eligibility_info.exam_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Exam",
            value_pattern=r"(?:eligible|Eligible|YES|Yes|yes)"
        )
    ]
)

# Define pattern groups for lenses eligibility
LENSES_ELIGIBILITY_PATTERNS = PatternGroup(
    name="lenses_eligibility",
    patterns=[
        RegexPattern(
            name="member_is_eligible_column_lenses",
            description="Pattern for 'Member is Eligible?' column with 'Yes' for lenses",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.lenses_eligible",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Lenses\s+Yes\s+",
                r"Lenses\s+Yes(?:\s+|$)",
            ]
        ),
        TablePattern(
            name="tabular_lenses_eligible",
            description="Tabular pattern for lenses eligibility",
            pattern_type=PatternType.TABLE,
            target_field="eligibility_info.lenses_eligible",
            confidence=ConfidenceLevel.HIGH,
            row_header="Lenses",
            column_header="Member is Eligible?"
        ),
        RegexPattern(
            name="member_eligible_as_of_lenses",
            description="Pattern for 'Member Eligible As Of' date for lenses",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.lenses_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            patterns=[
                r"Lenses(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{4})",
                r"Lenses(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{2})",
            ]
        ),
        SectionPattern(
            name="section_lenses_eligible",
            description="Section-based pattern for lenses eligibility",
            pattern_type=PatternType.SECTION,
            target_field="eligibility_info.lenses_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Lenses",
            value_pattern=r"(?:eligible|Eligible|YES|Yes|yes)"
        )
    ]
)

# Define pattern groups for frame eligibility
FRAME_ELIGIBILITY_PATTERNS = PatternGroup(
    name="frame_eligibility",
    patterns=[
        RegexPattern(
            name="member_is_eligible_column_frame",
            description="Pattern for 'Member is Eligible?' column with 'Yes' for frame",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.frame_eligible",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Frame\s+Yes\s+",
                r"Frame\s+Yes(?:\s+|$)",
            ]
        ),
        TablePattern(
            name="tabular_frame_eligible",
            description="Tabular pattern for frame eligibility",
            pattern_type=PatternType.TABLE,
            target_field="eligibility_info.frame_eligible",
            confidence=ConfidenceLevel.HIGH,
            row_header="Frame",
            column_header="Member is Eligible?"
        ),
        RegexPattern(
            name="member_eligible_as_of_frame",
            description="Pattern for 'Member Eligible As Of' date for frame",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.frame_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            patterns=[
                r"Frame(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{4})",
                r"Frame(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{2})",
            ]
        ),
        SectionPattern(
            name="section_frame_eligible",
            description="Section-based pattern for frame eligibility",
            pattern_type=PatternType.SECTION,
            target_field="eligibility_info.frame_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Frame",
            value_pattern=r"(?:eligible|Eligible|YES|Yes|yes)"
        )
    ]
)

# Define pattern groups for contact lenses eligibility
CONTACTS_ELIGIBILITY_PATTERNS = PatternGroup(
    name="contacts_eligibility",
    patterns=[
        RegexPattern(
            name="member_is_eligible_column_contacts",
            description="Pattern for 'Member is Eligible?' column with 'Yes' for contact lenses",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.contact_lenses_eligible",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Contact\s+Lenses\s+Yes\s+",
                r"Contact\s+Lenses\s+Yes(?:\s+|$)",
            ]
        ),
        TablePattern(
            name="tabular_contacts_eligible",
            description="Tabular pattern for contact lenses eligibility",
            pattern_type=PatternType.TABLE,
            target_field="eligibility_info.contact_lenses_eligible",
            confidence=ConfidenceLevel.HIGH,
            row_header="Contact Lenses",
            column_header="Member is Eligible?"
        ),
        RegexPattern(
            name="member_eligible_as_of_contacts",
            description="Pattern for 'Member Eligible As Of' date for contact lenses",
            pattern_type=PatternType.EXACT,
            target_field="eligibility_info.contact_lenses_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            patterns=[
                r"Contact\s+Lenses(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{4})",
                r"Contact\s+Lenses(?:.*?)Member Eligible As Of(?:.*?)(\d{1,2}/\d{1,2}/\d{2})",
            ]
        ),
        SectionPattern(
            name="section_contacts_eligible",
            description="Section-based pattern for contact lenses eligibility",
            pattern_type=PatternType.SECTION,
            target_field="eligibility_info.contact_lenses_eligible",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Contact Lenses",
            value_pattern=r"(?:eligible|Eligible|YES|Yes|yes)"
        )
    ]
) 