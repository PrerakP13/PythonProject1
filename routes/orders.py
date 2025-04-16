from datetime import datetime, timezone  # For handling datetime operations
from typing import Optional  # For defining optional parameters

from bson import ObjectId  # For working with MongoDB Object IDs
from fastapi import APIRouter, HTTPException  # FastAPI utilities for routing and exception handling
from pydantic import ValidationError  # For handling validation errors in models

from database import order_collection, items_collection  # Importing collections for database operations
from models.orders import Order, Item  # Importing data models for orders and items
from utils.helpers import serialize_order, generate_short_order_id, generate_invoice_pdf, send_email
# Utility functions for serialization, ID generation, invoice creation, and sending emails

router = APIRouter()  # Creating a router instance for grouping related endpoints

# Endpoint to retrieve item details from the database
@router.get("/get_items")
async def show_items():
    item_cursor = items_collection.find({}, {"item_id": 1, "item_name": 1, "item_inventory": 1, "sku": 1, "price": 1, "_id": 0})
    item_list = await item_cursor.to_list(length=None)  # Convert cursor to a list
    return {"orders": item_list}  # Return the list of items

# Endpoint to retrieve all orders based on optional filters
@router.get("/get_all_orders")
async def get_all_orders(
    status: Optional[str] = None,  # Filter by order status
    managed_by: Optional[str] = None,  # Filter by manager
    sort_by: Optional[str] = "created_date",  # Field to sort by (default: created_date)
    sort_order: Optional[int] = -1  # Sort order (-1 for descending, 1 for ascending)
):
    try:
        query = {}  # Initialize query dictionary
        if status:
            query["status"] = status  # Add status filter if provided
        if managed_by:
            query["managed_by"] = managed_by  # Add manager filter if provided

        # Fetch matching orders and sort results
        cursor = order_collection.find(query).sort(sort_by, sort_order)
        orders = await cursor.to_list(length=None)  # Convert cursor to list

        # Serialize orders for response
        serialized_orders = [serialize_order(order) for order in orders]
        return {"orders": serialized_orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Handle unexpected errors

# Endpoint to create a new order
@router.post("/create_order")
async def create_order(order_data: dict):
    try:
        # Generate an order ID if missing
        order_data["order_id"] = order_data.get("order_id") or await generate_short_order_id()

        # Fetch item price if not provided
        if "price" not in order_data or not order_data["price"]:
            item = await items_collection.find_one({"item_name": order_data["item_name"]}, {"price": 1, "_id": 0})
            if not item or "price" not in item:
                raise HTTPException(status_code=404, detail="Item not found or price missing")
            order_data["price"] = item["price"]

        # Add other computed fields to the order
        order_data["created_date"] = datetime.now(timezone.utc).isoformat()  # Add current timestamp
        order_data["status"] = order_data.get("status", "Pending")  # Default status: Pending

        # Save the order to the database
        await order_collection.insert_one(order_data)
        print("Order added to the database")

        # Convert order data to Order model for email and other operations
        order_model = Order(**order_data)
        print("Order converted to model")

        # Generate invoice and send email
        pdf_path = generate_invoice_pdf(order_data)
        print("Order invoice saved")

        print("Sending email")
        await send_email(order_model, pdf_path)
        print("Email sent")

        return {"message": "Order created successfully", "order_id": order_data["order_id"]}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Invalid order data: {str(e)}")  # Handle validation errors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")  # Handle unexpected errors

# Endpoint to update an order
@router.put("/{id}")
async def update_order(id: str, updated_order: Order):
    updated_order_dict = updated_order.model_dump(exclude_unset=True)  # Convert model to dictionary
    updated_order_dict["modified_date"] = datetime.now(timezone.utc)  # Add modified_date field

    try:
        result = await order_collection.update_one({"order_id": id}, {"$set": updated_order_dict})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to delete an order by ID
@router.delete("/{id}")
async def delete_order(id: str):
    try:
        result = await order_collection.delete_one({"order_id": id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        return {"message": "Order deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to list orders with pagination and sorting
@router.get("/list_orders")
async def list_orders(
    page: int = 1,  # Page number (default: 1)
    limit: int = 10,  # Number of items per page (default: 10)
    status: Optional[str] = None,  # Filter by order status
    managed_by: Optional[str] = None,  # Filter by manager
    sort_by: Optional[str] = "created_date",  # Field to sort by (default: created_date)
    sort_order: Optional[int] = -1  # Sort order (-1 for descending, 1 for ascending)
):
    try:
        query = {}  # Initialize query dictionary
        if status:
            query["status"] = status  # Add status filter if provided
        if managed_by:
            query["managed_by"] = managed_by  # Add manager filter if provided

        # Calculate pagination parameters
        skip = (page - 1) * limit
        cursor = order_collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        orders = await cursor.to_list(length=limit)

        # Count total matching orders
        total_orders = await order_collection.count_documents(query)

        # Serialize and return response
        serialized_orders = [serialize_order(order) for order in orders]
        return {"orders": serialized_orders, "total": total_orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints follow a similar structure with their respective logic
# Each endpoint ensures proper handling of database queries, serialization, and error handling