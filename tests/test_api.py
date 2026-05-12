import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base, BankAccount, ExpenseGroup, ExpenseType, Transaction, ExpensePayment
from datetime import date

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_finance.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_create_account():
    response = client.post("/accounts", params={"name": "Test Account", "balance": 1000.0})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Account"

def test_missed_payments_logic():
    # Setup: Create account, group, and expense type
    client.post("/accounts", params={"name": "Main", "balance": 1000})
    client.post("/expense-groups", params={"name": "Bills"})

    # Create an expense that is due on the 1st of the month
    # Assuming today is after the 1st
    client.post("/expense-types", params={
        "name": "Rent",
        "description1": "Monthly Rent",
        "description2": "",
        "duration": -1,
        "payment_day": 1,
        "total_spend_target": 1200.0,
        "group_id": 1
    })

    response = client.get("/dashboard/missed-payments")
    assert response.status_code == 200
    missed = response.json()

    # If today's day > 1, it should be missed
    if date.today().day > 1:
        assert len(missed) == 1
        assert missed[0]["name"] == "Rent"
    else:
        assert len(missed) == 0

def test_reconciliation():
    # Setup
    client.post("/accounts", params={"name": "Main", "balance": 1000})
    client.post("/expense-groups", params={"name": "Bills"})
    client.post("/expense-types", params={
        "name": "Netflix",
        "description1": "Streaming",
        "description2": "",
        "duration": -1,
        "payment_day": 15,
        "total_spend_target": 15.99,
        "group_id": 1
    })

    # Manually add a transaction that matches
    db = TestingSessionLocal()
    tx = Transaction(
        date=date.today(),
        amount=15.99,
        description="NETFLIX.COM PAYMENT",
        is_income=False,
        account_id=1
    )
    db.add(tx)
    db.commit()

    from app.reconciliation import reconcile_transactions
    count = reconcile_transactions(db, 1)
    assert count == 1

    # Check if payment was created
    payment = db.query(ExpensePayment).filter(ExpensePayment.expense_type_id == 1).first()
    assert payment is not None
    assert payment.amount == 15.99
