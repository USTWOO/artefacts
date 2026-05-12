import pandas as pd
from sqlalchemy.orm import Session
from .models import Transaction, ExpenseType, ExpensePayment, BankAccount, Card
import io

def export_to_excel(db: Session):
    # Fetch all data
    txs = db.query(Transaction).all()
    expenses = db.query(ExpenseType).all()
    payments = db.query(ExpensePayment).all()
    accounts = db.query(BankAccount).all()
    cards = db.query(Card).all()

    # Convert to DataFrames
    df_txs = pd.DataFrame([{
        "Date": t.date,
        "Amount": t.amount,
        "Description": t.description,
        "Income": t.is_income,
        "Account": t.account.name if t.account else ""
    } for t in txs])

    df_expenses = pd.DataFrame([{
        "Name": e.name,
        "Desc 1": e.description1,
        "Desc 2": e.description2,
        "Duration": e.duration,
        "Payment Day": e.payment_day,
        "Target Spend": e.total_spend_target,
        "Group": e.group.name if e.group else ""
    } for e in expenses])

    df_accounts = pd.DataFrame([{
        "Name": a.name,
        "Balance": a.balance
    } for a in accounts])

    df_cards = pd.DataFrame([{
        "Type": c.card_type,
        "Name on Card": c.name_on_card,
        "Number": c.card_number,
        "Expiry": c.expiry_date,
        "Account": c.account.name if c.account else ""
    } for c in cards])

    # Create Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_txs.to_excel(writer, sheet_name='Transactions', index=False)
        df_expenses.to_excel(writer, sheet_name='Expenses', index=False)
        df_accounts.to_excel(writer, sheet_name='Accounts', index=False)
        df_cards.to_excel(writer, sheet_name='Cards', index=False)

    return output.getvalue()
