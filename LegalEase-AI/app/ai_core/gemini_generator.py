from google import genai
from google.genai import types

from app.config import Settings


SYSTEM_INSTRUCTIONS = """
You are LegalEase's legal-document drafting assistant.

Your job is to create professional legal document DRAFTS
from the information supplied by the user.

Important rules:

1. Do not invent facts that were not supplied.
2. Do not claim the document is legally valid or lawyer-reviewed.
3. Use professional and neutral legal language.
4. Preserve names, dates, amounts and requirements accurately.
5. If important information is missing, use:
   [TO BE COMPLETED]
6. Organize the document with a title and numbered sections.
7. Include signature sections when appropriate.
8. Return plain text only.
9. Do not use Markdown code fences.
10. Do not provide an explanation before or after the document.
"""


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.gemini_model

        if not settings.gemini_api_key:
            self.client = None
        else:
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str,
        language: str,
    ) -> str:

        return f"""
{SYSTEM_INSTRUCTIONS}

Create a {document_type}.

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE / DATES:
{dates}

JURISDICTION:
{jurisdiction or "[NOT SUPPLIED]"}

OUTPUT LANGUAGE:
{language}

Create a structured legal document draft.

Depending on the document type, include appropriate sections such as:

- Title
- Parties
- Definitions
- Scope
- Responsibilities
- Payment
- Confidentiality
- Term and termination
- Representations
- Dispute resolution
- Governing law
- Notices
- Severability
- Entire agreement
- Signatures

Only include sections appropriate for the selected document.

Do not invent important facts.
"""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str = "",
        language: str = "English",
    ) -> str:

        if self.client is None:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Please add your Gemini API key to .env."
            )

        prompt = self.build_prompt(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
            jurisdiction=jurisdiction,
            language=language,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.settings.temperature,
                max_output_tokens=self.settings.max_output_tokens,
                candidate_count=1,
            ),
        )

        text = (response.text or "").strip()

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text