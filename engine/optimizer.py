import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_gap_analysis(data, jd_input, client):
    """Identifies missing skills like Vector Search and LLM frameworks."""
    prompt = f"Analyze gaps between this Resume data: {data} and Job Description: {jd_input}. List top 5 missing skills."
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return response.choices[0].message.content

def get_humanized_projects(data, client):
    """Level 9: STAR Interview Generator for project descriptions."""
    prompt = f"Rewrite these projects using the STAR method (Situation, Task, Action, Result): {data}"
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
    )
    return response.choices[0].message.content