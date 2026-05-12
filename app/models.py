from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./finance_manager.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    balance = Column(Float, default=0.0)
    cards = relationship("Card", back_populates="account")
    transactions = relationship("Transaction", back_populates="account")

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    card_type = Column(String)
    name_on_card = Column(String)
    card_number = Column(String)
    expiry_date = Column(String)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    account = relationship("BankAccount", back_populates="cards")

class ExpenseGroup(Base):
    __tablename__ = "expense_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    expenses = relationship("ExpenseType", back_populates="group")

class ExpenseType(Base):
    __tablename__ = "expense_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description1 = Column(String)
    description2 = Column(String)
    duration = Column(Integer)  # months, e.g. 1-36, or -1 for indefinite
    start_date = Column(Date)
    payment_day = Column(Integer)
    total_spend_target = Column(Float)
    group_id = Column(Integer, ForeignKey("expense_groups.id"))
    group = relationship("ExpenseGroup", back_populates="expenses")
    payments = relationship("ExpensePayment", back_populates="expense_type")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    description = Column(String)
    is_income = Column(Boolean, default=False)
    account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    account = relationship("BankAccount", back_populates="transactions")
    payment = relationship("ExpensePayment", back_populates="transaction", uselist=False)

class ExpensePayment(Base):
    __tablename__ = "expense_payments"
    id = Column(Integer, primary_key=True, index=True)
    expense_type_id = Column(Integer, ForeignKey("expense_types.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    date = Column(Date)
    amount = Column(Float)
    expense_type = relationship("ExpenseType", back_populates="payments")
    transaction = relationship("Transaction", back_populates="payment")

def init_db():
    Base.metadata.create_all(bind=engine)
