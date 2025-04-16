
import logging
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


from database import register_collection, employee_collection, order_collection
from models.users import SignUp

from routes import orders, users, auth
from utils import export_csv, import_csv, helpers
from utils.export_csv import export_orders

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Print a start message immediately on startup
print("Server is starting...", flush=True)


app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(users.router, prefix="", tags=["Users"])
app.include_router(auth.router, prefix="", tags=["Authentication"])
app.include_router(export_csv.router, prefix="", tags=["export"])
app.include_router(import_csv.router, prefix="", tags=["import"])








@app.post('/signup')
async def post_signup(user: SignUp):
    """
    Signup endpoint that:
      1. Logs the received user data.
      2. Checks if the user already exists.
      3. Computes the usertype based on email logic.
      4. Inserts the user into the database.
      5. Returns a success message with the computed role.
    """
    print("Received signup request", flush=True)
    try:
        print("Signup data received:", user.model_dump(), flush=True)

        # Check if a user with the given email already exists.
        existing_user = await employee_collection.find_one({"email": user.personal_email})
        if existing_user:
            print("User already exists with email:", user.email, flush=True)
            raise HTTPException(status_code=400, detail="User already exists")

        name = f"{user.firstname} {user.lastname}"

        user_data = {
            "name":name,
            "personal_email": user.personal_email,
            "phone_number": user.phone_number,
            "password": user.password,
            "usertype": 'visitor'
        }



        # Insert the new user into the database.
        await register_collection.insert_one(user_data)
        print("User inserted successfully:", user_data, flush=True)

        return {"message": "You are registered successfully"}

    except Exception as e:
        print("Error during signup:", e, flush=True)
        raise HTTPException(status_code=500, detail=str(e))





























