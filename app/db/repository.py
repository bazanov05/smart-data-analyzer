from app.db.models import (
    StructuringAttempt,
    UnverifiedOriginator,
    HighVelocityTransfer,
    GeographicalInflow
)
from sqlalchemy.orm import Session


def create_structuring_attempt_report(db: Session, data: dict) -> StructuringAttempt:
    """
    Saves a structuring attempt to the database.
    Returns the saved object with generated id and created_at.
    Rolls back and raises on commit failure.
    """
    try:
        new_structuring_attempt_report = StructuringAttempt(**data)
        db.add(new_structuring_attempt_report)
        db.commit()
        db.refresh(new_structuring_attempt_report)
        return new_structuring_attempt_report
    except Exception as e:
        db.rollback()
        raise e


def create_unverified_originator_report(db: Session, data: dict) -> UnverifiedOriginator:
    """
    Saves an unverified originator transaction to the database.
    sender_id may be None — that is expected for this report type.
    Returns the saved object with generated id and created_at.
    Rolls back and raises on commit failure.
    """
    try:
        new_unverified_originator_report = UnverifiedOriginator(**data)
        db.add(new_unverified_originator_report)
        db.commit()
        db.refresh(new_unverified_originator_report)
        return new_unverified_originator_report
    except Exception as e:
        db.rollback()
        raise e


def create_high_velocity_transfer_report(db: Session, data: dict) -> HighVelocityTransfer:
    """
    Saves a high velocity transfer to the database.
    Expects timegap field in data representing time between transactions.
    Returns the saved object with generated id and created_at.
    Rolls back and raises on commit failure.
    """
    try:
        new_high_velocity_transfer_report = HighVelocityTransfer(**data)
        db.add(new_high_velocity_transfer_report)
        db.commit()
        db.refresh(new_high_velocity_transfer_report)
        return new_high_velocity_transfer_report
    except Exception as e:
        db.rollback()
        raise e


def create_geographical_inflow_report(db: Session, data: dict) -> GeographicalInflow:
    """
    Saves a geographical inflow aggregation to the database.
    Expects only country and inflow fields — no transaction details.
    Returns the saved object with generated id and created_at.
    Rolls back and raises on commit failure.
    """
    try:
        new_geographical_inflow_report = GeographicalInflow(**data)
        db.add(new_geographical_inflow_report)
        db.commit()
        db.refresh(new_geographical_inflow_report)
        return new_geographical_inflow_report
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
