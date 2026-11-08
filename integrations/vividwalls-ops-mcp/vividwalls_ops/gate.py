"""Approval gate for any function that changes the store (CLAUDE.md rule 1)."""
from . import config


def blocked(confirm: bool, action: str, change: dict) -> dict | None:
    """Return a preview instead of acting unless confirmed AND writes are switched on."""
    if confirm and config.writes_allowed():
        return None
    reason = (
        "preview only: call again with confirm=true after the owner approves"
        if not confirm
        else "writes are switched off (VIVIDWALLS_ALLOW_WRITES is not 1); ask the owner to apply it"
    )
    return {"applied": False, "action": action, "reason": reason, "change": change}
