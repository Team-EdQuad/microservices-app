# from fastapi import HTTPException, status
# from app.utils.mongodb_connection import class_attendance_summery
# from datetime import datetime


# async def fetch_attendance_summary(class_id: str, subject_id: str, date: str):
#     # Fetch the document for the class
#     class_summary = await class_attendance_summery.find_one({"class_id": class_id})
#     if not class_summary:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Class not found"
#         )

#     # Find the subject attendance record
#     subject_record = next(
#         (record for record in class_summary.get("attendance", []) if record["subject_id"] == subject_id),
#         None
#     )
#     if not subject_record:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Subject '{subject_id}' not found in class '{class_id}'"
#         )
    
#     def month_to_number(month_name):
#         try:
#             return datetime.strptime(month_name, "%B").month  # "%B" for full month name
#         except ValueError:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Invalid month name"
#             )

#     try:
#         # Extract and format month from date
#         month_num = date.split("-")[1]  # Extract month number (e.g., "05")
#         month_name = datetime.strptime(month_num, "%m").strftime("%B")  # Convert to "May"
        
#         # Get current month from record and ensure same format
#         current_month = subject_record.get("current_month", {}).get("month")
#         if current_month and current_month.isdigit():  # If stored as "05"
#             current_month_name = datetime.strptime(current_month, "%m").strftime("%B")
#         else:
#             current_month_name = current_month  # Assume already in "May" format

#         if month_name == current_month_name:
#             daily_attendance = subject_record.get("current_month", {}).get("daily_attendance", {})
#             status = daily_attendance.get(date, {}).get("status", None)
#             if status is None:
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"No attendance record found for date {date} in current month"
#                 )
        
#         elif month_to_number(month_name) < month_to_number(current_month_name):
#             previous_months = subject_record.get("previous_months", [])
#             for month_data in previous_months:
#                 # Compare month numbers to avoid format issues
#                 month_data_num = datetime.strptime(month_data.get("month"), "%B").month
#                 if month_data_num == datetime.strptime(month_name, "%B").month:
#                     daily_attendance = month_data.get("daily_attendance", {})
#                     status = daily_attendance.get(date, {}).get("status", None)
#                     if status is None:
#                         raise HTTPException(
#                             status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"No attendance record found for date {date} in previous months"
#                         )
#                     break
#             else:  # If loop completes without finding the month
#                 raise HTTPException(
#                     status_code=status.HTTP_404_NOT_FOUND,
#                     detail=f"No attendance data found for month {month_name} in previous records"
#                 )
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Month {month_name} is in the future or invalid"
#             )
        
#         return {
#             "class_id": class_id,
#             "subject_id": subject_id,
#             "date": date,
#             "result": status
#         }
    
#     except HTTPException:
#         raise  # Re-raise HTTPExceptions we've created
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid date or month format: {str(e)}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred while fetching attendance: {str(e)}"
#         )



# async def get_class_history_service(class_id: str, subject_id: str, date: str):
#     try:
#         result = await fetch_attendance_summary(class_id, subject_id, date)
#         return {"data": result}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred in get_history_of_class: {str(e)}"
#         )






from fastapi import HTTPException, status
from app.utils.mongodb_connection import class_attendance_summery
from datetime import datetime


async def calculate_attendance_summary(class_id: str, subject_id: str, date: str):
    """
    Calculate attendance summary for a given class, subject, and date.
    Returns all students' attendance status.
    """
    # Fetch the class summary
    class_summary = await class_attendance_summery.find_one({"class_id": class_id})
    if not class_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found"
        )

    # Find the subject record
    subject_record = next(
        (record for record in class_summary.get("attendance", []) if record["subject_id"] == subject_id),
        None
    )
    if not subject_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject_id}' not found in class '{class_id}'"
        )

    try:
        # Extract month name from the given date
        month_num = int(date.split("-")[1])
        month_name = datetime.strptime(str(month_num), "%m").strftime("%B")

        # Check current month
        current_month_data = subject_record.get("current_month")
        if current_month_data and current_month_data.get("month") == month_name:
            daily_attendance = current_month_data.get("daily_attendance", {})
            day_record = daily_attendance.get(date)
            if day_record is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No attendance record found for date {date} in current month"
                )
            return {
                "class_id": class_id,
                "subject_id": subject_id,
                "date": date,
                "result": day_record  # Directly return status dictionary
            }

        # Check previous months
        for prev_month_data in subject_record.get("previous_months", []):
            if prev_month_data.get("month") == month_name:
                daily_attendance = prev_month_data.get("daily_attendance", {})
                day_record = daily_attendance.get(date)
                if day_record is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No attendance record found for date {date} in previous months"
                    )
                return {
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "date": date,
                    "result": day_record  # Directly return status dictionary
                }

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance record found for date {date}"
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected YYYY-MM-DD."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching attendance: {str(e)}"
        )


async def get_class_history_service(class_id: str, subject_id: str, date: str):
    """
    Service to get the attendance history of a class.
    """
    try:
        result = await calculate_attendance_summary(class_id, subject_id, date)
        return {"data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_class_history_service: {str(e)}"
        )
