import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List


logger = logging.getLogger("shopping_agent")
_CONSOLE_HANDLER_NAME = "shopping_agent_json_console"


def configure_logger() -> logging.StreamHandler:
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handlers = [
        handler
        for handler in logger.handlers
        if handler.get_name() == _CONSOLE_HANDLER_NAME
    ]

    if handlers:
        for duplicate_handler in handlers[1:]:
            logger.removeHandler(duplicate_handler)
        return handlers[0]

    handler = logging.StreamHandler()
    handler.set_name(_CONSOLE_HANDLER_NAME)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return handler


configure_logger()


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log_event(event: str, run_id: str, **fields: Any) -> None:
    try:
        payload = {
            "schema_version": 1,
            "timestamp": utc_timestamp(),
            "event": event,
            "run_id": run_id,
            **fields,
        }
        logger.info(json.dumps(payload, separators=(",", ":")))
    except Exception:
        return


def extract_usage(response: Any) -> Dict[str, Any]:
    empty_usage = {
        "usage_available": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_input_tokens": 0,
        "reasoning_tokens": 0,
    }

    try:
        usage = getattr(response, "usage", None)
        if usage is None:
            return empty_usage
        core_usage = [
            getattr(usage, field, None)
            for field in ("input_tokens", "output_tokens", "total_tokens")
        ]
        if not all(_is_non_negative_int(value) for value in core_usage):
            return empty_usage

        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)
        return {
            "usage_available": True,
            "input_tokens": _usage_value(usage.input_tokens),
            "output_tokens": _usage_value(usage.output_tokens),
            "total_tokens": _usage_value(usage.total_tokens),
            "cached_input_tokens": _usage_value(
                getattr(input_details, "cached_tokens", 0)
            ),
            "reasoning_tokens": _usage_value(
                getattr(output_details, "reasoning_tokens", 0)
            ),
        }
    except Exception:
        return empty_usage


def extract_argument_names(raw_arguments: str) -> List[str]:
    try:
        arguments = json.loads(raw_arguments)
        if not isinstance(arguments, dict):
            return []
        return sorted(arguments.keys())
    except Exception:
        return []


def _usage_value(value: Any) -> int:
    return value if _is_non_negative_int(value) else 0


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
