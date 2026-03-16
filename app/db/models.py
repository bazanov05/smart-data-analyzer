from sqlalchemy import Integer, Column, String, Double
from db.database import Base


class AmlReport(Base):
    __tablename__ = "aml_report"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String)
    sender_id = Column(String)
    receiver_id = Column(String)
    amount = Column(Double)
    country = Column(String)
    type = Column(String)
