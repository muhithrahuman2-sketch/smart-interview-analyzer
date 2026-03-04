import streamlit as st
from gtts import gTTS
import os
import fitz  # PyMuPDF
import google.generativeai as genai
import time
import random

# 1. Gemini AI Config
API_KEY = "AIzaSyAontyPh3U60WXVQ98on8nYT-dH9L2f870" 
genai.configure(api_key=API_KEY)

# Using 'models/gemini-pro' to ensure no 404 error
ai_model = genai.GenerativeModel('models/gemini-pro')

# 2. Page Config
st.set_page_config(page_title="HireVibe AI", layout="wide")

# Session State Initialization
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.total_marks = 100
    st.session_state.current_q = ""
    st.session_state.ai_questions = []

# PDF Text Extractor
def extract_pdf_content(pdf_file):
    try:
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "".join([page.get_text() for page in doc])
    except: return ""

# UI Header
st.markdown("""
    <div style="background-color: #001f3f; padding: 15px; border-radius: 10px; text-align: center; border: 2px solid #00d4ff;">
        <h1 style="color: white; margin: 0;">🎓 HireVibe AI: Deep Analyst</h1>
        <p style="color: #00d4ff; margin: 5px;">Strictly analyzed from your uploaded Documents</p>
    </div>
    <br>
""", unsafe_allow_html=True)

app_mode = st.sidebar.selectbox("Choose Mode", ["Live Interview", "Exam Preparation"])
st.sidebar.metric("Current Score", f"{st.session_state.total_marks}/100")

col1, col2 = st.columns([1, 1], gap="large")

if app_mode == "Live Interview":
    with col1:
        st.header("📂 Step 1: Document Upload")
        role = st.selectbox("Target Role", ["Python Developer", "Java Developer", "Data Scientist"])
        res_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

        if res_file and st.button("Generate Interview from Document"):
            with st.spinner("AI is deep-scanning your document..."):
                text = extract_pdf_content(res_file)
                
                # Strict Prompt: Asking only from the document and making it random
                prompt = (f"Document Content: {text[:4000]}. Role: {role}. "
                          f"Task: Generate 5 unique technical interview questions based ONLY on this specific document. "
                          f"Ask about projects, specific skills, or experience mentioned. "
                          f"Return questions in English ONLY, separated by '|'.")
                
                try:
                    response = ai_model.generate_content(prompt)
                    # Splitting and Shuffling to ensure randomness
                    q_list = [q.strip() for q in response.text.split('|') if len(q) > 5]
                    random.shuffle(q_list) 
                    st.session_state.ai_questions = q_list
                    st.session_state.step = 0
                    st.success("✅ Deep Analysis Complete. Ready to start!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.button("Get Next Question") and st.session_state.ai_questions:
            if st.session_state.step < len(st.session_state.ai_questions):
                st.session_state.current_q = st.session_state.ai_questions[st.session_state.step]
                st.session_state.step += 1
                
                # Dynamic Voice generation
                tts = gTTS(text=st.session_state.current_q, lang='en')
                tts.save("q.mp3")
                st.audio("q.mp3", autoplay=True)
            else:
                st.balloons()
                st.success("Interview Finished!")

    with col2:
        if st.session_state.current_q:
            st.info(f"*Question:* {st.session_state.current_q}")
            user_ans = st.text_area("Type your answer here:", key=f"ans_{st.session_state.step}")
            if st.button("Submit Answer"):
                st.success("✅ Recorded!")

# --- EXAM MODE (Similar Strict Logic) ---
else:
    st.header("📝 Exam Pattern Prediction")
    exam_file = st.file_uploader("Upload Syllabus (PDF)", type=["pdf"])
    if exam_file and st.button("Predict Questions"):
        text = extract_pdf_content(exam_file)
        prompt = f"Based ONLY on this syllabus: {text[:4000]}, predict 10 important exam questions in English."
        response = ai_model.generate_content(prompt)
        st.markdown(response.text)