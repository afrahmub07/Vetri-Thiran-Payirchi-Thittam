from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=200
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=500
    )

    jurisdiction: str = Field(
        default="",
        max_length=300
    )

    language: str = Field(
        default="English",
        min_length=2,
        max_length=100
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates",
        "jurisdiction",
        "language"
    )
    @classmethod
    def clean_values(cls, value: str) -> str:
        return value.strip()


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    model: str
    warning: str | None = None


class HealthResponse(BaseModel):
    status: str
    app: str