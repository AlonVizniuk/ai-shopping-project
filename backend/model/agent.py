from typing import List, Literal, Optional

from pydantic import BaseModel, Field, root_validator, validator


class AgentRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)

    @validator("prompt")
    def prompt_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be blank")
        return value


class AgentResponse(BaseModel):
    answer: str
    prompts_left: int = Field(..., ge=0)


class SearchProductsArguments(BaseModel):
    name: Optional[str] = ""
    min_price: Optional[float] = Field(0, ge=0)
    max_price: Optional[float] = Field(999999, ge=0)
    min_stock: Optional[int] = Field(0, ge=0)
    max_stock: Optional[int] = Field(999999, ge=0)
    in_stock_only: Optional[bool] = False
    sort_by: Optional[Literal["name", "price", "stock"]] = "name"

    @root_validator
    def valid_ranges(cls, values):
        min_price = values.get("min_price")
        max_price = values.get("max_price")
        min_stock = values.get("min_stock")
        max_stock = values.get("max_stock")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("min_price must not exceed max_price")
        if min_stock is not None and max_stock is not None and min_stock > max_stock:
            raise ValueError("min_stock must not exceed max_stock")
        return values


class GetProductDetailsArguments(BaseModel):
    item_id: int = Field(..., gt=0)


class CheckInventoryArguments(BaseModel):
    item_id: int = Field(..., gt=0)
    requested_quantity: Optional[int] = Field(None, gt=0)


class ProductResult(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    available: bool


class ProductSearchResult(BaseModel):
    products: List[ProductResult]
    count: int = Field(..., ge=0)


class InventoryResult(BaseModel):
    item_id: int
    name: str
    stock: int
    available: bool
    requested_quantity: Optional[int] = None
    requested_quantity_available: Optional[bool] = None


class ProductNotFoundResult(BaseModel):
    item_id: int
    found: bool = False
