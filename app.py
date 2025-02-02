import streamlit as st
from docx import Document
import io

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
        # Placeholder: Read the PDF file if needed (logic TBD)
        # For now, we simply note that the PDF was uploaded.
        pdf_info = f"PDF file '{pdf_file.name}' received."

        # --- Document Generation using python-docx ---
        doc = Document()
        doc.add_heading("Custom Generated Document", level=0)

        # Insert PDF info (this is just an example placeholder)
        doc.add_paragraph(pdf_info)

        # Insert the user profile text
        doc.add_heading("User Profile", level=1)
        doc.add_paragraph(user_profile)

        # Additional processing logic can be added here (TBD)
        doc.add_paragraph("\n[TBD: Additional logic and content processing based on the inputs...]")

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
