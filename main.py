import streamlit as st
from openai import OpenAI
import PyPDF2
from dotenv import load_dotenv
import io
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Streamlit page
st.set_page_config(page_title="AI Resume Assistant", layout="centered", page_icon="✨")
st.title("AI Resume Assistant")
st.markdown("Select your mode and get specialized resume assistance")

# Clear mode selection at the top
mode = st.radio(
    "Select what you need:",
    ("Resume Improvement Advisor", "ATS Checker & Interview Prep"),
    horizontal=True,
)

st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

# Mode-specific inputs
if mode == "Resume Improvement Advisor":
    st.subheader("Resume Improvement Settings")
    job_role = st.text_input("Target job role (for tailored suggestions)")
    experience_level = st.selectbox(
        "Your career level",
        ("Entry Level", "Mid Career", "Senior", "Executive"),
        help="Select the level that matches your experience",
    )
else:
    st.subheader("ATS Checker Settings")
    job_description = st.text_area(
        "Paste the job description (for accurate ATS matching)",
        height=150,
        help="Optional but recommended for better analysis",
    )

analyze = st.button("Analyze My Resume", type="primary")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")


def analyze_with_gpt(resume_text, prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a professional career advisor specializing in resume optimization.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


if analyze and uploaded_file:
    with st.spinner(f"Analyzing your resume for {mode}..."):
        resume_text = extract_text_from_file(uploaded_file)

        if mode == "Resume Improvement Advisor":
            # Focused resume improvement prompt
            prompt = f"""Analyze this resume for a {experience_level} candidate applying for {job_role or 'a position'}:
            
            RESUME CONTENT:
            {resume_text}
            
            Provide CONCISE, ACTIONABLE feedback in this EXACT structure:
            
            ### Strengths
            - [3-5 key strengths]
            
            ### Immediate Improvements Needed
            - [3-5 critical fixes]
            
            ### Content Suggestions
            - [Specific section rewrites]
            
            ### ATS Optimization
            - [Missing keywords for this role]
            
            ### Final Rating
            [1-5 stars] with brief explanation
            
            Keep all suggestions practical and implementable."""

            feedback = analyze_with_gpt(resume_text, prompt)

            st.subheader("Your Resume Improvement Plan")
            st.markdown(feedback)

            # Download improved version
            if st.button("Generate Enhanced Version"):
                enhance_prompt = f"""Rewrite this resume for a {experience_level} {job_role or 'candidate'}:
                {resume_text}
                - Keep original information but enhance wording
                - Optimize for ATS scanning
                - Use professional resume formatting
                - Include only the rewritten resume content"""

                enhanced_resume = analyze_with_gpt(resume_text, enhance_prompt)
                st.download_button(
                    "Download Enhanced Resume",
                    enhanced_resume,
                    file_name="enhanced_resume.txt",
                )

        else:  # ATS Checker & Interview Prep mode
            # Focused ATS analysis prompt
            prompt = f"""Analyze this resume for ATS compatibility:
            
            RESUME CONTENT:
            {resume_text}
            
            JOB DESCRIPTION:
            {job_description or 'Not provided'}
            
            Provide analysis in this EXACT structure:
            
            ### ATS Compatibility Score
            [X/100] - Brief explanation
            
            ### Keyword Matching
            - [Present keywords]
            - [Missing keywords]
            
            ### Technical Skills Assessment
            - [Skills verification]
            
            ### Recommended Interview Questions
            1. [Technical question]
            2. [Behavioral question]
            3. [Role-specific question]
            
            Keep analysis factual and data-oriented."""

            analysis = analyze_with_gpt(resume_text, prompt)

            st.subheader("ATS Analysis Report")
            st.markdown(analysis)

            # Additional interview questions
            if st.checkbox("Generate more interview questions"):
                questions_prompt = f"""Generate 5 technical and 5 behavioral questions for:
                RESUME: {resume_text}
                JOB DESC: {job_description or 'Not provided'}
                Format as numbered lists with explanations."""

                questions = analyze_with_gpt(resume_text, questions_prompt)
                st.markdown("### Extended Interview Preparation")
                st.markdown(questions)

# Footer
st.markdown("---")
st.caption("Note: AI-generated suggestions should be reviewed by a human professional.")
