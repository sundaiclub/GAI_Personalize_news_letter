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
from extract_links import extract_links_from_pdf, filter_article_links
import tempfile

load_dotenv()  # take environment variables from .env.

# Initialize LLM
@st.cache_resource
def get_llm(use_mock=True, model="gpt-3.5-turbo"):
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
        return LLMFactory.create_llm("chatgpt", api_key=api_key, model=model)

# Function to process content through LLM
def summarize_content(llm, content, user_profile):
    # prompt = f"""
    # Given the following user profile:
    # {user_profile}
    
    # Please provide a concise summary of the following content, focusing on aspects that would be most relevant to the user profile:
    
    # {content}
    
    # Please strictly limit the summary to 2-3 paragraphs. If there is no content that is directly relevant to the user profile and their business strategy, please indicate this in your response and do not provide a summary.
    # """

    prompt = f"""
    Please provide a concise summary of the following content, focusing on aspects that would be most relevant to the user profile:
    
    {content}
    
    Please strictly limit the summary to 2-3 paragraphs.
    """
    
    response = llm.generate_response(prompt, max_tokens=300, temperature=0.7)
    return response.text


def synthesize_summaries(llm, user_profile, summaries):
    with open('prompt.txt', 'r') as f:
        prompt = f.read()

    prompt = prompt.replace('{profile}', user_profile)

    summaries = [f"## Article {idx+1}\nURL: {url}\n{summary}" for idx, (url, summary) in enumerate(summaries)]
    prompt = prompt.replace('{articles}', '\n'.join(summaries))

    response = llm.generate_response(prompt, max_tokens=5000, temperature=0.4)
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
# use_real_llm = st.checkbox("Use real ChatGPT (requires API key)", value=False)
use_real_llm = True

# --- Processing Section ---
st.header("Step 2: Generate Your Document")

if st.button("Generate Document"):
    # Check if both inputs are provided
    if pdf_file is None:
        st.error("Please upload a PDF resource file.")
    elif not user_profile.strip():
        st.error("Please enter your user profile text.")
    else:
        pdf_info = f"PDF file '{pdf_file.name}' received."

        try:
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Initialize LLM
            status_text.text("Initializing LLM...")
            llm = get_llm(use_mock=not use_real_llm)  # Use mock by default
            progress_bar.progress(10)
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                tmp_path = tmp_file.name
            
            # Extract links from PDF using the improved extractor
            status_text.text("Extracting links from PDF...")
            raw_links = extract_links_from_pdf(tmp_path)
            links = filter_article_links(raw_links)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            progress_bar.progress(20)

            # Process each link
            total_links = len(links)

            summaries = []

            if total_links == 0:
                status_text.text("No valid links found in the PDF...")
            else:

                for idx, link in enumerate(links, 1):
                    print(link)
                    status_text.text(f"Processing link {idx} of {total_links}...")
                    progress = 20 + (60 * idx // total_links)  # Progress from 20% to 80%
                    progress_bar.progress(progress)
                    
                    try:
                        # Clean and validate the URL
                        clean_url = urllib.parse.unquote(link).strip()
                        
                        # Extract content from the link
                        title, content = extract_main_content(clean_url)
                        
                        if content:  # TODO: report on links for which we did not extract the content
                            # Summarize content using LLM

                            print(len(content))
                            summary = summarize_content(llm, content, user_profile)

                            print('SUMMARY: ', summary)

                            summaries.append((clean_url,summary))
                        
                    except Exception as e:
                        continue


            # Final document preparation
            status_text.text("Preparing final document...")
            progress_bar.progress(90)

            synthesis_llm = get_llm(use_mock=not use_real_llm, model="gpt-4o")

            markdown_output = synthesize_summaries(synthesis_llm, user_profile, summaries)


            print('MARKDOWN OUTPUT: ', markdown_output)

            

            doc = generate_word_doc_from_markdown(markdown_output)

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

# Close the main container div
st.markdown("</div>", unsafe_allow_html=True)
