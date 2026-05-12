from sqlalchemy.orm import Session
from .models import Transaction, ExpenseType, ExpensePayment
from datetime import date

def reconcile_transactions(db: Session, account_id: int):
    # Fetch all unreconciled transactions for this account
    unreconciled = db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.payment == None
    ).all()

    # Fetch all expense types
    expense_types = db.query(ExpenseType).all()

    reconciled_count = 0
    for tx in unreconciled:
        for et in expense_types:
            # Simple matching: description match and amount similarity (or just description for now)
            # In a real app, this would use fuzzy matching and more criteria
            if et.name.lower() in tx.description.lower() or (et.description1 and et.description1.lower() in tx.description.lower()):
                # Create a payment record
                payment = ExpensePayment(
                    expense_type_id=et.id,
                    transaction_id=tx.id,
                    date=tx.date,
                    amount=tx.amount
                )
                db.add(payment)
                reconciled_count += 1
                break # Move to next transaction

    db.commit()
    return reconciled_count

def get_missed_payments(db: Session):
    # This logic identifies expected payments that haven't happened yet for the current month
    today = date.today()
    current_month = today.month
    current_year = today.year

    expense_types = db.query(ExpenseType).all()
    missed = []

    for et in expense_types:
        # Check if a payment exists for this month
        payment_this_month = db.query(ExpensePayment).filter(
            ExpensePayment.expense_type_id == et.id,
            ExpensePayment.date >= date(current_year, current_month, 1)
        ).first()

        if not payment_this_month:
            # Check if it should have happened by now
            if today.day > et.payment_day:
                # Check duration
                # Simplified duration check: if start_date + duration (months) > today
                # For now, let's just use the payment_day
                missed.append({
                    "id": et.id,
                    "name": et.name,
                    "expected_day": et.payment_day,
                    "amount": et.total_spend_target
                })

    return missed
