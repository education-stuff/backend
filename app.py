from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from typing import List, Optional, Dict, Any
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SAT Questions API",
    description="API to retrieve SAT Math and Reading/Writing questions",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # modify this to 1600.lol when deployed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the data
DATA_DIR = "data"
STATS_DIR = "total_questions"

# Stats model
class StatsResponse(BaseModel):
    total_questions: int
    total_active: int
    total_inactive: int
    by_program: Dict[str, Any]
    by_main_category_overall: Dict[str, Any]
    by_subcategory_overall: Dict[str, Any]
    by_difficulty_overall: Dict[str, Any]
    by_score_band_overall: Dict[str, Any]

class DetailedStatsResponse(BaseModel):
    total_questions: int
    total_active: int
    total_inactive: int
    by_program: Dict[str, Any]
    by_main_category_overall: Dict[str, Any]
    by_subcategory_overall: Dict[str, Any]
    by_difficulty_overall: Dict[str, Any]
    by_score_band_overall: Dict[str, Any]
    detailed: Dict[str, Any]

try:
    with open(os.path.join(DATA_DIR, "SAT_math.json"), "r") as f:
        math_questions = json.load(f)
except FileNotFoundError:
    math_questions = []

try:
    with open(os.path.join(DATA_DIR, "SAT_RW.json"), "r") as f:
        rw_questions = json.load(f)
except FileNotFoundError:
    rw_questions = []

try:
    with open(os.path.join(DATA_DIR, "PSAT89_math.json"), "r") as f:
        psat89_math_questions = json.load(f)
except FileNotFoundError:
    psat89_math_questions = []

try:
    with open(os.path.join(DATA_DIR, "PSAT89_RW.json"), "r") as f:
        psat89_rw_questions = json.load(f)
except FileNotFoundError:
    psat89_rw_questions = []

class QuestionBasic(BaseModel):
    questionId: str
    difficulty: str
    skill_desc: str
    primary_class_cd_desc: str
    program: str
    question: str
    explanation: str
    answerOptions: List[Dict[str, str]]
    questionDetail: Optional[str] = None
    correct_answer: List[str]

class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    questions: List[QuestionBasic]

def extract_question_data(question: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "questionId": question.get("questionId", ""),
        "difficulty": question.get("difficulty", ""),
        "skill_desc": question.get("skill_desc", ""),
        "primary_class_cd_desc": question.get("primary_class_cd_desc", ""),
        "program": question.get("program", ""),
        "question": question.get("question", ""),
    }
    if "questionDetail" in question:
        result["questionDetail"] = question.get("questionDetail", "")
    result["answerOptions"] = question.get("options", [])
    result["correct_answer"] = question.get("correct_answer", [])
    result["explanation"] = question.get("explanation", "")
    return result

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the SAT Questions API",
        "endpoints": [
            "/questions/math",
            "/questions/rw",
            "/questions/psat89/math",
            "/questions/psat89/rw",
            "/questions/by-category/{category}",
            "/stats",
            "/stats/detailed",
        ],
    }

@app.get("/questions/by-category/{category}", response_model=PaginatedResponse)
def get_questions_by_category(
    category: str,
    program: str = Query(..., description="Program type (SAT or PSAT89)", enum=["SAT", "PSAT89"]),
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
):
    # Define valid categories
    rw_categories = [
        "Craft and Structure",
        "Expression of Ideas",
        "Information and Ideas",
        "Standard English Conventions",
    ]
    math_categories = [
        "Advanced Math",
        "Algebra",
        "Geometry and Trigonometry",
        "Problem-Solving and Data Analysis",
    ]
    valid_categories = rw_categories + math_categories

    if category not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid category. Valid categories are: {', '.join(valid_categories)}")

    # Validate category against program
    if program == "SAT":
        if category in rw_categories:
            questions = rw_questions
        elif category in math_categories:
            questions = math_questions
        else:
            questions = []
    elif program == "PSAT89":
        if category in rw_categories:
            questions = psat89_rw_questions
        elif category in math_categories:
            questions = psat89_math_questions
        else:
            questions = []
    else:
        raise HTTPException(status_code=400, detail="Invalid program. Use 'SAT' or 'PSAT89'.")

    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset

    # Filter by category
    filtered = [q for q in questions if q.get("primary_class_cd_desc") == category]

    # Apply additional filters
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]

    paginated = filtered[calculated_offset : calculated_offset + limit]
    result_questions = [extract_question_data(q) for q in paginated]

    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions,
    }

@app.get("/questions/math", response_model=PaginatedResponse)
def get_math_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description"),
):
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset

    filtered = math_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]

    paginated = filtered[calculated_offset : calculated_offset + limit]
    result_questions = [extract_question_data(q) for q in paginated]

    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions,
    }

@app.get("/questions/rw", response_model=PaginatedResponse)
def get_rw_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description"),
):
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset

    filtered = rw_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]

    paginated = filtered[calculated_offset : calculated_offset + limit]
    result_questions = [extract_question_data(q) for q in paginated]

    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions,
    }

@app.get("/questions/psat89/math", response_model=PaginatedResponse)
def get_psat89_math_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description"),
):
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset

    filtered = psat89_math_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]

    paginated = filtered[calculated_offset : calculated_offset + limit]
    result_questions = [extract_question_data(q) for q in paginated]

    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions,
    }

@app.get("/questions/psat89/rw", response_model=PaginatedResponse)
def get_psat89_rw_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description=" SLS: Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description"),
):
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset

    filtered = psat89_rw_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]

    paginated = filtered[calculated_offset : calculated_offset + limit]
    result_questions = [extract_question_data(q) for q in paginated]

    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions,
    }

@app.get("/stats", response_model=StatsResponse)
def get_stats():
    """
    Get statistics about the number of questions in the system.
    Returns total question count and breakdown by program, subject, and main category.
    """
    try:
        with open(os.path.join(STATS_DIR, "simplified_stats.json"), "r") as f:
            stats = json.load(f)
        return stats
    except FileNotFoundError:
        # If stats file doesn't exist, generate it on the fly
        from stats_generator import generate_stats_files
        generate_stats_files()
        
        with open(os.path.join(STATS_DIR, "simplified_stats.json"), "r") as f:
            stats = json.load(f)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/stats/detailed", response_model=DetailedStatsResponse)
def get_detailed_stats():
    """
    Get detailed statistics about the number of questions in the system.
    Returns total question count and complete breakdown by program, subject, main category, and subcategory.
    """
    try:
        with open(os.path.join(STATS_DIR, "question_stats.json"), "r") as f:
            stats = json.load(f)
        return stats
    except FileNotFoundError:
        # If stats file doesn't exist, generate it on the fly
        from stats_generator import generate_stats_files
        generate_stats_files()
        
        with open(os.path.join(STATS_DIR, "question_stats.json"), "r") as f:
            stats = json.load(f)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving detailed statistics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)