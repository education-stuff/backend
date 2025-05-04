# SAT Questions API

A FastAPI application that serves SAT Math and Reading/Writing questions.

https://1600-questions-api-aza2bggzf9avesee.eastus-01.azurewebsites.net/

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Make sure your data files (`SAT_math.json` and `SAT_RW.json`) are in the `data/` directory.

3. Run the application:
```
python app.py
```

Or alternatively:
```
uvicorn app:app --reload
```

## API Endpoints

- `GET /`: Welcome page with list of available endpoints
- `GET /questions/math`: Get paginated math questions
- `GET /questions/math/{question_id}`: Get a specific math question
- `GET /questions/rw`: Get paginated reading/writing questions
- `GET /questions/rw/{question_id}`: Get a specific reading/writing question

## Query Parameters

For list endpoints (`/questions/math` and `/questions/rw`):
- `limit` (default: 10): Number of questions to return
- `offset` (default: 0): Starting position for pagination
- `page` (default: 1): Page number for pagination
- `difficulty` (optional): Filter by difficulty level (E, M, H)
- `skill` (optional): Filter questions by skill description (partial match)
- `primary_class` (optional): Filter questions by primary class description (partial match)

For detail endpoints (`/questions/math/{question_id}` and `/questions/rw/{question_id}`):
- `include_rationale` (default: true): Whether to include the rationale in the response

## Response Format

The API returns a consistent format for questions with only the relevant details:
- Basic question information (questionId, difficulty, skill_desc, etc.)
- Question content (stem, answerOptions, correct_answer)
- Rationale (when requested)

## Interactive Documentation

When the server is running, visit `/docs` for interactive API documentation. 
