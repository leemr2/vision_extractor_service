"""
Pattern manager for orchestrating extraction patterns
"""
from typing import Dict, List, Any, Optional
import logging
from app.core.pattern_library.base.pattern_base import PatternGroup, ExtractionPattern

class PatternManager:
    """Manages extraction patterns and orchestrates the extraction process"""
    
    def __init__(self, provider: str):
        """
        Initialize the pattern manager for a specific provider
        
        Args:
            provider: The insurance provider name
        """
        self.provider = provider
        self.pattern_groups = {}
        self.logger = logging.getLogger(f"pattern_manager.{provider}")
    
    def register_pattern_group(self, group: PatternGroup):
        """
        Register a pattern group with the manager
        
        Args:
            group: The pattern group to register
        """
        self.pattern_groups[group.name] = group
        self.logger.debug(f"Registered pattern group: {group.name} with {len(group.patterns)} patterns")
    
    def register_pattern_groups(self, groups: List[PatternGroup]):
        """
        Register multiple pattern groups
        
        Args:
            groups: List of pattern groups to register
        """
        for group in groups:
            self.register_pattern_group(group)
    
    def extract(self, text: str, field_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract data for a specific field path using appropriate patterns
        
        Args:
            text: The document text to extract from
            field_path: The target field path (e.g., "exam_services.exam")
            
        Returns:
            Extraction result or None if no match found
        """
        # Find pattern groups that target this field path
        matching_groups = []
        for group in self.pattern_groups.values():
            for pattern in group.patterns:
                if pattern.target_field == field_path:
                    matching_groups.append(group)
                    break
        
        if not matching_groups:
            self.logger.warning(f"No pattern groups found for field path: {field_path}")
            return None
        
        # Try each group and return the highest confidence result
        results = []
        for group in matching_groups:
            result = group.extract(text)
            if result:
                results.append(result)
        
        if not results:
            return None
        
        # Return the highest confidence result
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results[0]
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all fields from the text
        
        Args:
            text: The document text to extract from
            
        Returns:
            Dictionary with all extracted field values
        """
        results = {}
        
        for group in self.pattern_groups.values():
            result = group.extract(text)
            if result:
                field_path = result["field"]
                
                # Handle nested fields
                parts = field_path.split(".")
                current = results
                
                # Create nested structure
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value
                current[parts[-1]] = result["value"]
        
        return results
