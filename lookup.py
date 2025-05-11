"""
Script to interact with the College Board SAT Question Bank API endpoint:
/questionbank/lookup

Purpose:
Fetches essential metadata and lookup tables used across the Question Bank application.
This endpoint is crucial for understanding the meaning of various IDs and codes used in other API calls
and for populating filter options in the UI.
It requires no payload.

Expected Response (Confirmed by examining lookup.txt):
- A JSON object containing a `lookupData` key.
- Inside `lookupData`, key mappings are provided:
    - `assessment`: Maps `id` (e.g., "99") to assessment `text` (e.g., "SAT"). Corresponds to `asmtEventId` in `/get-questions`.
    - `test`: Maps `id` (e.g., "1") to subject `text` (e.g., "Reading and Writing"). Corresponds to `test` in `/get-questions`.
    - `domain`: Nested object containing "R&W" and "Math" keys.
        - Each subject contains a list of domains, mapping `primaryClassCd` (e.g., "H") to `text` (e.g., "Algebra")
          and listing associated `skill` texts.
    - `stateOfferings`: List of states with `stateCd` (e.g., "CA") and `name` (e.g., "California"). Used by `/state-standards`.
    - Likely contains mappings for difficulty codes, score bands, etc., although not fully shown in the initial 200 lines read.
- The full structure is saved to 'lookup.json' in the script's root directory.

Relationships with other endpoints:
- Defines the meaning of IDs used in `/get-questions` (`asmtEventId`, `test`, `domain` codes).
- Provides the valid `stateCd` values required by `/state-standards`.
- Acts as the central source for populating UI filters and displaying descriptive names.
"""
import requests
import json
import os

# Define the URL
url = "https://qbank-api.collegeboard.org/msreportingquestionbank-prod/questionbank/lookup"

# Define the headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    # "Content-Type": "application/json", # Not typically needed for GET requests without a body
    "Origin": "https://satsuitequestionbank.collegeboard.org",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://satsuitequestionbank.collegeboard.org/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers"
}

# Define the output file path in the root directory
output_filename = "lookup.json"
# The output path will be in the same directory as the script, or the current working directory if run directly
output_path = output_filename


try:
    # Make the GET request (no data payload needed for this endpoint based on the cURL)
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

    # Print the status code
    print(f"Status Code: {response.status_code}")

    # Print the response JSON content to console
    print("Response JSON (Console):")
    response_json = response.json() # Decode JSON once
    print(json.dumps(response_json, indent=4))

    # Save the response JSON content to a file
    print(f"Saving response to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(response_json, f, indent=4, ensure_ascii=False) # Use json.dump
    print("Response saved successfully.")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status Code: {e.response.status_code}")
        print(f"Response Text: {e.response.text}")