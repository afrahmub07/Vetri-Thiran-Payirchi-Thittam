from fastapi import APIRouter, Depends, HTTPException

from app.ai_core.gemini_generator import GeminiDocumentGenerator
from app.config import Settings, get_settings
from app.schemas import DocumentRequest, DocumentResponse


router = APIRouter(
    prefix="",
    tags=["Documents"],
)


def get_generator(
    settings: Settings = Depends(get_settings),
):
    return GeminiDocumentGenerator(settings)


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    request: DocumentRequest,
    settings: Settings = Depends(get_settings),
    generator: GeminiDocumentGenerator = Depends(
        get_generator
    ),
):
    total_input = (
        len(request.document_type)
        + len(request.parties)
        + len(request.terms)
        + len(request.dates)
        + len(request.jurisdiction)
        + len(request.language)
    )

    if total_input > settings.max_input_chars:
        raise HTTPException(
            status_code=413,
            detail="Input is too large.",
        )

    try:
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
            jurisdiction=request.jurisdiction,
            language=request.language,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI generation failed: {error}",
        )

    return DocumentResponse(
        document_type=request.document_type,
        content=content,
        model=settings.gemini_model,
        warning=(
            "AI-generated draft. "
            "Review with a qualified legal professional "
            "before use."
        ),
    )