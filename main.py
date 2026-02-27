from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uuid
import os

app = FastAPI()

# Allow Bolt frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "FastAPI running"}

@app.post("/datasets")
async def upload_dataset(file: UploadFile = File(...)):
    dataset_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    df = pd.read_csv(file_path)

    return {
        "dataset_id": dataset_id,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns)
    }

@app.get("/datasets/{dataset_id}/profile")
def profile_dataset(dataset_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{dataset_id}.csv")

    df = pd.read_csv(file_path)

    profile = []
    for col in df.columns:
        profile.append({
            "name": col,
            "null_pct": float(df[col].isna().mean() * 100),
            "unique_count": int(df[col].nunique()),
            "dtype": str(df[col].dtype)
        })

    return {"columns": profile}
