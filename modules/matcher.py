from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match(resume_text, job_description):
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    return round(similarity[0][0] * 100, 2)

def extract_skills(text):
    skills_list = [
        "python", "java", "sql", "machine learning",
        "deep learning", "nlp", "pandas", "numpy",
        "scikit-learn", "streamlit", "flask",
        "tensorflow", "pytorch", "matplotlib",
        "data analysis", "feature engineering",
        "data cleaning", "random forest"
    ]

    text = text.lower()

    return [
        skill for skill in skills_list
        if skill in text
    ]


def compare_skills(resume_text, job_description):
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    return matched, missing