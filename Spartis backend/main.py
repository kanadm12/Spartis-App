from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks, Request

import shutil
import uuid
import os
from pathlib import Path
import mimetypes
from typing import Dict, Union
from azure.storage.blob.aio import BlobServiceClient

from kv_helpers import set_progress, get_progress_from_kv, set_progress_sync
from pipeline import full_pipeline
from viewer import view_stl

app = FastAPI(title="NIfTI to Mesh Pipeline API")

# --- Azure Blob Storage Configuration ---
# WARNING: For production, use environment variables or Azure Key Vault, not hardcoded strings.
BLOB_CONNECTION_STRING: str = (
    "DefaultEndpointsProtocol=https;AccountName=spartis9488473038;"
    "AccountKey=WxiLwTEm+WEut0AIFRTLiWcXgHhDixXtYtF5gbbGIKLMWANt5wHOVwg/"
    "QzRgz2uG1CHcazDil58i+ASttN+yaA==;EndpointSuffix=core.windows.net"
)
CONTAINER_NAME: str = "azureml-blobstore-d58bdc01-dd56-4b93-815a-7c70b6e606d6"
UPLOAD_FOLDER_NAME: str = "app_uploaded_data"

# Ensure .stl files are served with the correct media type.
# Some systems may not have this mimetype registered by default.
mimetypes.add_type("model/stl", ".stl")

# Vercel has a read-only filesystem, except for the /tmp directory.
TMP_DIR = "/tmp"
UPLOAD_DIR = os.path.join(TMP_DIR, "uploads")
OUTPUT_DIR = os.path.join(TMP_DIR, "outputs")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Allow frontend requests (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Limit this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def upload_to_blob(file_path: str, original_filename: str):
    """
    Uploads a file to Azure Blob Storage.
    """
    if not BLOB_CONNECTION_STRING:
        print("⚠️ BLOB_CONNECTION_STRING is not set. Skipping blob upload.")
        return

    blob_name = f"{UPLOAD_FOLDER_NAME}/{original_filename}"
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
        async with blob_service_client:
            container_client = blob_service_client.get_container_client(CONTAINER_NAME)
            
            print(f"Uploading to Azure Blob Storage as blob:\n\t{blob_name}")
            
            with open(file_path, "rb") as data:
                await container_client.upload_blob(name=blob_name, data=data, overwrite=True)
                
            print(f"✅ Upload successful for {original_filename}")

    except Exception as e:
        print(f"❌ Failed to upload to Azure Blob Storage: {e}")

@app.post("/api/process-nifti/")
async def process_nifti_file(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks(), request: Request = None):
    if not file.filename.endswith(".nii.gz"):
        raise HTTPException(status_code=400, detail="Only .nii.gz files are supported.")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize progress
    await set_progress(file_id, {"step": "Uploading", "progress": 0})

    # --- Upload to Azure Blob Storage ---
    # We add this as a background task so it doesn't block the initial response to the user.
    background_tasks.add_task(upload_to_blob, input_path, file.filename)

    background_tasks.add_task(run_pipeline_async, input_path, file_id)

    return {"file_id": file_id}

async def run_pipeline_async(input_path: str, file_id: str) -> str:
    from asyncio import to_thread

    def on_progress(step: str, percent: int):
        print(f"[{file_id}] Progress: {step} - {percent}%")  # Optional debug print
        set_progress_sync(file_id, {"step": step, "progress": percent})

    try:
        stl_path = await to_thread(
            # To segment bone from a CT scan, a higher threshold is needed.
            # Common Hounsfield Unit (HU) values for bone are > 250.
            # However, the error "No mesh could be created" indicates that for the current NIfTI file,
            # a threshold of 250 is too high. This often happens with segmentation masks where the target value is 1.
            lambda: full_pipeline(input_path, OUTPUT_DIR, threshold=1, file_id=file_id, progress_callback=on_progress)
        )
        print(f"stl_path: {stl_path}")
        await set_progress(file_id, {
            "step": "Completed",
            "progress": 100,
            "filename": os.path.basename(stl_path)
        })
        return stl_path
    except Exception as e:
        await set_progress(file_id, {"step": "Error", "progress": 0})
        print(f"❌ Pipeline failed for {file_id}: {e}")


@app.get("/api/progress/{file_id}")
async def get_progress(file_id: str):
    progress = await get_progress_from_kv(file_id)
    return progress or {"step": "Pending", "progress": 0}

@app.get("/api/outputs/{filename}")
async def get_output_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(file_path)

# Serve the frontend application
# This must be mounted AFTER your API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")
