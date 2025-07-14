# from fastapi import APIRouter, HTTPException, status, Query
# from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
# from datetime import datetime


# async def fetch_attendance_ratio(subject_id: str, summary_type: str, class_id: str = None, student_id: str = None):
#     if student_id:
#         summary = await student_attendance_summery.find_one({"student_id": student_id})
#     else:
#         summary = await class_attendance_summery.find_one({"class_id": class_id})

#     if not summary:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Class not found"
#         )

#     subject_record = next(
#         (record for record in summary.get("attendance", []) if record["subject_id"] == subject_id),
#         None
#     )
#     if not subject_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Subject '{subject_id}' not found in class '{class_id}'."
#         )

#     today = datetime.now().strftime("%Y-%m-%d")

#     if summary_type == "monthly":
#         ratio = subject_record.get("current_month", {}).get("monthly_attendance_ratio", None)
#     elif summary_type == "daily" and class_id:
#         ratio = subject_record.get("current_month", {}).get("daily_attendance", {}).get(today, {}).get("ratio", None)
#     elif summary_type == "yearly":
#         ratio = subject_record.get("current_year", {}).get("yearly_attendance_ratio", None)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid summary_type. Choose from: monthly, daily, yearly."
#         )

#     if ratio is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No attendance ratio found for {summary_type} summary."
#         )

#     if student_id:
#         return {
#             "student_id": student_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "attendance_ratio": ratio
#         }
#     else:
#         return {
#             "class_id": class_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "attendance_ratio": ratio
#         }
    

# async def get_class_academic_ratio_service(class_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )


# async def get_class_nonacademic_ratio_service(class_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
#         )


# async def get_student_academic_ratio_service(student_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )


# async def get_student_nonacademic_ratio_service(student_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
#         )






# from fastapi import APIRouter, HTTPException, status, Query
# from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
# from datetime import datetime


# async def fetch_attendance_ratio(subject_id: str, summary_type: str, class_id: str = None, student_id: str = None):
#     if student_id:
#         summary = await student_attendance_summery.find_one({"student_id": student_id})
#     else:
#         summary = await class_attendance_summery.find_one({"class_id": class_id})

#     if not summary:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Class not found"
#         )

#     subject_record = next(
#         (record for record in summary.get("attendance", []) if record["subject_id"] == subject_id),
#         None
#     )
#     if not subject_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Subject '{subject_id}' not found in class '{class_id}'."
#         )

#     today = datetime.now().strftime("%Y-%m-%d")

#     if summary_type == "monthly":
#         ratio = subject_record.get("current_month", {}).get("monthly_attendance_ratio", None)
#     elif summary_type == "daily" and class_id:
#         ratio = subject_record.get("current_month", {}).get("daily_attendance", {}).get(today, {}).get("ratio", None)
#     elif summary_type == "yearly":
#         ratio = subject_record.get("current_year", {}).get("yearly_attendance_ratio", None)
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid summary_type. Choose from: monthly, daily, yearly."
#         )

#     if ratio is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"No attendance ratio found for {summary_type} summary."
#         )

#     if student_id:
#         return {
#             "student_id": student_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "attendance_ratio": ratio
#         }
#     else:
#         return {
#             "class_id": class_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "attendance_ratio": ratio
#         }
    

# async def get_class_academic_ratio_service(class_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )


# async def get_class_nonacademic_ratio_service(class_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, class_id=class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
#         )


# async def get_student_academic_ratio_service(student_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )


# async def get_student_nonacademic_ratio_service(student_id: str, subject_id: str, summary_type: str):
#     try:
#         result = await fetch_attendance_ratio(subject_id, summary_type, student_id=student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
#         )









from fastapi import HTTPException, status
from app.utils.mongodb_connection import class_attendance_summery, attendance_store
from datetime import datetime

async def calculate_attendance_ratio(subject_id: str, summary_type: str, class_id: str = None, student_id: str = None):
    """
    Calculates attendance ratio for the given subject and summary_type.
    Handles both class-level and student-level queries.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")
    current_year = datetime.now().strftime("%Y")

    query = {"subject_id": subject_id}

    if student_id is None and class_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="class_id is required for class-level calculations."
        )

    if student_id is None and class_id:
        query["class_id"] = class_id

    records_cursor = attendance_store.find(query)
    records = await records_cursor.to_list(length=None)

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for subject '{subject_id}'."
        )

    if summary_type == "daily":
        filtered_records = [r for r in records if r.get("date") == today]
        period = today
    elif summary_type == "monthly":
        filtered_records = [r for r in records if r.get("date", "").startswith(current_month)]
        period = current_month
    elif summary_type == "yearly":
        filtered_records = [r for r in records if r.get("date", "").startswith(current_year)]
        period = current_year
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid summary_type. Choose from: daily, monthly, yearly."
        )

    if not filtered_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance data found for the given period '{period}'."
        )

    if student_id:
        # Corrected student-level attendance ratio logic
        total_days = len(filtered_records)
        present_days = 0
        t_days = 0

        for record in filtered_records:
            status_dict = record.get("status", {})
            student_status = status_dict.get(student_id, "").strip().lower()
            if student_status == "present":
                present_days += 1
                t_days += 1
            elif student_status == "absent":
                t_days += 1
            # If missing or not 'present', considered absent

        ratio = round((present_days / t_days) * 100, 2)
        print(f"present_days: {present_days}, total_days: {t_days}, ratio: {ratio}")

        result = {
            "subject_id": subject_id,
            "summary_type": summary_type,
            "student_id": student_id,
            "attendance_ratio": ratio
        }

    else:
        # Class-level logic remains the same
        total_percentage = 0
        count = 0

        for record in filtered_records:
            status_dict = record.get("status", {})
            total_students = len(status_dict)
            if total_students == 0:
                continue

            present_count = sum(1 for status in status_dict.values() if status.strip().lower() == "present")
            attendance_percentage = (present_count / total_students)
            # attendance_percentage = (present_count / total_students) * 100
            total_percentage += attendance_percentage
            count += 1

        if count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No valid attendance data found for the given period '{period}'."
            )

        ratio = round(total_percentage / count, 2)

        result = {
            "subject_id": subject_id,
            "summary_type": summary_type,
            "class_id": class_id,
            "attendance_ratio": ratio
        }

    return result


# The rest of the code remains the same — you just need to update the function calls:
# Replace fetch_attendance_ratio(...) with calculate_attendance_ratio(...)
# Example:
async def get_class_academic_ratio_service(class_id: str, subject_id: str, summary_type: str):
    try:
        result = await calculate_attendance_ratio(subject_id, summary_type, class_id=class_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_academic_ratio: {str(e)}"
        )

async def get_class_nonacademic_ratio_service(class_id: str, subject_id: str, summary_type: str):
    try:
        result = await calculate_attendance_ratio(subject_id, summary_type, class_id=class_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
        )


async def get_student_academic_ratio_service(student_id: str, subject_id: str, summary_type: str):
    try:
        result = await calculate_attendance_ratio(subject_id, summary_type, student_id=student_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_academic_ratio: {str(e)}"
        )


async def get_student_nonacademic_ratio_service(student_id: str, subject_id: str, summary_type: str):
    try:
        result = await calculate_attendance_ratio(subject_id, summary_type, student_id=student_id)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_nonacademic_ratio: {str(e)}"
        )