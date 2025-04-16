from pydantic import BaseModel, EmailStr, Field, field_validator  # Importing Pydantic for data validation

# Users class to represent user details with validation rules
class Users(BaseModel):
    personal_email: EmailStr  # Validates personal email to ensure proper email format
    company_email: str  # Requires company email as a string without specific format validation
    password: str = Field(..., min_length=6, description="Password must contain 6 characters")
    # Password field must have at least 6 characters
    usertype: str  # A field representing the user type without validation or default value

    # Custom validator for company_email to check if the email contains '@'
    @field_validator('company_email')
    def validate_email(cls, value):
        if "@" not in value:  # Raises an error if '@' is missing in the email
            raise ValueError("Email must contain @")
        return value

    # Custom validator for password to check length and the presence of a number
    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 6:  # Ensures password is at least 6 characters long
            raise ValueError("Password is less than 6 characters")
        if not any(char.isdigit() for char in value):  # Checks if password contains at least one number
            raise ValueError("Password must contain at least 1 number")
        return value

# SignUp class to represent signup details
class SignUp(BaseModel):
    firstname: str  # First name of the user as a required field
    lastname: str  # Last name of the user as a required field
    personal_email: EmailStr  # Validates personal email for proper format
    phone_number: str  # Phone number of the user as a string
    password: str  # Password without additional validation here
    usertype: str  # User type required during signup

# LoginModel class to represent login details
class LoginModel(BaseModel):
    company_email: str  # Requires company email as a string
    password: str = Field(..., min_length=6, description="Password must contain 6 characters")
    # Password field with a minimum length requirement

# EmailSchema class for email validation
class EmailSchema(BaseModel):
    email: EmailStr  # Validates that the email provided is in a proper format

# RecaptchaSchema class to represent recaptcha response
class RecaptchaSchema(BaseModel):
    recaptcha: str  # Recaptcha response as a required string