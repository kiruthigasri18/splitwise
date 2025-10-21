# admins.py
from fastapi import APIRouter, HTTPException, Depends
from auth import verify_token, hash_password, verify_password, create_access_token
from db import groups_db, balances_db, transactions_db, users_db

router = APIRouter(prefix="/admin", tags=["admin"])

# In-memory admin store
admins_db = {}

def _is_admin(token: dict):
    return token.get("role") == "admin"

# -----------------------------------------------------
# Register a new admin
# -----------------------------------------------------
@router.post("/register")
def register_admin(data: dict):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    if username in admins_db:
        raise HTTPException(status_code=400, detail="Admin already exists.")
    admins_db[username] = hash_password(password)
    return {"message": f"Admin '{username}' registered successfully."}

# -----------------------------------------------------
# Login admin
# -----------------------------------------------------
@router.post("/login")
def login_admin(data: dict):
    username = data.get("username")
    password = data.get("password")
    if username not in admins_db or not verify_password(password, admins_db[username]):
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")
    token = create_access_token({"sub": username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------------------------------
# Admin dashboard
# -----------------------------------------------------
# -----------------------------------------------------
# Admin dashboard with analytics
# -----------------------------------------------------
@router.get("/dashboard")
def admin_dashboard(token: dict = Depends(verify_token)):
    if not _is_admin(token):
        raise HTTPException(status_code=403, detail="Only admin users can access this endpoint.")

    dashboard = {}
    all_user_summary = {}

    for gname, gdata in groups_db.items():
        group_info = {}
        group_info["members"] = gdata.get("members", [])
        group_info["expenses"] = gdata.get("expenses", [])
        group_info["wallet_balances"] = {m: balances_db.get(m, 0) for m in group_info["members"]}

        # Compute totals
        total_expense = sum(exp.get("amount", 0) for exp in gdata.get("expenses", []))
        total_paid = sum(sum(exp.get("per_user_paid", {}).values()) for exp in gdata.get("expenses", []))
        group_info["total_spent"] = total_expense
        group_info["total_paid_by_members"] = total_paid

        # Track per-member spending analytics
        spend_by_member = {}
        for exp in gdata.get("expenses", []):
            per_user_paid = exp.get("per_user_paid", {})
            for user, amt in per_user_paid.items():
                spend_by_member[user] = spend_by_member.get(user, 0) + amt
        group_info["analytics"] = {
            "spend_by_member": spend_by_member,
            "total_expense": total_expense,
        }

        # Aggregate global summary
        for member in group_info["members"]:
            if member not in all_user_summary:
                all_user_summary[member] = {
                    "balance": balances_db.get(member, 0),
                    "total_paid": 0,
                    "total_expense": 0,
                }
            all_user_summary[member]["total_paid"] += spend_by_member.get(member, 0)
            all_user_summary[member]["total_expense"] += total_expense / max(len(group_info["members"]), 1)

        dashboard[gname] = group_info

    # Attach overall user analytics
    dashboard["_summary"] = {"users": all_user_summary}
    return dashboard
