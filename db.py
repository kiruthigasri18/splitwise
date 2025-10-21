# db.py
from collections import defaultdict
from typing import List, Dict
from datetime import datetime

# Existing in-memory stores (keep whatever you had — these are default/initial)
groups_db: Dict[str, Dict] = {}
balances_db: Dict[str, int] = {}
# users_db: username -> user data (simple in-memory user registry)
users_db: Dict[str, Dict] = {}

# Transactions store (in-memory)
transactions_db: List[Dict] = []
_transaction_id_counter = 1

def _now_iso():
    return datetime.utcnow().isoformat() + "Z"

def add_user(username: str, full_name: str = ""):
    if username in users_db:
        return users_db[username]
    users_db[username] = {"username": username, "full_name": full_name, "created_at": _now_iso()}
    balances_db.setdefault(username, 0)
    return users_db[username]

def add_transaction(tx: Dict) -> Dict:
    """
    tx: dict with keys:
      timestamp (optional), user, type, amount, currency, paid_from, paid_to, group, expense, note, status
    """
    global _transaction_id_counter
    tx_copy = tx.copy()
    tx_copy.setdefault("timestamp", _now_iso())
    tx_copy["id"] = _transaction_id_counter
    _transaction_id_counter += 1
    transactions_db.append(tx_copy)
    return tx_copy

def get_transactions_for_user(username: str):
    username = username.lower()
    return [t for t in transactions_db if (str(t.get("user","")).lower() == username
                                          or str(t.get("paid_from","")).lower() == username
                                          or (isinstance(t.get("paid_to"), str) and str(t.get("paid_to","")).lower() == username)
                                          or (isinstance(t.get("paid_to"), list) and username in [p.lower() for p in t.get("paid_to")]))]

def get_transactions_for_group(group_name: str):
    return [t for t in transactions_db if str(t.get("group","")).lower() == str(group_name).lower()]

def get_valid_transactions():
    return [t for t in transactions_db if t.get("status", "valid") == "valid"]

def search_transactions(filter_fn):
    return list(filter(filter_fn, transactions_db))
