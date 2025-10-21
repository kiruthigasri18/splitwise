# analytics.py
from fastapi import APIRouter, Depends
from collections import defaultdict
from auth import verify_token
from db import transactions_db, get_transactions_for_group

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/spend")
def spend_breakdown(group: str = None, token: dict = Depends(verify_token)):
    """
    Returns simple breakdown of credits by recipient.
    Response: {"labels": [...], "values":[...]}
    """
    txs = transactions_db if not group else get_transactions_for_group(group)
    spend_by_recipient = defaultdict(int)
    for t in txs:
        amt = int(t.get("amount", 0))
        paid_to = t.get("paid_to")
        if isinstance(paid_to, list):
            # distribute equally
            per = amt // max(1, len(paid_to))
            for r in paid_to:
                spend_by_recipient[r] += per
        elif isinstance(paid_to, str):
            spend_by_recipient[paid_to] += amt
    labels = list(spend_by_recipient.keys())
    values = [spend_by_recipient[k] for k in labels]
    return {"labels": labels, "values": values}
