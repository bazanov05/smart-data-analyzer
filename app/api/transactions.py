from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import pandas as pd
from app.services.analyzer import AML_System
from fastapi.concurrency import run_in_threadpool  # for pd.read_csv()
from app.db.database import get_db
from app.db.repository import(
    get_structuring_attempt_report_by_id,
    get_geographical_inflow_report_by_id,
    get_high_velocity_transfer_report_by_id,
    get_unverified_originator_report_by_id
)
from app.db.schemas import(
    StructuringAttemptResponse,
    UnverifiedOriginatorResponse,
    GeographicalInflowResponse,
    HighVelocityTransferResponse
)
from sqlalchemy.orm import Session


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type', 'timestamp'}


def _save_report_with_timestamp(db, reports: list):
    """
    Saves reports with timestamp in db
    """
    saved = []
    for report in reports:
        if "timestamp" in report:
            report["timestamp"] = report['timestamp'].to_pydatetime()
            new_report = create_report(db, report)
            saved.append(new_report)
    return saved


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

    saved_struct_attempt_reports = _save_report_with_timestamp(db, structuring_attemps)

    saved_unver_org_reports = _save_report_with_timestamp(db, unverified_originators)

    saved_velocity_transfers_reports = _save_report_with_timestamp(db, high_velocity_transfers)

    result = {
        "structuring_attempts": saved_struct_attempt_reports,
        "unverified_originators": saved_unver_org_reports,
        "geographi_inflows": geographic_inflows,
        "high_velocity_transfers": saved_velocity_transfers_reports

    }
    return result


@app.get("/reports/structuring_attempt/{report_id}", response_model=StructuringAttemptResponse)
def get_structuring_attempt(report_id: int, db: Session = Depends(get_db)):
    report = get_structuring_attempt_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/unverified_originator/{report_id}", response_model=UnverifiedOriginatorResponse)
def get_unverified_originator(report_id: int, db: Session = Depends(get_db)):
    report = get_unverified_originator_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/geographical_inflow/{report_id}", response_model=GeographicalInflowResponse)
def get_geographical_inflow(report_id: int, db: Session = Depends(get_db)):
    report = get_geographical_inflow_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/high_velocity_transfer/{report_id}", response_model=HighVelocityTransferResponse)
def get_high_velocity_transfer(report_id: int, db: Session = Depends(get_db)):
    report = get_high_velocity_transfer_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report
