# AI Resume Analyzer

An AI-powered resume analysis application that compares a candidate's resume with a job description using Machine Learning and LLM-based analysis.

## Features

- Upload resume in PDF format
- Extract resume text automatically
- Compare resume with job description
- Calculate overall resume match score
- Identify matched and missing skills
- Calculate skill match percentage
- Generate optional AI-powered resume feedback
- Provide personalized improvement suggestions
- Generate downloadable PDF analysis reports
- Professional Streamlit-based dashboard

## Technologies Used

- Python
- Streamlit
- Scikit-learn
- Pandas
- NumPy
- PyMuPDF
- Groq API
- ReportLab
- HTML/CSS

## How It Works

1. Upload a resume in PDF format.
2. Paste the target job description.
3. The application extracts the resume text.
4. Machine Learning calculates the resume-job similarity.
5. Required skills are compared with the resume.
6. Missing skills are identified.
7. Optional LLM analysis provides personalized feedback.
8. A PDF report can be downloaded.

## Project Structure

```text
AI_Resume_Analyzer/
│
├── assets/
│   └── style.css
│
├── modules/
│   ├── __init__.py
│   ├── llm_analyzer.py
│   ├── matcher.py
│   ├── report_generator.py
│   └── resume_parser.py
│
├── .gitignore
├── app.py
├── requirements.txt
└── README.md

## Environment Variable

Create a `.env` file for local development:

```text
GROQ_API_KEY=your_groq_api_key
```

## Run Locally
```bash
streamlit run app.py
```
## Deployment

The application is deployed using Streamlit Community Cloud.

The `GROQ_API_KEY` is configured securely using Streamlit Secrets.
## Future Improvements

- More advanced semantic resume-job matching
- Support for multiple resume formats
- Job recommendation system
- Resume section scoring
- ATS optimization analysis
- Resume improvement suggestions
