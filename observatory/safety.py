from functools import wraps
from contextvars import ContextVar, Token
from fastapi import HTTPException, Header, Request
from inspect import isawaitable, signature, iscoroutinefunction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.observatory import Observatory


_current_observatory: ContextVar["Observatory | None"] = ContextVar(
    "current_observatory",
    default=None,
)


def set_current_observatory(observatory: "Observatory | None") -> Token:
    return _current_observatory.set(observatory)


def reset_current_observatory(token: Token) -> None:
    _current_observatory.reset(token)


def get_current_observatory() -> "Observatory | None":
    return _current_observatory.get()


def _looks_like_observatory(value) -> bool:
    return hasattr(value, "state") and hasattr(value, "get_device")


def _resolve_observatory(*args, **kwargs):
    observatory = kwargs.get("observatory")
    if observatory is not None:
        return observatory

    request = kwargs.get("request")
    if isinstance(request, Request):
        return getattr(request.app.state, "observatory", None)

    for arg in args:
        if _looks_like_observatory(arg):
            return arg

        observatory = getattr(arg, "observatory", None)
        if observatory is not None:
            return observatory

    observatory = _current_observatory.get()
    if observatory is not None:
        return observatory

    return None


async def _evaluate_condition(condition, observatory, kwargs):
    sig = signature(condition)
    accepted_args = {
        k: v for k, v in kwargs.items()
        if k in sig.parameters
    }
    if "observatory" in sig.parameters:
        accepted_args["observatory"] = observatory

    result = condition(**accepted_args)
    if isawaitable(result):
        result = await result
    return result


def _evaluate_condition_sync(condition, observatory, kwargs):
    sig = signature(condition)
    accepted_args = {
        k: v for k, v in kwargs.items()
        if k in sig.parameters
    }
    if "observatory" in sig.parameters:
        accepted_args["observatory"] = observatory

    result = condition(**accepted_args)
    if isawaitable(result):
        import asyncio

        result = asyncio.run(result)
    return result


def require_conditions(*conditions):
    def decorator(func):
        is_async = iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            override: bool = bool(kwargs.get("override", False))

            if not override:
                observatory = _resolve_observatory(*args, **kwargs)
                if observatory is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Observatory instance not found for safety checks"
                    )

                for condition in conditions:
                    result = await _evaluate_condition(condition, observatory, kwargs)
                    success, reason = result
                    if not success:
                        raise HTTPException(status_code=403, detail=reason)

            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            override: bool = bool(kwargs.get("override", False))

            if not override:
                observatory = _resolve_observatory(*args, **kwargs)
                if observatory is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Observatory instance not found for safety checks"
                    )

                for condition in conditions:
                    result = _evaluate_condition_sync(condition, observatory, kwargs)
                    success, reason = result
                    if not success:
                        raise HTTPException(status_code=403, detail=reason)

            return func(*args, **kwargs)

        return async_wrapper if is_async else sync_wrapper
    return decorator



def safety_override(
    x_safety_override: str | None = Header(None)
) -> bool:
    return (x_safety_override or "").lower() == "true"
