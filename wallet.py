# # wallet.py
# from fastapi import APIRouter, Depends
# from auth import verify_token
# from db import get_transactions_for_user, transactions_db

# router = APIRouter(prefix="/wallet", tags=["wallet"])

# @router.get("/transactions/me")
# def my_wallet_transactions(token: dict = Depends(verify_token)):
#     username = token["username"]
#     return {"transactions": get_transactions_for_user(username)}

# @router.get("/transactions/all")
# def all_transactions(token: dict = Depends(verify_token)):
#     # NOTE: you may want to restrict this to admin users only
#     return {"transactions": transactions_db}


# wallet.py
from fastapi import APIRouter, Depends
from auth import verify_token
from db import get_transactions_for_user, transactions_db

router = APIRouter(prefix="/wallet", tags=["wallet"])

def classify_tx_for_user(tx: dict, username: str) -> str:
    """
    Determine transaction type (credit, debit, deposit)
    from the perspective of the given username.
    """
    tx_type = tx.get("type", "").lower()
    paid_from = str(tx.get("paid_from", "")).lower()
    paid_to = tx.get("paid_to")

    # Deposit (user adds money to wallet)
    if tx_type == "deposit" or (paid_from == username.lower() and paid_to == username):
        return "deposit"

    # Debit (money goes out from user)
    if paid_from == username.lower():
        return "debit"

    # Credit (money comes in to user)
    if isinstance(paid_to, list):
        if username.lower() in [p.lower() for p in paid_to]:
            return "credit"
    elif isinstance(paid_to, str) and paid_to.lower() == username.lower():
        return "credit"

    # Default fallback
    return "other"

@router.get("/transactions/me")
def my_wallet_transactions(token: dict = Depends(verify_token)):
    username = token["username"]
    txs = get_transactions_for_user(username)
    # Annotate each transaction with credit/debit/deposit
    for t in txs:
        t["payment_type"] = classify_tx_for_user(t, username)
        # Optionally remove internal "type" for clarity
        if "type" in t:
            del t["type"]
    return {"transactions": txs}

@router.get("/transactions/all")
def all_transactions(token: dict = Depends(verify_token)):
    """
    Returns all transactions with their type classified for each user (admin use).
    """
    txs = []
    for t in transactions_db:
        txs.append(t.copy())
    return {"transactions": txs}
