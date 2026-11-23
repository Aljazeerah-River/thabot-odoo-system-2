import asyncio
import functools
import logging
import time
from typing import Any, Dict

from google.cloud import firestore

from config import settings

logger = logging.getLogger("thabot.governance")
KILL_SWITCH_DOC = "thabot_governance/kill_switch"
_client = None


def get_firestore_client() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=settings.GCP_PROJECT)
    return _client


def get_kill_switch_state() -> Dict[str, Any]:
    """Returns {"killed": bool, "readable": bool}. readable=False means Firestore could not be read."""
    try:
        doc = get_firestore_client().document(KILL_SWITCH_DOC).get()
        state = (doc.to_dict() or {}) if doc.exists else {"killed": False}
        return {**state, "readable": True}
    except Exception:
        logger.warning("Kill-switch state unreadable from Firestore.")
        return {"killed": False, "readable": False}


def _write_state(killed: bool, actor: str, reason: Any) -> Dict[str, Any]:
    state = {"killed": killed, "reason": reason, "actor": actor, "updated_at": int(time.time())}
    get_firestore_client().document(KILL_SWITCH_DOC).set(state)
    return state


def activate_kill_switch(actor_email: str, reason: str) -> Dict[str, Any]:
    logger.critical("KILL SWITCH ACTIVATED by %s", actor_email)
    return _write_state(True, actor_email, reason[:255])


def reset_kill_switch(actor_email: str) -> Dict[str, Any]:
    logger.warning("KILL SWITCH RESET by %s", actor_email)
    return _write_state(False, actor_email, None)


class SystemHaltedException(RuntimeError):
    pass


def _enforce(state: Dict[str, Any], fail_closed: bool) -> None:
    if state.get("killed"):
        raise SystemHaltedException("System halted by governance kill-switch.")
    if fail_closed and not state.get("readable", False):
        # Write tools must not run when the halt state cannot be confirmed.
        raise SystemHaltedException("Kill-switch state unavailable; write operations are blocked.")


def check_kill_switch(func=None, *, fail_closed: bool = False):
    """@check_kill_switch for read tools (fail-open on unreadable state);
    @check_kill_switch(fail_closed=True) for write tools (blocked when state is unreadable)."""

    def decorate(fn):
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def awrapper(*args, **kwargs):
                _enforce(await asyncio.to_thread(get_kill_switch_state), fail_closed)
                return await fn(*args, **kwargs)
            return awrapper

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            _enforce(get_kill_switch_state(), fail_closed)
            return fn(*args, **kwargs)
        return wrapper

    return decorate(func) if func is not None else decorate
