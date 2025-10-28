"""
Mappings from Davis PDF terms to standardized template keys.

This helps the DavisExtractor identify the correct lines or sections
in the PDF text corresponding to the fields in the DavisTemplate.
The keys in this dictionary should generally match the field names
(or aliases) in the Pydantic models defined in davis_template.py.
The values are lists of potential string representations found in PDFs.
"""

# Using lists allows for variations in terminology if encountered in different PDFs.
# Prioritize exact matches from known samples (like davis3.pdf).

DAVIS_TERM_MAP = {
    "coverage": {
        "eye_examination": ["Eye examination"],
        "frame": ["Frame"], # Found in Coverage Section II
        "spectacle_lenses": ["Spectacle Lenses"],
    },
    "allowances": {
        # These terms are typically headers in Section III
        "frame": ["Frame"],
        "contact_lens_material": ["Contact Lens Material"],
        "visually_required_contact_lens_material": ["Visually Required Contact Lens Material"],
    },
    "lens_benefits": {
        "digital_single_vision_lenses": {
            "digital_single_vision": ["Digital Single Vision Lenses", "Digital Single Vision"],
        },
        "progressive_lenses": {
            "standard_progressive": ["Standard Progressive Addition Multifocals", "Standard Tier PAL", "Progressive Standard"],
            "premium_progressive": ["Premium Progressive Addition Multifocals", "Premium Tier PAL", "Progressive Premium"],
            "ultra_progressive": ["Ultra Progressive Addition Multifocals", "Ultra-Tier PAL", "Progressive Ultra"],
            "ultimate_progressive": ["Ultimate Progressive Addition Multifocals", "Ultimate Tier PAL", "Progressive Ultimate"],
        },
        "anti_reflective_lenses": {
            "standard_ar": ["Standard ARC", "Standard ARC (anti-reflective coating)", "Standard Tier AR", "AR Coating Standard"],
            "premium_ar": ["Premium ARC", "Premium ARC (anti-reflective coating)", "Premium Tier AR", "AR Coating Premium"],
            "ultra_ar": ["Ultra ARC", "Ultra ARC (anti-reflective coating)", "Ultra-Tier AR", "AR Coating Ultra"],
            "ultimate_ar": ["Ultimate ARC", "Ultimate ARC (anti-reflective coating)", "Ultimate Tier AR", "AR Coating Ultimate"],
        },
        "polarized_lenses": {
            "polarized": ["Polarized Lenses"],
        },
        "blue_light_filtering": {
            "blue_light_filtering": ["Blue Light Filtering", "Blue Light Filtering - EBS"],
        },
        "photochromic_lenses": {
            "plastic_photosensitive": [
                "Plastic Photosensitive Lenses", 
                "Photochromic, non-glass (Transitions)",
                "Single Vision - Tint Plastic - Photosensitive",
                "Multivision - Tint Plastic - Photosensitive"
            ],
            "photochromic_glass": [
                "Photochromic (PGX), Glass",
                "Single Vision - Tint Photogrey",
                "Multivision - Tint Photogrey"
            ],
            "transitions": [
                "Transitions",
                "Transitions - Single Vision",
                "Transitions - Multifocal"
            ],
        },
        "lens_materials": {
            # "standard_plastic" - Typically assumed $0 or "Included" if not listed with cost
            "polycarbonate": [
                "Polycarbonate Lenses", 
                "Polycarbonate Lenses***", 
                "Polycarbonate", 
                "Polycarbonate - Single Vision",
                "Polycarbonate - Multifocal",
                "Polycarbonate Provided",
                "HD Polycarbonate - Multifocal",
                "HD Polycarbonate - Single Vision"
            ],
            "trivex": ["Trivex Lenses", "Trivex"],
            "high_index_1_67": [
                "High Index Lenses 1.67", 
                "High-Index 1.67", 
                "HighIndex 1.67", 
                "HighIndex 1.67 - Single Vision",
                "HighIndex 1.67 - Multifocal"
            ],
            "high_index_1_74": [
                "High Index Lenses 1.74", 
                "High-Index 1.74", 
                "HighIndex 1.74", 
                "HighIndex 1.74 - Multifocal",
                "HighIndex 1.74 - Single Vision"
            ],
            "glass": [
                "Glass Lenses",
                "Glass - Single Vision",
                "Glass - Bifocal", 
                "Glass - Trifocal"
            ],
        },
        "other_add_on_options": {
            "tint": ["Tinted Lenses"],
            "mirror_solid_single_double_gradient": [
                "Mirror Coat", 
                "Mirror – Solid, Single and Double Gradient", 
                "Mirror - Solid, Single & Double Gradient"
            ],
            "scratch_resistant_coating_standard": [
                "Scratch-Resistant Coating", 
                "Scratch Resistant Coating - Standard", 
                "Scratch Resistant Coating"
            ], # Note: Often "Included"
            "scratch_resistant_coating_premium_td2": ["Premium Scratch Resistent Coating"], # Note typo "Resistent" in davis3.pdf
            "scratch_protection_plan_single_vision": ["Scratch Protection Plan Single Vision"],
            "scratch_protection_plan_multifocal": [
                "Scratch Protection Plan Multifocal",
                "Multivision - Scratch Resistant Coating Protection"
            ],
            "coating_non_edp": ["Coating (Non EDP)"],
            "uv_coat": ["Ultraviolet Coating", "UV Coat"],
            "edge_polish": ["Edge Polish"],
            "high_luster_edge_polish": ["High Luster Edge Polish"],
            "roll_and_polish": ["Roll & Polish"],
            "roll_polish": ["Roll Polish"],
            "roll_edge": ["Roll Edge"],
            "rimless_drill": ["Rimless Drill"],
            "slab_off": ["Slab Off"],
            "specialty_lenses": ["Specialty Lens", "Specialty Lenses"], # Followed by examples in parens in PDF
            "oversized_lenses": ["Oversized Lenses"],
            "blended_segment": ["Blended Segment"],
        }
    }
}

# You might add more specific mappings or regex patterns here later if needed.
# For example, mapping specific brand names if they relate to tiers.