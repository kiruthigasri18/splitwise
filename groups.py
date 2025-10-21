# groups.py
from fastapi import APIRouter, HTTPException, Depends
from models import GroupCreateModel, GroupJoinModel, ExpenseModel
from auth import verify_token
from db import groups_db, balances_db, users_db, add_transaction

router = APIRouter(prefix="/groups", tags=["groups"])

# Helper: case-insensitive group lookup
def _get_group_by_name(group_name: str):
    if not group_name:
        return None, None
    for gname, gdata in groups_db.items():
        if gname.lower() == group_name.lower():
            return gname, gdata
    return None, None

def rollup_balances(group_name: str):
    group_name, group = _get_group_by_name(group_name)
    if not group:
        return
    members = group["members"]
    for exp in group["expenses"]:
        split_members = [m for m in exp.get("split_members", []) if m in members]
        if not split_members:
            split_members = members.copy()
        exp["split_members"] = split_members
        total_split = len(split_members)
        amount = exp["amount"]
        new_share = int(round(amount / total_split))
        exp["expected_share"] = {m: new_share for m in split_members}
        per_user_paid = exp.get("per_user_paid", {})
        for m in split_members:
            per_user_paid.setdefault(m, 0)
        payer = exp.get("paid_by")
        if payer:
            per_user_paid.setdefault(payer, 0)
        exp["per_user_paid"] = per_user_paid

@router.post("/create")
def create_group(data: GroupCreateModel, token: dict = Depends(verify_token)):
    # Validate members registered
    for m in data.members:
        if m not in users_db:
            raise HTTPException(status_code=400, detail=f"User '{m}' is not registered. All group members must be registered users.")

    if data.group_name in groups_db:
        raise HTTPException(status_code=400, detail="Group already exists")
    groups_db[data.group_name] = {
        "members": data.members,
        "expenses": [],
        "payments": {}
    }
    for m in data.members:
        balances_db.setdefault(m, 0)
    return {"message": f"Group '{data.group_name}' created successfully"}

@router.post("/join")
def join_group(data: GroupJoinModel, token: dict = Depends(verify_token)):
    username = token["username"]
    group_name, group = _get_group_by_name(data.group_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group '{data.group_name}' not found.")
    if username in group["members"]:
        raise HTTPException(status_code=400, detail="Already a member")
    group["members"].append(username)
    balances_db.setdefault(username, 0)
    rollup_balances(group_name)
    return {"message": f"{username} joined group '{group_name}' successfully"}

@router.post("/add_expense")
def add_expense(data: ExpenseModel, token: dict = Depends(verify_token)):
    username = token["username"]
    group_name, group = _get_group_by_name(data.group_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group '{data.group_name}' not found.")
    members = group["members"]
    if username not in members:
        raise HTTPException(status_code=403, detail="Not a member of this group")
    # ensure split members (if any) are registered and members of group
    split_members = list(dict.fromkeys(data.split_members or []))
    if username not in split_members:
        split_members.append(username)
    # validate registrations and membership
    for sm in split_members:
        if sm not in users_db:
            raise HTTPException(status_code=400, detail=f"User '{sm}' is not registered; cannot add to expense.")
        if sm not in members:
            raise HTTPException(status_code=400, detail=f"'{sm}' must join the group before being added to this expense.")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Expense amount must be greater than 0")
    existing = [e["description"].lower() for e in group["expenses"]]
    if data.description.lower() in existing:
        raise HTTPException(status_code=400, detail=f"Expense '{data.description}' already exists in '{data.group_name}'.")
    total_split = len(split_members)
    amount = data.amount
    share_per_user = int(round(amount / total_split))
    per_user_paid = {m: 0 for m in split_members}
    expected_share = {m: share_per_user for m in split_members}
    if data.paid_option == "Full Amount Paid":
        per_user_paid[username] = amount
    elif data.paid_option == "Share Paid":
        per_user_paid[username] = share_per_user
    elif data.paid_option not in ["Not Paid"]:
        raise HTTPException(status_code=400, detail="Invalid paid_option specified")
    exp = {
        "description": data.description,
        "amount": amount,
        "paid_option": data.paid_option,
        "paid_by": username,
        "split_members": split_members,
        "per_user_paid": per_user_paid,
        "expected_share": expected_share,
    }
    group["expenses"].append(exp)
    return {
        "message": f"Expense '{data.description}' recorded successfully in '{group_name}'.",
        "info": {
            "paid_by": username,
            "split_members": split_members,
            "share_each": share_per_user,
            "creator_already_paid": per_user_paid[username],
        },
    }

@router.post("/join_expense")
def join_expense(data: dict, token: dict = Depends(verify_token)):
    username = token["username"]
    group_name = data.get("group_name")
    expense_desc = data.get("expense_description")
    group_name, group = _get_group_by_name(group_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found.")
    expense = next((e for e in group["expenses"] if e["description"].lower() == expense_desc.lower()), None)
    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_desc}' not found.")
    if username in expense["split_members"]:
        raise HTTPException(status_code=400, detail="Already part of this expense.")
    # Add new member
    expense["split_members"].append(username)
    total_split = len(expense["split_members"])
    amount = expense["amount"]
    new_share = int(round(amount / total_split))
    expense["expected_share"] = {m: new_share for m in expense["split_members"]}
    for m in expense["split_members"]:
        expense["per_user_paid"].setdefault(m, 0)
    overpaid_summary = {}
    for m in expense["split_members"]:
        paid = expense["per_user_paid"][m]
        share = expense["expected_share"][m]
        overpaid_summary[m] = paid - share
    return {
        "message": f"{username} joined '{expense_desc}' in '{group_name}'. Shares recalculated to ₹{new_share} each.",
        "updated_expense": expense,
        "overpaid_status": overpaid_summary
    }

@router.post("/pay_expense")
def pay_specific_expense(data: dict, token: dict = Depends(verify_token)):
    return _handle_payment(data, token, single_expense=True)

@router.post("/pay")
def pay_group_balance(data: dict, token: dict = Depends(verify_token)):
    return _handle_payment(data, token, single_expense=False)

# def _handle_payment(data: dict, token: dict, single_expense: bool):
#     username = token["username"]
#     group_name = data.get("group_name")
#     expense_desc = data.get("expense_description") if single_expense else None
#     group_name, group = _get_group_by_name(group_name)
#     if not group:
#         raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found in memory.")
#     wallet_balance = balances_db.get(username, 0)
#     if single_expense:
#         expense = next((e for e in group["expenses"] if e["description"].lower() == expense_desc.lower()), None)
#         if not expense:
#             raise HTTPException(status_code=404, detail=f"Expense '{expense_desc}' not found.")
#         expenses = [expense]
#     else:
#         expenses = [e for e in group["expenses"] if username in e["split_members"]]
#     total_paid = 0
#     credited_total = []
#     txs_to_log = []
#     for expense in expenses:
#         split_members = expense["split_members"]
#         expected_share = {m: int(round(expense["amount"] / len(split_members))) for m in split_members}
#         per_user_paid = {m: int(round(expense["per_user_paid"].get(m, 0))) for m in split_members}
#         # Prevent creator from paying themselves
#         if expense.get("paid_by") == username:
#             raise HTTPException(status_code=400, detail="You created this expense — no payment required.")
#         share = expected_share[username]
#         paid = per_user_paid[username]
#         due = share - paid
#         if due <= 0:
#             raise HTTPException(status_code=400, detail="Already settled — no remaining amount to pay.")
#         # Require exact payment
#         pay_amount = int(data.get("amount", 0))
#         if pay_amount != due:
#             raise HTTPException(status_code=400, detail=f"You must pay the exact amount owed: ₹{due}.")
#         if pay_amount > wallet_balance:
#             raise HTTPException(status_code=400, detail=f"Insufficient wallet balance for '{expense['description']}'.")
#         wallet_balance -= pay_amount
#         total_paid += pay_amount
#         # Update payer’s record
#         expense["per_user_paid"][username] = paid + pay_amount
#         # Determine overpayers (current)
#         overpayers = {}
#         for m in split_members:
#             overpaid = expense["per_user_paid"][m] - expected_share[m]
#             if overpaid > 0 and m != username:
#                 overpayers[m] = overpaid
#         credited = []
#         allocations = {}
#         if overpayers:
#             valid_overpayers = {m: amt for m, amt in overpayers.items() if amt > 0}
#             remaining = pay_amount
#             # Reimburse overpaid first
#             for m, over_amt in valid_overpayers.items():
#                 credit_amt = min(over_amt, remaining)
#                 allocations[m] = credit_amt
#                 remaining -= credit_amt
#                 if remaining <= 0:
#                     break
#             # remainder => original payer
#             payer = expense.get("paid_by")
#             if remaining > 0 and payer and payer != username:
#                 allocations[payer] = allocations.get(payer, 0) + remaining
#             for m, credit_amt in allocations.items():
#                 balances_db[m] = balances_db.get(m, 0) + credit_amt
#                 credited.append({"user": m, "credited_amount": credit_amt})
#                 # adjust effective payment so they are less overpaid
#                 expense["per_user_paid"][m] -= credit_amt
#         else:
#             payer = expense.get("paid_by")
#             if payer and payer != username:
#                 balances_db[payer] = balances_db.get(payer, 0) + pay_amount
#                 credited.append({"user": payer, "credited_amount": pay_amount})
#                 allocations[payer] = pay_amount

#         credited_total.extend(credited)

#         # Prepare transactions to log:
#         # One transaction for the payer paying (shows who they paid to)
#         tx = {
#             "type": "payment",
#             "amount": pay_amount,
#             "currency": "INR",
#             "paid_from": username,
#             "paid_to": list(allocations.keys()) if allocations else expense.get("paid_by"),
#             "group": group_name,
#             "expense": expense.get("description"),
#             "note": f"Payment for expense '{expense.get('description')}' in group '{group_name}'",
#             "status": "valid"
#         }
#         txs_to_log.append(tx)

#         # Optionally, log reimbursements as separate transactions (payer receives credit)
#         for r_user, r_amt in allocations.items():
#             # create a small transaction indicating credit to recipient
#             tx_credit = {
#                 "type": "credit",
#                 "amount": r_amt,
#                 "currency": "INR",
#                 "paid_from": username,
#                 "paid_to": r_user,
#                 "group": group_name,
#                 "expense": expense.get("description"),
#                 "note": f"Allocation from {username} for expense '{expense.get('description')}'",
#                 "status": "valid"
#             }
#             txs_to_log.append(tx_credit)

#     # Update payer wallet balance AFTER all expense iterations
#     balances_db[username] = wallet_balance

#     # Persist transaction logs
#     for t in txs_to_log:
#         add_transaction(t)

#     return {
#         "message": f"Paid total ₹{total_paid} across {len(expenses)} expense(s) in '{group_name}'.",
#         "credited_to": credited_total,
#         "balances": {m: balances_db.get(m, 0) for m in group['members']},
#     }

def _handle_payment(data: dict, token: dict, single_expense: bool):
    username = token["username"]
    group_name = data.get("group_name")
    expense_desc = data.get("expense_description") if single_expense else None
    group_name, group = _get_group_by_name(group_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found in memory.")

    wallet_balance = balances_db.get(username, 0)

    # Select relevant expenses
    if single_expense:
        expense = next((e for e in group["expenses"] if e["description"].lower() == expense_desc.lower()), None)
        if not expense:
            raise HTTPException(status_code=404, detail=f"Expense '{expense_desc}' not found.")
        expenses = [expense]
    else:
        expenses = [e for e in group["expenses"] if username in e["split_members"]]

    total_paid = 0
    credited_total = []
    txs_to_log = []

    for expense in expenses:
        split_members = expense["split_members"]
        expected_share = {m: int(round(expense["amount"] / len(split_members))) for m in split_members}
        per_user_paid = {m: int(round(expense["per_user_paid"].get(m, 0))) for m in split_members}

        if expense.get("paid_by") == username:
            raise HTTPException(status_code=400, detail="You created this expense — no payment required.")

        share = expected_share[username]
        paid = per_user_paid[username]
        due = share - paid
        if due <= 0:
            raise HTTPException(status_code=400, detail="Already settled — no remaining amount to pay.")

        pay_amount = int(data.get("amount", 0))
        if pay_amount != due:
            raise HTTPException(status_code=400, detail=f"You must pay the exact amount owed: ₹{due}.")
        if pay_amount > wallet_balance:
            raise HTTPException(status_code=400, detail=f"Insufficient wallet balance for '{expense['description']}'.")

        # Deduct wallet balance and mark payment done
        wallet_balance -= pay_amount
        total_paid += pay_amount
        expense["per_user_paid"][username] = paid + pay_amount

        # Find who should receive this money
        overpayers = {}
        for m in split_members:
            overpaid = expense["per_user_paid"][m] - expected_share[m]
            if overpaid > 0 and m != username:
                overpayers[m] = overpaid

        credited = []
        allocations = {}

        if overpayers:
            valid_overpayers = {m: amt for m, amt in overpayers.items() if amt > 0}
            remaining = pay_amount
            # Reimburse overpaid first
            for m, over_amt in valid_overpayers.items():
                credit_amt = min(over_amt, remaining)
                allocations[m] = credit_amt
                remaining -= credit_amt
                if remaining <= 0:
                    break
            payer = expense.get("paid_by")
            if remaining > 0 and payer and payer != username:
                allocations[payer] = allocations.get(payer, 0) + remaining
        else:
            payer = expense.get("paid_by")
            if payer and payer != username:
                allocations[payer] = pay_amount

        # Update balances (receiver side)
        for m, credit_amt in allocations.items():
            balances_db[m] = balances_db.get(m, 0) + credit_amt
            credited.append({"user": m, "credited_amount": credit_amt})
            expense["per_user_paid"][m] -= credit_amt  # Adjust overpayment

        credited_total.extend(credited)

        # ✅ Log only "credit" transactions — clean version (no "payment" duplicates)
        for r_user, r_amt in allocations.items():
            tx_credit = {
                "type": "credit",
                "amount": r_amt,
                "currency": "INR",
                "paid_from": username,
                "paid_to": r_user,
                "group": group_name,
                "expense": expense.get("description"),
                "note": f"Transfer from {username} for '{expense.get('description')}' in '{group_name}'",
                "status": "valid"
            }
            txs_to_log.append(tx_credit)

    # Update payer's wallet after all payments
    balances_db[username] = wallet_balance

    # Save all transactions
    for t in txs_to_log:
        add_transaction(t)

    return {
        "message": f"Paid total ₹{total_paid} across {len(expenses)} expense(s) in '{group_name}'.",
        "credited_to": credited_total,
        "balances": {m: balances_db.get(m, 0) for m in group['members']},
    }

@router.get("/{group_name}/balance")
def get_balance(group_name: str, token: dict = Depends(verify_token)):
    username = token["username"]
    group_name, group = _get_group_by_name(group_name)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group '{group_name}' not found.")
    balance = 0
    for exp in group["expenses"]:
        members = exp["split_members"]
        share_map = exp.get("expected_share", {m: exp["amount"] // len(members) for m in members})
        paid = exp["per_user_paid"].get(username, 0)
        if username in members:
            balance += share_map.get(username, exp["amount"] // len(members)) - paid
    return {"balance": balance}
