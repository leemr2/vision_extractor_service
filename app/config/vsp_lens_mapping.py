"""
VSP Lens Enhancement Mapping

This module provides a structured mapping of VSP lens enhancement codes,
their descriptions, and their hierarchical organization, intended for use
by the VSP extractor.
"""

# Complete hierarchical structure of VSP lens enhancements
# Based on tests/samples/VSP/vsp-code-mapping.py
VSP_LENS_STRUCTURE = [
    {
        "category": "LENSES",
        "subcategories": [
            {
                "name": "Aspheric",
                "options": [
                    {"code": "AA", "description": "Plastic 1.50 - Aspheric"},
                    {"code": "BA", "description": "Digital Aspheric lenses-Plastic"}
                ]
            },
            {
                "name": "Oversize Lenses",
                "options": [
                    {"code": "RM", "description": "Frames stamped 61mm Eye Size or Greater-Plastic"},
                    {"code": "RN", "description": "Frames stamped 61mm Eye Size or Greater-Glass"}
                ]
            },
            {
                "name": "Blended Bifocal",
                "options": [
                    {"code": "GA", "description": "Blended Bifocal Plastic"}
                ]
            },
            {
                "name": "Standard Progressives",
                "options": [
                    {"code": "KA", "description": "Progressive K Plastic"},
                    {"code": "KE", "description": "Progressive K Glass"}
                ]
            },
            {
                "name": "Premium Progressives",
                "options": [
                    {"code": "FA", "description": "Progressive F Plastic"},
                    {"code": "FE", "description": "Progressive F Glass"},
                    {"code": "JA", "description": "Progressive J Plastic"},
                    {"code": "JE", "description": "Progressive J Glass"}
                ]
            },
            {
                "name": "Custom Progressives",
                "options": [
                    {"code": "NA", "description": "Progressive N Plastic"},
                    {"code": "OA", "description": "Progressive O Plastic"},
                    {"code": "CM", "description": "Custom Measurement"}
                ]
            },
            {
                "name": "Polycarbonate",
                "options": [
                    {"code": "AD", "description": "Polycarbonate"},
                    {"code": "BD", "description": "Polycarbonate (Digital Aspheric add-on)"},
                    {"code": "DD", "description": "Polycarbonate (Polarized add-on)"},
                    {"code": "FD", "description": "Polycarbonate (Progressive F add-on)"},
                    {"code": "ID", "description": "Polycarbonate (Near Variable Focus add-on)"},
                    {"code": "JD", "description": "Polycarbonate (Progressive J add-on)"},
                    {"code": "KD", "description": "Polycarbonate (Progressive K add-on)"},
                    {"code": "ND", "description": "Polycarbonate (Progressive N add-on)"},
                    {"code": "OD", "description": "Polycarbonate (Progressive O add-on)"}
                ]
            },
            {
                "name": "High Index",
                "options": [
                    {"code": "AB", "description": "High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "AF", "description": "High-Index Glass 1.60-1.80 (Clear)"},
                    {"code": "AH", "description": "High-Index Plastic 1.66/1.67"},
                    {"code": "AJ", "description": "High-Index Plastic 1.71 & above"},
                    {"code": "BB", "description": "Digital Lenses-High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "BH", "description": "Digital Lenses-High Index Plastic 1.66/1.67"},
                    {"code": "BJ", "description": "Digital Lenses-High Index Plastic 1.70 & Above"},
                    {"code": "DB", "description": "Polarized Lenses-High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "DH", "description": "High-Index Plastic 1.66 (Polarized add-on)"},
                    {"code": "DJ", "description": "High-Index Plastic 1.70 & above - Polarized"},
                    {"code": "FB", "description": "Progressive F - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "FH", "description": "High-Index Plastic 1.66 (Progressive F add-on)"},
                    {"code": "FJ", "description": "High-Index Plastic 1.71 (Progressive F add-on)"},
                    {"code": "IB", "description": "Near Variable Focus - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "II", "description": "Near Variable Focus High-Index Plastic 1.66"},
                    {"code": "IJ", "description": "Near Variable Focus-High Index Plastic 1.70 & above"},
                    {"code": "JB", "description": "Progressive J - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "JH", "description": "High-Index Plastic 1.66 (Progressive J add-on)"},
                    {"code": "JJ", "description": "High-Index Plastic 1.71 (Progressive J add-on)"},
                    {"code": "KB", "description": "Progressive K - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "KH", "description": "High-Index Plastic 1.66 (Progressive K add-on)"},
                    {"code": "KJ", "description": "High-Index Plastic 1.71 (Progressive K add-on)"},
                    {"code": "NB", "description": "Progressive N - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "NH", "description": "High-Index Plastic 1.66 (Progressive N add-on)"},
                    {"code": "NJ", "description": "High-Index Plastic 1.71 (Progressive N add-on)"},
                    {"code": "OB", "description": "Progressive O - High Index Plastic 1.60 & Below/Trivex"},
                    {"code": "OH", "description": "High-Index Plastic 1.66 (Progressive O add-on)"},
                    {"code": "OJ", "description": "High-Index Plastic 1.71 (Progressive O add-on)"}
                ]
            },
            {
                "name": "Photochromic",
                "options": [
                    {"code": "PM", "description": "Photochromatics Glass"},
                    {"code": "PR", "description": "Photochromatics Plastic"}
                ]
            },
            {
                "name": "Polarized/Laminated",
                "options": [
                    {"code": "DA", "description": "Polarized Plastic A"},
                    {"code": "DE", "description": "Polarized Glass"},
                    {"code": "FP", "description": "Polarized (Progressive F add-on)"},
                    {"code": "JP", "description": "Polarized (Progressive J add-on)"},
                    {"code": "KP", "description": "Polarized (Progressive K add-on)"},
                    {"code": "NP", "description": "Polarized (Progressive N add-on)"},
                    {"code": "OP", "description": "Polarized (Progressive O add-on)"}
                ]
            },
            {
                "name": "UV Protection",
                "options": [
                    {"code": "BV", "description": "UV Protection Backside lens"},
                    {"code": "SV", "description": "UV Protection"}
                ]
            }
        ]
    },
    {
        "category": "TINTS",
        "subcategories": [
            {
                "name": "Solid Tints and Dyes",
                "options": [
                    {"code": "MN", "description": "Plastic Dyes (excludes Pink I & II)"},
                    {"code": "MR", "description": "Glass Tints (excludes Pink I & II & Yellow)"}
                ]
            },
            {
                "name": "Plastic Gradient Dyes",
                "options": [
                    {"code": "MP", "description": "Plastic Dyes Gradient"}
                ]
            }
        ]
    },
    {
        "category": "COATINGS",
        "subcategories": [
            {
                "name": "Scratch Resistant Coating",
                "options": [
                    {"code": "QQ", "description": "Scratch Resistant A"},
                    {"code": "QS", "description": "Scratch Resistant B"}
                ]
            },
            {
                "name": "Anti-Reflective Coating",
                "options": [
                    {"code": "QM", "description": "Anti-Reflective A"},
                    {"code": "QT", "description": "Anti-Reflective C"},
                    {"code": "QV", "description": "Anti-Reflective D"}
                ]
            },
            {
                "name": "Color Coating",
                "options": [
                    {"code": "MS", "description": "Glass Color Coatings Solid"},
                    {"code": "MT", "description": "Glass Color Coatings Gradient"}
                ]
            },
            {
                "name": "Mirror and Ski Type Coating",
                "options": [
                    {"code": "QP", "description": "Mirror Solid"},
                    {"code": "QR", "description": "Ski Type"}
                ]
            }
        ]
    },
    {
        "category": "MISCELLANEOUS",
        "subcategories": [
            {
                "name": "Edge Treatments",
                "options": [
                    {"code": "SP", "description": "High Luster Edge Polish"},
                    {"code": "SQ", "description": "Edge Coating"}
                ]
            },
            {
                "name": "Facets",
                "options": [
                    {"code": "SR", "description": "Facetted Lenses"}
                ]
            },
            {
                "name": "Rimless Mounting",
                "options": [
                    {"code": "SW", "description": "Rimless Drill"}
                ]
            },
            {
                "name": "Near Variable Focus",
                "options": [
                    {"code": "IA", "description": "Near Variable Focus Plastic A"}
                ]
            },
            {
                "name": "Technical Add On",
                "options": [
                    {"code": "AE", "description": "Technical Add On A"},
                    {"code": "TA", "description": "Technical Add On A"}
                ]
            },
            {
                "name": "Light Filter",
                "options": [
                    {"code": "LF", "description": "Light Filter"}
                ]
            }
        ]
    }
]

# Simplified flat mapping (optional, but can be useful)
VSP_CODE_DESCRIPTION_MAP = {
    option["code"]: option["description"]
    for category in VSP_LENS_STRUCTURE
    for subcategory in category["subcategories"]
    for option in subcategory["options"]
}

def get_description_by_code(code):
    """Get the description for a VSP lens code."""
    return VSP_CODE_DESCRIPTION_MAP.get(code.upper())

def find_category_for_code(code):
    """Find the category and subcategory for a VSP lens code."""
    code = code.upper()
    for category in VSP_LENS_STRUCTURE:
        for subcategory in category["subcategories"]:
            for option in subcategory["options"]:
                if option["code"] == code:
                    return category["category"], subcategory["name"]
    return None, None

def is_valid_vsp_code(code):
    """Check if a code is a valid VSP lens code."""
    return code.upper() in VSP_CODE_DESCRIPTION_MAP