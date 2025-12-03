import contextvars
from typing import Optional

# Define context variable with a default value of None
_current_user_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("current_user_id", default=None)

def get_current_user_id() -> str:
    """
    Get the current user ID from the context.
    Raises RuntimeError if user ID is not set.
    """
    user_id = _current_user_id.get()
    if user_id is None:
        raise RuntimeError("Current user ID is not set in context")
    return user_id

def set_current_user_id(user_id: str):
    """
    Set the current user ID in the context.
    """
    _current_user_id.set(user_id)
