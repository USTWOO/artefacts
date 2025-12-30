from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, index=True)
    date = Column(Date)
    amount = Column(Float)
    vat = Column(Float)
    total_amount = Column(Float)
