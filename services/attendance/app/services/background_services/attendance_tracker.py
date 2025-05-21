from motor.motor_asyncio import AsyncIOMotorCollection
from .attendance_summary_process import attendance_summary_process

from app.services.delete_class_attendance_service import attendance_delete_cache

async def attendance_tracker(attendance_store: AsyncIOMotorCollection):
    pipeline = [
        {'$match': {'operationType': {'$in': ['insert', 'update', 'delete']}}}
    ]
    
    async with attendance_store.watch(pipeline, full_document="updateLookup") as stream:
        async for change in stream:
            operation_type = change.get("operationType")

            if operation_type in ['insert', 'update']:
                full_doc = change.get('fullDocument')
                if full_doc:
                    class_id = full_doc.get('class_id')
                    subject_id = full_doc.get('subject_id')
                    date = full_doc.get('date')
                    status = full_doc.get('status')

                    if class_id and subject_id and isinstance(status, dict):
                        print(f"Updating attendance summary for class_id: {class_id}, subject_id: {subject_id}, date: {date}")
                        await attendance_summary_process(class_id, subject_id, date)

                        # Loop through each student
                        for student_id in status:
                            print(f"Updating attendance summary for student_id: {student_id}, class_id: {class_id}, subject_id: {subject_id}, date: {date}")
                            await attendance_summary_process(class_id, subject_id, date, student_id=student_id)
                        
                        print(f"Attendance summary updated for class_id: {class_id}, subject_id: {subject_id}, date: {date}")


            elif operation_type == 'delete':
                document_id = change.get("documentKey", {}).get("_id")
                if document_id:
                    cached = attendance_delete_cache.pop(str(document_id), None)
                    if cached:
                        class_id = cached["class_id"]
                        subject_id = cached["subject_id"]
                        date = cached["date"]

                        print(f"Cache Data for class_id: {class_id}, subject_id: {subject_id}, date: {date}")
                        await attendance_summary_process(class_id, subject_id, date)

                        for student_id in cached["status"]:
                            print(f"Updating attendance summary for student_id: {student_id}, class_id: {class_id}, subject_id: {subject_id}, date: {date}")
                            await attendance_summary_process(class_id, subject_id, date, student_id=student_id)
                    else:
                        print(f"No cached data found for deleted document {document_id}")
