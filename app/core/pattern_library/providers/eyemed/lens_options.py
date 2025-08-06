"""
EyeMed-specific patterns for lens options
"""
from app.core.pattern_library.base.pattern_base import (
    RegexPattern, PatternType, ConfidenceLevel, PatternGroup, SectionPattern, TablePattern
)

# Anti-reflective coating patterns
def create_ar_coating_tier_pattern(tier: int) -> PatternGroup:
    """Create pattern group for a specific AR coating tier"""
    return PatternGroup(
        name=f"ar_coating_tier_{tier}",
        patterns=[
            RegexPattern(
                name=f"ar_tier_{tier}_exact",
                description=f"Exact pattern for AR Coating Tier {tier}",
                pattern_type=PatternType.EXACT,
                target_field=f"lens_options.anti_reflective_coating.premium_tier_{tier}",
                confidence=ConfidenceLevel.HIGH,
                patterns=[
                    rf"Anti[-\s]Reflective Coating - Premium Tier {tier}:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
                    rf"Anti Reflective Coating - Premium Tier {tier}\s+(\$\d+(?:\.\d+)?)",
                    rf"Anti[-\s]Reflective Coating - Premium Tier {tier}:?\s*((?:\d+)%\s+off\s+retail(?:\s+price)?)",
                    rf"Anti Reflective Coating - Premium Tier {tier}\s+((?:\d+)%\s+(?:off|of)\s+retail(?:\s+price)?)"
                ]
            ),
            SectionPattern(
                name=f"ar_tier_{tier}_section",
                description=f"Section-based pattern for AR Coating Tier {tier}",
                pattern_type=PatternType.SECTION,
                target_field=f"lens_options.anti_reflective_coating.premium_tier_{tier}",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Lens Options",
                value_pattern=rf"Anti[-\s]Reflective Coating - Premium Tier {tier}:?\s*(\$\d+(?:\.\d+)?|\d+%\s+off\s+retail)"
            ),
            TablePattern(
                name=f"ar_tier_{tier}_table",
                description=f"Table-based pattern for AR Coating Tier {tier}",
                pattern_type=PatternType.TABLE,
                target_field=f"lens_options.anti_reflective_coating.premium_tier_{tier}",
                confidence=ConfidenceLevel.MEDIUM,
                row_header=f"Anti-Reflective Coating - Premium Tier {tier}",
                column_header="Cost"
            )
        ]
    )

# Standard anti-reflective coating
STANDARD_AR_COATING_PATTERNS = PatternGroup(
    name="standard_ar_coating",
    patterns=[
        RegexPattern(
            name="standard_ar_exact",
            description="Exact pattern for standard AR coating",
            pattern_type=PatternType.EXACT,
            target_field="lens_options.anti_reflective_coating.standard",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"(?:Standard\s+)?Anti[-\s]Reflective (?:Coating)?(?:\s+-\s+Standard)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
                r"Anti Reflective Coating - Standard\s+(\$\d+(?:\.\d+)?)",
                r"Anti[-\s]Reflective (?:Coating)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)"
            ]
        ),
        SectionPattern(
            name="standard_ar_section",
            description="Section-based pattern for standard AR coating",
            pattern_type=PatternType.SECTION,
            target_field="lens_options.anti_reflective_coating.standard",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Lens Options",
            value_pattern=r"(?:Standard\s+)?Anti[-\s]Reflective (?:Coating)?(?:\s+-\s+Standard)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)"
        ),
        TablePattern(
            name="standard_ar_table",
            description="Table-based pattern for standard AR coating",
            pattern_type=PatternType.TABLE,
            target_field="lens_options.anti_reflective_coating.standard",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Anti-Reflective Coating - Standard",
            column_header="Cost"
        )
    ]
)

# Premium anti-reflective coating (general)
PREMIUM_AR_COATING_PATTERNS = PatternGroup(
    name="premium_ar_coating",
    patterns=[
        RegexPattern(
            name="premium_ar_exact",
            description="Exact pattern for premium AR coating",
            pattern_type=PatternType.EXACT,
            target_field="lens_options.anti_reflective_coating.premium",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"Anti[-\s]Reflective Coating - Premium:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
                r"Anti Reflective Coating - Premium\s+(\$\d+(?:\.\d+)?)",
                r"Anti[-\s]Reflective Coating - Premium:?\s*((?:\d+)%\s+off\s+retail(?:\s+price)?)",
                r"Premium Anti[-\s]Reflective (?:Coating)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?|(?:\d+)%\s+off\s+retail(?:\s+price)?)"
            ]
        ),
        SectionPattern(
            name="premium_ar_section",
            description="Section-based pattern for premium AR coating",
            pattern_type=PatternType.SECTION,
            target_field="lens_options.anti_reflective_coating.premium",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Lens Options",
            value_pattern=r"(?:Premium\s+)?Anti[-\s]Reflective (?:Coating)?(?:\s+-\s+Premium)?:?\s*(\$\d+(?:\.\d+)?|\d+%\s+off\s+retail)"
        ),
        TablePattern(
            name="premium_ar_table",
            description="Table-based pattern for premium AR coating",
            pattern_type=PatternType.TABLE,
            target_field="lens_options.anti_reflective_coating.premium",
            confidence=ConfidenceLevel.MEDIUM,
            row_header="Anti-Reflective Coating - Premium",
            column_header="Cost"
        )
    ]
)

# Generate AR coating tier patterns for tiers 1-3
AR_COATING_TIER_PATTERNS = {
    tier: create_ar_coating_tier_pattern(tier) for tier in range(1, 4)
}

# Add premium generic pattern to the collection
AR_COATING_TIER_PATTERNS[0] = PREMIUM_AR_COATING_PATTERNS

# Other lens option patterns
LENS_OPTION_PATTERNS = {
    option: PatternGroup(
        name=option,
        patterns=[
            RegexPattern(
                name=f"{option}_exact",
                description=f"Exact pattern for {option}",
                pattern_type=PatternType.EXACT,
                target_field=f"lens_options.{option}",
                confidence=ConfidenceLevel.HIGH,
                patterns=[pattern]
            ),
            SectionPattern(
                name=f"{option}_section",
                description=f"Section-based pattern for {option}",
                pattern_type=PatternType.SECTION,
                target_field=f"lens_options.{option}",
                confidence=ConfidenceLevel.MEDIUM,
                section_identifier="Lens Options",
                value_pattern=pattern
            )
        ]
    )
    for option, pattern in {
        "photochromic": r"Photochromic(?:/Transitions)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
        "polycarbonate": r"Polycarbonate(?:\s+-\s+Standard)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
        "scratch_coating": r"Scratch (?:Coating|Resistant)(?:\s+-\s+Standard Plastic)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
        "tint": r"Tint(?:\s+-\s+Solid and Gradient)?:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)",
        "uv_treatment": r"UV Treatment:?\s*(\$\d+(?:\.\d+)?\s*(?:copay)?)"
    }.items()
}

# Pattern for other lens options
OTHER_OPTIONS_PATTERNS = PatternGroup(
    name="other_options",
    patterns=[
        RegexPattern(
            name="other_options_exact",
            description="Exact pattern for other lens options",
            pattern_type=PatternType.EXACT,
            target_field="lens_options.other_options",
            confidence=ConfidenceLevel.HIGH,
            patterns=[
                r"All Other Lens Options:?\s*((?:\d+)%\s+off\s+retail)",
                r"Other Lens Options:?\s*((?:\d+)%\s+off\s+retail)"
            ]
        ),
        SectionPattern(
            name="other_options_section",
            description="Section-based pattern for other lens options",
            pattern_type=PatternType.SECTION,
            target_field="lens_options.other_options",
            confidence=ConfidenceLevel.MEDIUM,
            section_identifier="Lens Options",
            value_pattern=r"(?:All )?Other Lens Options:?\s*((?:\d+)%\s+off\s+retail)"
        )
    ]
) 