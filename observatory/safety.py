from functools import wraps
from contextvars import ContextVar
from fastapi import HTTPException, Header, Request
from inspect import signature, iscoroutinefunction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from observatory.observatory import Observatory


_current_observatory: ContextVar["Observatory | None"] = ContextVar(
    "current_observatory",
    default=None,
)


def set_current_observatory(observatory: "Observatory | None") -> None:
    _current_observatory.set(observatory)


def _resolve_observatory(*args, **kwargs):
    observatory = kwargs.get("observatory")
    if observatory:
        return observatory

    request = kwargs.get("request")
    if isinstance(request, Request):
        return getattr(request.app.state, "observatory", None)

    observatory = _current_observatory.get()
    if observatory:
        return observatory

    if len(args) > 0:
        from observatory.observatory import Observatory
        from observatory.devices.base import ObservatoryDevice

        if isinstance(args[0], Observatory):
            return args[0]
        if isinstance(args[0], ObservatoryDevice):
            return args[0].observatory

    return None

def require_conditions(*conditions):
    def decorator(func):
        is_async = iscoroutinefunction(func)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            override: bool = bool(kwargs.get("override", False))

            if not override:
                observatory = _resolve_observatory(*args, **kwargs)
                
                if not observatory:
                    raise HTTPException(
                        status_code=500,
                        detail="Observatory instance not found for safety checks"
                    )
                
                for condition in conditions:
                    sig = signature(condition)
                    accepted_args = {
                        k: v for k, v in kwargs.items()
                        if k in sig.parameters
                    }
                    if "observatory" in sig.parameters:
                        accepted_args["observatory"] = observatory

                    result = condition(**accepted_args)
                    if iscoroutinefunction(condition):
                        result = await result

                    success, reason = result
                    if not success:
                        raise HTTPException(status_code=403, detail=reason)

            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            override: bool = bool(kwargs.get("override", False))

            if not override:
                observatory = _resolve_observatory(*args, **kwargs)
                
                if not observatory:
                    raise HTTPException(
                        status_code=500,
                        detail="Observatory instance not found for safety checks"
                    )
                
                for condition in conditions:
                    sig = signature(condition)
                    accepted_args = {
                        k: v for k, v in kwargs.items()
                        if k in sig.parameters
                    }
                    if "observatory" in sig.parameters:
                        accepted_args["observatory"] = observatory

                    result = condition(**accepted_args)
                    if iscoroutinefunction(condition):
                        import asyncio
                        result = asyncio.run(result)

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