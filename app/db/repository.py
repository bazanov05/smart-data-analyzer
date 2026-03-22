from app.db.models import (
    StructuringAttempt,
    UnverifiedOriginator,
    HighVelocityTransfer,
    GeographicalInflow
)
from sqlalchemy.orm import Session


def create_structuring_attempt_report(db: Session, data: dict) -> StructuringAttempt:
    try:
        # here there is no validation
        new_structuring_attempt_report = StructuringAttempt(**data)

        db.add(new_structuring_attempt_report)
        db.commit()  # validation comes here, when we want to commit

        db.refresh(new_structuring_attempt_report)  # we want to return object with new rows as well
        return new_structuring_attempt_report
    except Exception as e:
        db.rollback()  # clean the session before raising
        raise e


def create_unverified_originator_report(db: Session, data: dict) -> UnverifiedOriginator:
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
    return db.query(StructuringAttempt).filter(StructuringAttempt.id == report_id).first()


def get_unverified_originator_report_by_id(db: Session, report_id: int):
    return db.query(UnverifiedOriginator).filter(UnverifiedOriginator.id == report_id).first()


def get_high_velocity_transfer_report_by_id(db: Session, report_id: int):
    return db.query(HighVelocityTransfer).filter(HighVelocityTransfer.id == report_id).first()


def get_geographical_inflow_report_by_id(db: Session, report_id: int):
    return db.query(GeographicalInflow).filter(GeographicalInflow.id == report_id).first()