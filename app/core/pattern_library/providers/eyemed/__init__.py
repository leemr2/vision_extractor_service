"""
EyeMed-specific extraction patterns
"""
# Import eligibility patterns
from app.core.pattern_library.providers.eyemed.eligibility import (
    EXAM_ELIGIBILITY_PATTERNS,
    LENSES_ELIGIBILITY_PATTERNS,
    FRAME_ELIGIBILITY_PATTERNS,
    CONTACTS_ELIGIBILITY_PATTERNS
)

# Group all patterns for easy reference
EYEMED_PATTERNS = {
    "eligibility": [
        EXAM_ELIGIBILITY_PATTERNS,
        LENSES_ELIGIBILITY_PATTERNS,
        FRAME_ELIGIBILITY_PATTERNS,
        CONTACTS_ELIGIBILITY_PATTERNS
    ]
}

# Import progressive patterns
try:
    from app.core.pattern_library.providers.eyemed.progressive import (
        EYEMED_PROGRESSIVE_PATTERNS
    )
    EYEMED_PATTERNS["progressive"] = EYEMED_PROGRESSIVE_PATTERNS
    print("Successfully imported progressive patterns")
except ImportError as e:
    # Skip progressive patterns if they can't be imported
    print(f"Error importing progressive patterns: {e}")
    pass
except Exception as e:
    # Log more detailed errors
    print(f"Error loading progressive patterns: {e}")
    pass

# Import lens options patterns
try:
    from app.core.pattern_library.providers.eyemed.lens_options import (
        STANDARD_AR_COATING_PATTERNS,
        PREMIUM_AR_COATING_PATTERNS,
        AR_COATING_TIER_PATTERNS,
        LENS_OPTION_PATTERNS,
        OTHER_OPTIONS_PATTERNS
    )
    EYEMED_PATTERNS["lens_options"] = [
        STANDARD_AR_COATING_PATTERNS,
        PREMIUM_AR_COATING_PATTERNS,
        *[AR_COATING_TIER_PATTERNS[i] for i in range(1, 4)],
        *LENS_OPTION_PATTERNS.values(),
        OTHER_OPTIONS_PATTERNS
    ]
    print("Successfully imported lens option patterns")
except ImportError as e:
    # Skip lens option patterns if they can't be imported
    print(f"Error importing lens option patterns: {e}")
    pass
except Exception as e:
    # Log more detailed errors
    print(f"Error loading lens option patterns: {e}")
    pass

# Import exam patterns
try:
    from app.core.pattern_library.providers.eyemed.exam import (
        EXAM_COST_PATTERNS,
        RETINAL_IMAGING_PATTERNS,
        FREE_EXAM_PATTERNS
    )
    EYEMED_PATTERNS["exam"] = [
        EXAM_COST_PATTERNS,
        RETINAL_IMAGING_PATTERNS,
        FREE_EXAM_PATTERNS
    ]
    print("Successfully imported exam patterns")
except ImportError as e:
    # Skip exam patterns if they can't be imported
    print(f"Error importing exam patterns: {e}")
    pass
except Exception as e:
    # Log more detailed errors
    print(f"Error loading exam patterns: {e}")
    pass 