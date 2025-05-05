# SAT/PSAT Questions API

A FastAPI application that serves SAT and PSAT Math and Reading/Writing questions.

The live deployment (may not always be up-to-date with the `main` branch) can be found at: 
https://1600-questions-api-aza2bggzf9avesee.eastus-01.azurewebsites.net/

## Features

- **Retrieve Questions**: Access SAT and PSAT questions via a RESTful API.
- **Filtering**: Filter questions by difficulty, skill, and main category.
- **Pagination**: Efficiently navigate through large sets of questions.
- **Statistics**: Get detailed counts of questions by program, subject, main category, and subcategory.
- **Dynamic Data Loading**: Automatically loads question data from JSON files following the naming convention `PROGRAM_(math|RW).json` in the `data/` directory.
- **Automated Stats Update**: A GitHub Actions workflow automatically regenerates and commits question statistics daily.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Ensure your question data files (e.g., `SAT_math.json`, `PSAT89_RW.json`, `PSAT10NMSQT_math.json`) are placed in the `data/` directory. The `stats_generator.py` script will automatically detect files matching the `PROGRAM_(math|RW).json` pattern.

3.  (Optional) Generate initial statistics:
    ```bash
    python stats_generator.py
    ```
    This will create/update the JSON files in the `total_questions/` directory. This step is optional because the API endpoints will generate the files on the fly if they don't exist.

4.  Run the application:
    ```bash
    uvicorn app:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

-   `GET /`: Welcome page with a list of available endpoints.
-   `GET /questions/math`: Get paginated SAT math questions.
-   `GET /questions/rw`: Get paginated SAT Reading/Writing questions.
-   `GET /questions/psat89/math`: Get paginated PSAT 8/9 math questions.
-   `GET /questions/psat89/rw`: Get paginated PSAT 8/9 Reading/Writing questions.
-   `GET /questions/by-category/{category}`: Get questions by a specific main category (e.g., "Algebra", "Craft and Structure"). Requires the `program` query parameter (e.g., `?program=SAT`).
-   `GET /stats`: Get simplified statistics about the question bank (total questions, counts by program, subject, and main category). Reads from `total_questions/simplified_stats.json`.
-   `GET /stats/detailed`: Get detailed statistics including subcategory counts. Reads from `total_questions/question_stats.json`.

*Note: Currently, there isn't a dedicated endpoint for PSAT10NMSQT, but questions from this program (if data files exist) are included in the `/stats` and `/stats/detailed` endpoints.*

## Query Parameters (for list endpoints)

-   `limit` (default: 10): Number of questions per page.
-   `offset` (default: 0): Starting index for results (alternative to `page`).
-   `page` (default: 1): Page number for pagination (overrides `offset` if provided).
-   `difficulty` (optional): Filter by difficulty (E, M, H).
-   `skill` (optional): Filter by skill description (case-insensitive partial match).
-   `primary_class` (optional, **not** for `/by-category`): Filter by main category description (case-insensitive partial match).
-   `program` (**required** for `/by-category`): Filter by program ("SAT" or "PSAT89").

## Statistics Generation (`stats_generator.py`)

The `stats_generator.py` script performs the following:

1.  Scans the `data/` directory for files matching the `PROGRAM_(math|RW).json` pattern.
2.  Loads questions from each detected file.
3.  Analyzes the questions to count totals by program, subject, main category (`primary_class_cd_desc`), and subcategory (`skill_desc`).
4.  Saves the results into two files in the `total_questions/` directory:
    -   `simplified_stats.json`: Contains high-level counts.
    -   `question_stats.json`: Contains detailed counts including subcategories.

## Automation (GitHub Actions)

A GitHub Actions workflow defined in `.github/workflows/update_stats.yml`:

-   Runs the `stats_generator.py` script daily at midnight UTC.
-   Can also be triggered manually via the GitHub Actions UI.
-   If the script generates changes in the statistics files (`total_questions/*.json`), the workflow automatically commits and pushes these changes to the repository.

## Interactive Documentation

When the server is running, visit `/docs` (e.g., `http://127.0.0.1:8000/docs`) for interactive API documentation provided by Swagger UI. 
