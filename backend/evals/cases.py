from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, List, Optional, Tuple


ALL_PRODUCT_TOOLS = frozenset({
    "search_products",
    "get_product_details",
    "check_inventory",
})


class EvalStatus(str, Enum):
    PASS = "PASS"
    BEHAVIOR_FAIL = "BEHAVIOR_FAIL"
    INFRA_ERROR = "INFRA_ERROR"


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    category: str
    prompt: str
    required_tools: FrozenSet[str] = frozenset()
    allowed_tools: Optional[FrozenSet[str]] = None
    forbidden_tools: FrozenSet[str] = frozenset()
    min_tool_calls: Optional[int] = None
    max_tool_calls: Optional[int] = None
    required_answer_patterns: Tuple[str, ...] = ()
    forbidden_answer_patterns: Tuple[str, ...] = ()


@dataclass
class EvalResult:
    case_id: str
    category: str
    status: EvalStatus
    reasons: List[str] = field(default_factory=list)
    run_id: Optional[str] = None
    selected_tools: Tuple[str, ...] = ()
    model_call_count: int = 0
    tool_call_count: int = 0
    duration_ms: Optional[float] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cached_input_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    usage_complete: Optional[bool] = None
    error_type: Optional[str] = None


EVAL_CASES = (
    EvalCase(
        case_id="cheapest_in_stock",
        category="grounded_search",
        prompt="What is the cheapest jersey currently in stock?",
        required_tools=frozenset({"search_products"}),
        allowed_tools=ALL_PRODUCT_TOOLS,
        min_tool_calls=1,
    ),
    EvalCase(
        case_id="brazil_price_and_availability",
        category="grounded_search",
        prompt="What is the current price and availability of the Brazil Jersey?",
        required_tools=frozenset({"search_products"}),
        allowed_tools=ALL_PRODUCT_TOOLS,
        min_tool_calls=1,
    ),
    EvalCase(
        case_id="product_details_by_id",
        category="product_details",
        prompt="Give me the current details for product ID 2.",
        required_tools=frozenset({"get_product_details"}),
        allowed_tools=frozenset({"get_product_details"}),
        min_tool_calls=1,
    ),
    EvalCase(
        case_id="inventory_for_quantity",
        category="inventory",
        prompt="Can product ID 2 fulfill a requested quantity of 2?",
        required_tools=frozenset({"check_inventory"}),
        allowed_tools=frozenset({"check_inventory"}),
        min_tool_calls=1,
    ),
    EvalCase(
        case_id="missing_product_name",
        category="missing_product",
        prompt="Do you have an Atlantis Jersey?",
        required_tools=frozenset({"search_products"}),
        allowed_tools=frozenset({"search_products"}),
        min_tool_calls=1,
        required_answer_patterns=(
            r"\b(?:not found|couldn't find|could not find|unable to find|"
            r"no matching|no results|don't have|do not have|don't carry|"
            r"do not carry|not in (?:the )?(?:catalog|store))\b",
        ),
    ),
    EvalCase(
        case_id="missing_product_id",
        category="missing_product",
        prompt="Give me product details for item ID 999999.",
        required_tools=frozenset({"get_product_details"}),
        allowed_tools=frozenset({"get_product_details"}),
        min_tool_calls=1,
        required_answer_patterns=(r"\b(not found|couldn't find)\b",),
    ),
    EvalCase(
        case_id="add_to_cart_refusal",
        category="unsupported_action",
        prompt="Add the Brazil Jersey to my cart.",
        allowed_tools=frozenset(),
        forbidden_tools=ALL_PRODUCT_TOOLS,
        max_tool_calls=0,
        required_answer_patterns=(
            r"\b(can(?:not|'t)|unable)\b",
            r"\bcart\b",
        ),
        forbidden_answer_patterns=(
            r"\bhow many\b.*\b(cart|add)\b",
            r"\bwhat quantity\b",
        ),
    ),
    EvalCase(
        case_id="checkout_refusal",
        category="unsupported_action",
        prompt="Complete checkout for me.",
        allowed_tools=frozenset(),
        forbidden_tools=ALL_PRODUCT_TOOLS,
        max_tool_calls=0,
        required_answer_patterns=(
            r"\b(can(?:not|'t)|unable)\b",
            r"\b(checkout|purchase|order)\b",
        ),
    ),
    EvalCase(
        case_id="capabilities_question",
        category="no_tool_information",
        prompt="What can you help me with in this store?",
        allowed_tools=frozenset(),
        forbidden_tools=ALL_PRODUCT_TOOLS,
        max_tool_calls=0,
    ),
    EvalCase(
        case_id="unrelated_request",
        category="no_tool_scope",
        prompt="Write a short poem about the ocean.",
        allowed_tools=frozenset(),
        forbidden_tools=ALL_PRODUCT_TOOLS,
        max_tool_calls=0,
        required_answer_patterns=(r"\b(store|shopping|jersey|cannot|can't|unable)\b",),
    ),
)
