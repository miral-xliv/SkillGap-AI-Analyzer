from sentence_transformers import SentenceTransformer, util

# Optimized model for career context
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_ats_score(data, jd_input):
    """
    Calculates semantic similarity and returns both Match and Gap scores.
    """
    # Convert structured data back to text for embedding
    resume_text = str(data)
    
    embeddings = model.encode([resume_text, jd_input])
    # Compute Cosine Similarity
    cosine_sim = util.cos_sim(embeddings[0], embeddings[1])
    
    score = round(float(cosine_sim) * 100, 2)
    gap_score = round(100 - score, 2)
    
    # Returning a tuple solves the 'non-iterable' error
    return score, gap_score
