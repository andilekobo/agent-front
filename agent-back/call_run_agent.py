import asyncio
import traceback

from api import routes
from models.schemas import AgentRequest

async def main():
    try:
        req = AgentRequest(message="Find junior software developer jobs in Johannesburg")
        resp = await routes.run_agent(req)
        print("RESP:", resp)
    except Exception:
        traceback.print_exc()

asyncio.run(main())