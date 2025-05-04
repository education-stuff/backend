import json
from typing import List, Set

def get_unique_skill_descriptions(file_path: str) -> List[str]:
    try:
        # Read the JSON file
        with open(file_path, 'r') as f:
            questions = json.load(f)
        
        # Extract unique skill_desc values using a set
        unique_skills: Set[str] = {question.get('primary_class_cd_desc', '') for question in questions}
        
        # Convert set to sorted list for consistent output
        return sorted(unique_skills)
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'.")
        return []

# Example usage
file_path = 'data/SAT_RW.json'  # Replace with your JSON file path
skills = get_unique_skill_descriptions(file_path)

# Print the results
print("Unique skill descriptions:")
for skill in skills:
    print(skill)