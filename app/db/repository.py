from app.db.models import (
    StructuringAttempt,
    UnverifiedOriginator,
    HighVelocityTransfer,
    GeographicalInflow,
    RawData,
    AISummary
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def create_structuring_attempt_report(db: Session, data: dict) -> StructuringAttempt:
    """
    Saves a structuring attempt to the database.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_structuring_attempt_report = StructuringAttempt(**data)
        db.add(new_structuring_attempt_report)
        db.commit()
        db.refresh(new_structuring_attempt_report)
        return new_structuring_attempt_report

    # catching this error allows us to ignore the duplicates
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def create_unverified_originator_report(db: Session, data: dict) -> UnverifiedOriginator:
    """
    Saves an unverified originator transaction to the database.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_unverified_originator_report = UnverifiedOriginator(**data)
        db.add(new_unverified_originator_report)
        db.commit()
        db.refresh(new_unverified_originator_report)
        return new_unverified_originator_report
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def create_high_velocity_transfer_report(db: Session, data: dict) -> HighVelocityTransfer:
    """
    Saves a high velocity transfer to the database.
    Expects timegap field in data representing time between transactions.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_high_velocity_transfer_report = HighVelocityTransfer(**data)
        db.add(new_high_velocity_transfer_report)
        db.commit()
        db.refresh(new_high_velocity_transfer_report)
        return new_high_velocity_transfer_report
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def create_geographical_inflow_report(db: Session, data: dict) -> GeographicalInflow:
    """
    Saves a geographical inflow aggregation to the database.
    Expects only country and inflow fields — no transaction details.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_geographical_inflow_report = GeographicalInflow(**data)
        db.add(new_geographical_inflow_report)
        db.commit()
        db.refresh(new_geographical_inflow_report)
        return new_geographical_inflow_report
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def get_structuring_attempt_report_by_id(db: Session, report_id: int):
    """Returns a structuring attempt by id, or None if not found."""
    return db.query(StructuringAttempt).filter(StructuringAttempt.id == report_id).first()


def get_unverified_originator_report_by_id(db: Session, report_id: int):
    """Returns an unverified originator report by id, or None if not found."""
    return db.query(UnverifiedOriginator).filter(UnverifiedOriginator.id == report_id).first()


def get_high_velocity_transfer_report_by_id(db: Session, report_id: int):
    """Returns a high velocity transfer report by id, or None if not found."""
    return db.query(HighVelocityTransfer).filter(HighVelocityTransfer.id == report_id).first()


def get_geographical_inflow_report_by_id(db: Session, report_id: int):
    """Returns a geographical inflow report by id, or None if not found."""
    return db.query(GeographicalInflow).filter(GeographicalInflow.id == report_id).first()


def create_raw_data_report(db: Session, data: dict) -> RawData:
    """
    Saves a raw data to the database.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_raw_data = RawData(**data)
        db.add(new_raw_data)
        db.commit()
        db.refresh(new_raw_data)
        return new_raw_data
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def get_raw_data_report(db: Session, report_id: int) -> RawData:
    """Returns a raw data report by id, or None if not found."""
    return db.query(RawData).filter(RawData.id == report_id).first()


def create_ai_summary_report(db: Session, data: dict):
    """
    Saves an AI-generated summary report to the database.
    Returns the saved object with generated id and created_at.
    Rolls back when catches duplicates and ignores them.
    Rolls back and raises when catch another error than Integrity
    """
    try:
        new_ai_summary_report = AISummary(**data)
        db.add(new_ai_summary_report)
        db.commit()
        db.refresh(new_ai_summary_report)
        return new_ai_summary_report
    except IntegrityError:
        db.rollback()
        return None
    except Exception as e:
        db.rollback()
        raise e


def get_ai_summary_report(db: Session, report_id: int) -> AISummary:
    """Returns a raw data report by id, or None if not found."""
    return db.query(AISummary).filter(AISummary.id == report_id).first()
