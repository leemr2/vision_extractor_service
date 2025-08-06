"""
Vision Insurance Term Dictionary

A comprehensive collection of vision insurance terminology organized by categories.
This dictionary preserves provider-specific codes and terminology while standardizing
terms for cross-provider analysis.
"""

VISION_INSURANCE_TERMS = {
    # Lens Types - Different ways to refer to various lens designs
    "lens_types": [
        {
            "term": "single vision",
            "variations": [
                "sv", "single vis", "standard lenses", "lenses / standard lenses", 
                "single vision", "free-form sv lenses"
            ],
            "providers": {
                "vsp": ["Single Vision"],
                "eyemed": ["Single Vision"],
                "davis": ["Single Vision"],
                "spectera": ["Lenses / Standard Lenses", "Free-form SV Lenses"]
            }
        },
        {
            "term": "bifocal",
            "variations": ["bi-focal", "bf", "blended bifocal", "bifocals"],
            "providers": {
                "vsp": ["Bifocal"],
                "eyemed": ["Bifocal"],
                "davis": ["Bifocal", "Blended Segment"],
                "spectera": ["Bifocal"]
            }
        },
        {
            "term": "trifocal",
            "variations": ["tri-focal", "tf"],
            "providers": {
                "vsp": ["Trifocal"],
                "eyemed": ["Trifocal"],
                "davis": ["Trifocal"],
                "spectera": ["Trifocal"]
            }
        },
        {
            "term": "progressive",
            "variations": [
                "prog", "no-line", "pal", "multi-focal", "progressive lenses",
                "progressive lenses: tier i", "progressive lenses: tier ii", 
                "progressive lenses: tier iii", "progressive lenses: tier iv", 
                "progressive lenses: tier v", "progressive lenses: non-formulary",
                "standard progressives", "premium progressives", "custom progressives",
                "standard progressive addition multifocals", "premium progressive addition multifocals", 
                "ultra progressive addition multifocals", "ultimate progressive addition multifocals",
                "progressive standard", "progressive premium", "progressive ultra", "progressive ultimate"
            ],
            "providers": {
                "vsp": {
                    "codes": ["NA", "OA", "FA", "FE", "JA", "JE", "KA", "KE"],
                    "tiers": {
                        "standard": "KA, KE",
                        "premium": "FA, FE, JA, JE",
                        "custom": "NA, OA"
                    },
                    "descriptions": [
                        "Progressive K Plastic", "Progressive K Glass",
                        "Progressive F Plastic", "Progressive F Glass",
                        "Progressive J Plastic", "Progressive J Glass",
                        "Progressive N Plastic", "Progressive O Plastic"
                    ]
                },
                "eyemed": {
                    "tiers": {
                        "standard": "Progressive - Standard",
                        "premium_tier_1": "Progressive - Premium Tier 1",
                        "premium_tier_2": "Progressive - Premium Tier 2",
                        "premium_tier_3": "Progressive - Premium Tier 3",
                        "premium_tier_4": "Progressive - Premium Tier 4"
                    }
                },
                "davis": {
                    "tiers": {
                        "standard_progressive": ["Standard Tier PAL", "Standard Progressive Addition Multifocals", "Progressive Standard"],
                        "premium_progressive": ["Premium Tier PAL", "Premium Progressive Addition Multifocals", "Progressive Premium"],
                        "ultra_progressive": ["Ultra-Tier PAL", "Ultra Progressive Addition Multifocals", "Progressive Ultra"],
                        "ultimate_progressive": ["Ultimate Tier PAL", "Ultimate Progressive Addition Multifocals", "Progressive Ultimate"]
                    }
                },
                "spectera": {
                    "tiers": {
                        "non_formulary": "Lenses / Progressive Lenses: Non-Formulary",
                        "tier_1": "Lenses / Progressive Lenses: Tier I",
                        "tier_2": "Lenses / Progressive Lenses: Tier II",
                        "tier_3": "Lenses / Progressive Lenses: Tier III",
                        "tier_4": "Lenses / Progressive Lenses: Tier IV",
                        "tier_5": "Lenses / Progressive Lenses: Tier V"
                    }
                }
            }
        },
        {
            "term": "lenticular",
            "variations": ["lenticular lenses", "lenticular grind"],
            "providers": {
                "vsp": ["Lenticular"],
                "eyemed": ["Lenticular"],
                "spectera": ["Lenticular"]
            }
        },
        {
            "term": "digital single vision",
            "variations": ["digital sv", "digitally surfaced aspheric", "digital single vision (intermediate)"],
            "providers": {
                "vsp": {
                    "codes": ["BA"],
                    "descriptions": ["Digital Aspheric lenses-Plastic"]
                },
                "davis": ["Digital Single Vision (Intermediate)", "Digital Single Vision Lenses", "Digital Single Vision"]
            }
        },
        {
            "term": "aspheric",
            "variations": [
                "aspheric lenses", "sv aspheric lenses", "mf aspheric lenses",
                "aspheric", "digital aspheric"
            ],
            "providers": {
                "vsp": {
                    "codes": ["AA", "BA"],
                    "descriptions": ["Plastic 1.50 - Aspheric", "Digital Aspheric lenses-Plastic"]
                },
                "spectera": ["SV Aspheric Lenses", "MF Aspheric Lenses"]
            }
        },
        {
            "term": "blended",
            "variations": ["blended bifocals", "blended bifocal plastic", "blended myodisc"],
            "providers": {
                "vsp": {
                    "codes": ["GA"],
                    "descriptions": ["Blended Bifocal Plastic"]
                },
                "spectera": ["Lenses / Blended Bifocals"]
            }
        },
        {
            "term": "occupational",
            "variations": [
                "occupational lenses", "occupational double seg lenses",
                "double seg", "crt trifocal"
            ],
            "providers": {
                "vsp": ["Occupational Lenses"],
                "spectera": ["Lenses / Occupational Double Seg Lenses"]
            }
        }
    ],

    # Lens Materials - Different types of lens materials across providers
    "lens_materials": [
        {
            "term": "polycarbonate",
            "variations": [
                "poly", "polycarbonate lenses", "polycarbonate polarized",
                "polycarbonate essential blue series", "polycarbonate lenses***"
            ],
            "providers": {
                "vsp": {
                    "codes": [
                        "AD", "BD", "DD", "FD", "ID", "JD", "KD", "ND", "OD"
                    ],
                    "descriptions": [
                        "Polycarbonate",
                        "Polycarbonate (Digital Aspheric add-on)",
                        "Polycarbonate (Polarized add-on)",
                        "Polycarbonate (Progressive F add-on)",
                        "Polycarbonate (Near Variable Focus add-on)",
                        "Polycarbonate (Progressive J add-on)",
                        "Polycarbonate (Progressive K add-on)",
                        "Polycarbonate (Progressive N add-on)",
                        "Polycarbonate (Progressive O add-on)"
                    ]
                },
                "eyemed": ["Polycarbonate - Standard"],
                "davis": [
                    "Polycarbonate", 
                    "Polycarbonate Polarized", 
                    "Polycarbonate Essential Blue Series", 
                    "Polycarbonate Lenses***", 
                    "Polycarbonate - Single Vision", 
                    "Polycarbonate Provided",
                    "HD Polycarbonate - Multifocal",
                    "HD Polycarbonate - Single Vision"
                ],
                "spectera": ["Polycarbonate Lenses"]
            }
        },
        {
            "term": "high index",
            "variations": [
                "high-index", "hi index", "high index plastic", "high-index glass",
                "high index lenses 1.67", "high index lenses 1.74"
            ],
            "providers": {
                "vsp": {
                    "codes": ["AB", "AF", "AH", "AJ"],
                    "tiers": {
                        "1.60_trivex": "AB",
                        "1.66_1.67": "AH",
                        "1.71_plus": "AJ",
                        "glass": "AF"
                    },
                    "descriptions": [
                        "High Index Plastic 1.60 & Below/Trivex",
                        "High-Index Glass 1.60-1.80 (Clear)",
                        "High-Index Plastic 1.66/1.67",
                        "High-Index Plastic 1.71 & above"
                    ]
                },
                "davis": [
                    "High-Index 1.67", 
                    "High-Index 1.74", 
                    "High Index Lenses 1.67", 
                    "High Index Lenses 1.74",
                    "HighIndex 1.67",
                    "HighIndex 1.67 - Single Vision",
                    "HighIndex 1.74",
                    "HighIndex 1.74 - Multifocal", 
                    "HighIndex 1.74 - Single Vision"
                ],
                "spectera": [
                    "High Index 1.66 - 1.73",
                    "High Index less than or equal to 1.66",
                    "High Index, >= 1.74"
                ]
            }
        },
        {
            "term": "trivex",
            "variations": ["trivex essential blue series", "trivex lenses"],
            "providers": {
                "vsp": {
                    "codes": ["AB"],  # Shared with High Index 1.60
                    "descriptions": ["High Index Plastic 1.60 & Below/Trivex"]
                },
                "davis": ["Trivex", "Trivex Essential Blue Series", "Trivex Lenses"]
            }
        },
        {
            "term": "standard plastic",
            "variations": ["plastic", "cr-39", "standard (plastic)"],
            "providers": {
                "vsp": ["Standard Plastic"],
                "eyemed": ["Standard Plastic"],
                "davis": ["Standard (Plastic)"],
                "spectera": ["Standard Plastic"]
            }
        },
        {
            "term": "glass",
            "variations": ["glass single vision", "glass multifocal"],
            "providers": {
                "vsp": {
                    "codes": ["AE"],
                    "descriptions": ["Glass"]
                },
                "davis": ["Glass Single Vision", "Glass Multifocal", "Glass Polarized"]
            }
        }
    ],

    # Lens Treatments and Enhancements
    "lens_treatments": [
        {
            "term": "anti-reflective coating",
            "variations": [
                "ar coating", "anti reflective", "ar", "anti-reflect", "arc",
                "standard arc (anti-reflective coating)", "premium arc (anti-reflective coating)", 
                "ultra arc (anti-reflective coating)", "ultimate arc (anti-reflective coating)",
                "ar coating standard", "ar coating premium", "ar coating ultra", "ar coating ultimate"
            ],
            "providers": {
                "vsp": {
                    "codes": ["QM", "QT", "QV"],
                    "tiers": {
                        "standard": "QM",
                        "premium": "QT",
                        "custom": "QV"
                    },
                    "descriptions": [
                        "Anti-Reflective A",
                        "Anti-Reflective C",
                        "Anti-Reflective D",
                        "Standard Anti-Reflective Coating",
                        "Custom Anti-Reflective Coating",
                        "Premium Anti-Reflective"
                    ]
                },
                "eyemed": {
                    "tiers": {
                        "standard": "Anti Reflective Coating - Standard",
                        "premium_tier_1": "Anti Reflective Coating - Premium Tier 1",
                        "premium_tier_2": "Anti Reflective Coating - Premium Tier 2",
                        "premium_tier_3": "Anti Reflective Coating - Premium Tier 3"
                    }
                },
                "davis": {
                    "tiers": {
                        "standard": ["Standard Tier AR", "Standard ARC (anti-reflective coating)", "AR Coating Standard"],
                        "premium": ["Premium Tier AR", "Premium ARC (anti-reflective coating)", "AR Coating Premium"],
                        "ultra": ["Ultra-Tier AR", "Ultra ARC (anti-reflective coating)", "AR Coating Ultra"],
                        "ultimate": ["Ultimate Tier AR", "Ultimate ARC (anti-reflective coating)", "AR Coating Ultimate"]
                    }
                },
                "spectera": {
                    "tiers": {
                        "non_formulary": "Anti-Reflective Coating: Non-Formulary",
                        "tier_1": "Anti-Reflective Coating: Tier I",
                        "tier_2": "Anti-Reflective Coating: Tier II",
                        "tier_3": "Anti-Reflective Coating: Tier III",
                        "tier_4": "Anti-Reflective Coating: Tier IV"
                    }
                }
            }
        },
        {
            "term": "photochromic",
            "variations": [
                "transitions", "photochromatic", "photo", "light adaptive", 
                "photochromics", "photochromics glass", "photochromics plastic",
                "plastic photosensitive lenses", "tint photogrey", "tint plastic - photosensitive"
            ],
            "providers": {
                "vsp": {
                    "codes": ["PM", "PR"],
                    "descriptions": ["Photochromatics Glass", "Photochromatics Plastic"]
                },
                "eyemed": ["Photochromic - Non-Glass"],
                "davis": [
                    "Photochromic, non-glass (Transitions)", 
                    "Photochromic (PGX), Glass", 
                    "Plastic Photosensitive Lenses",
                    "Single Vision - Tint Plastic - Photosensitive",
                    "Multivision - Tint Plastic - Photosensitive",
                    "Single Vision - Tint Photogrey",
                    "Multivision - Tint Photogrey"
                ],
                "spectera": ["Photochromic"]
            }
        },
        {
            "term": "polarized",
            "variations": [
                "polar", "polarized/laminated", "polarized plastic", "polarized glass",
                "plastic polarized", "polycarbonate polarized", "high-index polarized",
                "polarized lenses"
            ],
            "providers": {
                "vsp": {
                    "codes": ["DA", "DE", "FP", "JP", "KP", "NP", "OP", "DB", "DH", "DJ"],
                    "descriptions": [
                        "Polarized Plastic A",
                        "Polarized Glass",
                        "Polarized (Progressive F add-on)",
                        "Polarized (Progressive J add-on)",
                        "Polarized (Progressive K add-on)",
                        "Polarized (Progressive N add-on)",
                        "Polarized (Progressive O add-on)",
                        "Polarized Lenses-High Index Plastic 1.60 & Below/Trivex",
                        "High-Index Plastic 1.66 (Polarized add-on)",
                        "High-Index Plastic 1.70 & above - Polarized"
                    ]
                },
                "davis": [
                    "Plastic Polarized", 
                    "Polycarbonate Polarized", 
                    "High-Index 1.67 Polarized", 
                    "Glass Polarized",
                    "Polarized Lenses"
                ],
                "spectera": ["Polarized"]
            }
        },
        {
            "term": "scratch resistant coating",
            "variations": [
                "scratch coating", "scratch resistance", "scratch resistant", 
                "scratch coating", "scratch protection plan",
                "scratch-resistant coating", "premium scratch resistent coating",
                "scratch resistant coating protection"
            ],
            "providers": {
                "vsp": {
                    "codes": ["QQ", "QS"],
                    "tiers": {
                        "standard": "QQ",
                        "premium": "QS"
                    },
                    "descriptions": ["Scratch Resistant A", "Scratch Resistant B"]
                },
                "eyemed": ["Scratch Coating - Standard Plastic"],
                "davis": [
                    "Scratch Resistant Coating - Standard", 
                    "Scratch Resistant Coating – Premium (TD2)",
                    "Scratch Protection Plan Single Vision",
                    "Scratch Protection Plan Multifocal",
                    "Scratch-Resistant Coating",
                    "Premium Scratch Resistent Coating",
                    "Scratch Resistant Coating",
                    "Multivision - Scratch Resistant Coating Protection"
                ],
                "spectera": ["Scratch Coating", "One Year Scratch Warranty"]
            }
        },
        {
            "term": "uv protection",
            "variations": [
                "uv", "ultraviolet", "uv coat", "uv coating", "uv treatment",
                "ultraviolet coating"
            ],
            "providers": {
                "vsp": {
                    "codes": ["SV", "BV"],
                    "descriptions": ["UV Protection", "UV Protection Backside lens"]
                },
                "eyemed": ["UV Treatment"],
                "davis": ["UV Coat", "Ultraviolet Coating"],
                "spectera": ["UV Coating"]
            }
        },
        {
            "term": "blue light filtering",
            "variations": [
                "blue light", "blue light filter", "essential blue series", "blue light filtering - ebs"
            ],
            "providers": {
                "davis": [
                    "Plastic Essential Blue Series",
                    "Polycarbonate Essential Blue Series",
                    "Trivex Essential Blue Series",
                    "High-Index 1.67 Essential Blue Series",
                    "High-Index 1.74 Essential Blue Series",
                    "Blue Light Filtering",
                    "Blue Light Filtering - EBS"
                ]
            }
        },
        {
            "term": "tint",
            "variations": [
                "tints", "tinted", "solid tints", "plastic dyes", "glass tints",
                "tint - solid and gradient", "plastic gradient dyes", "tint - gradient",
                "tinted lenses"
            ],
            "providers": {
                "vsp": {
                    "codes": ["MN", "MP", "MR"],
                    "descriptions": [
                        "Plastic Dyes (excludes Pink I & II)",
                        "Plastic Dyes Gradient",
                        "Glass Tints (excludes Pink I & II & Yellow)"
                    ]
                },
                "eyemed": ["Tint - Solid and Gradient"],
                "davis": ["Tint", "Tint - Gradient", "Tinted Lenses"],
                "spectera": ["Tint"]
            }
        },
        {
            "term": "mirror coating",
            "variations": [
                "mirror", "mirror solid", "mirror – solid, single and double gradient",
                "mirror coat", "mirror - solid, single & double gradient"
            ],
            "providers": {
                "vsp": {
                    "codes": ["QP", "QR"],
                    "descriptions": ["Mirror Solid", "Ski Type"]
                },
                "davis": [
                    "Mirror – Solid, Single and Double Gradient", 
                    "Mirror Coat", 
                    "Mirror - Solid, Single & Double Gradient"
                ]
            }
        },
        {
            "term": "color coating",
            "variations": [
                "glass color coatings solid", "glass color coatings gradient"
            ],
            "providers": {
                "vsp": {
                    "codes": ["MS", "MT"],
                    "descriptions": ["Glass Color Coatings Solid", "Glass Color Coatings Gradient"]
                }
            }
        },
        {
            "term": "edge treatments",
            "variations": [
                "edge coating", "high luster edge polish", "polished edges",
                "roll & polish", "roll and polish", "roll edge", "edge polish"
            ],
            "providers": {
                "vsp": {
                    "codes": ["SP", "SQ"],
                    "descriptions": ["High Luster Edge Polish", "Edge Coating"]
                },
                "davis": ["Edge Polish", "High Luster Edge Polish", "Roll and Polish", "Roll Edge", "Roll & Polish"],
                "spectera": ["Polished Edges / Roll & Polish", "Edge Coating"]
            }
        },
        {
            "term": "oversize lenses",
            "variations": [
                "frames stamped 61mm eye size or greater", "oversized lenses"
            ],
            "providers": {
                "vsp": {
                    "codes": ["RM", "RN"],
                    "descriptions": [
                        "Frames stamped 61mm Eye Size or Greater-Plastic",
                        "Frames stamped 61mm Eye Size or Greater-Glass"
                    ]
                },
                "davis": ["Oversized Lenses"],
                "spectera": ["Oversize Lenses"]
            }
        },
        {
            "term": "rimless mounting",
            "variations": [
                "rimless drill", "rimless", "rimless drill/notched"
            ],
            "providers": {
                "vsp": {
                    "codes": ["SW"],
                    "descriptions": ["Rimless Drill"]
                },
                "davis": ["Rimless Drill"]
            }
        },
        {
            "term": "facets",
            "variations": ["facetted lenses"],
            "providers": {
                "vsp": {
                    "codes": ["SR"],
                    "descriptions": ["Facetted Lenses"]
                }
            }
        },
        {
            "term": "near variable focus",
            "variations": [
                "near variable"
            ],
            "providers": {
                "vsp": {
                    "codes": ["IA", "IB", "ID", "II", "IJ"],
                    "descriptions": [
                        "Near Variable Focus Plastic A",
                        "Near Variable Focus - High Index Plastic 1.60 & Below/Trivex",
                        "Polycarbonate (Near Variable Focus add-on)",
                        "Near Variable Focus High-Index Plastic 1.66",
                        "Near Variable Focus-High Index Plastic 1.70 & above"
                    ]
                }
            }
        },
        {
            "term": "specialty lenses",
            "variations": [
                "myodisc", "lenticular grind", "double sided grind", "slab off",
                "specialty lens (myodisc,lenticular grind, double sided grind)"
            ],
            "providers": {
                "davis": [
                    "Specialty Lenses (Myodisc, Lenticular Grind, Double Sided Grind)",
                    "Slab Off",
                    "Specialty Lens (myodisc,lenticular grind, double sided grind)"
                ]
            }
        }
    ],

    # Pricing and Coverage Terms
    "pricing_terms": [
        {
            "term": "copay",
            "variations": ["co-pay", "copayment", "$0 copay", "$10.00", "$25 copay"],
            "providers": {
                "vsp": ["Copay", "Materials Copay", "Lens Copay", "Exam Copay"],
                "eyemed": ["$10 copay", "$25 copay", "$45 copay", "$55 copay"],
                "spectera": ["$10.00"]
            }
        },
        {
            "term": "covered",
            "variations": [
                "covered-in-full", "covered in full", "$0", 
                "covered with additional copay", "covered with additional copay, 80% of u&c to max",
                "covered with additional copay, 80% of u&c"
            ],
            "providers": {
                "vsp": [
                    "Covered",
                    "Covered With Additional Copay",
                    "Covered With Additional Copay, 80% of U&C to Max",
                    "Covered With Additional Copay, 80% of U&C"
                ],
                "eyemed": ["$0 copay"],
                "spectera": ["Covered-in-Full"]
            }
        },
        {
            "term": "not covered",
            "variations": ["not available", "not included"],
            "providers": {
                "vsp": ["Not Covered"],
                "spectera": ["Not Covered"]
            }
        },
        {
            "term": "allowance",
            "variations": [
                "benefit allowance", "frame allowance", "materials allowance",
                "balance over allowance"
            ],
            "providers": {
                "vsp": ["Frame Allowance", "CL Materials"],
                "eyemed": [
                    "$140 allowance", 
                    "$150 allowance", 
                    "15% off balance over $150 allowance",
                    "100% of balance over $150 allowance"
                ],
                "spectera": [
                    "$130.00 Benefit Allowance", 
                    "$125.00 Benefit Allowance",
                    "70.00% of Balance over $130.00 Benefit Allowance",
                    "100.00% of Balance over $125.00 Benefit Allowance"
                ]
            }
        },
        {
            "term": "discount",
            "variations": [
                "% off", "percent off", "off retail price", "off balance",
                "u&c", "billed charges"
            ],
            "providers": {
                "vsp": ["80% of U&C", "80% of U&C to Max"],
                "eyemed": [
                    "20% off retail price", 
                    "15% off balance over",
                    "10% off retail price"
                ],
                "spectera": [
                    "80% of Billed Charges",
                    "100% of Billed Charges"
                ]
            }
        },
        {
            "term": "patient responsibility",
            "variations": [
                "member out-of-pocket", "out of pocket", "patient cost"
            ],
            "providers": {
                "davis": ["Member Out-of-Pocket"],
                "spectera": ["Patient Responsibility"]
            }
        }
    ],

    # Contact Lens Terms
    "contact_lens_terms": [
        {
            "term": "contact lens fit",
            "variations": [
                "contact lens fit and follow-up", "contact lens evaluation",
                "fit and follow-up", "contact lens fitting"
            ],
            "providers": {
                "vsp": ["Contact Lens Exam", "CL Exam Services"],
                "eyemed": [
                    "Contact Lens Fit and Follow-up",
                    "Fit and Follow-up - Standard",
                    "Fit and Follow-up - Premium"
                ],
                "spectera": [
                    "Non-Selection Contact Lens Fit",
                    "Selection Contact Lens Fit"
                ]
            }
        },
        {
            "term": "contact lenses",
            "variations": [
                "contacts", "selection contact lenses", "non-selection contact lenses",
                "conventional", "disposable", "medically necessary"
            ],
            "providers": {
                "vsp": ["Contacts", "CL Materials", "Necessary Contact Lenses"],
                "eyemed": [
                    "Contact Lenses",
                    "Contacts - Conventional",
                    "Contacts - Disposable",
                    "Contacts - Medically Necessary"
                ],
                "spectera": [
                    "Necessary Contact Lenses",
                    "Non-Selection Contact Lenses",
                    "Selection Contact Lenses - Daily/Biweekly Wear",
                    "Selection Contact Lenses - Monthly Wear"
                ]
            }
        }
    ],

    # Service Frequencies and Eligibility Terms
    "eligibility_terms": [
        {
            "term": "frequency",
            "variations": [
                "service frequency", "every year", "every month", "once every"
            ],
            "providers": {
                "vsp": ["Service Freq", "Every year beginning in", "Every month beginning in"],
                "eyemed": ["Once every calendar year", "Unlimited"],
                "spectera": ["Once every 12 month(s)", "Once every 24 month(s)", "Every 12 month(s)"]
            }
        },
        {
            "term": "eligibility",
            "variations": [
                "patient is eligible", "member is eligible", "available", "not covered"
            ],
            "providers": {
                "vsp": ["Eligibility", "YES", "NO"],
                "eyemed": ["Member is Eligible?", "Yes", "No", "Member Eligible As Of"],
                "spectera": ["Benefit Eligibility", "Available", "Not Covered"]
            }
        },
        {
            "term": "exam",
            "variations": [
                "eye exam", "vision exam", "routine eye exam", "exam/profsvcs",
                "exam services", "professional services", "maternity exam"
            ],
            "providers": {
                "vsp": ["Exam", "Exam/ProfSvcs", "WellVision Exam"],
                "eyemed": ["Exam", "Exam Services"],
                "spectera": ["Exam", "Maternity Exam", "Professional Services"]
            }
        },
        {
            "term": "frame",
            "variations": ["frames", "eyeglass frames"],
            "providers": {
                "vsp": ["Frame"],
                "eyemed": ["Frame"],
                "spectera": ["Frame"]
            }
        }
    ],

    # VSP-specific Code System
    "vsp_code_system": {
        "material_codes": [
            # Aspheric & Digital Aspheric
            {"code": "AA", "description": "Plastic 1.50 - Aspheric"},
            {"code": "BA", "description": "Digital Aspheric lenses-Plastic"},
            
            # Polycarbonate
            {"code": "AD", "description": "Polycarbonate"},
            {"code": "BD", "description": "Polycarbonate (Digital Aspheric add-on)"},
            {"code": "DD", "description": "Polycarbonate (Polarized add-on)"},
            {"code": "FD", "description": "Polycarbonate (Progressive F add-on)"},
            {"code": "ID", "description": "Polycarbonate (Near Variable Focus add-on)"},
            {"code": "JD", "description": "Polycarbonate (Progressive J add-on)"},
            {"code": "KD", "description": "Polycarbonate (Progressive K add-on)"},
            {"code": "ND", "description": "Polycarbonate (Progressive N add-on)"},
            {"code": "OD", "description": "Polycarbonate (Progressive O add-on)"},
            
            # Glass 
            {"code": "AE", "description": "Glass"},
            
            # High Index Materials
            {"code": "AB", "description": "High Index Plastic 1.60 & Below/Trivex"},
            {"code": "AF", "description": "High-Index Glass 1.60-1.80 (Clear)"},
            {"code": "AH", "description": "High-Index Plastic 1.66/1.67"},
            {"code": "AJ", "description": "High-Index Plastic 1.71 & above"},
            {"code": "BB", "description": "Digital Lenses-High Index Plastic 1.60 & Below/Trivex"},
            {"code": "BH", "description": "Digital Lenses-High Index Plastic 1.66/1.67"},
            {"code": "BJ", "description": "Digital Lenses-High Index Plastic 1.70 & Above"},
            
            # Polarized Lenses
            {"code": "DA", "description": "Polarized Plastic A"},
            {"code": "DB", "description": "Polarized Lenses-High Index Plastic 1.60 & Below/Trivex"},
            {"code": "DE", "description": "Polarized Glass"},
            {"code": "DH", "description": "High-Index Plastic 1.66 (Polarized add-on)"},
            {"code": "DJ", "description": "High-Index Plastic 1.70 & above - Polarized"},
            
            # Progressive Lenses
            {"code": "FA", "description": "Progressive F Plastic"},
            {"code": "FB", "description": "Progressive F - High Index Plastic 1.60 & Below/Trivex"},
            {"code": "FE", "description": "Progressive F Glass"},
            {"code": "FH", "description": "High-Index Plastic 1.66 (Progressive F add-on)"},
            {"code": "FJ", "description": "High-Index Plastic 1.71 (Progressive F add-on)"},
            {"code": "FP", "description": "Polarized (Progressive F add-on)"},
            
            # Blended Bifocal
            {"code": "GA", "description": "Blended Bifocal Plastic"},
            
            # Near Variable Focus
            {"code": "IA", "description": "Near Variable Focus Plastic A"},
            {"code": "IB", "description": "Near Variable Focus - High Index Plastic 1.60 & Below/Trivex"},
            {"code": "II", "description": "Near Variable Focus High-Index Plastic 1.66"},
            {"code": "IJ", "description": "Near Variable Focus-High Index Plastic 1.70 & above"},
            
            # Progressive J
            {"code": "JA", "description": "Progressive J Plastic"},
            {"code": "JB", "description": "Progressive J - High Index Plastic 1.60 & Below/Trivex"},
            # Progressive J (continued)
            {"code": "JE", "description": "Progressive J Glass"},
            {"code": "JH", "description": "High-Index Plastic 1.66 (Progressive J add-on)"},
            {"code": "JJ", "description": "High-Index Plastic 1.71 (Progressive J add-on)"},
            {"code": "JP", "description": "Polarized (Progressive J add-on)"},
            
            # Progressive K
            {"code": "KA", "description": "Progressive K Plastic"},
            {"code": "KB", "description": "Progressive K - High Index Plastic 1.60 & Below/Trivex"},
            {"code": "KE", "description": "Progressive K Glass"},
            {"code": "KH", "description": "High-Index Plastic 1.66 (Progressive K add-on)"},
            {"code": "KJ", "description": "High-Index Plastic 1.71 (Progressive K add-on)"},
            {"code": "KP", "description": "Polarized (Progressive K add-on)"},
            
            # Progressive N
            {"code": "NA", "description": "Progressive N Plastic"},
            {"code": "NB", "description": "Progressive N - High Index Plastic 1.60 & Below/Trivex"},
            {"code": "NH", "description": "High-Index Plastic 1.66 (Progressive N add-on)"},
            {"code": "NJ", "description": "High-Index Plastic 1.71 (Progressive N add-on)"},
            {"code": "NP", "description": "Polarized (Progressive N add-on)"},
            
            # Progressive O
            {"code": "OA", "description": "Progressive O Plastic"},
            {"code": "OB", "description": "Progressive O - High Index Plastic 1.60 & Below/Trivex"},
            {"code": "OH", "description": "High-Index Plastic 1.66 (Progressive O add-on)"},
            {"code": "OJ", "description": "High-Index Plastic 1.71 (Progressive O add-on)"},
            {"code": "OP", "description": "Polarized (Progressive O add-on)"},
            
            # Photochromic
            {"code": "PM", "description": "Photochromatics Glass"},
            {"code": "PR", "description": "Photochromatics Plastic"},
            
            # Oversize
            {"code": "RM", "description": "Frames stamped 61mm Eye Size or Greater-Plastic"},
            {"code": "RN", "description": "Frames stamped 61mm Eye Size or Greater-Glass"}
        ],
        
        "treatment_codes": [
            # UV Protection
            {"code": "BV", "description": "UV Protection Backside lens"},
            {"code": "SV", "description": "UV Protection"},
            
            # Custom Measurement
            {"code": "CM", "description": "Custom Measurement"},
            
            # Light Filter
            {"code": "LF", "description": "Light Filter"},
            
            # Tints and Dyes
            {"code": "MN", "description": "Plastic Dyes (excludes Pink I & II)"},
            {"code": "MP", "description": "Plastic Dyes Gradient"},
            {"code": "MR", "description": "Glass Tints (excludes Pink I & II & Yellow)"},
            
            # Color Coatings
            {"code": "MS", "description": "Glass Color Coatings Solid"},
            {"code": "MT", "description": "Glass Color Coatings Gradient"},
            
            # Anti-Reflective Coatings
            {"code": "QM", "description": "Anti-Reflective A"},
            {"code": "QT", "description": "Anti-Reflective C"},
            {"code": "QV", "description": "Anti-Reflective D"},
            
            # Mirror Coatings
            {"code": "QP", "description": "Mirror Solid"},
            {"code": "QR", "description": "Ski Type"},
            
            # Scratch Resistant Coatings
            {"code": "QQ", "description": "Scratch Resistant A"},
            {"code": "QS", "description": "Scratch Resistant B"},
            
            # Edge Treatments
            {"code": "SP", "description": "High Luster Edge Polish"},
            {"code": "SQ", "description": "Edge Coating"},
            
            # Facets
            {"code": "SR", "description": "Facetted Lenses"},
            
            # Rimless
            {"code": "SW", "description": "Rimless Drill"},
            
            # Technical Add-On
            {"code": "TA", "description": "Technical Add On A"}
        ]
    },
    
    # EyeMed-specific terminology
    "eyemed_specific_terms": {
        "progressive_tiers": [
            {"tier": "standard", "description": "Progressive - Standard"},
            {"tier": "premium_tier_1", "description": "Progressive - Premium Tier 1"},
            {"tier": "premium_tier_2", "description": "Progressive - Premium Tier 2"},
            {"tier": "premium_tier_3", "description": "Progressive - Premium Tier 3"},
            {"tier": "premium_tier_4", "description": "Progressive - Premium Tier 4"}
        ],
        "ar_coating_tiers": [
            {"tier": "standard", "description": "Anti Reflective Coating - Standard"},
            {"tier": "premium_tier_1", "description": "Anti Reflective Coating - Premium Tier 1"},
            {"tier": "premium_tier_2", "description": "Anti Reflective Coating - Premium Tier 2"},
            {"tier": "premium_tier_3", "description": "Anti Reflective Coating - Premium Tier 3"}
        ],
        "contact_lens_types": [
            {"type": "conventional", "description": "Contacts - Conventional"},
            {"type": "disposable", "description": "Contacts - Disposable"},
            {"type": "medically_necessary", "description": "Contacts - Medically Necessary"}
        ],
        "price_formats": [
            {"format": "copay", "example": "$25 copay"},
            {"format": "copay_with_discount", "example": "$0 copay; 15% off balance over $150 allowance"},
            {"format": "copay_with_balance", "example": "$0 copay; 100% of balance over $150 allowance"},
            {"format": "copay_with_discount_less_allowance", "example": "$25 copay; 20% off retail price less $120 allowance"},
            {"format": "percentage_discount", "example": "20% off retail price"},
            {"format": "up_to_amount", "example": "Up to $39"}
        ]
    },
    
    # Davis Vision-specific terminology
    "davis_specific_terms": {
        "progressive_tiers": [
            {"tier": "standard_progressive", "description": "Standard Tier PAL"},
            {"tier": "premium_progressive", "description": "Premium Tier PAL"},
            {"tier": "ultra_progressive", "description": "Ultra-Tier PAL"},
            {"tier": "ultimate_progressive", "description": "Ultimate Tier PAL"}
        ],
        "ar_coating_tiers": [
            {"tier": "standard_ar", "description": "Standard Tier AR"},
            {"tier": "premium_ar", "description": "Premium Tier AR"},
            {"tier": "ultra_ar", "description": "Ultra-Tier AR"},
            {"tier": "ultimate_ar", "description": "Ultimate Tier AR"}
        ],
        "blue_light_filtering": [
            {"material": "plastic", "description": "Plastic Essential Blue Series"},
            {"material": "polycarbonate", "description": "Polycarbonate Essential Blue Series"},
            {"material": "trivex", "description": "Trivex Essential Blue Series"},
            {"material": "hi_index_1.67", "description": "High-Index 1.67 Essential Blue Series"},
            {"material": "hi_index_1.74", "description": "High-Index 1.74 Essential Blue Series"}
        ],
        "specialty_lenses": [
            {"type": "myodisc", "description": "Specialty Lenses (Myodisc, Lenticular Grind, Double Sided Grind)"},
            {"type": "slab_off", "description": "Slab Off"}
        ],
        "fee_components": [
            {"component": "member_out_of_pocket", "description": "Member Out-of-Pocket"},
            {"component": "provider_surfee", "description": "Provider Surfee"}
        ]
    },
    
    # Spectera/UHC Vision-specific terminology
    "spectera_specific_terms": {
        "progressive_tiers": [
            {"tier": "non_formulary", "description": "Lenses / Progressive Lenses: Non-Formulary"},
            {"tier": "tier_1", "description": "Lenses / Progressive Lenses: Tier I"},
            {"tier": "tier_2", "description": "Lenses / Progressive Lenses: Tier II"},
            {"tier": "tier_3", "description": "Lenses / Progressive Lenses: Tier III"},
            {"tier": "tier_4", "description": "Lenses / Progressive Lenses: Tier IV"},
            {"tier": "tier_5", "description": "Lenses / Progressive Lenses: Tier V"}
        ],
        "ar_coating_tiers": [
            {"tier": "non_formulary", "description": "Anti-Reflective Coating: Non-Formulary"},
            {"tier": "tier_1", "description": "Anti-Reflective Coating: Tier I"},
            {"tier": "tier_2", "description": "Anti-Reflective Coating: Tier II"},
            {"tier": "tier_3", "description": "Anti-Reflective Coating: Tier III"},
            {"tier": "tier_4", "description": "Anti-Reflective Coating: Tier IV"}
        ],
        "contact_lens_types": [
            {"type": "necessary", "description": "Necessary Contact Lenses"},
            {"type": "non_selection", "description": "Non-Selection Contact Lenses"},
            {"type": "selection_daily", "description": "Selection Contact Lenses - Daily/Biweekly Wear"},
            {"type": "selection_monthly", "description": "Selection Contact Lenses - Monthly Wear"}
        ],
        "coverage_patterns": [
            {"pattern": "percent_of_billed_charges", "example": "80% of Billed Charges"},
            {"pattern": "percent_of_balance_over", "example": "70.00% of Balance over $130.00 Benefit Allowance"},
            {"pattern": "fixed_amount", "example": "$10.00"}
        ]
    },
    
    # Common Coverage Descriptions
    "coverage_descriptions": [
        {"term": "covered in full", "variations": ["covered-in-full", "$0", "$0 copay", "covered"]},
        {"term": "not covered", "variations": ["not available", "not eligible"]},
        {"term": "percentage of billed charges", "variations": ["% of billed charges", "billed charges"]},
        {"term": "dollar copay", "variations": ["$x copay", "$xx.xx"]},
        {"term": "percentage discount", "variations": ["% off retail price", "% off balance over allowance"]},
        {"term": "allowance with overage", "variations": [
            "allowance with % off balance", 
            "% of balance over $ allowance", 
            "% off balance over $ allowance"
        ]}
    ],
    
    # Common Benefit Types
    "benefit_types": [
        {"term": "routine vision", "variations": ["routine", "vision benefits"]},
        {"term": "medical eye care", "variations": ["medical", "medical eye services"]},
        {"term": "additional purchases", "variations": ["additional pairs", "second pairs", "routine additional purchase"]}
    ]
}

# Helper functions for working with the term dictionary

def find_standard_term(category, term_or_variation):
    """
    Find the standard term for a given variation within a category
    
    Args:
        category (str): Dictionary category (e.g., 'lens_types', 'lens_materials')
        term_or_variation (str): Term or variation to look up
    
    Returns:
        str: The standardized term, or the original input if not found
    """
    term_or_variation = term_or_variation.lower()
    
    if category in VISION_INSURANCE_TERMS:
        for term_entry in VISION_INSURANCE_TERMS[category]:
            # Check if it's the standard term
            if term_entry["term"].lower() == term_or_variation:
                return term_entry["term"]
            
            # Check variations
            if "variations" in term_entry:
                for variation in term_entry["variations"]:
                    if variation.lower() == term_or_variation:
                        return term_entry["term"]
                    
                    # Partial matching for complex variations
                    if variation.lower() in term_or_variation or term_or_variation in variation.lower():
                        # Only match if significant overlap (over 50% of characters)
                        common_length = len(set(variation.lower()) & set(term_or_variation))
                        min_length = min(len(variation), len(term_or_variation))
                        if common_length / min_length > 0.5:
                            return term_entry["term"]
    
    # Return original if no match found
    return term_or_variation

def get_vsp_code_description(code):
    """
    Get the description for a VSP code
    
    Args:
        code (str): VSP code (e.g., 'AD', 'QM')
    
    Returns:
        str: Description of the code, or None if not found
    """
    code = code.upper()
    
    # Check material codes
    for code_entry in VISION_INSURANCE_TERMS["vsp_code_system"]["material_codes"]:
        if code_entry["code"] == code:
            return code_entry["description"]
    
    # Check treatment codes
    for code_entry in VISION_INSURANCE_TERMS["vsp_code_system"]["treatment_codes"]:
        if code_entry["code"] == code:
            return code_entry["description"]
    
    return None

def is_vsp_code(code):
    """
    Check if a string is a valid VSP code
    
    Args:
        code (str): String to check
    
    Returns:
        bool: True if it's a valid VSP code, False otherwise
    """
    if not code or len(code) != 2:
        return False
    
    code = code.upper()
    
    # Check material codes
    for code_entry in VISION_INSURANCE_TERMS["vsp_code_system"]["material_codes"]:
        if code_entry["code"] == code:
            return True
    
    # Check treatment codes
    for code_entry in VISION_INSURANCE_TERMS["vsp_code_system"]["treatment_codes"]:
        if code_entry["code"] == code:
            return True
    
    return False

def get_provider_specific_term(provider, category, term):
    """
    Get provider-specific terminology for a standard term
    
    Args:
        provider (str): Provider name (e.g., 'vsp', 'eyemed', 'davis', 'spectera')
        category (str): Term category (e.g., 'lens_types', 'lens_treatments')
        term (str): Standard term to look up
    
    Returns:
        list: Provider-specific terminology for the term, or empty list if not found
    """
    provider = provider.lower()
    
    for term_entry in VISION_INSURANCE_TERMS.get(category, []):
        if term_entry["term"].lower() == term.lower():
            provider_terms = term_entry.get("providers", {}).get(provider, [])
            
            # Handle both list and dictionary provider terms
            if isinstance(provider_terms, dict):
                if "descriptions" in provider_terms:
                    return provider_terms["descriptions"]
                elif "tiers" in provider_terms:
                    return list(provider_terms["tiers"].values())
                else:
                    return []


# Create TERM_DICTIONARY for compatibility with term_annotator
# This maps provider names to their specific terminology patterns
TERM_DICTIONARY = {
    "vsp": {
        "lens_types": {
            "single_vision": [r"\bsingle\s+vision\b", r"\bsv\b"],
            "progressive": [r"\bprogressive\b", r"\bprog\b", r"\bpal\b"],
            "bifocal": [r"\bbifocal\b", r"\bbi-focal\b"],
            "trifocal": [r"\btrifocal\b", r"\btri-focal\b"]
        },
        "lens_materials": {
            "polycarbonate": [r"\bpolycarbonate\b", r"\bpoly\b"],
            "high_index": [r"\bhigh\s+index\b", r"\bhi\s+index\b"],
            "trivex": [r"\btrivex\b"]
        },
        "lens_treatments": {
            "anti_reflective": [r"\banti.reflective\b", r"\bar\s+coating\b", r"\barc\b"],
            "photochromic": [r"\bphotochromic\b", r"\btransitions\b"],
            "polarized": [r"\bpolarized\b", r"\bpolar\b"]
        }
    },
    "eyemed": {
        "lens_types": {
            "single_vision": [r"\bsingle\s+vision\b"],
            "progressive": [r"\bprogressive\b", r"\bpremium\s+tier\b"],
            "bifocal": [r"\bbifocal\b"],
            "trifocal": [r"\btrifocal\b"]
        },
        "lens_treatments": {
            "anti_reflective": [r"\banti\s+reflective\s+coating\b", r"\bar\s+coating\b"],
            "photochromic": [r"\bphotochromic\b"]
        }
    },
    "davis": {
        "lens_types": {
            "single_vision": [r"\bsingle\s+vision\b"],
            "progressive": [r"\bprogressive\b", r"\bstandard\s+tier\s+pal\b", r"\bpremium\s+tier\s+pal\b"],
            "bifocal": [r"\bbifocal\b"],
            "trifocal": [r"\btrifocal\b"]
        },
        "lens_treatments": {
            "anti_reflective": [r"\bstandard\s+tier\s+ar\b", r"\bpremium\s+tier\s+ar\b"],
            "blue_light": [r"\bessential\s+blue\s+series\b"]
        }
    },
    "spectera": {
        "lens_types": {
            "single_vision": [r"\bstandard\s+lenses\b"],
            "progressive": [r"\bprogressive\s+lenses\b", r"\btier\s+[iv]+\b"],
            "bifocal": [r"\bbifocal\b"]
        },
        "lens_treatments": {
            "anti_reflective": [r"\banti.reflective\s+coating\b"]
        }
    }
}
