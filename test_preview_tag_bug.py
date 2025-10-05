#!/usr/bin/env python3
"""
test_preview_tag_bug.py - Test for Preview Tag Definition Bug

This test specifically validates the fix for the bug where the "Preview" tag
was used in operation definitions but not defined in the global tags section.

Bug Description:
    File: venice.openapi.v3.yaml
    Lines: 3925, 4054
    Issue: The "Preview" tag is referenced in two operations (/characters and
           /characters/{slug}) but was not defined in the global tags section.
    Impact: This causes linting warnings and violates OpenAPI best practices.
           Tools may not properly display or group these endpoints.

Fix Strategy:
    Add the "Preview" tag definition to the global tags section with an
    appropriate description indicating these are experimental/beta endpoints.

Test Approach:
    This test will fail if the "Preview" tag is used in operations but not
    defined globally, demonstrating the bug. After the fix, it will pass.

Author: Venice.ai API Reference Team
"""

import yaml
import sys
from typing import Set, Dict, Any


def load_openapi_spec(spec_path: str = "venice.openapi.v3.yaml") -> Dict[str, Any]:
    """
    Load the OpenAPI specification from a YAML file.
    
    Args:
        spec_path (str): Path to the OpenAPI specification file
        
    Returns:
        dict: Parsed OpenAPI specification
        
    Raises:
        FileNotFoundError: If the specification file doesn't exist
        yaml.YAMLError: If the YAML is invalid
    """
    with open(spec_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_globally_defined_tags(spec: Dict[str, Any]) -> Set[str]:
    """
    Extract all globally defined tag names from the specification.
    
    Args:
        spec (dict): OpenAPI specification dictionary
        
    Returns:
        set: Set of tag names that are globally defined
    """
    global_tags = spec.get('tags', [])
    return {tag['name'] for tag in global_tags if isinstance(tag, dict) and 'name' in tag}


def get_tags_used_in_operations(spec: Dict[str, Any]) -> Set[str]:
    """
    Extract all tag names that are used in path operations.
    
    Args:
        spec (dict): OpenAPI specification dictionary
        
    Returns:
        set: Set of tag names used in operations
    """
    used_tags: Set[str] = set()
    paths = spec.get('paths', {})
    
    for path, operations in paths.items():
        if not isinstance(operations, dict):
            print(f"Warning: Operations for path '{path}' is not a dict (type: {type(operations).__name__}), skipping.")
            continue
        for method, operation in operations.items():
            if isinstance(operation, dict) and 'tags' in operation:
                operation_tags = operation['tags']
                if isinstance(operation_tags, list):
                    used_tags.update(operation_tags)
    
    return used_tags


def test_preview_tag_defined():
    """
    Test that the "Preview" tag is properly defined in the global tags section.
    
    This test specifically checks for the bug where the "Preview" tag was
    used in operations but not defined globally.
    
    Returns:
        bool: True if the test passes (tag is defined), False otherwise
    """
    print("=" * 70)
    print("Test: Preview Tag Definition Bug")
    print("=" * 70)
    print()
    
    # Load specification
    print("Loading OpenAPI specification...")
    spec = load_openapi_spec()
    print("✓ Specification loaded successfully")
    print()
    
    # Get globally defined tags
    global_tags = get_globally_defined_tags(spec)
    print(f"Globally defined tags ({len(global_tags)}):")
    for tag in sorted(global_tags):
        print(f"  - {tag}")
    print()
    
    # Get tags used in operations
    used_tags = get_tags_used_in_operations(spec)
    print(f"Tags used in operations ({len(used_tags)}):")
    for tag in sorted(used_tags):
        print(f"  - {tag}")
    print()
    
    # Find undefined tags
    undefined_tags = used_tags - global_tags
    
    if undefined_tags:
        print("✗ FAIL: The following tags are used but not defined globally:")
        for tag in sorted(undefined_tags):
            print(f"  - {tag}")
        print()
        print("This violates OpenAPI best practices and causes linting warnings.")
        return False
    
    # Specifically check for Preview tag
    if "Preview" not in global_tags:
        print("✗ FAIL: 'Preview' tag is not defined globally")
        return False
    
    print("✓ PASS: All used tags are properly defined globally")
    print("✓ PASS: 'Preview' tag is correctly defined")
    print()
    
    # Additional validation: Check Preview tag has description
    preview_tag = None
    for tag in spec.get('tags', []):
        if tag.get('name') == 'Preview':
            preview_tag = tag
            break
    
    if preview_tag and 'description' in preview_tag:
        print(f"✓ Preview tag description: {preview_tag['description'][:80]}...")
    
    return True


def main():
    """
    Main entry point for the test.
    
    Runs the Preview tag definition test and exits with appropriate status code.
    """
    try:
        success = test_preview_tag_defined()
        
        print()
        print("=" * 70)
        if success:
            print("TEST RESULT: PASS ✓")
            print("The Preview tag bug has been fixed.")
        else:
            print("TEST RESULT: FAIL ✗")
            print("The Preview tag bug still exists.")
        print("=" * 70)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
