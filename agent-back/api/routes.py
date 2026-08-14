from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AgentRequest(BaseModel):
    message: str


@router.get("/")
def root():
    return {"message": "CareerOps API is running"}


@router.get("/health")
def health():
    return {"status": "healthy"}


@router.post("/agent")
def agent(request: AgentRequest):
    return {
        "response": f"CareerOps received: {request.message}"
    }


@router.get("/jobs")
def get_jobs():
    return {
        "jobs": []
    }


@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    return {
        "job_id": job_id,
        "message": "Job details will be added later"
    }