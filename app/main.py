from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import date, datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm

from . import models, ocr, reconciliation, export, auth
from .models import SessionLocal, init_db

app = FastAPI(title="Personal Finance Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Finance Manager API is running"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Hardcoded check for this personal app
    if form_data.username == "admin" and auth.verify_password(form_data.password, auth.ADMIN_PASSWORD_HASH):
        access_token = auth.create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

# Accounts
@app.get("/accounts")
def get_accounts(db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user)):
    return db.query(models.BankAccount).all()

@app.post("/accounts")
def create_account(name: str, balance: float = 0.0, db: Session = Depends(get_db)):
    account = models.BankAccount(name=name, balance=balance)
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

# Cards
@app.get("/cards")
def get_cards(db: Session = Depends(get_db)):
    return db.query(models.Card).all()

@app.post("/cards")
def create_card(card_type: str, name_on_card: str, card_number: str, expiry_date: str, account_id: int, db: Session = Depends(get_db)):
    card = models.Card(card_type=card_type, name_on_card=name_on_card, card_number=card_number, expiry_date=expiry_date, account_id=account_id)
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

# Expense Groups
@app.get("/expense-groups")
def get_expense_groups(db: Session = Depends(get_db)):
    return db.query(models.ExpenseGroup).all()

@app.post("/expense-groups")
def create_expense_group(name: str, db: Session = Depends(get_db)):
    group = models.ExpenseGroup(name=name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

# Expense Types
@app.get("/expense-types")
def get_expense_types(db: Session = Depends(get_db)):
    return db.query(models.ExpenseType).all()

@app.post("/expense-types")
def create_expense_type(
    name: str,
    description1: str,
    description2: str,
    duration: int,
    payment_day: int,
    total_spend_target: float,
    group_id: int,
    start_date: str = None,
    db: Session = Depends(get_db)
):
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date_obj = date.today()

    expense = models.ExpenseType(
        name=name,
        description1=description1,
        description2=description2,
        duration=duration,
        payment_day=payment_day,
        total_spend_target=total_spend_target,
        group_id=group_id,
        start_date=start_date_obj
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

# Import Statement
@app.post("/import-statement/{account_id}")
async def import_statement(account_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        text = ocr.extract_text_from_pdf(file_path)
        transactions_data = ocr.parse_transactions(text)

        tx_count = 0
        for tx_data in transactions_data:
            tx = models.Transaction(
                date=tx_data['date'],
                amount=tx_data['amount'],
                description=tx_data['description'],
                is_income=tx_data['is_income'],
                account_id=account_id
            )
            db.add(tx)
            tx_count += 1

        db.commit()

        # Run reconciliation
        reconciled_count = reconciliation.reconcile_transactions(db, account_id)

        return {
            "message": "Statement imported and processed",
            "transactions_imported": tx_count,
            "reconciled": reconciled_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Dashboard Stats
@app.get("/dashboard/missed-payments")
def get_missed_payments(db: Session = Depends(get_db)):
    return reconciliation.get_missed_payments(db)

@app.get("/dashboard/stats")
def get_stats(db: Session = Depends(get_db)):
    # Income vs Expense
    today = date.today()
    current_month_start = date(today.year, today.month, 1)

    income = db.query(models.Transaction).filter(
        models.Transaction.is_income == True,
        models.Transaction.date >= current_month_start
    ).all()

    expenses = db.query(models.Transaction).filter(
        models.Transaction.is_income == False,
        models.Transaction.date >= current_month_start
    ).all()

    total_income = sum([i.amount for i in income])
    total_expense = sum([e.amount for e in expenses])

    # Calculate spend per year and spend to date per year for each expense type
    expense_details = []
    all_expenses = db.query(models.ExpenseType).all()
    for et in all_expenses:
        # Spend to date per year (current year)
        payments_this_year = db.query(models.ExpensePayment).filter(
            models.ExpensePayment.expense_type_id == et.id,
            models.ExpensePayment.date >= date(today.year, 1, 1)
        ).all()
        spend_to_date_year = sum([p.amount for p in payments_this_year])

        # Spend per year (estimated based on target)
        estimated_spend_year = et.total_spend_target * (et.duration if et.duration > 0 and et.duration < 12 else 12)

        expense_details.append({
            "name": et.name,
            "spend_per_year_est": estimated_spend_year,
            "spend_to_date_year": spend_to_date_year
        })

    return {
        "total_income_month": total_income,
        "total_expense_month": total_expense,
        "expense_details": expense_details
    }

# Export
@app.get("/export")
def get_export(db: Session = Depends(get_db)):
    excel_data = export.export_to_excel(db)
    return Response(
        content=excel_data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=finance_data.xlsx"}
    )
