from db.models import AmlReport


def create_report(db, data: dict):
    try:
        new_aml_report = AmlReport(**data)  # creating Python object, it does not check and validate anything
        db.add(new_aml_report)
        db.commit()  # here validation happens
        db.refresh(new_aml_report)  # to have new_aml_report with id and created_at attributes
        return new_aml_report
    except Exception as e:
        db.rollback()  # cleans the session after failed operations
        raise e
