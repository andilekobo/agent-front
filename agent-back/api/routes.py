from fastapi import APIRouter, HTTPException
from models.schemas import AgentRequest
from agent.agent import talk_to_claude
import logging

router = APIRouter()

logger = logging.getLogger("careerops")


@router.post("/agent")
def agent_endpoint(request: AgentRequest):
    try:
        response = talk_to_claude(request.message)

        return {
            "response": response
        }

    except Exception as e:
        logger.exception("CareerOps agent failed")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )