from pydantic import BaseModel  # Importing Pydantic's BaseModel for data validation and serialization
from typing import Optional  # Importing Optional for fields that can be None
from datetime import datetime  # Importing datetime to handle date and time fields

from pydantic.v1 import Field  # Importing Field for setting default values and validation rules

# Order class for representing and validating order-related data
class Order(BaseModel):
    order_id: Optional[str]  # Optional unique identifier for the order
    customer_name: Optional[str]  # Optional customer name associated with the order
    customer_email: str  # Required email address of the customer
    item_name: str  # Required name of the item in the order
    price: Optional[float]  # Optional price of the item (float type)
    qty: int  # Required quantity of the item (integer type)
    sku: Optional[str] = None  # Optional stock keeping unit for identifying the item
    managed_by: Optional[str] = None  # Optional field for tracking who is managing the order
    added_by: Optional[str] = None  # Optional field for tracking who added the order
    status: str = Field(default="Pending", regex="^(Pending|Shipped|Delivered|Canceled)$")
    # Default status is "Pending"; validation ensures the status is one of the predefined options
    created_date: Optional[datetime] = None  # Optional field for tracking when the order was created
    modified_date: Optional[datetime] = None  # Optional field for tracking when the order was last modified

# Item class for representing and validating inventory-related data
class Item(BaseModel):
    item_inventory: str  # Required inventory ID or reference for the item
    item_name: str  # Required name of the item
    price: str  # Required price of the item (string type, possibly for currencies like "$50")
    sku: str  # Required stock keeping unit for identifying the item
    created_date: Optional[datetime] = None  # Optional field for tracking when the item was created