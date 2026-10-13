# utils.py
"""Shared utility functions for SmartSpend AI Streamlit app.
Includes data loading, KPI calculations, anomaly detection, and helper
functions used across multiple pages.
"""
import pandas as pd
import numpy as np
import os
from typing import Tuple, Optional

DATA_FILE = "sample_expense_data.csv"
USERS_FILE = "users.csv"


def load_data(file: Optional[object] = None) -> Optional[pd.DataFrame]:
    """Load expense data from uploaded file or default CSV.
    Returns a cleaned DataFrame with additional date-derived columns.
    """
    try:
        if file is None:
            path = os.path.join(os.path.dirname(__file__), DATA_FILE)
            df = pd.read_csv(path)
        else:
            df = pd.read_csv(file)
        required_cols = ["Date", "Category", "Amount", "Payment Method", "Description"]
        if not all(col in df.columns for col in required_cols):
            return None
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Date", "Amount"]).reset_index(drop=True)
        df["YearMonth"] = df["Date"].dt.to_period("M")
        df["MonthName"] = df["Date"].dt.strftime("%b %Y")
        df["DayOfWeek"] = df["Date"].dt.day_name()
        return df
    except Exception:
        return None


def get_month_df(df: pd.DataFrame, month: Optional[str] = None) -> pd.DataFrame:
    """Filter dataframe to a specific month (e.g., "Sep 2026").
    If month is None or "All", returns the original df.
    """
    if month is None or month == "All":
        return df.copy()
    return df[df["MonthName"] == month].copy()


def calculate_kpis(df: pd.DataFrame) -> Tuple[float, float, float, float]:
    """Return total_income, total_spent, total_saved, budget_remaining.
    The function assumes the DataFrame contains a column "Amount" where
    positive values are expenses. Income is derived from a special "Income"
    category if present; otherwise 0.
    """
    income_rows = df[df["Category"].str.lower() == "income"]
    total_income = float(income_rows["Amount"].sum())
    total_spent = float(df[~df["Category"].str.lower().eq("income")]["Amount"].sum())
    total_saved = max(total_income - total_spent, 0.0)
    budget_remaining = 0.0
    return total_income, total_spent, total_saved, budget_remaining


def get_category_totals(df: pd.DataFrame) -> pd.Series:
    """Return total amount per category (excluding Income)."""
    cat_df = df[~df["Category"].str.lower().eq("income")]
    return cat_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)


def detect_high_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Detect unusually high expenses using the IQR method.
    Returns a DataFrame of anomalous rows.
    """
    if df.empty:
        return df.copy()
    Q1 = df["Amount"].quantile(0.25)
    Q3 = df["Amount"].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    anomalies = df[df["Amount"] > upper_bound]
    return anomalies


def load_users() -> pd.DataFrame:
    """Load user profile information from USERS_FILE.
    If the file does not exist, create a default demo user.
    Columns: username,email,password_hash,monthly_income,monthly_budget,preferred_currency
    """
    if not os.path.isfile(USERS_FILE):
        df = pd.DataFrame([
            {
                "username": "demo",
                "email": "demo@example.com",
                "password_hash": "demo",
                "monthly_income": 75000,
                "monthly_budget": 50000,
                "preferred_currency": "₹",
                "joined": pd.Timestamp.now().date().isoformat(),
            }
        ])
        df.to_csv(USERS_FILE, index=False)
        return df
    else:
        return pd.read_csv(USERS_FILE)


def verify_user(username: str, password: str) -> Optional[pd.Series]:
    """Simple authentication against USERS_FILE. Returns user row if valid.
    Passwords are stored in plain text for this prototype.
    """
    users = load_users()
    match = users[(users["username"] == username) & (users["password_hash"] == password)]
    if not match.empty:
        return match.iloc[0]
    return None


def save_user(user_dict: dict) -> None:
    """Append or update a user record in USERS_FILE."""
    users = load_users()
    if user_dict["username"] in users["username"].values:
        users.loc[users["username"] == user_dict["username"], list(user_dict.keys())] = list(user_dict.values())
    else:
        users = pd.concat([users, pd.DataFrame([user_dict])], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Utility to convert a DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")

"""End of utils.py"""
