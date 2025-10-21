import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="💸 Expense Splitter", layout="wide")
st.title("💸 Group Expense Splitter with Wallet System")

# ---------------- Session State ----------------
if "token" not in st.session_state: st.session_state.token = None
if "username" not in st.session_state: st.session_state.username = None
if "admin_token" not in st.session_state: st.session_state.admin_token = None
if "admin_username" not in st.session_state: st.session_state.admin_username = None

def headers(token_type="user"):
    if token_type == "user" and st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    if token_type == "admin" and st.session_state.admin_token:
        return {"Authorization": f"Bearer {st.session_state.admin_token}"}
    return {}

# ---------------- Sidebar Wallet ----------------
st.sidebar.header("💰 Wallet")

if st.session_state.token:
    col1, col2 = st.sidebar.columns(2)

    if col1.button("Check Balance"):
        res = requests.get(f"{API_URL}/users/balance", headers=headers())
        if res.status_code == 200:
            st.sidebar.success(f"Balance: ₹{res.json().get('balance', 0)}")
        else:
            st.sidebar.error(res.json())

    deposit_amt = st.sidebar.number_input("Deposit Amount", min_value=1, step=1, key="deposit_input")
    if col2.button("Deposit"):
        res = requests.post(f"{API_URL}/users/deposit?amount={int(deposit_amt)}", headers=headers())
        if res.status_code == 200:
            st.sidebar.success(f"Deposited ₹{deposit_amt}")
        else:
            st.sidebar.error(res.json())
else:
    st.sidebar.info("Login to access wallet")

# ---------------- Tabs ----------------
tabs = [
    "User Register", "User Login",
    "Create/Join Group", "Add Expense", "Join Expense", "Pay Expense",
    "Wallet Transactions",
    "Admin Register", "Admin Login", "Admin Dashboard"
]
tab_selection = st.tabs(tabs)

# ---------------- USER REGISTER ----------------
with tab_selection[0]:
    st.subheader("User Register")
    username = st.text_input("Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pass")
    if st.button("Register User"):
        res = requests.post(f"{API_URL}/users/register", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("User registered successfully!")
        elif res.status_code == 400:
            st.warning("Username already exists. Try logging in instead.")
        else:
            st.error(res.json())

# ---------------- USER LOGIN ----------------
with tab_selection[1]:
    st.subheader("User Login")
    username = st.text_input("Login Username", key="login_user")
    password = st.text_input("Login Password", type="password", key="login_pass")
    if st.button("Login User"):
        res = requests.post(f"{API_URL}/users/login", json={"username": username, "password": password})
        if res.status_code == 200:
            data = res.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.success(f"Logged in as {username}")
        else:
            st.error(res.json())

# ---------------- CREATE / JOIN GROUP ----------------
with tab_selection[2]:
    st.subheader("Create Group")
    group_name = st.text_input("Group Name", key="create_group")
    members_input = st.text_input("Add Members (comma separated)", key="create_members")
    if st.button("Create Group"):
        members = list({m.strip() for m in members_input.split(",") if m.strip()})
        if st.session_state.username and st.session_state.username not in members:
            members.append(st.session_state.username)
        res = requests.post(f"{API_URL}/groups/create", json={"group_name": group_name, "members": members}, headers=headers())
        st.json(res.json())

    st.subheader("Join Group")
    group_name_join = st.text_input("Group Name to Join", key="join_group")
    if st.button("Join Group"):
        res = requests.post(f"{API_URL}/groups/join", json={"group_name": group_name_join}, headers=headers())
        st.json(res.json())

# ---------------- ADD EXPENSE ----------------
with tab_selection[3]:
    st.subheader("Add Expense")
    group_name_exp = st.text_input("Group Name", key="exp_group")
    description = st.text_input("Expense Description", key="exp_desc")
    amount = st.number_input("Amount", min_value=1, step=1, key="exp_amount")
    paid_option = st.radio("Payment Type", [ "Share Paid"], key="exp_paid_option")
    expense_members_input = st.text_input("Expense Members", key="exp_members")

    if st.button("Add Expense"):
        split_members = [m.strip() for m in expense_members_input.split(",") if m.strip()]
        payload = {
            "group_name": group_name_exp,
            "description": description,
            "amount": int(amount),
            "paid_option": paid_option,
        }
        if split_members:
            payload["split_members"] = split_members
        res = requests.post(f"{API_URL}/groups/add_expense", json=payload, headers=headers())
        if res.status_code == 200:
            st.success("Expense added successfully.")
            st.json(res.json())
        else:
            st.error(res.json())

# ---------------- JOIN EXPENSE ----------------
with tab_selection[4]:
    st.subheader("Join an Existing Expense")
    group_name_join_exp = st.text_input("Group Name", key="join_expense_group")
    expense_name_join = st.text_input("Expense Description to Join", key="join_expense_name")

    if st.button("Join This Expense"):
        if not st.session_state.token:
            st.warning("Please login to join an expense.")
        else:
            payload = {
                "group_name": group_name_join_exp,
                "expense_description": expense_name_join
            }
            res = requests.post(f"{API_URL}/groups/join_expense", json=payload, headers=headers())
            if res.status_code == 200:
                st.success("Joined the expense successfully!")
                st.json(res.json())
            else:
                st.error(res.json())

# ---------------- PAY EXPENSE ----------------
with tab_selection[5]:
    st.subheader("Pay for a Specific Expense")
    group_name_exp_pay = st.text_input("Group Name", key="group_pay_exp_group")
    expense_name_exp = st.text_input("Expense Description", key="group_pay_exp_name")
    pay_amount_exp = st.number_input("Amount to Pay (Expense)", min_value=1, step=1, key="group_pay_exp_amount")
    if st.button("Pay This Expense"):
        res = requests.post(
            f"{API_URL}/groups/pay_expense",
            json={
                "group_name": group_name_exp_pay,
                "expense_description": expense_name_exp,
                "amount": int(pay_amount_exp)
            },
            headers=headers()
        )
        if res.status_code == 200:
            result = res.json()
            st.success(result.get("message", "Payment successful."))
            st.json(result)
        else:
            st.error(res.json())

# ---------------- WALLET TRANSACTIONS ----------------
with tab_selection[6]:
    st.subheader("💳 Wallet Transactions")
    if not st.session_state.token:
        st.warning("Please login to view your wallet transactions.")
    else:
        res = requests.get(f"{API_URL}/wallet/transactions/me", headers=headers())
        if res.status_code == 200:
            txs = res.json().get("transactions", [])
            if not txs:
                st.info("No wallet transactions yet.")
            else:
                df = pd.DataFrame(txs)
                for col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: ", ".join(x) if isinstance(x, list)
                        else str(x) if x is not None
                        else ""
                    )
                st.dataframe(df, use_container_width=True)
        else:
            st.error(res.json())

# ---------------- ADMIN REGISTER ----------------
with tab_selection[7]:
    st.subheader("Admin Register")
    admin_user_reg = st.text_input("Admin Username", key="admin_reg_user_input")
    admin_pass_reg = st.text_input("Admin Password", type="password", key="admin_reg_pass_input")
    if st.button("Register Admin", key="admin_reg_button"):
        res = requests.post(f"{API_URL}/admin/register", json={"username": admin_user_reg, "password": admin_pass_reg})
        if res.status_code == 200:
            st.success(f"Admin '{admin_user_reg}' registered successfully!")
        else:
            st.error(res.json())

# ---------------- ADMIN LOGIN ----------------
with tab_selection[8]:
    st.subheader("Admin Login")
    admin_user_login = st.text_input("Admin Login Username", key="admin_login_user_input")
    admin_pass_login = st.text_input("Admin Login Password", type="password", key="admin_login_pass_input")
    if st.button("Login Admin", key="admin_login_button"):
        res = requests.post(f"{API_URL}/admin/login", json={"username": admin_user_login, "password": admin_pass_login})
        if res.status_code == 200:
            data = res.json()
            st.session_state.admin_token = data["access_token"]
            st.session_state.admin_username = admin_user_login
            st.success(f"Logged in as Admin {admin_user_login}")
        else:
            st.error(res.json())

# ---------------- ADMIN DASHBOARD ----------------
# ---------------- ADMIN DASHBOARD ----------------
# ---------------- ADMIN DASHBOARD ----------------
with tab_selection[9]:
    st.subheader("📊 Admin Dashboard – Group Expense Overview")
    if not st.session_state.admin_token:
        st.warning("Please login as admin to see the dashboard.")
    else:
        # Fetch admin dashboard data (groups, expenses)
        res_dash = requests.get(f"{API_URL}/admin/dashboard", headers=headers(token_type="admin"))
        if res_dash.status_code != 200:
            st.error("Unable to load dashboard data.")
            st.stop()
        dashboard = res_dash.json()

        # Fetch all wallet transactions for detailed logs
        res_txs = requests.get(f"{API_URL}/wallet/transactions/all", headers=headers(token_type="admin"))
        if res_txs.status_code != 200:
            st.error("Unable to load transaction logs.")
            st.stop()
        all_txs = res_txs.json().get("transactions", [])

        # Iterate through each group
        for group_name, data in dashboard.items():
            if group_name == "_summary":
                continue

            st.markdown(f"## 🏷️ Group: {group_name}")
            st.write("**Members:**", ", ".join(data["members"]))
            # st.write(f"**Total Expenses:** ₹{data['total_spent']}")
            # st.write(f"**Total Paid by Members:** ₹{data['total_paid_by_members']}")

            # ---------------- EXPENSE HISTORY ----------------
            if data["expenses"]:
                st.write("### 📋 Expense History")
                exp_df = pd.DataFrame(data["expenses"])

                # Drop 'per_user_paid' column if it exists
                if "per_user_paid" in exp_df.columns:
                    exp_df.drop(columns=["per_user_paid"], inplace=True)

                for col in exp_df.columns:
                    exp_df[col] = exp_df[col].apply(
                        lambda x: ", ".join(x) if isinstance(x, list)
                        else str(x) if x is not None
                        else ""
                    )

                st.dataframe(exp_df, use_container_width=True)

                # Export CSV for expense history
                csv_exp = exp_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"⬇️ Export '{group_name}' Expense History as CSV",
                    data=csv_exp,
                    file_name=f"{group_name}_expense_history.csv",
                    mime="text/csv"
                )

                st.divider()

                # ---------------- DETAILED EXPENSE TRANSACTIONS ----------------
                st.write("### 💳 Detailed Expense Transactions")

                for exp in data["expenses"]:
                    exp_name = exp.get("description")
                    exp_txs = [
                        t for t in all_txs
                        if t.get("group") == group_name
                        and t.get("expense") == exp_name
                        and t.get("type") != "deposit"
                    ]

                    if exp_txs:
                        df_exp_txs = pd.DataFrame(exp_txs)

                        # Drop unwanted fields
                        drop_cols = ["payment_type", "timestamp", "currency", "status", "user", "group"]
                        for c in drop_cols:
                            if c in df_exp_txs.columns:
                                df_exp_txs.drop(columns=c, inplace=True)

                        # Normalize lists and dicts
                        for col in df_exp_txs.columns:
                            df_exp_txs[col] = df_exp_txs[col].apply(
                                lambda x: ", ".join(x) if isinstance(x, list)
                                else str(x) if x is not None
                                else ""
                            )

                        st.markdown(f"**Expense:** {exp_name}")
                        st.dataframe(df_exp_txs, use_container_width=True)

                        # Export CSV for this expense’s transactions
                        csv_logs = df_exp_txs.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label=f"⬇️ Export '{exp_name}' Logs as CSV",
                            data=csv_logs,
                            file_name=f"{group_name}_{exp_name}_transactions.csv",
                            mime="text/csv"
                        )
                    else:
                        st.markdown(f"**Expense:** {exp_name}")
                        st.info("No transactions found for this expense.")

                    st.divider()

            else:
                st.info("No expenses recorded yet.")
