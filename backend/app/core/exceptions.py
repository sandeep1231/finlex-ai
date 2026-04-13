from fastapi import HTTPException


class FinLexException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class QuotaExceededException(FinLexException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Monthly query quota exceeded. Please upgrade your plan.",
        )


class DocumentLimitException(FinLexException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Document upload limit reached. Please upgrade your plan.",
        )


class UnsupportedFileTypeException(FinLexException):
    def __init__(self, file_type: str):
        super().__init__(
            status_code=400,
            detail=f"Unsupported file type: {file_type}. Supported: PDF, DOCX, XLSX, CSV, TXT",
        )
