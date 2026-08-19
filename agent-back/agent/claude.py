from agent.agent import talk_to_claude


def ask_claude(user_message: str) -> str:
    """Local wrapper that reuses the internal agent implementation.

    This keeps a compatible function name so external callers can still call
    ask_claude(...) and receive a useful local response. An LLM client can be
    reintroduced later by replacing this module with one that calls an API.
    """
    return talk_to_claude(user_message)
