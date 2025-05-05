import json
import os
import re
from collections import defaultdict

# Define the paths
DATA_DIR = "data"
OUTPUT_DIR = "total_questions"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_data():
    """
    Analyze all data files and generate statistics about question counts
    by program, category, and subcategory.
    """
    # Initialize stats dictionary
    stats = {
        "total_questions": 0,
        "by_program": {},
        "by_main_category": defaultdict(int),
        "by_subcategory": defaultdict(int),
        "detailed": {}
    }
    
    # Dynamically find all JSON files in the data directory
    files = {}
    file_pattern = re.compile(r"^(\w+)_(math|RW)\.json$", re.IGNORECASE)
    
    print(f"Looking for question files in {DATA_DIR}:")
    for filename in os.listdir(DATA_DIR):
        print(f"  Checking file: {filename}")
        match = file_pattern.match(filename)
        if match and filename.endswith('.json'):
            program = match.group(1)
            subject = match.group(2)
            # Normalize subject case
            if subject.lower() == "math":
                subject = "math"
            else:
                subject = "RW"
            
            # Use the program_subject as key
            program_subject = f"{program}_{subject}"
            files[program_subject] = os.path.join(DATA_DIR, filename)
            print(f"  ✓ Found question file: {filename} -> Program: {program}, Subject: {subject}")
    
    if not files:
        print(f"Warning: No question files found in {DATA_DIR}")
    else:
        print(f"Found {len(files)} question files to process")
    
    # Process each file
    for program_type, file_path in files.items():
        try:
            with open(file_path, "r") as f:
                questions = json.load(f)
                
            program, subject = program_type.split("_")
            print(f"Processing {file_path}: {len(questions)} questions")
            
            # Initialize program stats if not exists
            if program not in stats["by_program"]:
                stats["by_program"][program] = {
                    "total": 0,
                    "subjects": {}
                }
            
            # Initialize subject stats if not exists
            if subject not in stats["by_program"][program]["subjects"]:
                stats["by_program"][program]["subjects"][subject] = {
                    "total": 0,
                    "categories": defaultdict(int),
                    "subcategories": defaultdict(int)
                }
            
            # Count questions
            num_questions = len(questions)
            stats["total_questions"] += num_questions
            stats["by_program"][program]["total"] += num_questions
            stats["by_program"][program]["subjects"][subject]["total"] += num_questions
            
            # Initialize detailed stats for the program if not exists
            if program not in stats["detailed"]:
                stats["detailed"][program] = {}
            
            # Initialize detailed stats for the subject if not exists
            if subject not in stats["detailed"][program]:
                stats["detailed"][program][subject] = {
                    "main_categories": {},
                    "subcategories": {}
                }
            
            # Count by category and subcategory
            category_counts = defaultdict(int)
            subcategory_counts = defaultdict(int)
            
            for question in questions:
                main_category = question.get("primary_class_cd_desc", "Unknown")
                subcategory = question.get("skill_desc", "Unknown")
                
                # Update main category counts
                category_counts[main_category] += 1
                stats["by_main_category"][main_category] += 1
                stats["by_program"][program]["subjects"][subject]["categories"][main_category] += 1
                
                # Update subcategory counts
                subcategory_counts[subcategory] += 1
                stats["by_subcategory"][subcategory] += 1
                stats["by_program"][program]["subjects"][subject]["subcategories"][subcategory] += 1
            
            # Store detailed counts
            stats["detailed"][program][subject]["main_categories"] = dict(category_counts)
            stats["detailed"][program][subject]["subcategories"] = dict(subcategory_counts)
            
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Convert defaultdicts to regular dicts for JSON serialization
    stats["by_main_category"] = dict(stats["by_main_category"])
    stats["by_subcategory"] = dict(stats["by_subcategory"])
    
    for program in stats["by_program"]:
        for subject in stats["by_program"][program]["subjects"]:
            stats["by_program"][program]["subjects"][subject]["categories"] = dict(
                stats["by_program"][program]["subjects"][subject]["categories"]
            )
            stats["by_program"][program]["subjects"][subject]["subcategories"] = dict(
                stats["by_program"][program]["subjects"][subject]["subcategories"]
            )
    
    return stats

def generate_stats_files():
    """
    Generate and save statistics files.
    """
    stats = analyze_data()
    
    # Save complete stats
    with open(os.path.join(OUTPUT_DIR, "question_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    
    # Save simplified stats for quick access
    simplified_stats = {
        "total_questions": stats["total_questions"],
        "by_program": {
            program: {
                "total": data["total"],
                "by_subject": {
                    subject: data["subjects"][subject]["total"]
                    for subject in data["subjects"]
                }
            }
            for program, data in stats["by_program"].items()
        },
        "by_main_category": stats["by_main_category"]
    }
    
    with open(os.path.join(OUTPUT_DIR, "simplified_stats.json"), "w") as f:
        json.dump(simplified_stats, f, indent=2)
    
    print(f"Statistics generated successfully in {OUTPUT_DIR}.")

if __name__ == "__main__":
    generate_stats_files() 