from fastapi import FastAPI, Response, HTTPException, APIRouter
from fastapi.responses import StreamingResponse
import csv
from io import StringIO
from bson import ObjectId
from datetime import datetime

from database import order_collection

router = APIRouter()


@router.get("/export", response_class=StreamingResponse)
async def export_orders():
    try:
        # Fetch all orders from MongoDB
        orders = await order_collection.find().to_list(length=None)

        # Create a StringIO object to write CSV data
        csv_file = StringIO()
        writer = csv.writer(csv_file)

        # Write the CSV header
        writer.writerow(["Order ID", "Customer Name", "Customer Email", "Item Name", "Price", "QTY", "SKU",
                         "Managed By", "Added By", "Status", "Created Date", "Modified Date"])

        # Write the rows from the MongoDB data
        for order in orders:
            writer.writerow([
                order.get("order_id", ""),
                order.get("customer_name", ""),
                order.get("customer_email", ""),
                order.get("item_name", ""),
                order.get("price", ""),
                order.get("qty", ""),
                order.get("sku", ""),
                order.get("managed_by", ""),
                order.get("added_by", ""),
                order.get("status", ""),
                order.get("created_date", "").strftime("%Y-%m-%d %H:%M:%S") if "created_date" in order else "",
                order.get("modified_date", "").strftime("%Y-%m-%d %H:%M:%S") if "modified_date" in order else ""
            ])

        # Reset the file pointer to the beginning
        csv_file.seek(0)

        # Return the CSV file as a response
        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting orders: {str(e)}")
