import json
import os
import requests
import sys
from docx import Document
from PyPDF2 import PdfReader

# --- Configuration ---
# IMPORTANT: Replace "YOUR_GEMINI_API_KEY" with your actual Gemini API Key.
# You can get one for free from Google AI Studio: https://aistudio.google.com/
# Ensure your usage stays within the free tier limits.
GEMINI_API_KEY = "AIzaSyA0DMEtVd-01K09wKkHF7vlFCz-NYLAsu4"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Supported resume file extensions
SUPPORTED_EXTENSIONS = ('.pdf', '.docx', '.txt')

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    Args:
        pdf_path (str): The path to the PDF file.
    Returns:
        str: The extracted text, or None if an error occurs.
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}", file=sys.stderr)
        return None

def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file.
    Args:
        docx_path (str): The path to the DOCX file.
    Returns:
        str: The extracted text, or None if an error occurs.
    """
    try:
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX {docx_path}: {e}", file=sys.stderr)
        return None

def get_resume_score(job_description, resume_text):
    """
    Uses the Gemini API to score a resume against a job description.
    Args:
        job_description (str): The text of the job description.
        resume_text (str): The text of the resume.
    Returns:
        tuple: A tuple containing the score (int, 0-100) and justification (str).
               Returns (0, "Error message") if an error occurs.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        error_msg = "Error: GEMINI_API_KEY is not set. Please replace 'YOUR_GEMINI_API_KEY' with your actual API key."
        print(error_msg, file=sys.stderr)
        return 0, error_msg

    prompt = f"""
    You are an expert HR agent. Your task is to evaluate a resume against a job description and provide a relevance score from 0 to 100, and a brief justification for the score.
    Focus on skills, experience, and qualifications directly relevant to the job description.

    Job Description:
    {job_description}

    Resume:
    {resume_text}

    Please provide your response in JSON format with the following keys:
    "score": (integer from 0 to 100)
    "justification": (string explaining the score, max 2-3 sentences)
    """

    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "score": {"type": "INTEGER"},
                    "justification": {"type": "STRING"}
                },
                "propertyOrdering": ["score", "justification"]
            }
        }
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            try:
                parsed_response = json.loads(response_text)
                score = parsed_response.get("score", 0)
                justification = parsed_response.get("justification", "No justification provided.")
                return score, justification
            except json.JSONDecodeError:
                error_msg = f"Error decoding JSON from LLM response: {response_text}"
                print(error_msg, file=sys.stderr)
                return 0, error_msg
        else:
            error_msg = f"Unexpected LLM response structure: {result}"
            print(error_msg, file=sys.stderr)
            return 0, error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"API call failed: {e}"
        print(error_msg, file=sys.stderr)
        return 0, error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred during scoring: {e}"
        print(error_msg, file=sys.stderr)
        return 0, error_msg

def find_resume_files_in_folder(resume_folder_path):
    """
    Scans a folder for supported resume file types.
    Args:
        resume_folder_path (str): The path to the folder containing resumes.
    Returns:
        list: A list of full paths to supported resume files found.
    """
    found_resume_paths = []
    if not os.path.isdir(resume_folder_path):
        print(f"Error: Resume folder not found or is not a directory: {resume_folder_path}", file=sys.stderr)
        return []

    for filename in os.listdir(resume_folder_path):
        file_path = os.path.join(resume_folder_path, filename)
        if os.path.isfile(file_path) and file_path.lower().endswith(SUPPORTED_EXTENSIONS):
            found_resume_paths.append(file_path)
    return found_resume_paths

def process_and_score_resumes(job_description_path, resume_folder_path):
    """
    Main function to process a job description and all resumes in a given folder.
    It reads the job description, finds resume files, scores each resume,
    sorts them, and returns the top 3.

    Args:
        job_description_path (str): The file path to the job description (e.g., .txt).
        resume_folder_path (str): The path to the folder containing resume files.
    Returns:
        dict: A dictionary containing the top 3 resumes with their scores and justifications.
              Includes an "error" key if something goes wrong.
    """
    job_description = ""
    try:
        if not os.path.isfile(job_description_path):
            error_msg = f"Error: Job description file not found: {job_description_path}"
            print(error_msg, file=sys.stderr)
            return {"error": error_msg}
        with open(job_description_path, 'r', encoding='utf-8') as f:
            job_description = f.read()
    except Exception as e:
        error_msg = f"Error reading job description file {job_description_path}: {e}"
        print(error_msg, file=sys.stderr)
        return {"error": error_msg}

    if not job_description.strip():
        error_msg = "Job description is empty or could not be read. Please provide valid content."
        print(error_msg, file=sys.stderr)
        return {"error": error_msg}

    # Find resume files in the specified folder
    resume_files_found = find_resume_files_in_folder(resume_folder_path)
    if not resume_files_found:
        warning_msg = f"No supported resume files found in folder: {resume_folder_path}"
        print(warning_msg, file=sys.stderr)
        return {"top_resumes": [], "warning": warning_msg}

    resume_results = []
    for resume_path in resume_files_found:
        resume_text = None
        # Determine file type and extract text accordingly
        if resume_path.lower().endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_path)
        elif resume_path.lower().endswith('.docx'):
            resume_text = extract_text_from_docx(resume_path) # Fixed: changed docx_path to resume_path
        elif resume_path.lower().endswith('.txt'):
            try:
                with open(resume_path, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
            except Exception as e:
                print(f"Error reading text file {resume_path}: {e}", file=sys.stderr)
                resume_text = None
        else:
            # This case should ideally not be hit if find_resume_files_in_folder is correct
            print(f"WARNING: Unsupported file type for {resume_path}. Skipping.", file=sys.stderr)
            continue

        if resume_text:
            score, justification = get_resume_score(job_description, resume_text)
            resume_results.append({
                "filename": os.path.basename(resume_path),
                "score": score,
                "justification": justification,
            })
        else:
            print(f"WARNING: Could not extract text from resume file: {resume_path}. Skipping.", file=sys.stderr)

    # Sort resumes by score in descending order
    sorted_resumes = sorted(resume_results, key=lambda x: x["score"], reverse=True)

    # Get the top 3 resumes
    top_3_resumes = sorted_resumes[:3]

    return {"top_resumes": top_3_resumes}

if __name__ == "__main__":
    # This block now expects ONE command-line argument: the path to a JSON config file
    if len(sys.argv) < 2:
        print("Usage: python hr_agent_resume_screener.py <config_file_path>", file=sys.stderr)
        print("Example (Windows PowerShell):", file=sys.stderr)
        print("python hr_agent_resume_screener.py \"C:\\Users\\tangy\\OneDrive\\Documents\\AiHrAgent\\config.json\"", file=sys.stderr)
        print("NOTE: The config.json file should contain 'job_description_path' and 'resume_folder_path'.", file=sys.stderr)
        sys.exit(1)

    config_file_path = sys.argv[1]

    try:
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError(f"Config file not found: {config_file_path}")

        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        job_description_file = config.get("job_description_path")
        resume_folder = config.get("resume_folder_path")

        if not job_description_file:
            raise ValueError("'job_description_path' missing in config.json")
        if not resume_folder:
            raise ValueError("'resume_folder_path' missing in config.json")

        output_data = process_and_score_resumes(job_description_file, resume_folder)
        print(json.dumps(output_data, indent=2)) # Print the final JSON output to stdout

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}", file=sys.stderr)
        sys.exit(1)

#run
#python hr_agent_resume_screener.py "C:\Users\tangy\OneDrive\Documents\AiHrAgent\config.json" 