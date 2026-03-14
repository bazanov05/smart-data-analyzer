from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import io
from app.services.analyzer import AML_System


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type'}


@app.post("/update")
async def upload_a_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=415, detail="Unsupported media type")
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    cols_in_df = set(df.columns)
    missing_cols = REQUIRED_COLUMNS - cols_in_df
    if len(missing_cols) != 0:
        raise HTTPException(status_code=400, detail=missing_cols)
    aml = AML_System(df)
    structuring_attemps = aml.detect_structuring_attempts().fillna("None").to_dict(orient='records')
    unverified_originators = aml.identify_unverified_originators().fillna("None").to_dict(orient='records')
    geografical_inflow = aml.aggregate_geographic_inflow().to_dict()
    result = {
        "structuring_attemps": structuring_attemps,
        "unverified_originators": unverified_originators,
        "geografical_inflow": geografical_inflow
    }
    return result
