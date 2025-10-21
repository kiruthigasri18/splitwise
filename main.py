# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers from your modules
from groups import router as groups_router
from users import router as users_router
from admins import router as admins_router
from transactions import router as transactions_router
from analytics import router as analytics_router
from wallet import router as wallet_router  # new

import auth

# --------------------------------------------------------
# Initialize FastAPI app
# --------------------------------------------------------
app = FastAPI(
    title="Expense Management App",
    description="FastAPI backend for managing group expenses, payments, and analytics.",
    version="2.0"
)

# --------------------------------------------------------
# Middleware (CORS for Streamlit / Frontend access)
# --------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # You can restrict this to ["http://localhost:8501"] for Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# Register Routers
# --------------------------------------------------------
app.include_router(users_router)
app.include_router(groups_router)
app.include_router(admins_router)
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(wallet_router)

# --------------------------------------------------------
# Root Endpoint
# --------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "Welcome to the Expense Management API 🚀",
        "endpoints": {
            "/users": "User registration, login, balance operations",
            "/groups": "Group and expense management",
            "/transactions": "Transaction history APIs",
            "/analytics": "Spending analytics endpoints",
            "/admin": "Admin operations (dashboard, summary)",
            "/wallet": "Wallet transaction APIs",
        },
    }

# --------------------------------------------------------
# Run with: uvicorn main:app --reload
# --------------------------------------------------------
