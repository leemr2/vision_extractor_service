"""
VSP Lens Enhancement Mapping

This module provides a structured mapping of VSP lens enhancement codes, 
their descriptions, and their hierarchical organization.
"""

# Complete hierarchical structure of VSP lens enhancements
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

# Simplified flat mapping of all VSP lens codes to their descriptions
VSP_CODE_DESCRIPTION_MAP = {
    # Aspheric
    "AA": "Plastic 1.50 - Aspheric",
    "BA": "Digital Aspheric lenses-Plastic",
    
    # Oversize Lenses
    "RM": "Frames stamped 61mm Eye Size or Greater-Plastic",
    "RN": "Frames stamped 61mm Eye Size or Greater-Glass",
    
    # Blended Bifocal
    "GA": "Blended Bifocal Plastic",
    
    # Standard Progressives
    "KA": "Progressive K Plastic",
    "KE": "Progressive K Glass",
    
    # Premium Progressives
    "FA": "Progressive F Plastic",
    "FE": "Progressive F Glass",
    "JA": "Progressive J Plastic",
    "JE": "Progressive J Glass",
    
    # Custom Progressives
    "NA": "Progressive N Plastic",
    "OA": "Progressive O Plastic",
    "CM": "Custom Measurement",
    
    # Polycarbonate
    "AD": "Polycarbonate",
    "BD": "Polycarbonate (Digital Aspheric add-on)",
    "DD": "Polycarbonate (Polarized add-on)",
    "FD": "Polycarbonate (Progressive F add-on)",
    "ID": "Polycarbonate (Near Variable Focus add-on)",
    "JD": "Polycarbonate (Progressive J add-on)",
    "KD": "Polycarbonate (Progressive K add-on)",
    "ND": "Polycarbonate (Progressive N add-on)",
    "OD": "Polycarbonate (Progressive O add-on)",
    
    # High Index
    "AB": "High Index Plastic 1.60 & Below/Trivex",
    "AF": "High-Index Glass 1.60-1.80 (Clear)",
    "AH": "High-Index Plastic 1.66/1.67",
    "AJ": "High-Index Plastic 1.71 & above",
    "BB": "Digital Lenses-High Index Plastic 1.60 & Below/Trivex",
    "BH": "Digital Lenses-High Index Plastic 1.66/1.67",
    "BJ": "Digital Lenses-High Index Plastic 1.70 & Above",
    "DB": "Polarized Lenses-High Index Plastic 1.60 & Below/Trivex",
    "DH": "High-Index Plastic 1.66 (Polarized add-on)",
    "DJ": "High-Index Plastic 1.70 & above - Polarized",
    "FB": "Progressive F - High Index Plastic 1.60 & Below/Trivex",
    "FH": "High-Index Plastic 1.66 (Progressive F add-on)",
    "FJ": "High-Index Plastic 1.71 (Progressive F add-on)",
    "IB": "Near Variable Focus - High Index Plastic 1.60 & Below/Trivex",
    "II": "Near Variable Focus High-Index Plastic 1.66",
    "IJ": "Near Variable Focus-High Index Plastic 1.70 & above",
    "JB": "Progressive J - High Index Plastic 1.60 & Below/Trivex",
    "JH": "High-Index Plastic 1.66 (Progressive J add-on)",
    "JJ": "High-Index Plastic 1.71 (Progressive J add-on)",
    "KB": "Progressive K - High Index Plastic 1.60 & Below/Trivex",
    "KH": "High-Index Plastic 1.66 (Progressive K add-on)",
    "KJ": "High-Index Plastic 1.71 (Progressive K add-on)",
    "NB": "Progressive N - High Index Plastic 1.60 & Below/Trivex",
    "NH": "High-Index Plastic 1.66 (Progressive N add-on)",
    "NJ": "High-Index Plastic 1.71 (Progressive N add-on)",
    "OB": "Progressive O - High Index Plastic 1.60 & Below/Trivex",
    "OH": "High-Index Plastic 1.66 (Progressive O add-on)",
    "OJ": "High-Index Plastic 1.71 (Progressive O add-on)",
    
    # Photochromic
    "PM": "Photochromatics Glass",
    "PR": "Photochromatics Plastic",
    
    # Polarized/Laminated
    "DA": "Polarized Plastic A",
    "DE": "Polarized Glass",
    "FP": "Polarized (Progressive F add-on)",
    "JP": "Polarized (Progressive J add-on)",
    "KP": "Polarized (Progressive K add-on)",
    "NP": "Polarized (Progressive N add-on)",
    "OP": "Polarized (Progressive O add-on)",
    
    # UV Protection
    "BV": "UV Protection Backside lens",
    "SV": "UV Protection",
    
    # Tints
    "MN": "Plastic Dyes (excludes Pink I & II)",
    "MR": "Glass Tints (excludes Pink I & II & Yellow)",
    "MP": "Plastic Dyes Gradient",
    
    # Coatings
    "QQ": "Scratch Resistant A",
    "QS": "Scratch Resistant B",
    "QM": "Anti-Reflective A",
    "QT": "Anti-Reflective C",
    "QV": "Anti-Reflective D",
    "MS": "Glass Color Coatings Solid",
    "MT": "Glass Color Coatings Gradient",
    "QP": "Mirror Solid",
    "QR": "Ski Type",
    
    # Miscellaneous
    "SP": "High Luster Edge Polish",
    "SQ": "Edge Coating",
    "SR": "Facetted Lenses",
    "SW": "Rimless Drill",
    "IA": "Near Variable Focus Plastic A",
    "AE": "Technical Add On A",
    "TA": "Technical Add On A",
    "LF": "Light Filter"
}

# Helper functions
def get_description_by_code(code):
    """
    Get the description for a VSP lens code
    
    Args:
        code (str): The VSP lens code
        
    Returns:
        str: The description for the code, or None if not found
    """
    return VSP_CODE_DESCRIPTION_MAP.get(code.upper())

def find_category_for_code(code):
    """
    Find the category and subcategory for a VSP lens code
    
    Args:
        code (str): The VSP lens code
        
    Returns:
        tuple: (category, subcategory) for the code, or (None, None) if not found
    """
    code = code.upper()
    for category in VSP_LENS_STRUCTURE:
        for subcategory in category["subcategories"]:
            for option in subcategory["options"]:
                if option["code"] == code:
                    return category["category"], subcategory["name"]
    return None, None

def is_valid_vsp_code(code):
    """
    Check if a code is a valid VSP lens code
    
    Args:
        code (str): The code to check
        
    Returns:
        bool: True if it's a valid VSP code, False otherwise
    """
    return code.upper() in VSP_CODE_DESCRIPTION_MAP
