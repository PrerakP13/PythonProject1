from fastapi import APIRouter, HTTPException, UploadFile, File
from database import order_collection
from models.orders import Order
import csv
from io import StringIO
import openpyxl

router = APIRouter()

@router.post("/upload_csv")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and validate a file (CSV or XLSX), then insert valid rows into the database.
    For CSV files, we read and decode the content.
    For XLSX files, we use the file-like object provided by FastAPI.
    """
    if not (file.filename.endswith(".csv") or file.filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Only .csv and .xlsx files are allowed")

    valid_orders = []
    invalid_orders = []

    if file.filename.endswith(".csv"):
        # Read the whole file content as bytes, decode to string, and process with csv.DictReader.
        content = await file.read()  # This returns bytes.
        decoded_content = content.decode("utf-8")
        csv_reader = csv.DictReader(StringIO(decoded_content))

        for row in csv_reader:
            try:
                order = Order(**row)
                valid_orders.append(order.model_dump())
            except Exception as e:
                invalid_orders.append({"row": row, "error": str(e)})

    elif file.filename.endswith(".xlsx"):
        # Instead of reading the bytes and wrapping in BytesIO,
        # use the file-like object directly. Ensure the pointer is at the start.
        file.file.seek(0)
        workbook = openpyxl.load_workbook(file.file)
        sheet = workbook.active

        # Get headers from the first row.
        headers = [cell.value for cell in sheet[1]]

        # Process each subsequent row.
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_data = dict(zip(headers, row))
            try:
                order = Order(**row_data)
                valid_orders.append(order.model_dump())
            except Exception as e:
                invalid_orders.append({"row": row_data, "error": str(e)})

    # Insert valid orders into the database.
    if valid_orders:
        await order_collection.insert_many(valid_orders)

    return {
        "message": "File processed successfully",
        "valid_orders_count": len(valid_orders),
        "invalid_orders_count": len(invalid_orders),
        "invalid_orders": invalid_orders,
    }
