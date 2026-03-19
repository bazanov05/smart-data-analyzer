from db.models import AmlReport
from sqlalchemy.orm import Session


def create_report(db: Session, data: dict):
    """
    Adds a new AML report to the database.
    Returns the created report with generated id and created_at.
    Rolls back the session and raises the exception if commit fails.
    """
    try:
        new_aml_report = AmlReport(**data)  # creating Python object, it does not check and validate anything
        db.add(new_aml_report)
        db.commit()  # here validation happens
        db.refresh(new_aml_report)  # to have new_aml_report with id and created_at attributes
        return new_aml_report
    except Exception as e:
        db.rollback()  # cleans the session after failed operations
        raise e


def get_report_by_id(db: Session, report_id: int):
    """
    Fetches a single AML report by its internal database id.
    Returns None if no report with the given id exists.
    """
    return db.query(AmlReport).filter(AmlReport.id == report_id).first()
