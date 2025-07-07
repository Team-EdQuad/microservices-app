
# from fastapi import APIRouter, HTTPException, status, Query
# from app.utils.mongodb_connection import class_attendance_summery, student_attendance_summery
# from datetime import datetime



# async def fetch_attendance_summary(subject_id: str, summary_type: str, month: str = None, class_id: str = None, student_id: str = None):
#     # Fetch the document for the class
#     if student_id:
#         summary = await student_attendance_summery.find_one({"student_id": student_id})
#     else:
#         summary = await class_attendance_summery.find_one({"class_id": class_id})

#     if not summary:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="data not found"
#         )

#     # Find the subject attendance record
#     subject_record = next(
#         (record for record in summary.get("attendance", []) if record["subject_id"] == subject_id),
#         None
#     )
#     if not subject_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Subject '{subject_id}' not found."
#         )
    
#     monthly_attendance_ratios = {}
#     weekly_attendance_ratios = {}
#     daily_attendance_ratios = {}

#     current_month = subject_record.get("current_month", {}).get("month", None)

#     # Convert month names to numbers (e.g., "January" → 1, "February" → 2, etc.)
#     def month_to_number(month_name):
#         try:
#             return datetime.strptime(month_name, "%B").month  # "%B" for full month name
#         except ValueError:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid month name"
#             )

#     # Get ratio based on summary_type
#     if summary_type == "monthly":
#         # Retrieve all available months in previous_months
#         previous_months = subject_record.get("previous_months", [])

#         # Loop through each available month and get the monthly attendance ratio
#         for month_data in previous_months:
#             month_name = month_data.get("month", "")
#             if month_name:
#                 monthly_attendance_ratios[month_name] = month_data.get("monthly_attendance_ratio", None)

#         if not monthly_attendance_ratios:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No previous monthly attendance data found"
#             )

#     elif summary_type == "weekly":
#         # Retrieve weekly attendance ratios
#         if month == "all":
#             # If month is "all" or not provided, fetch weekly attendance for the entire year
#             weekly_attendance_ratios = subject_record.get("current_year", {}).get("weekday_attendance_ratio", None)
#         elif month:
#             if month_to_number(month) == month_to_number(current_month):
#                 # If current month is provided, fetch weekly attendance for the current month
#                 weekly_attendance_ratios = subject_record.get("current_month", {}).get("weekday_attendance_ratio", None)
#             elif month_to_number(month) >= month_to_number(current_month):
#                 # If month is in the future, raise an error
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="Month cannot be in the future"
#                 )
#             elif month:
#                 # If a specific month is provided, fetch weekly attendance from previous months
#                 previous_months = subject_record.get("previous_months", [])
#                 for month_data in previous_months:
#                     if month_data.get("month") == month:
#                         weekly_attendance_ratios = month_data.get("weekday_attendance_ratio", None)
#                         break

#         if not weekly_attendance_ratios:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No weekly attendance data found"
#             )

#     elif summary_type == "daily":
#         # Retrieve daily attendance records for the current or previous month
#         if month == current_month:
#             # If current month is provided, fetch daily attendance for the current month
#             daily_attendance = subject_record.get("current_month", {}).get("daily_attendance", {})
#             if student_id:
#                 daily_attendance_ratios = daily_attendance
#             else:
#                 daily_attendance_ratios = {date: data["ratio"] for date, data in daily_attendance.items()}

#         elif month_to_number(month) >= month_to_number(current_month):
#             # If month is in the future, raise an error
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Month cannot be in the future"
#             )

#         elif month:
#             # If a specific month is provided, fetch daily attendance from that month
#             previous_months = subject_record.get("previous_months", [])
#             for month_data in previous_months:
#                 if month_data.get("month") == month:
#                     daily_attendance = month_data.get("daily_attendance", {})
#                     if student_id:
#                         daily_attendance_ratios = daily_attendance
#                     else:
#                         daily_attendance_ratios = {date: data["ratio"] for date, data in daily_attendance.items()}
#                     break

#         if not daily_attendance_ratios:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="No daily attendance data found"
#             )

#     else:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid summary_type. Choose from: monthly, weekly, daily."
#         )
    
#     attendance_data = {
#         "monthly": monthly_attendance_ratios,
#         "weekly": weekly_attendance_ratios,
#         "daily": daily_attendance_ratios
#     }

#     if student_id:
#         return {
#             "student_id": student_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "result": attendance_data.get(summary_type, None)
#         }
#     else:
#         return {
#             "class_id": class_id,
#             "subject_id": subject_id,
#             "summary_type": summary_type,
#             "result": attendance_data.get(summary_type, None)
#         }


# async def get_class_academic_summary_service(class_id: str, subject_id: str, summary_type: str, month: str):
#     try:
#         result = await fetch_attendance_summary(subject_id, summary_type, month=month, class_id= class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )
    


# async def get_class_nonacademic_summary_service(class_id: str, subject_id: str, summary_type: str, month: str):
#     try:
#         result = await fetch_attendance_summary(subject_id, summary_type, month=month, class_id= class_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )
    


# async def get_student_academic_summary_service(student_id: str, subject_id: str, summary_type: str, month: str):
#     try:
#         result = await fetch_attendance_summary(subject_id, summary_type, month=month, student_id= student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )
    


# async def get_student_nonacademic_summary_service(student_id: str, subject_id: str, summary_type: str, month: str):
#     try:
#         result = await fetch_attendance_summary(subject_id, summary_type, month=month, student_id= student_id)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_academic_ratio: {str(e)}"
#         )









from fastapi import HTTPException, status
from app.utils.mongodb_connection import attendance_store
from datetime import datetime
from collections import defaultdict

async def calculate_attendance_summary(
    subject_id: str,
    summary_type: str,
    month: str = None,
    class_id: str = None,
    student_id: str = None
):
    # Filter query
    query = {"subject_id": subject_id}
    if class_id:
        query["class_id"] = class_id
    if student_id:
        query[f"status.{student_id}"] = {"$exists": True}

    records_cursor = attendance_store.find(query)
    records = await records_cursor.to_list(length=None)

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance records found."
        )

    def month_to_number(month_name):
        try:
            return datetime.strptime(month_name, "%B").month
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid month name: {month_name}"
            )

    result_data = {}

    if summary_type == "monthly":
        monthly_data = defaultdict(list)
        for record in records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            month_name = record_date.strftime("%B")
            if student_id:
                status = record["status"].get(student_id)
                if status == "present":
                    monthly_data[month_name].append(1)
                elif status == "absent":
                    monthly_data[month_name].append(0)
            else:
                monthly_data[month_name].append(record["attendance_percentage"])

        for month_name, values in monthly_data.items():
            avg_attendance = sum(values) / len(values) * 100 if student_id else sum(values) / len(values)
            result_data[month_name] = round(avg_attendance, 2)

    elif summary_type == "weekly":
        weekday_data = defaultdict(list)
        for record in records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            record_month = record_date.strftime("%B")
            if month and month != "all" and month_to_number(record_month) != month_to_number(month):
                continue

            weekday = record["weekday"]
            if student_id:
                status = record["status"].get(student_id)
                if status == "present":
                    weekday_data[weekday].append(1)
                elif status == "absent":
                    weekday_data[weekday].append(0)
            else:
                weekday_data[weekday].append(record["attendance_percentage"])

        if not weekday_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weekly attendance data found for the specified month."
            )

        for weekday, values in weekday_data.items():
            avg_attendance = sum(values) / len(values) * 100 if student_id else sum(values) / len(values)
            result_data[weekday] = round(avg_attendance, 2)

    elif summary_type == "daily":
        daily_data = {}
        for record in records:
            record_date = datetime.strptime(record["date"], "%Y-%m-%d")
            record_month = record_date.strftime("%B")
            if month and month_to_number(record_month) != month_to_number(month):
                continue

            date_str = record["date"]
            if student_id:
                status = record["status"].get(student_id)
                ratio = 100 if status == "present" else 0 if status == "absent" else None
            else:
                ratio = record["attendance_percentage"]

            if ratio is not None:
                daily_data[date_str] = ratio

        if not daily_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No daily attendance data found for the specified month."
            )

        result_data = daily_data

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid summary_type. Choose from: monthly, weekly, daily."
        )

    response = {
        "data": {
            "subject_id": subject_id,
            "summary_type": summary_type,
            "result": result_data
        }
    }
    if student_id:
        response["data"]["student_id"] = student_id
    else:
        response["data"]["class_id"] = class_id

    return response


# Service Layer
async def get_class_academic_summary_service(class_id: str, subject_id: str, summary_type: str, month: str):
    try:
        result = await calculate_attendance_summary(subject_id, summary_type, month=month, class_id=class_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


async def get_class_nonacademic_summary_service(class_id: str, subject_id: str, summary_type: str, month: str):
    try:
        result = await calculate_attendance_summary(subject_id, summary_type, month=month, class_id=class_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


async def get_student_academic_summary_service(student_id: str, subject_id: str, summary_type: str, month: str):
    try:
        result = await calculate_attendance_summary(subject_id, summary_type, month=month, student_id=student_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


async def get_student_nonacademic_summary_service(student_id: str, subject_id: str, summary_type: str, month: str):
    try:
        result = await calculate_attendance_summary(subject_id, summary_type, month=month, student_id=student_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
