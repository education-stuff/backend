from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from typing import List, Optional, Dict, Any
import os

app = FastAPI(title="SAT Questions API", 
             description="API to retrieve SAT Math and Reading/Writing questions")

# Load the data
DATA_DIR = "data"

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

class QuestionBasic(BaseModel):
    questionId: str
    difficulty: str
    skill_desc: str
    primary_class_cd_desc: str
    program: str
    
    stem: str
    answerOptions: List[Dict[str, str]]
    type: str
    correct_answer: List[str]

class QuestionDetails(QuestionBasic):
    rationale: str
    
class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    questions: List[QuestionBasic]

def extract_question_data(question: Dict[str, Any], include_rationale: bool = False) -> Dict[str, Any]:
    # Basic question data
    result = {
        "questionId": question.get("questionId", ""),
        "difficulty": question.get("difficulty", ""),
        "skill_desc": question.get("skill_desc", ""),
        "primary_class_cd_desc": question.get("primary_class_cd_desc", ""),
        "program": question.get("program", ""),
    }
    
    details = question.get("details", {})
    
    result["stem"] = details.get("stem", "")
    
    result["answerOptions"] = details.get("answerOptions", [])
    
    result["type"] = details.get("type", "")
    
    result["correct_answer"] = details.get("correct_answer", [])
    
    if include_rationale:
        result["rationale"] = details.get("rationale", "")
    
    return result

@app.get("/")
def read_root():
    return {"message": "Welcome to the SAT Questions API",
            "endpoints": ["/questions/math", "/questions/rw", "/questions/math/{question_id}", "/questions/rw/{question_id}"]}

@app.get("/questions/math", response_model=PaginatedResponse)
def get_math_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description")
):
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset
    
    # Apply filters
    filtered = math_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]
    
    paginated = filtered[calculated_offset:calculated_offset + limit]
    
    result_questions = [extract_question_data(q) for q in paginated]
    
    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions
    }

@app.get("/questions/math/{question_id}")
def get_math_question(question_id: str, include_rationale: bool = Query(True, description="Include rationale in response")):
    for question in math_questions:
        if question.get("questionId") == question_id:
            return extract_question_data(question, include_rationale)
    raise HTTPException(status_code=404, detail="Question not found")

@app.get("/questions/rw", response_model=PaginatedResponse)
def get_rw_questions(
    limit: int = Query(10, description="Number of questions to return"),
    offset: int = Query(0, description="Starting position"),
    page: int = Query(1, description="Page number"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (E, M, H)"),
    skill: Optional[str] = Query(None, description="Filter by skill description"),
    primary_class: Optional[str] = Query(None, description="Filter by primary class description")
):
    # Calculate the correct offset based on page and limit
    calculated_offset = (page - 1) * limit
    if offset > 0:
        calculated_offset = offset
    
    # Apply filters
    filtered = rw_questions
    if difficulty:
        filtered = [q for q in filtered if q.get("difficulty") == difficulty]
    if skill:
        filtered = [q for q in filtered if skill.lower() in q.get("skill_desc", "").lower()]
    if primary_class:
        filtered = [q for q in filtered if primary_class.lower() in q.get("primary_class_cd_desc", "").lower()]
    
    # Paginate
    paginated = filtered[calculated_offset:calculated_offset + limit]
    
    result_questions = [extract_question_data(q) for q in paginated]
    
    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "questions": result_questions
    }

@app.get("/questions/rw/{question_id}")
def get_rw_question(question_id: str, include_rationale: bool = Query(True, description="Include rationale in response")):
    for question in rw_questions:
        if question.get("questionId") == question_id:
            return extract_question_data(question, include_rationale)
    raise HTTPException(status_code=404, detail="Question not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 