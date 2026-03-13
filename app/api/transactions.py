from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io
from app.services.analyzer import AML_System


app = FastAPI()


@app.post("/update")
async def upload_a_csv_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        return {"Error": "not csv format"}
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
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
