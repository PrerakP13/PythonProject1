from bson import ObjectId
from fastapi import Request, Response, HTTPException, APIRouter

from database import register_collection, employee_collection
from models.users import Users

from utils.helpers import serialize_user

router = APIRouter()


@router.post("/show_user")
async def show_user(request: Request):
    user_role = request.session.get('usertype', 'manager')  # Default to 'manager' if not found
    users = []

    try:
        if user_role == 'admin':
            managers = await employee_collection.find(
                {"usertype": "manager"},
                {"name": 1, "usertype": 1, "_id": 1}
            ).to_list(length=None)
            employees = await employee_collection.find(
                {"usertype": "employee"},
                {"name": 1, "usertype": 1, "_id": 1}
            ).to_list(length=None)
            users.extend(managers)
            users.extend(employees)

        elif user_role == 'manager':
            employees = await employee_collection.find(
                {"usertype": "employee"},
                {"name": 1, "usertype": 1, "_id": 1}
            ).to_list(length=None)
            users.extend(employees)

        # Serialize all users to handle ObjectId
        serialized_users = [serialize_user(user) for user in users]

        return {"message": "Users retrieved successfully", "users": serialized_users}

    except Exception as e:
        print(f"Error retrieving users: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving users.")


@router.post("/assign_role")
async def assign_user(request:Request, user:Users):
    user_role = request.session.get('usertype', 'manager')
    existing_user = await register_collection.find_one({"email": user.personal_email})
    if not existing_user:
        print("User already exists with email:", user.email, flush=True)
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = {
        "user_id": existing_user["_id"],
        "name": existing_user["name"],
        "company_email":user.company_email,
        "password": user.password,
        "usertype": user.usertype
    }

    if user_role == 'manager' and user_role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can assign the manager role")

        # Ensure only admin or manager can assign employee role
    if user.usertype == 'employee' and user_role not in ['admin', 'manager']:
        raise HTTPException(status_code=403, detail="Only admins and managers can assign the employee role")


    await employee_collection.insert_one(user_data)

       # Send email notification to the user
    #await send_email(existing_user["email"], user.company_email, user.password)

       # Remove the user from the user_collection
    await register_collection.delete_one({"email": user.personal_email})
    return {"message":"user created successfully", "user role assigned":{user.usertype}, "created by":{user_role}}

@router.post("/unassigned_user")
async def get_unassigned_users():
    unassigned = await register_collection.find(
        {"usertype": "visitor"},
        {"email": 1, "_id": 1, "usertype":1}
    ).to_list(length=None)
    # Apply your serializer to each user in the list
    serialized_users = [serialize_user(user) for user in unassigned]
    return {"unassigned_users": serialized_users}

@router.get("/unassigned_user/{user_id}")
async def get_unassigned_user(user_id: str):
    user_doc = await register_collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": serialize_user(user_doc)}