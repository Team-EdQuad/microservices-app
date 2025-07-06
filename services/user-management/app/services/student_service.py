from fastapi import HTTPException
from datetime import datetime
from app.db.database import db
from app.models.student_model import StudentRegistration
import bcrypt  # for password hashing (Install it using pip install bcrypt)
from datetime import datetime, time, date

async def register_student(student: StudentRegistration):
    student_collection = db["student"]
    teacher_collection = db["teacher"]
    admin_collection = db["admin"]
    subjects_collection = db["subject"]

    # Subject count validation
    # subject_count = len(student.subject)
    # if 1 <= student.grade <= 9 and subject_count != 12:
    #     raise HTTPException(status_code=400, detail="Grades 1–9 require exactly 12 subjects.")
    # elif 10 <= student.grade <= 11 and subject_count != 9:
    #     raise HTTPException(status_code=400, detail="Grades 10–11 require exactly 9 subjects.")
    # elif 12 <= student.grade <= 13 and subject_count != 4:
    #     raise HTTPException(status_code=400, detail="Grades 12–13 require exactly 4 subjects.")

    # Check for existing student_id/email/phone in all collections
    for collection in [student_collection, teacher_collection, admin_collection]:
        if await collection.find_one({"student_id": student.student_id}):
            raise HTTPException(status_code=400, detail="Student ID already exists.")
        if await collection.find_one({"email": student.email}):
            raise HTTPException(status_code=400, detail="Email already exists.")
        if await collection.find_one({"phone_no": student.phone_no}):
            raise HTTPException(status_code=400, detail="Phone number already exists.")

    # Hash password (using bcrypt)
    # hashed_password = bcrypt.hashpw(student.password.encode('utf-8'), bcrypt.gensalt())  # Hash the password
    student_data = student.dict()
    # student_data["password"] = hashed_password.decode('utf-8')  # Store the hashed password
    student_data["password"] = student.password  # Store the plain password (not recommended for production)
    student_data["full_name"] = f"{student.first_name} {student.last_name}"
    student_data["join_date"] = datetime.utcnow().date().isoformat()
    student_data["last_edit_date"] = datetime.utcnow().date().isoformat()
    
    for date_field in ["join_date", "last_edit_date"]:
        if date_field in student_data and isinstance(student_data[date_field], date):
            student_data[date_field] = datetime.combine(student_data[date_field], time.min)

    try:
        # Insert student into the database
        result = await student_collection.insert_one(student_data)
        if result.inserted_id:
            student_data["_id"] = str(result.inserted_id)

            # Update subject-student relationship
            for subject_id in student.subject:
                await subjects_collection.update_one(
                    {"subject_id": subject_id},
                    {"$addToSet": {"students": student.student_id}},
                    upsert=True
                )

            return {"message": "Student registered successfully", "student": student_data}
        else:
            raise HTTPException(status_code=500, detail="Failed to register student")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def get_user_by_email(email: str):
    student_collection = db["student"]
    student = await student_collection.find_one({"email": email})
    if student:
        student["_id"] = str(student["_id"])
    return student
