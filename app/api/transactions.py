from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
from app.services.analyzer import AML_System
from fastapi.concurrency import run_in_threadpool


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type'}


@app.post("/update")
async def upload_a_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=415, detail="Unsupported media type")
    df = await run_in_threadpool(pd.read_csv, file.file)  # send it to thread so API is not blocked
    cols_in_df = set(df.columns)
    missing_cols = REQUIRED_COLUMNS - cols_in_df
    if len(missing_cols) != 0:
        raise HTTPException(status_code=400, detail=list(missing_cols))
    aml = AML_System(df)
    structuring_attemps = aml.detect_structuring_attempts().fillna("None").to_dict(orient='records')
    unverified_originators = aml.identify_unverified_originators().fillna("None").to_dict(orient='records')
    geografical_inflow = aml.aggregate_geographic_inflow().to_dict()
    high_velocity = aml.detect_high_velocity_transfers().astype(str).to_dict(orient='records')

    result = {
        "structuring_attempts": structuring_attemps,
        "unverified_originators": unverified_originators,
        "geographical_inflow": geografical_inflow,
        "high_velocity_transfers": high_velocity
    }
    return result
