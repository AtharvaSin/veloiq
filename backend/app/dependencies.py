from fastapi import Header


def get_current_actor(x_user_id: str | None = Header(default="anonymous")) -> str:
    """Extract the acting user's identity from the X-User-Id header.

    Phase A mock auth. Production replaces this with real OAuth/JWT-derived identity.
    Returns 'anonymous' when the header is missing or empty.
    """
    return x_user_id or "anonymous"
