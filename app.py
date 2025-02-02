import streamlit as st
from docx import Document
import io
from dotenv import load_dotenv
import os
import PyPDF2
import re
from extract_content import extract_main_content
from llm_interface import LLMFactory
import urllib.parse

load_dotenv()  # take environment variables from .env.

# Initialize LLM
@st.cache_resource
def get_llm(use_mock=True):
    """
    Get an LLM instance, either mock or real ChatGPT.
    
    Args:
        use_mock (bool): If True, returns a mock LLM for testing.
                        If False, returns real ChatGPT (requires API key).
    """
    if use_mock:
        return LLMFactory.create_llm("mock")
    else:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        return LLMFactory.create_llm("chatgpt", api_key=api_key)

# Function to extract links from PDF
def extract_links_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    links = set()
    
    # Regular expression for finding URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    
    for page in pdf_reader.pages:
        text = page.extract_text()
        found_links = re.findall(url_pattern, text)
        links.update(found_links)
    
    return list(links)

# Function to process content through LLM
def summarize_content(llm, content, user_profile):
    prompt = f"""
    Given the following user profile:
    {user_profile}
    
    Please provide a concise summary of the following content, focusing on aspects that would be most relevant to the user profile:
    
    {content}
    
    Provide the summary in 2-3 paragraphs.
    """
    
    response = llm.generate_response(prompt, max_tokens=300, temperature=0.7)
    return response.text

from GenerateWordDocument import generate_word_doc_from_markdown

# --- Custom CSS for a cool, neat design ---
st.markdown(
    """
    <style>
    /* Set a background gradient */
    .stApp {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
    }
    /* Style the main container */
    .main-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* Header style */
    .header {
        font-size: 3rem;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-bottom: 1rem;
    }
    /* Subheader style */
    .subheader {
        font-size: 1.25rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App Title and Description
st.markdown('<div class="header">Personalized GAI News-Letter</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subheader">Upload a PDF resource and paste your user profile to generate a custom Word document.</div>',
    unsafe_allow_html=True,
)

# --- Input Section ---
st.header("Step 1: Provide Your Inputs")

# PDF file uploader for resources
pdf_file = st.file_uploader("Upload your PDF resource", type=["pdf"])

# Text area for the user profile
user_profile = st.text_area("Enter your user profile text", height=200)

# Add toggle for using real/mock LLM
use_real_llm = st.checkbox("Use real ChatGPT (requires API key)", value=False)

# --- Processing Section ---
st.header("Step 2: Generate Your Document")

if st.button("Generate Document"):
    # Check if both inputs are provided
    if pdf_file is None:
        st.error("Please upload a PDF resource file.")
    elif not user_profile.strip():
        st.error("Please enter your user profile text.")
    else:
<<<<<<< Updated upstream
        pdf_info = f"PDF file '{pdf_file.name}' received."

        # todo: replace the markdown output with LLM call output
        markdown_output = """
            # Header 1
            This is the first paragraph of the document.
            
            ## Header 2
            This is another paragraph that follows a header.
            
            - Item 1 in a list
            - Item 2 in a list
            
            Another paragraph here.
        """
        doc = generate_word_doc_from_markdown(markdown_output)

        # Save the document to a BytesIO stream
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)

        # Provide a download button for the generated DOCX file
        st.success("Document generated successfully!")
        st.download_button(
            label="Download Generated Document",
            data=doc_io,
            file_name="generated_document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
=======
        try:
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize LLM
            status_text.text("Initializing LLM...")
            llm = get_llm(use_mock=not use_real_llm)  # Use mock by default
            progress_bar.progress(10)
            
            # Extract links from PDF
            status_text.text("Extracting links from PDF...")
            links = extract_links_from_pdf(pdf_file)
            progress_bar.progress(20)
            
            # Create document
            doc = Document()
            doc.add_heading("Personalized Content Summary", level=0)
            doc.add_heading("User Profile", level=1)
            doc.add_paragraph(user_profile)
            
            # Process each link
            total_links = len(links)
            for idx, link in enumerate(links, 1):
                status_text.text(f"Processing link {idx} of {total_links}...")
                progress = 20 + (60 * idx // total_links)  # Progress from 20% to 80%
                progress_bar.progress(progress)
                
                try:
                    # Clean and validate the URL
                    clean_url = urllib.parse.unquote(link).strip()
                    
                    # Extract content from the link
                    title, content = extract_main_content(clean_url)
                    
                    if content:
                        # Summarize content using LLM
                        summary = summarize_content(llm, content, user_profile)
                        
                        # Add to document
                        doc.add_heading(f"Source {idx}: {title or clean_url}", level=2)
                        doc.add_paragraph(f"URL: {clean_url}")
                        doc.add_paragraph(summary)
                        doc.add_paragraph()  # Add spacing
                    
                except Exception as e:
                    doc.add_heading(f"Source {idx}: {clean_url}", level=2)
                    doc.add_paragraph(f"Error processing this link: {str(e)}")
                    continue
            
            # Final document preparation
            status_text.text("Preparing final document...")
            progress_bar.progress(90)
            
            # Save the document to a BytesIO stream
            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("Document generation complete!")
            
            # Provide download button
            st.success("Document generated successfully!")
            st.download_button(
                label="Download Generated Document",
                data=doc_io,
                file_name="personalized_summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        finally:
            # Clear progress indicators
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
>>>>>>> Stashed changes

# Close the main container div
st.markdown("</div>", unsafe_allow_html=True)
