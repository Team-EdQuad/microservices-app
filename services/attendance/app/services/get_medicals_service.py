from fastapi import APIRouter, HTTPException, status, Query
from app.utils.mongodb_connection import document_store  # your MongoDB collection
from bson import ObjectId


async def get_medicals_service(class_id: str, subject_id: str, student_id: str):
    try:
        # Create dynamic query filter
        query = {}
        if class_id != "all":
            query["class_id"] = class_id
        if subject_id != "all":
            query["subject_id"] = subject_id
        if student_id != "all":
            query["student_id"] = student_id

        def convert_objectid(doc):
            doc["_id"] = str(doc["_id"])  # convert ObjectId to str
            return doc

        documents = await document_store.find(query).to_list(length=100)
        formatted_docs = [convert_objectid(doc) for doc in documents]

        return {"data": formatted_docs}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred in get_documents: {str(e)}"
        )
