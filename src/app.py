
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src import rag_engine


# --------------------------------------------------
# 1. Initialize FastAPI
# --------------------------------------------------

app = FastAPI(
    title="AI PDF Question Answering API",
    description="Upload PDFs and ask questions using RAG.",
    version="1.0.0",
)


# --------------------------------------------------
# 2. Configure CORS for React
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --------------------------------------------------
# 3. Request and response models
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="Question to ask about the PDF",
    )


class AnswerResponse(BaseModel):
    question: str
    answer: str


# --------------------------------------------------
# 4. Active uploaded document
# --------------------------------------------------

uploaded_chunks = None
uploaded_index = None
uploaded_filename = None

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


# --------------------------------------------------
# 5. Home endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI PDF Question Answering API is running!",
        "status": "success",
    }


# --------------------------------------------------
# 6. Health check endpoint
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "uploaded_pdf": uploaded_filename,
    }


# --------------------------------------------------
# 7. Upload PDF endpoint
# --------------------------------------------------

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global uploaded_chunks
    global uploaded_index
    global uploaded_filename

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file.",
        )

    try:
        # Read at most 10 MB plus one byte to enforce the limit.
        pdf_bytes = await file.read(MAX_PDF_SIZE + 1)

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if len(pdf_bytes) > MAX_PDF_SIZE:
            raise HTTPException(
                status_code=413,
                detail="PDF must be 10 MB or smaller.",
            )

        # Build the chunks and FAISS index for this PDF.
        chunks, index = rag_engine.build_document_index(pdf_bytes)

        # Replace the active PDF only after processing succeeds.
        uploaded_chunks = chunks
        uploaded_index = index
        uploaded_filename = file.filename

        return {
            "message": "PDF uploaded and indexed successfully.",
            "filename": uploaded_filename,
            "chunks": len(uploaded_chunks),
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        print(f"PDF processing error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Could not process the uploaded PDF.",
        ) from error

    finally:
        await file.close()


# --------------------------------------------------
# 8. Ask a question endpoint
# --------------------------------------------------

@app.post("/ask", response_model=AnswerResponse)
def ask_pdf(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty.",
        )

    try:
        # Use the uploaded PDF if one is active.
        if uploaded_chunks is not None and uploaded_index is not None:
            retrieved_chunks = rag_engine.retrieve_chunks(
                question,
                uploaded_chunks,
                uploaded_index,
                rag_engine.embedding_model,
            )

            answer = rag_engine.generate_answer(
                question,
                retrieved_chunks,
            )

        # Otherwise, use the PDF loaded from the data folder.
        else:
            answer = rag_engine.ask_question(question)

        return AnswerResponse(
            question=question,
            answer=answer,
        )

    except Exception as error:
        print(f"Answer generation error: {error}")

        raise HTTPException(
            status_code=500,
            detail="Could not generate an answer. Check the backend terminal.",
        ) from error
