"""
Mapping configurations for Spectera document extraction
"""

# Section headers and patterns for identifying document sections
SECTION_PATTERNS = {
    "member_info": r"(?:Patient Name|Medical Record Number|ID Number)",
    "eligibility": r"(?:Service|Service Category|SERVICE\s+CATEGORY|SERVICE|FREQUENCY)",
    "professional_services": r"(?:Comprehensive\s+Exam|Eye\s+Examination|EXAM|Maternity\s+Exam|Retinal\s+Screening)",
    "frames": r"(?:FRAME|Frame|FRAMES|Frames)",
    "lenses": r"(?:LENS|Lens|LENSES|Lenses|Standard\s+Lenses)",
    "lens_options": r"(?:Lens Enhancement|LENS OPTIONS|Lens Options|Lens Treatment)",
    "progressive_lenses": r"(?:Progressive|PROGRESSIVE|Progressive Lenses)",
    "anti_reflective": r"(?:Anti-Reflective|ANTI-REFLECTIVE|Anti Reflective|AR Coating)",
    "contact_lenses": r"(?:CONTACT LENSES|Contact Lenses|CONTACTS|Contacts)"
}

# Row patterns for extracting benefit information
ROW_PATTERNS = {
    # Professional Services
    "exam": [
        r"(?:Exam|Eye Exam|Eye Examination)",
        r"(?:Comprehensive Eye Exam|Comprehensive Examination)"
    ],
    "retinal_screening": [
        r"(?:Retinal Screening Photography for Diabetics|Retinal Photography)"
    ],
    
    # Frames
    "frame": [
        r"(?:Frame|Frame Allowance)",
        r"(?:Frame Selection|Frame Benefit)"
    ],
    
    # Standard Lenses
    "standard_lenses": [
        r"(?:Standard Lenses|Basic Lenses)",
        r"(?:Lenses / Standard Lenses|Lenses / Basic Lenses)"
    ],
    "blended_bifocals": [
        r"(?:Blended Bifocals|Blended Bifocal Lenses)",
        r"(?:Lenses / Blended Bifocals|Lenses / Blended Bifocal)"
    ],
    "free_form_sv_lenses": [
        r"(?:Free-form SV Lenses|Free-form Single Vision)",
        r"(?:Lenses / Free-form SV|Lenses / Free-form Single Vision)"
    ],
    "sv_aspheric_lenses": [
        r"(?:SV Aspheric Lenses|Single Vision Aspheric)",
        r"(?:Lenses / SV Aspheric|Lenses / Single Vision Aspheric)"
    ],
    "mf_aspheric_lenses": [
        r"(?:MF Aspheric Lenses|Multi-focal Aspheric)",
        r"(?:Lenses / MF Aspheric|Lenses / Multi-focal Aspheric)"
    ],
    "occupational_double_seg_lenses": [
        r"(?:Occupational Double Seg Lenses|Double Segment Occupational)",
        r"(?:Lenses / Occupational Double Seg|Lenses / Double Segment Occupational)"
    ],
    
    # Progressive Lenses
    "progressive_non_formulary": [
        r"(?:Progressive Lenses: Non-Formulary|Non-Formulary Progressive)",
        r"(?:Lenses / Progressive: Non-Formulary|Lenses / Non-Formulary Progressive)"
    ],
    "progressive_tier_1": [
        r"(?:Progressive Lenses: Tier I|Tier I Progressive)",
        r"(?:Lenses / Progressive: Tier I|Lenses / Tier I Progressive)"
    ],
    "progressive_tier_2": [
        r"(?:Progressive Lenses: Tier II|Tier II Progressive)",
        r"(?:Lenses / Progressive: Tier II|Lenses / Tier II Progressive)"
    ],
    "progressive_tier_3": [
        r"(?:Progressive Lenses: Tier III|Tier III Progressive)",
        r"(?:Lenses / Progressive: Tier III|Lenses / Tier III Progressive)"
    ],
    "progressive_tier_4": [
        r"(?:Progressive Lenses: Tier IV|Tier IV Progressive)",
        r"(?:Lenses / Progressive: Tier IV|Lenses / Tier IV Progressive)"
    ],
    "progressive_tier_5": [
        r"(?:Progressive Lenses: Tier V|Tier V Progressive)",
        r"(?:Lenses / Progressive: Tier V|Lenses / Tier V Progressive)"
    ],
    
    # Lens Materials
    "high_index_standard": [
        r"(?:High Index less than or equal to 1.66|High Index ≤ 1.66)",
        r"(?:High Index Standard|High Index 1.66 or less)"
    ],
    "high_index_premium": [
        r"(?:High Index 1.66 - 1.73|High Index 1.66 to 1.73)",
        r"(?:High Index Premium|High Index 1.66-1.73)"
    ],
    "high_index_ultra": [
        r"(?:High Index, >= 1.74|High Index ≥ 1.74)",
        r"(?:High Index Ultra|High Index 1.74 or higher)"
    ],
    "polycarbonate_child": [
        r"(?:Polycarbonate Lenses for Ages 0-18|Polycarbonate Child)",
        r"(?:Polycarbonate Lenses Ages 0-18|Polycarbonate for Children)"
    ],
    "polycarbonate_adult": [
        r"(?:Polycarbonate Lenses for Ages 19+|Polycarbonate Adult)",
        r"(?:Polycarbonate Lenses Ages 19+|Polycarbonate for Adults)"
    ],
    
    # Anti-reflective Coating
    "ar_non_formulary": [
        r"(?:Anti-Reflective Coating: Non-Formulary|Non-Formulary AR Coating)",
        r"(?:AR Coating: Non-Formulary|Non-Formulary Anti-reflective)"
    ],
    "ar_tier_1": [
        r"(?:Anti-Reflective Coating: Tier I|Tier I AR Coating)",
        r"(?:AR Coating: Tier I|Tier I Anti-reflective)"
    ],
    "ar_tier_2": [
        r"(?:Anti-Reflective Coating: Tier II|Tier II AR Coating)",
        r"(?:AR Coating: Tier II|Tier II Anti-reflective)"
    ],
    "ar_tier_3": [
        r"(?:Anti-Reflective Coating: Tier III|Tier III AR Coating)",
        r"(?:AR Coating: Tier III|Tier III Anti-reflective)"
    ],
    "ar_tier_4": [
        r"(?:Anti-Reflective Coating: Tier IV|Tier IV AR Coating)",
        r"(?:AR Coating: Tier IV|Tier IV Anti-reflective)"
    ],
    
    # Other Lens Options
    "scratch_coating": [
        r"(?:Scratch Coating|Scratch Resistant Coating)",
        r"(?:Scratch Protection|Scratch Resistant)"
    ],
    "one_year_scratch_warranty": [
        r"(?:One Year Scratch Warranty|Scratch Warranty)",
        r"(?:1 Year Scratch Warranty|Scratch Protection Warranty)"
    ],
    "edge_coating": [
        r"(?:Edge Coating|Edge Polish)",
        r"(?:Edge Treatment|Edge Protection)"
    ],
    "photochromic": [
        r"(?:Photochromic|Transition Lenses)",
        r"(?:Light Adaptive|Light Sensitive)"
    ],
    "polarized": [
        r"(?:Polarized|Polarized Lenses)",
        r"(?:Polarization|Polarized Protection)"
    ],
    "tint": [
        r"(?:Tint|Tinted Lenses)",
        r"(?:Lens Tinting|Color Tint)"
    ],
    "uv_coating": [
        r"(?:UV Coating|Ultraviolet Coating)",
        r"(?:UV Protection|UV Blocking)"
    ],
    "polished_edges": [
        r"(?:Polished Edges|Roll & Polish)",
        r"(?:Edge Polish|Edge Finishing)"
    ],
    "oversize_lenses": [
        r"(?:Oversize Lenses|Oversized Lenses)",
        r"(?:Large Lenses|Extra Large Lenses)"
    ],
    "chemistrie_clip": [
        r"(?:Chemistrie Clip|Clip-on)",
        r"(?:Clip-on Lenses|Clip-on Protection)"
    ],
    "miscellaneous_lens_options": [
        r"(?:Miscellaneous Lens Options|Other Lens Options)",
        r"(?:Additional Lens Options|Extra Lens Options)"
    ]
}

# Patterns for identifying patient responsibility values
PATIENT_RESPONSIBILITY_PATTERNS = [
    r"\$([\d\.]+)",  # Dollar amounts: $100.00
    r"([\d\.]+)%",   # Percentages: 20%
    r"(Covered(?:-in-Full)?)",  # Covered or Covered-in-Full
    r"(Not Covered)",  # Not Covered
    r"(Included)",   # Included
    r"(Optional)",   # Optional
    r"(No Charge)",  # No Charge
    r"(Free)",       # Free
    r"(Waived)"      # Waived
]

# Age-specific patterns
AGE_PATTERNS = [
    r"for Ages (\d+)-(\d+)",  # for Ages 0-18
    r"for Ages (\d+)\+",      # for Ages 19+
    r"Ages (\d+)-(\d+)",      # Ages 0-18
    r"Ages (\d+)\+"           # Ages 19+
]

# Common prefixes to remove from patient responsibility values
PREFIX_PATTERNS = [
    r"Patient pays ",
    r"Member pays ",
    r"Copay: ",
    r"Cost: ",
    r"Price: ",
    r"Fee: "
]

# Section headers to skip (irrelevant sections)
SKIP_SECTIONS = [
    "Safety Eyewear",
    "Post-Cataract",
    "Out-of-Network Reimbursement",
    "Employee Only",
    "Maternity"
] 