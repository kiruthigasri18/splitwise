# users.py
from fastapi import APIRouter, HTTPException, Depends
from models import RegisterModel, LoginModel
from auth import hash_password, verify_password, create_access_token, verify_token
from db import users_db, balances_db, add_transaction


# users.py
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register")
def register(data: RegisterModel):
    if data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[data.username] = hash_password(data.password)
    balances_db[data.username] = 0  # Initialize wallet
    return {"message": f"User '{data.username}' registered successfully with ₹0 balance"}

@router.post("/login")
def login(data: LoginModel):
    if data.username not in users_db or not verify_password(data.password, users_db[data.username]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": data.username, "role": "user"})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/deposit")
def deposit(amount: int, token: dict = Depends(verify_token)):
    username = token["username"]
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit must be positive")
    balances_db[username] = balances_db.get(username, 0) + int(amount)
    # Log transaction
    tx = {
        "type": "deposit",
        "amount": int(amount),
        "currency": "INR",
        "paid_from": username,
        "paid_to": username,
        "group": None,
        "expense": None,
        "note": "Wallet deposit",
        "status": "valid"
    }
    add_transaction(tx)
    return {"message": f"Deposited ₹{amount}", "balance": balances_db[username]}

@router.get("/balance")
def get_balance(token: dict = Depends(verify_token)):
    username = token["username"]
    return {"balance": balances_db.get(username, 0)}
