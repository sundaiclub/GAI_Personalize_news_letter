import streamlit as st
from docx import Document
import io

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

# Close the main container div
st.markdown("</div>", unsafe_allow_html=True)
