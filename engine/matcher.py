from sentence_transformers import SentenceTransformer, util
import streamlit as st

@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

def calculate_ats_score(data, jd_input):
    resume_text = str(data)
    embeddings = model.encode([resume_text, jd_input])
    cosine_sim = util.cos_sim(embeddings[0], embeddings[1])
    score = round(float(cosine_sim) * 100, 2)
    gap_score = round(100 - score, 2)
    return score, gap_score
