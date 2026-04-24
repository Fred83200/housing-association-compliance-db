from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from app.query_router import answer_question, build_property_case_file

app = FastAPI(
    title="Housing Compliance Discovery API",
    description="Local discovery API for PostgreSQL housing association demo data.",
    version="0.1.0",
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: QuestionRequest) -> dict:
    return answer_question(request.question)


@app.get("/properties/{property_id}/case-file")
def property_case_file(property_id: int) -> dict:
    result = build_property_case_file(property_id)

    if result["overview"] is None:
        raise HTTPException(status_code=404, detail="Property not found")

    return result

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
