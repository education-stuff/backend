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
        "by_difficulty": {
            "E": defaultdict(int),  # Easy
            "M": defaultdict(int),  # Medium
            "H": defaultdict(int),  # Hard
            "total": {"E": 0, "M": 0, "H": 0}
        },
        "by_score_band": {
            "1": defaultdict(int),
            "2": defaultdict(int),
            "3": defaultdict(int),
            "4": defaultdict(int),
            "5": defaultdict(int),
            "6": defaultdict(int),
            "7": defaultdict(int),
            "total": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
        },
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
                    "subcategories": defaultdict(int),
                    "by_difficulty": {
                        "E": defaultdict(int),
                        "M": defaultdict(int),
                        "H": defaultdict(int),
                        "total": {"E": 0, "M": 0, "H": 0}
                    },
                    "by_score_band": {
                        "1": defaultdict(int),
                        "2": defaultdict(int),
                        "3": defaultdict(int),
                        "4": defaultdict(int),
                        "5": defaultdict(int),
                        "6": defaultdict(int),
                        "7": defaultdict(int),
                        "total": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
                    }
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
                    "subcategories": {},
                    "difficulties": {},
                    "score_bands": {}
                }
            
            # Count by category and subcategory
            category_counts = defaultdict(int)
            subcategory_counts = defaultdict(int)
            
            # Track counts by difficulty and score band
            difficulty_counts = {
                "E": defaultdict(lambda: defaultdict(int)),
                "M": defaultdict(lambda: defaultdict(int)),
                "H": defaultdict(lambda: defaultdict(int)),
                "total": {"E": 0, "M": 0, "H": 0}
            }
            
            score_band_counts = {
                "1": defaultdict(lambda: defaultdict(int)),
                "2": defaultdict(lambda: defaultdict(int)),
                "3": defaultdict(lambda: defaultdict(int)),
                "4": defaultdict(lambda: defaultdict(int)),
                "5": defaultdict(lambda: defaultdict(int)),
                "6": defaultdict(lambda: defaultdict(int)),
                "7": defaultdict(lambda: defaultdict(int)),
                "total": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0}
            }
            
            for question in questions:
                main_category = question.get("primary_class_cd_desc", "Unknown")
                subcategory = question.get("skill_desc", "Unknown")
                difficulty = question.get("difficulty", "Unknown")
                score_band = str(question.get("score_band_range_cd", 0))
                
                # Skip invalid score band values
                if score_band == "0" or not score_band.isdigit() or int(score_band) < 1 or int(score_band) > 7:
                    score_band = None
                
                # Update main category counts
                category_counts[main_category] += 1
                stats["by_main_category"][main_category] += 1
                stats["by_program"][program]["subjects"][subject]["categories"][main_category] += 1
                
                # Update subcategory counts
                subcategory_counts[subcategory] += 1
                stats["by_subcategory"][subcategory] += 1
                stats["by_program"][program]["subjects"][subject]["subcategories"][subcategory] += 1
                
                # Update difficulty counts
                if difficulty in ["E", "M", "H"]:
                    # Global difficulty counts
                    stats["by_difficulty"]["total"][difficulty] += 1
                    stats["by_difficulty"][difficulty][main_category] += 1
                    
                    # Program-subject difficulty counts
                    stats["by_program"][program]["subjects"][subject]["by_difficulty"]["total"][difficulty] += 1
                    stats["by_program"][program]["subjects"][subject]["by_difficulty"][difficulty][main_category] += 1
                    
                    # Detailed tracking
                    difficulty_counts["total"][difficulty] += 1
                    difficulty_counts[difficulty][main_category][subcategory] += 1
                
                # Update score band counts
                if score_band:
                    # Global score band counts
                    stats["by_score_band"]["total"][score_band] += 1
                    stats["by_score_band"][score_band][main_category] += 1
                    
                    # Program-subject score band counts
                    stats["by_program"][program]["subjects"][subject]["by_score_band"]["total"][score_band] += 1
                    stats["by_program"][program]["subjects"][subject]["by_score_band"][score_band][main_category] += 1
                    
                    # Detailed tracking
                    score_band_counts["total"][score_band] += 1
                    score_band_counts[score_band][main_category][subcategory] += 1
            
            # Store detailed counts
            stats["detailed"][program][subject]["main_categories"] = dict(category_counts)
            stats["detailed"][program][subject]["subcategories"] = dict(subcategory_counts)
            
            # Store detailed difficulty counts
            difficulty_details = {}
            for diff in ["E", "M", "H"]:
                main_cat_details = {}
                for main_cat, subcat_dict in difficulty_counts[diff].items():
                    if main_cat != "total":
                        main_cat_details[main_cat] = dict(subcat_dict)
                difficulty_details[diff] = main_cat_details
            difficulty_details["total"] = difficulty_counts["total"]
            stats["detailed"][program][subject]["difficulties"] = difficulty_details
            
            # Store detailed score band counts
            score_band_details = {}
            for band in ["1", "2", "3", "4", "5", "6", "7"]:
                main_cat_details = {}
                for main_cat, subcat_dict in score_band_counts[band].items():
                    if main_cat != "total":
                        main_cat_details[main_cat] = dict(subcat_dict)
                score_band_details[band] = main_cat_details
            score_band_details["total"] = score_band_counts["total"]
            stats["detailed"][program][subject]["score_bands"] = score_band_details
            
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found.")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    # Convert defaultdicts to regular dicts for JSON serialization
    stats["by_main_category"] = dict(stats["by_main_category"])
    stats["by_subcategory"] = dict(stats["by_subcategory"])
    
    for diff in ["E", "M", "H"]:
        stats["by_difficulty"][diff] = dict(stats["by_difficulty"][diff])
    
    for band in ["1", "2", "3", "4", "5", "6", "7"]:
        stats["by_score_band"][band] = dict(stats["by_score_band"][band])
    
    for program in stats["by_program"]:
        for subject in stats["by_program"][program]["subjects"]:
            stats["by_program"][program]["subjects"][subject]["categories"] = dict(
                stats["by_program"][program]["subjects"][subject]["categories"]
            )
            stats["by_program"][program]["subjects"][subject]["subcategories"] = dict(
                stats["by_program"][program]["subjects"][subject]["subcategories"]
            )
            
            for diff in ["E", "M", "H"]:
                stats["by_program"][program]["subjects"][subject]["by_difficulty"][diff] = dict(
                    stats["by_program"][program]["subjects"][subject]["by_difficulty"][diff]
                )
            
            for band in ["1", "2", "3", "4", "5", "6", "7"]:
                stats["by_program"][program]["subjects"][subject]["by_score_band"][band] = dict(
                    stats["by_program"][program]["subjects"][subject]["by_score_band"][band]
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
        "by_main_category": stats["by_main_category"],
        "by_difficulty": {
            "total": stats["by_difficulty"]["total"],
            "categories": {
                "E": stats["by_difficulty"]["E"],
                "M": stats["by_difficulty"]["M"],
                "H": stats["by_difficulty"]["H"]
            }
        },
        "by_score_band": {
            "total": stats["by_score_band"]["total"],
            "categories": {
                "1": stats["by_score_band"]["1"],
                "2": stats["by_score_band"]["2"],
                "3": stats["by_score_band"]["3"],
                "4": stats["by_score_band"]["4"],
                "5": stats["by_score_band"]["5"],
                "6": stats["by_score_band"]["6"],
                "7": stats["by_score_band"]["7"]
            }
        }
    }
    
    with open(os.path.join(OUTPUT_DIR, "simplified_stats.json"), "w") as f:
        json.dump(simplified_stats, f, indent=2)
    
    print(f"Statistics generated successfully in {OUTPUT_DIR}.")

if __name__ == "__main__":
    generate_stats_files() 