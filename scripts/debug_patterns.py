#!/usr/bin/env python
"""
Debug script to print progressive lens patterns
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)
logger.debug("Base imports successful")

from app.core.pattern_library.providers.eyemed import EYEMED_PATTERNS
from app.core.pattern_library.manager import PatternManager

def main():
    # Initialize pattern manager
    pattern_manager = PatternManager(provider="eyemed")
    
    # Register all pattern groups
    for category, patterns in EYEMED_PATTERNS.items():
        logger.debug(f"Registering {len(patterns)} patterns from category: {category}")
        for pattern_group in patterns:
            pattern_manager.register_pattern_group(pattern_group)
    
    logger.info(f"Registered {len(pattern_manager.pattern_groups)} pattern groups in total")
    
    # Print all registered patterns
    logger.info("\nRegistered pattern groups:")
    for name, group in pattern_manager.pattern_groups.items():
        logger.info(f"Pattern Group: {name}")
        target_fields = set()
        for pattern in group.patterns:
            target_fields.add(pattern.target_field)
        logger.info(f"  Target fields: {sorted(list(target_fields))}")
    
    # Test lookup by field path
    test_fields = [
        "progressive_lenses.standard",
        "progressive_lenses.premium",
        "progressive_lenses.premium_tier_1",
        "progressive_lenses.premium_tier_2",
        "progressive_lenses.premium_tier_3",
        "progressive_lenses.premium_tier_4",
        "progressive_lenses.premium_tier_5",
    ]
    
    logger.info("\nTesting field path lookups:")
    for field_path in test_fields:
        # Find pattern groups that target this field path
        matching_groups = []
        for group in pattern_manager.pattern_groups.values():
            for pattern in group.patterns:
                if pattern.target_field == field_path:
                    matching_groups.append(group.name)
                    break
        
        if matching_groups:
            logger.info(f"Field path: {field_path} - Found in groups: {matching_groups}")
        else:
            logger.warning(f"Field path: {field_path} - NOT FOUND")

if __name__ == "__main__":
    main()



