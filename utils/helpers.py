
import string
import random
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from database import order_collection
from fpdf import FPDF

from models.orders import Order


async def generate_short_order_id():
    """Generate a unique short order ID."""
    while True:
        prefix = "ORD"
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        short_id = f"{prefix}-{random_suffix}"

        # Check if this ID already exists
        existing_order = await order_collection.find_one({"order_id": short_id})
        if not existing_order:
            return short_id


from datetime import datetime


def serialize_order(order):
    """Convert MongoDB's ObjectId and any non-serializable fields to JSON-compatible types."""
    if "_id" in order:
        order["_id"] = str(order["_id"])  # Convert ObjectId to string

    # Check and handle created_date
    if "created_date" in order:
        if isinstance(order["created_date"], str):  # If it's an ISO-format string, keep it as is
            order["created_date"] = order["created_date"]
        elif isinstance(order["created_date"], datetime):  # If it's a datetime object, format it
            order["created_date"] = order["created_date"].isoformat()

    # Check and handle modified_date
    if "modified_date" in order:
        if isinstance(order["modified_date"], str):  # If it's an ISO-format string, keep it as is
            order["modified_date"] = order["modified_date"]
        elif isinstance(order["modified_date"], datetime):  # If it's a datetime object, format it
            order["modified_date"] = order["modified_date"].isoformat()

    return order

def serialize_user(user):
    """Convert ObjectId to string for JSON serialization."""
    if "_id" in user:
        user["_id"] = str(user["_id"])
    return user

async def send_email(order: Order, pdf_path: str):
    sender_email = "prerakp87@gmail.com"
    receiver_email = order.customer_email  # Access model attribute
    password =   # Replace with your App Password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"Invoice for Order {order.order_id}"  # Access model attribute

    body = "Please find your invoice attached."
    message.attach(MIMEText(body, "plain"))

    with open(pdf_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {order.order_id}.pdf",  # Access model attribute
        )
        message.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def generate_invoice_pdf(order):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Invoice", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Order ID: {order['order_id']}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Name: {order['customer_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Email: {order['customer_email']}", ln=True)
    pdf.cell(200, 10, txt=f"Item Name: {order['item_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Quantity: {order['qty']}", ln=True)
    pdf.output(f"./invoices/{order['order_id']}.pdf")
    return f"./invoices/{order['order_id']}.pdf"
