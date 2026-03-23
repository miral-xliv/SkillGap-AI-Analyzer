import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_career_advice(user_query, gap_context):
    """
    Level 10: Career Advisor Agent.
    Strictly provides concise, necessary answers based on identified gaps.
    """
    system_instruction = f"""
    You are a professional AI Career Coach. 
    CONTEXT: The candidate has these technical gaps: {gap_context}.
    STRICT RULES:
    1. Be concise and direct. Do not write long introductions.
    2. Only provide 'necessary' answers—actions, libraries, or concepts to bridge the gap.
    3. If the user says 'hi', acknowledge briefly and ask for their specific career question.
    4. Focus on the Python stack (FastAPI, SBERT, FAISS) and LLMs.
    """
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_query}
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3, # Lower temperature makes the AI more direct and less creative
    )
    return response.choices[0].message.content