import streamlit as st
import requests
import json
import PyPDF2
import time
import os

class JobApplicationGenerator:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.resume_path = "Rahul_2025_AI.pdf"  # Hardcoded resume path
    
    def extract_text_from_pdf(self) -> str:
        """Extract text content from the predefined resume PDF"""
        with open(self.resume_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return "\n".join([page.extract_text() for page in reader.pages])

    def query_ollama(self, prompt: str) -> str:
        """Send prompt to Ollama using llama3.2:latest"""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": "llama3.2:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_ctx": 4096
                    }
                },
                timeout=300
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def extract_job_details(self, jd_text: str) -> dict:
        """Extract position and company from JD"""
        prompt = f"""
        Extract the following from this job description in JSON format:
        {{
            "position": "job position title",
            "company": "company name (or empty if not specified)"
        }}
        
        Job Description:
        {jd_text}
        """
        result = self.query_ollama(prompt)
        try:
            return json.loads(result)
        except:
            return {"position": "", "company": ""}

    def generate_application(self, jd_text: str) -> str:
        """Generate complete job application"""
        # Get resume text
        resume_text = self.extract_text_from_pdf()
        
        # Extract position and company from JD
        job_details = self.extract_job_details(jd_text)
        position = job_details.get("position", "Generative AI Engineer")
        company = job_details.get("company", "")
        
        # Generate tailored application
        prompt = f"""
        Generate a job application email for a Generative AI/ML role using:
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {jd_text}
        
        GUIDELINES:
        1. Subject: "Application for {position}" + (" at {company}" if company else "")
        2. Open with strong technical introduction
        3. Highlight 3 most relevant projects matching the JD
        4. Focus on:
           - LLM fine-tuning/development
           - Technical architecture
           - Production deployments
           - Performance metrics
        5. Mention specific technologies (PyTorch, LangChain, etc.)
        6. Close professionally
        7. Length: 250-350 words
        8. Signature with contacts from resume
        
        FORMAT:
        Subject: [subject]
        
        Dear Hiring Manager,
        
        [Technical introduction]
        
        [Relevant project 1 with metrics]
        
        [Relevant project 2 with metrics]
        
        [Why excited about this opportunity]
        
        Best regards,
        Rahul Puri
        [contacts]
        """
        return self.query_ollama(prompt)

# Streamlit UI
st.set_page_config(page_title="AI Job Application Generator", layout="wide")

st.title("🤖 AI-Powered Job Application Generator")
st.markdown("""
Automatically generates tailored applications for:
- Generative AI Engineer
- Machine Learning Engineer
- LLM Developer
- Python Developer (AI/ML)
""")

# Check if resume exists
if not os.path.exists("Rahul_2025_AI.pdf"):
    st.error("Resume file 'Rahul_2025_AI.pdf' not found in current directory")
    st.stop()

# Main interface
job_description = st.text_area("Paste Job Description", height=300,
                             placeholder="Paste the complete job description here...")

generate_btn = st.button("Generate Application", type="primary")

if generate_btn and job_description.strip():
    with st.spinner("Analyzing JD and generating application..."):
        start_time = time.time()
        
        # Initialize generator
        generator = JobApplicationGenerator()
        
        # Generate application
        application = generator.generate_application(job_description)
        
        # Display results
        st.subheader("Generated Application")
        st.code(application, language="text")
        
        # Download button
        st.download_button(
            label="Download Application",
            data=application,
            file_name="ai_job_application.txt",
            mime="text/plain"
        )
        
        st.success(f"Application generated in {time.time()-start_time:.2f} seconds")

elif generate_btn:
    st.warning("Please paste a job description")

# Instructions
st.sidebar.markdown("""
### How It Works:
1. Paste the full job description
2. Click "Generate Application"
3. Review and download the result

### Current Configuration:
- Model: `llama3.2:latest`
- Resume: `Rahul_2025_AI.pdf`
- Auto-detects position/company

### Tips:
- Include full JD for best results
- Technical descriptions yield better matches
- Edit generated content as needed
""")