import json
import os
import re
from collections import defaultdict

# Define the paths
DATA_DIR = "data"
OUTPUT_DIR = "total_questions"
LOOKUP_FILE = "lookup.json"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to convert defaultdict to dict for JSON serialization
def defaultdict_to_dict(d):
    if isinstance(d, defaultdict):
        d = {k: defaultdict_to_dict(v) for k, v in d.items()}
    elif isinstance(d, dict):
        d = {k: defaultdict_to_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        d = [defaultdict_to_dict(x) for x in d]
    return d

def analyze_data(data_dir=DATA_DIR, lookup_file=LOOKUP_FILE):
    """
    Analyze all data files and generate statistics about question counts
    by program, category, and subcategory.
    """
    stats = {
        "total_questions": 0,
        "total_active": 0,
        "total_inactive": 0,
        "by_program": defaultdict(lambda: {
            "total": 0, "active": 0, "inactive": 0,
            "subjects": defaultdict(lambda: {
                "total": 0, "active": 0, "inactive": 0,
                "categories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
                "subcategories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
                "by_difficulty": defaultdict(lambda: { # difficulty_key
                    "categories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # main_cat -> counts
                    "total_counts": {"active": 0, "inactive": 0, "total": 0} 
                }),
                "by_score_band": defaultdict(lambda: { # score_band_key
                    "categories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # main_cat -> counts
                    "total_counts": {"active": 0, "inactive": 0, "total": 0}
                })
            })
        }),
        "by_main_category_overall": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
        "by_subcategory_overall": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
        "by_difficulty_overall": defaultdict(lambda: { # difficulty_key
            "categories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # main_cat -> counts
            "total_counts": {"active": 0, "inactive": 0, "total": 0}
        }),
        "by_score_band_overall": defaultdict(lambda: { # score_band_key
            "categories": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # main_cat -> counts
            "total_counts": {"active": 0, "inactive": 0, "total": 0}
        }),
        "detailed": defaultdict(lambda: defaultdict(lambda: { # program -> subject
            "main_categories_breakdown": defaultdict(lambda: { # main_category_name
                "active": 0, "inactive": 0, "total": 0,
                "by_difficulty_status": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # diff_key -> counts
                "by_score_band_status": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}), # band_key -> counts
                "subcategories_breakdown": defaultdict(lambda: { # sub_category_name
                    "active": 0, "inactive": 0, "total": 0,
                    "by_difficulty_status": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
                    "by_score_band_status": defaultdict(lambda: {"active": 0, "inactive": 0, "total": 0}),
                    "by_difficulty_scoreband_status": defaultdict( # difficulty_key
                        lambda: defaultdict( # score_band_key
                            lambda: {"active": 0, "inactive": 0}
                        )
                    )
                })
            })
        }))
    }

    math_live_items = set()
    rw_live_items = set()
    try:
        with open(lookup_file, 'r') as f:
            lookup_data = json.load(f)
            math_live_items = set(lookup_data.get("mathLiveItems", []))
            rw_live_items = set(lookup_data.get("readingLiveItems", []))
        print(f"Successfully loaded lookup data. Math live items: {len(math_live_items)}, RW live items: {len(rw_live_items)}")
    except FileNotFoundError:
        print(f"Warning: {lookup_file} not found. All items will be marked as inactive.")
    except json.JSONDecodeError:
        print(f"Warning: Error decoding {lookup_file}. All items will be marked as inactive.")

    file_pattern = re.compile(r"^(SAT|PSAT89|PSAT10NMSQT)_(math|RW)\.json$", re.IGNORECASE)
    found_files = []
    print(f"Looking for question files in {data_dir}:")

    for filename in os.listdir(data_dir):
        match = file_pattern.match(filename)
        if match:
            found_files.append(filename)
            program_name = match.group(1).upper()
            subject_name_raw = match.group(2) 
            subject_name = "RW" if subject_name_raw.upper() == "RW" else "MATH" # Normalize subject_name

            print(f"Processing file: {filename} for Program: {program_name}, Subject: {subject_name}")

            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    questions = json.load(f)
            except FileNotFoundError:
                print(f"Error: File {filepath} not found during processing loop.")
                continue
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {filepath}.")
                continue

            program_level_stats = stats["by_program"][program_name]
            subject_level_stats = program_level_stats["subjects"][subject_name]
            detailed_ps_stats = stats["detailed"][program_name][subject_name]

            questions_processed_for_diagnostic = 0 # Initialize counter for diagnostic prints per file
            for question in questions:
                stats["total_questions"] += 1
                program_level_stats["total"] += 1
                subject_level_stats["total"] += 1
                
                main_category = question.get("primary_class_cd_desc", "Unknown")
                subcategory = question.get("skill_desc", "Unknown")
                difficulty_key = question.get("difficulty", "Unknown")
                if difficulty_key not in ["E", "M", "H"]: # Normalize difficulty
                    difficulty_key = "Unknown"
                
                score_band_key = str(question.get("score_band_range_cd", "Unknown"))
                if not score_band_key.isdigit() or not (1 <= int(score_band_key) <= 7):
                    score_band_key = "Unknown"

                external_id = question.get("external_id")

                # Diagnostic prints for SAT and PSAT89
                # if program_name in ["SAT", "PSAT89"] and questions_processed_for_diagnostic < 3: # Print for first 3 questions
                #     print(f"  [DIAGNOSTIC] File: {filename}, Program: {program_name}, Subject: {subject_name}")
                #     print(f"    Q_ext_id: '{external_id}', MainCat: '{main_category}', Difficulty: '{difficulty_key}'")
                #     if external_id:
                #         target_set_name = "N/A"
                #         target_set = None
                #         is_in_set = False
                #         if subject_name == "MATH":
                #             target_set_name = "math_live_items"
                #             target_set = math_live_items
                #             if target_set is not None:
                #                 is_in_set = external_id in target_set
                #         elif subject_name == "RW":
                #             target_set_name = "rw_live_items"
                #             target_set = rw_live_items
                #             if target_set is not None:
                #                 is_in_set = external_id in target_set
                #         
                #         if target_set is not None:
                #             print(f"    Checking ID '{external_id}' in '{target_set_name}' (size {len(target_set)}): Found = {is_in_set}")
                #         else: # Should not happen with current subject_name normalization
                #             print(f"    Could not determine target_set for subject_name: {subject_name}")
                #     else:
                #         print(f"    External_id is None or empty.")
                
                # questions_processed_for_diagnostic += 1 # Increment after potential print

                is_active = False
                if external_id:
                    if subject_name == "MATH" and external_id in math_live_items:
                        is_active = True
                    elif subject_name == "RW" and external_id in rw_live_items:
                        is_active = True
                
                status_key = "active" if is_active else "inactive"

                # Increment active/inactive totals
                if is_active:
                    stats["total_active"] += 1
                    program_level_stats["active"] +=1
                    subject_level_stats["active"] += 1
                else:
                    stats["total_inactive"] += 1
                    program_level_stats["inactive"] +=1
                    subject_level_stats["inactive"] += 1

                # Overall aggregations
                stats["by_main_category_overall"][main_category][status_key] += 1
                stats["by_main_category_overall"][main_category]["total"] += 1
                stats["by_subcategory_overall"][subcategory][status_key] += 1
                stats["by_subcategory_overall"][subcategory]["total"] += 1
                
                stats["by_difficulty_overall"][difficulty_key]["total_counts"][status_key] += 1
                stats["by_difficulty_overall"][difficulty_key]["total_counts"]["total"] += 1
                stats["by_difficulty_overall"][difficulty_key]["categories"][main_category][status_key] += 1
                stats["by_difficulty_overall"][difficulty_key]["categories"][main_category]["total"] += 1

                stats["by_score_band_overall"][score_band_key]["total_counts"][status_key] += 1
                stats["by_score_band_overall"][score_band_key]["total_counts"]["total"] += 1
                stats["by_score_band_overall"][score_band_key]["categories"][main_category][status_key] += 1
                stats["by_score_band_overall"][score_band_key]["categories"][main_category]["total"] += 1

                # Program/Subject specific aggregations
                subject_level_stats["categories"][main_category][status_key] += 1
                subject_level_stats["categories"][main_category]["total"] += 1
                subject_level_stats["subcategories"][subcategory][status_key] += 1
                subject_level_stats["subcategories"][subcategory]["total"] += 1

                subject_level_stats["by_difficulty"][difficulty_key]["total_counts"][status_key] += 1
                subject_level_stats["by_difficulty"][difficulty_key]["total_counts"]["total"] += 1
                subject_level_stats["by_difficulty"][difficulty_key]["categories"][main_category][status_key] += 1
                subject_level_stats["by_difficulty"][difficulty_key]["categories"][main_category]["total"] += 1
                
                subject_level_stats["by_score_band"][score_band_key]["total_counts"][status_key] += 1
                subject_level_stats["by_score_band"][score_band_key]["total_counts"]["total"] += 1
                subject_level_stats["by_score_band"][score_band_key]["categories"][main_category][status_key] += 1
                subject_level_stats["by_score_band"][score_band_key]["categories"][main_category]["total"] += 1

                # Detailed stats
                main_cat_detailed = detailed_ps_stats["main_categories_breakdown"][main_category]
                main_cat_detailed[status_key] += 1
                main_cat_detailed["total"] += 1
                main_cat_detailed["by_difficulty_status"][difficulty_key][status_key] += 1
                main_cat_detailed["by_difficulty_status"][difficulty_key]["total"] += 1
                main_cat_detailed["by_score_band_status"][score_band_key][status_key] += 1
                main_cat_detailed["by_score_band_status"][score_band_key]["total"] += 1
                
                sub_cat_detailed = main_cat_detailed["subcategories_breakdown"][subcategory]
                sub_cat_detailed[status_key] += 1
                sub_cat_detailed["total"] += 1
                sub_cat_detailed["by_difficulty_status"][difficulty_key][status_key] += 1
                sub_cat_detailed["by_difficulty_status"][difficulty_key]["total"] += 1
                sub_cat_detailed["by_score_band_status"][score_band_key][status_key] += 1
                sub_cat_detailed["by_score_band_status"][score_band_key]["total"] += 1
                sub_cat_detailed["by_difficulty_scoreband_status"][difficulty_key][score_band_key][status_key] += 1
        else:
            if filename.endswith(".json") and "_" in filename:
                 print(f"Skipping file (does not match program/subject pattern): {filename}")

    if not found_files:
        print(f"No data files found matching the pattern (SAT|PSAT89|PSAT10NMSQT)_(math|RW).json in the '{data_dir}' directory.")
        print("Please ensure your data files are named correctly and are in the 'data' subdirectory.")

    return defaultdict_to_dict(stats) # Convert all defaultdicts to dicts

def generate_stats_files(output_dir=OUTPUT_DIR):
    stats_data = analyze_data()
    
    os.makedirs(output_dir, exist_ok=True)
    
    detailed_stats_path = os.path.join(output_dir, "question_stats.json")
    with open(detailed_stats_path, 'w') as f:
        json.dump(stats_data, f, indent=4)
    print(f"Detailed stats saved to {detailed_stats_path}")

    simplified_stats = {
        "total_questions": stats_data.get("total_questions", 0),
        "total_active": stats_data.get("total_active", 0),
        "total_inactive": stats_data.get("total_inactive", 0),
        "by_program": {},
        "by_main_category_overall": stats_data.get("by_main_category_overall", {}),
        "by_subcategory_overall": stats_data.get("by_subcategory_overall", {}),
        "by_difficulty_overall": {},
        "by_score_band_overall": {}
    }

    for prog_name, prog_data in stats_data.get("by_program", {}).items():
        simplified_stats["by_program"][prog_name] = {
            "total": prog_data.get("total", 0),
            "active": prog_data.get("active", 0),
            "inactive": prog_data.get("inactive", 0),
            "subjects": {}
        }
        for subj_name, subj_data in prog_data.get("subjects", {}).items():
            simplified_stats["by_program"][prog_name]["subjects"][subj_name] = {
                "total": subj_data.get("total", 0),
                "active": subj_data.get("active", 0),
                "inactive": subj_data.get("inactive", 0),
                "categories": subj_data.get("categories", {}),
                "subcategories": subj_data.get("subcategories", {}),
                "by_difficulty": {}, # Simplified view for difficulty per program/subject
                "by_score_band": {}  # Simplified view for score band per program/subject
            }
            # Populate simplified by_difficulty for program/subject
            for diff_key, diff_detail in subj_data.get("by_difficulty", {}).items():
                simplified_stats["by_program"][prog_name]["subjects"][subj_name]["by_difficulty"][diff_key] = {
                    "active": diff_detail.get("total_counts", {}).get("active", 0),
                    "inactive": diff_detail.get("total_counts", {}).get("inactive", 0),
                    "total": diff_detail.get("total_counts", {}).get("total", 0),
                    "categories": diff_detail.get("categories", {})
                }
            # Populate simplified by_score_band for program/subject
            for band_key, band_detail in subj_data.get("by_score_band", {}).items():
                simplified_stats["by_program"][prog_name]["subjects"][subj_name]["by_score_band"][band_key] = {
                    "active": band_detail.get("total_counts", {}).get("active", 0),
                    "inactive": band_detail.get("total_counts", {}).get("inactive", 0),
                    "total": band_detail.get("total_counts", {}).get("total", 0),
                    "categories": band_detail.get("categories", {})
                }
    
    for diff_key, diff_data in stats_data.get("by_difficulty_overall", {}).items():
        simplified_stats["by_difficulty_overall"][diff_key] = {
            "active": diff_data.get("total_counts", {}).get("active",0),
            "inactive": diff_data.get("total_counts", {}).get("inactive",0),
            "total": diff_data.get("total_counts", {}).get("total",0),
            "categories": diff_data.get("categories", {})
        }

    for band_key, band_data in stats_data.get("by_score_band_overall", {}).items():
        simplified_stats["by_score_band_overall"][band_key] = {
            "active": band_data.get("total_counts", {}).get("active",0),
            "inactive": band_data.get("total_counts", {}).get("inactive",0),
            "total": band_data.get("total_counts", {}).get("total",0),
            "categories": band_data.get("categories", {})
        }

    simplified_stats_path = os.path.join(output_dir, "simplified_stats.json")
    with open(simplified_stats_path, 'w') as f:
        json.dump(simplified_stats, f, indent=4)
    print(f"Simplified stats saved to {simplified_stats_path}")
    
    return detailed_stats_path, simplified_stats_path

if __name__ == "__main__":
    generate_stats_files() 