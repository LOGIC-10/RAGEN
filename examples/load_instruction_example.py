#!/usr/bin/env python3
"""
Example of how to load instruction mapping from criticsearch package
instead of relying on local files.
"""

from ragen.utils.instruction_loader import load_instruction_mapping, get_instruction_for_file


def main():
    # Example 1: Load entire instruction mapping
    print("Loading instruction mapping from criticsearch package...")
    instruction_mapping = load_instruction_mapping()
    
    if instruction_mapping:
        print(f"Successfully loaded {len(instruction_mapping)} instructions")
        
        # Show first few examples
        for i, (filename, instruction) in enumerate(instruction_mapping.items()):
            if i >= 3:  # Show only first 3 examples
                break
            print(f"\nFile: {filename}")
            print(f"Instruction: {instruction[:100]}...")  # Truncate for display
    else:
        print("Failed to load instruction mapping")

    # Example 2: Get instruction for a specific file
    print("\n" + "="*60)
    print("Example: Getting instruction for specific file")
    
    filename = "2024_Botswana_general_election.json"
    instruction = get_instruction_for_file(filename)
    
    if instruction:
        print(f"File: {filename}")
        print(f"Instruction: {instruction}")
    else:
        print(f"No instruction found for {filename}")

    # Example 3: Try different package names (for flexibility)
    print("\n" + "="*60)
    print("Example: Trying different package locations")
    
    # Try different possible package locations
    possible_packages = [
        "criticsearch.data",
        "criticsearch.resources", 
        "criticsearch",
        "criticsearch.reportbench.data"
    ]
    
    for pkg in possible_packages:
        try:
            mapping = load_instruction_mapping(pkg)
            if mapping:
                print(f"✓ Successfully loaded from {pkg}")
                break
            else:
                print(f"✗ Failed to load from {pkg}")
        except Exception as e:
            print(f"✗ Error loading from {pkg}: {e}")


if __name__ == "__main__":
    main() 