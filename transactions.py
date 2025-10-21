# transactions.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime
from auth import verify_token
from db import add_transaction, get_transactions_for_user, get_transactions_for_group, get_valid_transactions, transactions_db, users_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

def _now_iso():
    return datetime.utcnow().isoformat() + "Z"

@router.post("/log")
def log_transaction(data: dict, token: dict = Depends(verify_token)):

    username = token["username"]
    if "amount" not in data or "group" not in data:
        raise HTTPException(status_code=400, detail="amount and group are required")

    # basic validation for users referenced
    paid_from = data.get("paid_from", username)
    paid_to = data.get("paid_to")
    if paid_from and str(paid_from) not in users_db:
        raise HTTPException(status_code=400, detail=f"paid_from user '{paid_from}' is not registered")
    if isinstance(paid_to, list):
        for p in paid_to:
            if p not in users_db:
                raise HTTPException(status_code=400, detail=f"paid_to user '{p}' is not registered")
    elif isinstance(paid_to, str):
        if paid_to not in users_db:
            raise HTTPException(status_code=400, detail=f"paid_to user '{paid_to}' is not registered")

    tx = {
        "timestamp": _now_iso(),
        "user": username,
        "type": data.get("type", "payment"),
        "amount": int(data["amount"]),
        "currency": data.get("currency", "INR"),
        "paid_from": paid_from,
        "paid_to": paid_to,
        "group": data.get("group"),
        "expense": data.get("expense"),
        "note": data.get("note"),
        "status": data.get("status", "valid"),
    }
    saved = add_transaction(tx)
    return {"message": "logged", "transaction": saved}

@router.get("/me")
def my_transactions(token: dict = Depends(verify_token)):
    username = token["username"]
    return {"transactions": get_transactions_for_user(username)}

@router.get("/user/{username}")
def transactions_for_user(username: str, token: dict = Depends(verify_token)):
    # Add admin check here if required
    return {"transactions": get_transactions_for_user(username)}

@router.get("/group/{group_name}")
def transactions_for_group(group_name: str, token: dict = Depends(verify_token)):
    return {"transactions": get_transactions_for_group(group_name)}

@router.get("/valid")
def valid_transactions(token: dict = Depends(verify_token)):
    return {"transactions": get_valid_transactions()}

@router.get("/all")
def all_transactions(token: dict = Depends(verify_token)):
    # Add admin guard if needed
    return {"transactions": transactions_db}
