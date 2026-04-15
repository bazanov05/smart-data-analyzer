from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import pandas as pd
from app.services.analyzer import AML_System
from fastapi.concurrency import run_in_threadpool  # for pd.read_csv()
from app.db.database import get_db
from app.db.repository import (
    get_structuring_attempt_report_by_id,
    get_geographical_inflow_report_by_id,
    get_high_velocity_transfer_report_by_id,
    get_unverified_originator_report_by_id,
    get_all_raw_data,
    create_geographical_inflow_report,
    create_high_velocity_transfer_report,
    create_structuring_attempt_report,
    create_unverified_originator_report,
    create_raw_data_report
)
from app.db.schemas import (
    StructuringAttemptResponse,
    UnverifiedOriginatorResponse,
    GeographicalInflowResponse,
    HighVelocityTransferResponse,
    RawDataResponse
)
from sqlalchemy.orm import Session
from datetime import timedelta


app = FastAPI()
REQUIRED_COLUMNS = {'transaction_id', 'sender_id', 'receiver_id', 'amount', 'country', 'type', 'timestamp'}


def _save_report_with_timestamp(func_to_create, db, reports: list):
    """
    Recieves a func as a first argument, which makes it reusable
    Converts Pandas Timestamp to Python datetime before saving — SQLite rejects Pandas types
    Returns a list of saved database objects with generated id and created_at
    """
    saved = []
    for report in reports:
        if "timestamp" in report:
            if "timegap" in report:
                report["timegap"] = str(report["timegap"])
            report["timestamp"] = report['timestamp'].to_pydatetime()
            new_report = func_to_create(db, report)
            if new_report is not None:
                saved.append(new_report)
    return saved


@app.post("/update")
async def upload_a_csv_file(file: UploadFile = File(...), db=Depends(get_db)):
    """
    Accepts a CSV file, runs all four AML analyses and saves results to the database.
    Validates file type and required columns before processing.
    Returns all four saved report sets as a JSON response.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=415, detail="Unsupported media type")  # program supports only csv files

    #  pandas is not async so run_in_threadpool prevents blocking the entire API
    df = await run_in_threadpool(pd.read_csv, file.file)

    cols_in_df = set(df.columns)
    missing_cols = REQUIRED_COLUMNS - cols_in_df
    if len(missing_cols) != 0:
        raise HTTPException(status_code=400, detail=list(missing_cols))

    # convert to pandas TimeStamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    aml = AML_System(df)

    raw_data = df.fillna("None").to_dict(orient="records")
    structuring_attemps = aml.detect_structuring_attempts(timedelta(hours=1)).fillna("None").to_dict(orient='records')
    unverified_originators = aml.identify_unverified_originators().fillna("Unverified").to_dict(orient="records")
    geographic_inflows = aml.aggregate_geographic_inflow().to_dict(orient="records")
    high_velocity_transfers = aml.detect_high_velocity_transfers(timedelta(hours=1), 5).to_dict(orient="records")

    saved_struct_attempt_reports = _save_report_with_timestamp(create_structuring_attempt_report, db, structuring_attemps)
    saved_unver_org_reports = _save_report_with_timestamp(create_unverified_originator_report, db, unverified_originators)
    saved_velocity_transfers_reports = _save_report_with_timestamp(create_high_velocity_transfer_report, db, high_velocity_transfers)
    saved_raw_data = _save_report_with_timestamp(create_raw_data_report, db, raw_data)

    # geographical inflow has different shape — no transaction details, just country and total amount
    # so it cannot go through _save_report_with_timestamp

    saved_geo_inflow_reports = []
    for data in geographic_inflows:
        new_report = create_geographical_inflow_report(db, data)
        if new_report is not None:
            saved_geo_inflow_reports.append(new_report)

    result = {
        "Raw_data": [
            RawDataResponse.model_validate(r).model_dump() for r in saved_raw_data
        ],
        "structuring_attempts": [
            StructuringAttemptResponse.model_validate(r).model_dump() for r in saved_struct_attempt_reports
        ],
        "unverified_originators": [
           UnverifiedOriginatorResponse.model_validate(r).model_dump() for r in saved_unver_org_reports
        ],
        "geographical_inflows": saved_geo_inflow_reports,
        "high_velocity_transfers": [
            HighVelocityTransferResponse.model_validate(r).model_dump() for r in saved_velocity_transfers_reports
        ]
    }
    return result


@app.get("/reports/structuring_attempt/{report_id}", response_model=StructuringAttemptResponse)
def get_structuring_attempt(report_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single structuring attempt report by its internal database id.
    Returns 404 if no report with the given id exists.
    """
    report = get_structuring_attempt_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/unverified_originator/{report_id}", response_model=UnverifiedOriginatorResponse)
def get_unverified_originator(report_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single unverified originator report by its internal database id.
    Returns 404 if no report with the given id exists.
    """
    report = get_unverified_originator_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/geographical_inflow/{report_id}", response_model=GeographicalInflowResponse)
def get_geographical_inflow(report_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single geographical inflow report by its internal database id.
    Returns 404 if no report with the given id exists.
    """
    report = get_geographical_inflow_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/high_velocity_transfer/{report_id}", response_model=HighVelocityTransferResponse)
def get_high_velocity_transfer(report_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single high velocity transfer report by its internal database id.
    Returns 404 if no report with the given id exists.
    """
    report = get_high_velocity_transfer_report_by_id(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report


@app.get("/reports/raw_data/{report_id}", response_model=RawDataResponse)
def get_raw_data_report(report_id: int, db: Session = Depends(get_db)):
    """
    Fetches a single raw data report by its internal database id.
    Returns 404 if no report with the given id exists.
    """
    report = get_raw_data_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report with this id does not exist")
    return report
