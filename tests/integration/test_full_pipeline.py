#!/usr/bin/env python
"""
Test script for the EyeMed extractor with simplified plans
that don't break progressives and anti-reflective into tiers
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path if needed
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent  # tests/integration -> tests -> project_root
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    logger.info(f"Added {project_root} to sys.path")

from app.core.extractors.eyemed_extractor import EyeMedExtractor

def generate_simplified_plan_data():
    """
    Generate simplified EyeMed plan data that doesn't break 
    progressives and anti-reflective into tiers
    """
    simplified_data = """
    BENEFITS
    
    Service                  Member is Eligible?     Member Eligible As Of     Service Frequency
    --------------------------------------------------------------------------------------
    Exam                           Yes                 01/01/2025            Once every 12 months
    Lenses                         Yes                 01/01/2025            Once every 12 months
    Frame                          Yes                 01/01/2025            Once every 12 months
    Contact Lenses                 Yes                 01/01/2025            Once every 12 months
    
    Vision Care Services                       In-Network Member Cost
    --------------------------------------------------------
    Exam Services                              
    Exam                                       $0 copay
    
    Frame                                      
    Frame                                      $0 copay; 20% off balance over $75 allowance
    
    Lenses                                     
    Single Vision                              $0 copay
    Bifocal                                    $0 copay
    Trifocal                                   $0 copay
    Lenticular                                 20% off retail price
    Progressive - Premium                      20% off retail price
    Premium Tier 5 Innovations                 $120 copay; 20% off retail price less $120 allowance
    
    Lens Options                               
    Anti Reflective Coating - Standard         $45
    Anti Reflective Coating - Premium          20% off retail price
    Polycarbonate - Standard                   $35
    Scratch Coating - Standard Plastic         $15
    Tint - Solid and Gradient                  $15
    UV Treatment                               $15
    All Other Lens Options                     20% off retail price
    
    Contact Lenses                             
    Contacts - Medically Necessary             $0 copay
    """
    return simplified_data

async def test_with_simplified_plan():
    """
    Test the EyeMed extractor with simplified plan data
    """
    logger.info("Testing with simplified EyeMed plan")
    
    # Create simplified plan data
    simplified_plan_text = generate_simplified_plan_data()
    
    try:
        # Initialize the extractor
        extractor = EyeMedExtractor()
        
        # Process the simplified plan text
        results = await extractor.extract(simplified_plan_text, "simplified_eyemed_plan.txt")
        
        # Log the extraction results
        logger.info(f"Provider: {results.get('provider')}")
        logger.info(f"Confidence level: {results.get('confidence_score')}")
        
        # Print vision benefits
        vision_benefits = results.get('vision_benefits', {})
        logger.info("Vision Benefits:")
        
        # First check if progressive lenses are extracted correctly
        progressive_lenses = vision_benefits.get('progressive_lenses', {})
        logger.info("Progressive Lenses:")
        for key, value in progressive_lenses.items():
            logger.info(f"  {key}: {value}")
            
        # Check if anti-reflective coating is extracted correctly
        lens_options = vision_benefits.get('lens_options', {})
        anti_reflective = lens_options.get('anti_reflective_coating', {})
        logger.info("Anti-Reflective Coating:")
        for key, value in anti_reflective.items():
            logger.info(f"  {key}: {value}")
        
        # Save the results to a file
        output_file = "simplified_plan_result.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing simplified plan data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_simplified_plan()) 