# models.py
from pydantic import BaseModel
from typing import List, Optional

class RegisterModel(BaseModel):
    username: str
    password: str

class LoginModel(BaseModel):
    username: str
    password: str

class AdminRegisterModel(BaseModel):
    username: str
    password: str

class AdminLoginModel(BaseModel):
    username: str
    password: str

class GroupCreateModel(BaseModel):
    group_name: str
    members: List[str]

class GroupJoinModel(BaseModel):
    group_name: str

class ExpenseModel(BaseModel):
    group_name: str
    description: str
    amount: int
    paid_option: str  # "Full Amount Paid", "Share Paid", "Not Paid"
    split_members: Optional[List[str]] = None  # new: list of members involved in this expense; if None => all group members

class PayModel(BaseModel):
    group_name: str
    amount: int
