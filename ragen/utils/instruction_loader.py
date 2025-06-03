"""
Utility to load instruction mapping from the criticsearch package,
instead of relying on local files.
"""
import json
from typing import Dict


def load_instruction_mapping(package_name: str = "criticsearch.data") -> Dict[str, str]:
    """
    Load instruction_mapping.json from the criticsearch package using importlib.resources.
    
    Args:
        package_name: The package name containing the instruction_mapping.json file
        
    Returns:
        Dictionary mapping filenames to instructions
        
    Example:
        >>> mapping = load_instruction_mapping()
        >>> instruction = mapping.get("2024_Botswana_general_election.json", "")
    """
    try:
        # Use importlib.resources to read from the criticsearch package
        pkg = package_name
        with (
            __import__("importlib.resources").resources.files(pkg).
            joinpath("instruction_mapping.json")
        ) as instruction_file:
            with open(instruction_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (FileNotFoundError, ModuleNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load instruction_mapping.json from {package_name}: {e}")
        # Fallback to local file if package resource is not available
        try:
            with open("instruction_mapping.json", 'r', encoding='utf-8') as f:
                print("Loading instruction_mapping.json from local fallback")
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as fallback_e:
            print(f"Error: Could not load instruction_mapping.json from local fallback: {fallback_e}")
            return {}


def get_instruction_for_file(filename: str, package_name: str = "criticsearch.data") -> str:
    """
    Get instruction for a specific filename.
    
    Args:
        filename: The filename to get instruction for
        package_name: The package name containing the instruction_mapping.json file
        
    Returns:
        Instruction string for the given filename, or empty string if not found
    """
    mapping = load_instruction_mapping(package_name)
    return mapping.get(filename, "") 