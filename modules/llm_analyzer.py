
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None


def analyze_resume_with_llm(
    resume_text,
    job_description,
    missing_skills
):
    if not client:
        return "Groq API key is missing."

    prompt = f"""
You are a professional AI resume analysis assistant.

Analyze the candidate's resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

SKILLS NOT FOUND:
{', '.join(missing_skills)}

Provide your response using these sections:

1. Resume Analysis
2. Relevant Experience
3. Missing Skills Explanation
4. Personalized Improvement Suggestions
5. Resume Writing Recommendations

Important instructions:
- Use clear, professional, simple language.
- Keep the analysis relevant to the provided resume and job description.
- Do not invent experience, qualifications, achievements, or skills.
- Do not assume the candidate has experience that is not mentioned.
- If you provide example resume bullet points, clearly label them as examples.
- Do not create hypothetical performance metrics as if they are real.
- Complete every sentence and section.
- Keep the response concise but useful.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_completion_tokens=2000
        )

        feedback = response.choices[0].message.content

        if not feedback or not feedback.strip():
            return "LLM analysis failed: Empty response received."

        finish_reason = response.choices[0].finish_reason

        if finish_reason == "length":
            feedback += (
                "\n\nNote: The AI response may be incomplete "
                "because the output token limit was reached."
            )

        return feedback

    except Exception as e:
        return f"LLM analysis failed: {e}"
