import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import boto3

app = FastAPI()

# Clients
mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = mongo_client.file_database
s3_client = boto3.client('s3')

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

@app.post("/api/files/delete-one")
async def delete_one_file(payload: dict):
    file_id = payload.get("fileId")
    if not file_id:
        raise HTTPException(status_code=400, detail="Missing fileId")

    # 1. Fetch file from MongoDB
    file = await db.files.find_one({"_id": ObjectId(file_id)})
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        if file["status"] == "uploading":
            # 2. Cancel mid-flight chunked upload
            s3_client.abort_multipart_upload(
                Bucket=BUCKET_NAME,
                Key=file["key"],
                UploadId=file["uploadId"]
            )
        elif file["status"] == "completed":
            # 3. Delete standard finished file
            s3_client.delete_object(
                Bucket=BUCKET_NAME,
                Key=file["key"]
            )

        # 4. Clean up DB
        await db.files.delete_one({"_id": ObjectId(file_id)})
        return {"success": True, "message": f"Successfully removed {file['key']}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))