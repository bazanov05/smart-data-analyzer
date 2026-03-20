from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import pandas as pd
from app.services.analyzer import AML_System
from fastapi.concurrency import run_in_threadpool  # for pd.read_csv()
from db.database import get_db
from db.repository import create_report


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type'}


@app.post("/update")
async def upload_a_csv_file(file: UploadFile = File(...), db=Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=415, detail="Unsupported media type")  # program supports only csv files

    #  pandas is inawaitable so i use run_in_threadpool
    #  API will not be blocked
    df = await run_in_threadpool(pd.read_csv, file.file)

    cols_in_df = set(df.columns)
    missing_cols = REQUIRED_COLUMNS - cols_in_df
    if len(missing_cols) != 0:
        raise HTTPException(status_code=400, detail=list(missing_cols))

    aml = AML_System(df)
    structuring_attemps = aml.detect_structuring_attempts().fillna("None").to_dict(orient='records')
    for structuring_attempt in structuring_attemps:
        create_report(db, structuring_attempt)

    result = {
        "structuring_attempts": structuring_attemps
    }
    return result
