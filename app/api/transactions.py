from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import pandas as pd
from app.services.analyzer import AML_System
from fastapi.concurrency import run_in_threadpool  # for pd.read_csv()
from app.db.database import get_db
from app.db.repository import create_report, get_report_by_id
from app.db.schemas import AmlReportResponse
from sqlalchemy.orm import Session


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type', 'timestamp'}


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
    unverified_originators = aml.identify_unverified_originators().fillna("Unverified").to_dict(orient="records")
    geographic_inflows = aml.aggregate_geographic_inflow().to_dict()
    high_velocity_transfers = aml.detect_high_velocity_transfers().to_dict(orient="records")

    saved_struct_attempt_reports = []
    for structuring_attempt in structuring_attemps:
        new_report = create_report(db, structuring_attempt)
        saved_struct_attempt_reports.append(new_report)

    saved_unver_org_reports = []
    for unverified_originator in unverified_originators:
        new_report = create_report(db, unverified_originator)
        saved_unver_org_reports.append(new_report)

    saved_geo_inflow_reports = []
    for geographic_inflow in geographic_inflows:
        new_report = create_report(db, geographic_inflow)
        saved_geo_inflow_reports.append(new_report)

    saved_velocity_transfers_reports = []
    for high_velocity_transfer in high_velocity_transfers:
        new_report = create_report(db, high_velocity_transfer)
        saved_velocity_transfers_reports.append(new_report)

    result = {
        "structuring_attempts": saved_struct_attempt_reports,
        "unverified_originators": saved_unver_org_reports,
        "geographi_inflows": saved_geo_inflow_reports,
        "high_velocity_transfers": saved_velocity_transfers_reports

    }
    return result


@app.get("/reports/{report_id}", response_model=AmlReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = get_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
