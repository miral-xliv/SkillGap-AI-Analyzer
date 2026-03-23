def generate_assets(resume_json, jd_text, client):
    # Business-Standard Cover Letter Prompt
    cl_prompt = f"""
    Write a formal, corporate-style cover letter for a job application.
    Candidate Data: {resume_json}
    Job Role: {jd_text}
    
    Strict Instructions:
    - Include Placeholder for Date and Recruiter Name.
    - Paragraph 1: Mention the exact role and how my background in AI/ML aligns with it.
    - Paragraph 2: Highlight specific projects (e.g., YouTube QA Chatbot) and tech stack (FastAPI, SBERT).
    - Paragraph 3: Explain the 'Value Add' - what I bring to the team.
    - Closing: Professional sign-off with contact details.
    - TONE: Confident, professional, and results-oriented.
    - LIMIT: 200 words.
    """
    
    cl_res = client.chat.completions.create(
        messages=[{"role": "user", "content": cl_prompt}], 
        model="llama-3.3-70b-versatile"
    )
    
    # Interview questions logic
    int_res = client.chat.completions.create(
        messages=[{"role": "user", "content": "Generate 3 technical questions based on JD and Resume."}], 
        model="llama-3.3-70b-versatile"
    )
    
    return cl_res.choices[0].message.content, int_res.choices[0].message.content
