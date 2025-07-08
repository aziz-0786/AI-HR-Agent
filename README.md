# AI-HR-Agent
AI HR Agent
An intelligent HR automation project designed to streamline and enhance various human resources tasks using Python and n8n, powered by Google's Gemini AI. This project demonstrates how to build a "free" (local n8n, free-tier AI) AI agent to automate repetitive HR functions.

Features Implemented So Far
Automated Resume Screening:

Reads a job description and scans a designated folder for multiple resume files (PDF, DOCX, TXT).

Utilizes the Gemini AI model to score each resume based on its relevance to the job description (0-100 score) and provides a brief justification.

Identifies and outputs the top 3 most relevant resumes.

Agentic AI for Personalized Communication (Conceptualized & Basic Workflow Built):

Demonstrates a simple agentic AI capability where the AI perceives candidate data (skills), reasons (decides on a relevant resource/advice), and takes an action (drafts a personalized email).

This feature lays the groundwork for sending tailored interview invitations or constructive rejection emails.

Project Structure
AI_HR_Agent/
├── python_scripts/             # Contains all Python scripts for AI logic and data processing
│   ├── hr_agent_resume_screener.py # Main script for resume parsing and AI scoring
│   └── llm_agent.py              # Generic script for interacting with LLMs (e.g., for email generation)
├── n8n_workflows/              # Contains exported n8n workflow JSON files
│   └── ai_hr_agent_workflow.json # The primary n8n workflow for orchestration
├── config/                     # Configuration files for Python scripts
│   └── config.json             # Stores paths for job description and resume folder (local setup)
├── sample_data/                # Sample data for testing the project
│   ├── job_description.txt     # Example job description file
│   └── sample_resumes/         # Folder containing sample resume files (PDF, DOCX, TXT)
│       ├── backend developer.pdf
│       └── Software Engineer.pdf
│       └── (and other sample resumes you add)
├── .gitignore                  # Specifies files/folders to be ignored by Git (e.g., API keys, virtual environments)
└── README.md                   # This project overview and guide

Setup and Installation
Prerequisites
Before you begin, ensure you have the following installed:

Python 3.x: Download and install from python.org.

n8n: Download and run n8n locally. You can find instructions on the n8n website.

Git: Install Git from git-scm.com.

Gemini API Key: Obtain a free API key from Google AI Studio. This is essential for the AI functionalities.

1. Clone the Repository
Open your terminal or command prompt and clone this GitHub repository:

git clone https://github.com/aziz-0786/AI-HR-Agent.git
cd AI_HR_Agent


2. Python Environment Setup
It's highly recommended to use a Python virtual environment to manage dependencies.

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

# Install required Python packages
pip install PyPDF2 python-docx requests

3. Configuration
Gemini API Key:

Crucial: Do NOT hardcode your API key directly into the scripts for security reasons, especially if you plan to share your code publicly.

Set your Gemini API Key as an environment variable in your system where you run the Python scripts.

Windows (PowerShell):

$env:GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"

(For permanent setup, search for "Edit the system environment variables" in Windows and add GEMINI_API_KEY with your key as a user variable.)

Linux/macOS (Bash/Zsh):

export GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"

(To make it permanent, add this line to your ~/.bashrc or ~/.zshrc file and then run source ~/.bashrc or source ~/.zshrc)

Your Python scripts (hr_agent_resume_screener.py and llm_agent.py) are configured to read this environment variable:

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

Local Paths (config/config.json):

Create a file named config.json inside the config/ folder.

Populate it with the absolute paths to your job description file and the folder containing your resume files. Remember to use double backslashes \\ for Windows paths in JSON.

{
  "job_description_path": "C:\\Users\\tangy\\OneDrive\\Documents\\AiHrAgent\\job_description.txt",
  "resume_folder_path": "C:\\Users\\tangy\\OneDrive\\Documents\\AiHrAgent\\sample_resumes\\"
}

4. Import n8n Workflow
Open your local n8n instance in your web browser.

Click on "New Workflow" (or go to "Workflows" and click the + button).

In the top right corner, click the "Options" menu (three dots or gear icon).

Select "Import from File".

Navigate to AI_HR_Agent/n8n_workflows/ and select ai_hr_agent_workflow.json.

How to Run
Running the Python Script Directly (for Resume Screening)
You can test the core resume screening logic directly from your terminal.

Activate your Python virtual environment (if not already active).

Navigate to the root of your AI_HR_Agent project.

Run the hr_agent_resume_screener.py script, providing the path to your config.json:

# On Windows PowerShell (recommended for simpler path handling)
python python_scripts/hr_agent_resume_screener.py config/config.json

# On Linux/macOS (or if PowerShell is not preferred on Windows)
# python python_scripts/hr_agent_resume_screener.py config/config.json

The script will print the JSON output of the top 3 resumes to your console.

Running the n8n Workflow
The n8n workflow orchestrates the Python script and integrates with other services (like email).

Ensure your Python virtual environment is activated and your GEMINI_API_KEY environment variable is set.

Open the AI HR Agent Workflow in your local n8n instance.

Click "Execute Workflow" on the Start node.

Observe the output of each node in the n8n interface. For the email functionality, check the inbox of the email address configured in the workflow's email nodes.

Future Enhancements
This project can be expanded significantly to cover more HR automation needs:

Automated Interview Scheduling: Integrate with calendar APIs (Google Calendar, Outlook) to find mutual free times and send invites.

Advanced Candidate Communication: Use the agentic AI to draft more complex, multi-stage communication sequences (e.g., follow-ups, pre-interview guides).

Onboarding Automation: Generate offer letters, contracts, and welcome packets.

HR Policy Q&A Chatbot: Provide instant answers to employee questions based on internal policy documents.

Performance Review Summaries: Assist managers in drafting performance evaluations.

Data Persistence: Store processed resume data and communication history in a database or spreadsheet (e.g., Google Sheets, SQLite).

License
This project is open-source and available under the MIT License.
