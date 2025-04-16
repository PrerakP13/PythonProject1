import requests  # For making external HTTP requests
from fastapi import APIRouter  # For creating route groups in FastAPI
from fastapi import HTTPException, Request, Response  # For exception handling and working with requests/responses

from database import employee_collection  # Importing the employee database collection
from models.users import LoginModel, RecaptchaSchema  # Importing data validation models

# Create a router instance for grouping API endpoints
router = APIRouter()


# Endpoint for user login
@router.post("/login")
async def post_login(request: Request, user: LoginModel, response: Response):
    print("Login attempt for user:", user.company_email, flush=True)  # Log the login attempt

    try:
        # Fetch user details from the database using the company email
        db_user = await employee_collection.find_one({"company_email": user.company_email})
        if not db_user:
            # If user is not found in the database, return a 400 error
            print("User not found:", user.company_email, flush=True)
            raise HTTPException(status_code=400, detail="User does not exist")

        # Check if the provided password matches the stored password
        if db_user["password"] != user.password:
            print("Incorrect password for user:", user.company_email, flush=True)
            raise HTTPException(status_code=400, detail="Incorrect password")

        # Retrieve the user's role, defaulting to "visitor" if not found
        usertype = db_user.get("usertype", "visitor")
        print("Retrieved usertype:", usertype, flush=True)

        # Store the user type in the session for later use
        request.session["usertype"] = usertype

        # Add a custom header to the response for any additional metadata
        response.headers["Custom-Header"] = "custom-value"
        print("Login successful for user:", user.company_email, flush=True)

        # Return a success message and the user role
        return {"message": "Login successful", "role": usertype}

    except Exception as e:
        # Handle any unexpected exceptions during login
        print("Error during login:", e, flush=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# Endpoint for redirecting to login page
@router.get("/login")
async def gotologin():
    print("Redirecting to login page", flush=True)
    return {"message": "Redirect to login page"}


# Endpoint for logging out the user
@router.post("/logout")
async def userlogout(request: Request, response: Response):
    print("Logging out user", flush=True)
    # Clear the user's session to log them out
    request.session.clear()
    print("Session cleared, user logged out", flush=True)
    return {"message": "Log Out Successful"}


# Endpoint for accessing the home page
@router.get("/home")
async def gotohome(request: Request):
    print("Accessing /home endpoint", flush=True)
    # Retrieve the user's role from the session; default to "visitor" if not found
    user_role = request.session.get('usertype', "visitor")
    if user_role is None:
        print("User role not found in session, defaulting to visitor", flush=True)
        user_role = "visitor"
    print("Home endpoint user role:", user_role, flush=True)
    return {"message": "Welcome to Home Page", "role": user_role}


# Endpoint for verifying reCAPTCHA
@router.post("/recaptcha")
async def check_recaptcha(recaptcha: RecaptchaSchema):
    """
    Verify the reCAPTCHA token by sending it to Google's API.
    """
    print("Starting reCAPTCHA verification", flush=True)
    try:
        # Send a POST request to Google's reCAPTCHA verification API
        recaptcha_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": '6LcDF-QqAAAAAA_5-gFeSPror9HT0V4LJKXc-DQ-',
                # Replace with secret key from environment variables
                "response": recaptcha.recaptcha,  # The reCAPTCHA token provided by the client
            }
        )
        # Parse the response JSON
        recaptcha_result = recaptcha_response.json()
        print("Recaptcha response:", recaptcha_result, flush=True)

        # Check if the verification was successful
        if recaptcha_result.get("success"):
            print("Recaptcha verified successfully.", flush=True)
            return {"message": "Recaptcha Verified"}
        else:
            # Raise an error if the reCAPTCHA verification fails
            print("Invalid reCAPTCHA", flush=True)
            raise HTTPException(status_code=400, detail="Invalid reCAPTCHA")
    except Exception as e:
        # Handle any exceptions during reCAPTCHA verification
        print("Error during reCAPTCHA verification:", e, flush=True)
        raise HTTPException(status_code=500, detail="Recaptcha Error")