import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ---------------------------------------------------------
# STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .legal-title {
            text-align: center;
            padding: 10px;
        }

        .legal-title h1 {
            font-size: 3rem;
            margin-bottom: 0;
        }

        .legal-title p {
            font-size: 1.2rem;
            color: #777;
        }

        .document-box {
            border: 1px solid #cccccc;
            border-radius: 10px;
            padding: 25px;
            background-color: #f8f8f8;
            white-space: pre-wrap;
            line-height: 1.7;
            font-family: Georgia, serif;
        }

        .disclaimer {
            padding: 12px;
            border-radius: 8px;
            background-color: #fff3cd;
            border: 1px solid #ffe69c;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "content" not in st.session_state:
    st.session_state.content = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "terms" not in st.session_state:
    st.session_state.terms = ""


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="legal-title">
        <h1>⚖️ LegalEase</h1>
        <p>AI-Powered Legal Document Generator</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="disclaimer">
    <strong>Disclaimer:</strong>
    LegalEase generates AI-assisted legal drafts for
    informational and editing purposes. It is not a
    substitute for advice from a qualified legal professional.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("📋 Document Details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Service Agreement",
            "General Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":
        document_type = st.text_input(
            "Custom Document Type",
            placeholder="Example: Consulting Agreement",
        )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example:\n"
            "Jane Doe (Employee)\n"
            "ABC Corporation (Employer)"
        ),
        height=120,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Example:\n"
            "Salary paid monthly; "
            "Confidentiality applies; "
            "Either party may terminate "
            "with 15 days notice"
        ),
        height=180,
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        placeholder="Tamil Nadu, India",
    )

    language = st.selectbox(
        "Language",
        [
            "English",
            "Tamil",
            "Hindi",
            "Arabic",
        ],
    )

    generate_button = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# GENERATE DOCUMENT
# ---------------------------------------------------------

if generate_button:

    if not document_type.strip():
        st.error("Please enter a document type.")

    elif not parties.strip():
        st.error("Please enter the parties involved.")

    elif not terms.strip():
        st.error("Please enter the terms and conditions.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": effective_date.isoformat(),
            "jurisdiction": jurisdiction,
            "language": language,
        }

        try:

            with st.spinner("🤖 Generating your legal document..."):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

            if response.status_code != 200:

                try:
                    error_data = response.json()
                    detail = error_data.get(
                        "detail",
                        "Unknown backend error.",
                    )
                except Exception:
                    detail = response.text

                st.error(
                    f"Backend error ({response.status_code}): "
                    f"{detail}"
                )

            else:

                result = response.json()

                st.session_state.content = result.get(
                    "content",
                    "",
                )

                st.session_state.document_type = (
                    document_type
                )

                st.session_state.terms = terms

                st.success(
                    "✅ Document generated successfully!"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "❌ Cannot connect to the FastAPI backend."
            )

            st.info(
                "Make sure FastAPI is running on "
                f"{BACKEND_URL}"
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ The request took too long. "
                "Please try again."
            )

        except Exception as error:

            st.error(
                f"Unexpected error: {error}"
            )


# ---------------------------------------------------------
# DOCUMENT PREVIEW
# ---------------------------------------------------------

if st.session_state.content:

    st.divider()

    st.header("📄 Generated Document")

    edited_content = st.text_area(
        "Edit your document",
        value=st.session_state.content,
        height=600,
    )

    st.session_state.content = edited_content

    st.divider()

    st.subheader("⬇️ Download Document")

    try:

        from app.services.exporters import (
            format_txt,
            format_docx,
            format_pdf,
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.download_button(
                "📄 Download TXT",
                data=format_txt(
                    st.session_state.content
                ),
                file_name="legalease_document.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col2:

            st.download_button(
                "📝 Download DOCX",
                data=format_docx(
                    st.session_state.content,
                    st.session_state.document_type,
                    st.session_state.terms,
                ),
                file_name="legalease_document.docx",
                mime=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        with col3:

            st.download_button(
                "📑 Download PDF",
                data=format_pdf(
                    st.session_state.content,
                    st.session_state.document_type,
                    st.session_state.terms,
                ),
                file_name="legalease_document.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    except Exception as error:

        st.warning(
            f"Download tools could not be loaded yet: {error}"
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "LegalEase • AI-assisted legal document drafting • "
    "Review generated documents with a qualified legal professional."
)