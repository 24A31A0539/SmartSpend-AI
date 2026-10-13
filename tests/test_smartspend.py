# tests/test_smartspend.py
"""
Automated Test Suite for SmartSpend AI
Validates:
- Password hashing & authentication security
- Multi-user data isolation
- Transaction CRUD & transaction types (Expense, Income, Refund, Transfer)
- Accurate financial KPI calculations
- CSV Import validation & duplicate handling
- Savings Goals contribution tracking
- Spending Scenarios modeling
- Forecasting edge cases (< 3 months vs >= 3 months)
- Sensible anomaly detection (only high outliers)
- Alert dismissal persistence
- Ask SmartSpend intelligence responses
"""
import os
import shutil
import json
import pytest
import pandas as pd
from datetime import datetime

import data_service as ds

TEST_USER_A = "test_user_alpha"
TEST_USER_B = "test_user_beta"

@pytest.fixture(scope="module", autouse=True)
def setup_teardown_test_env():
    # Clean any prior test user directories
    for u in [TEST_USER_A, TEST_USER_B]:
        u_dir = ds._get_user_dir(u)
        if os.path.exists(u_dir):
            shutil.rmtree(u_dir)
            
    yield

    # Teardown test directories
    for u in [TEST_USER_A, TEST_USER_B]:
        u_dir = ds._get_user_dir(u)
        if os.path.exists(u_dir):
            shutil.rmtree(u_dir)
        idx = ds._load_users_index()
        if u in idx:
            del idx[u]
            ds._save_users_index(idx)


def test_password_hashing_and_auth():
    # 1. Signup User A
    prof_a, err = ds.signup_user(
        username=TEST_USER_A,
        name="Alpha Tester",
        email="alpha@test.com",
        password="SecurePassword123!",
        monthly_income=80000.0,
        monthly_budget=55000.0,
        preferred_currency="₹"
    )
    assert err is None
    assert prof_a is not None
    assert prof_a['username'] == TEST_USER_A

    # 2. Verify stored password is NOT plaintext
    disk_prof = ds.get_user_profile(TEST_USER_A)
    assert disk_prof['password_hash'] != "SecurePassword123!"
    assert 'password_salt' in disk_prof

    # 3. Successful login
    login_prof, login_err = ds.login_user(TEST_USER_A, "SecurePassword123!")
    assert login_err is None
    assert login_prof['username'] == TEST_USER_A

    # 4. Failed login
    bad_prof, bad_err = ds.login_user(TEST_USER_A, "WrongPassword!")
    assert bad_prof is None
    assert bad_err is not None

    # 5. Change password
    ok, msg = ds.change_user_password(TEST_USER_A, "SecurePassword123!", "NewPassword456!")
    assert ok is True
    ok_relogin, _ = ds.login_user(TEST_USER_A, "NewPassword456!")
    assert ok_relogin is not None


def test_multi_user_data_isolation():
    # Signup User B
    prof_b, err = ds.signup_user(
        username=TEST_USER_B,
        name="Beta Tester",
        email="beta@test.com",
        password="BetaPassword123!",
        monthly_income=60000.0,
        monthly_budget=40000.0
    )
    assert err is None

    # Add transaction to User A
    ds.save_new_transaction(TEST_USER_A, "2026-09-10", "Dining", 1200.0, "UPI", "User A Dinner", "Expense")

    # Add transaction to User B
    ds.save_new_transaction(TEST_USER_B, "2026-09-12", "Transport", 450.0, "Cash", "User B Taxi", "Expense")

    df_a = ds.load_transactions(TEST_USER_A)
    df_b = ds.load_transactions(TEST_USER_B)

    # Ensure User A only sees their own transactions
    assert len(df_a) == 1
    assert df_a.iloc[0]['Description'] == "User A Dinner"
    assert (df_a['Description'] == "User B Taxi").sum() == 0

    # Ensure User B only sees their own transactions
    assert len(df_b) == 1
    assert df_b.iloc[0]['Description'] == "User B Taxi"
    assert (df_b['Description'] == "User A Dinner").sum() == 0


def test_transaction_crud_and_types():
    # Add an Expense
    ds.save_new_transaction(TEST_USER_A, "2026-09-15", "Shopping", 3000.0, "Credit Card", "Shoes", "Expense")
    # Add an Income
    ds.save_new_transaction(TEST_USER_A, "2026-09-01", "Salary", 20000.0, "Bank Transfer", "Freelance Gig", "Income")
    # Add a Refund
    ds.save_new_transaction(TEST_USER_A, "2026-09-16", "Shopping", 500.0, "UPI", "Shoe Refund", "Refund")

    df = ds.load_transactions(TEST_USER_A)
    assert len(df) == 4  # 1 initial + 3 new

    # Test Update
    shoe_row = df[df['Description'] == "Shoes"].iloc[0]
    shoe_id = shoe_row['id']
    up_ok, _ = ds.update_transaction(
        username=TEST_USER_A,
        txn_id=shoe_id,
        date_str="2026-09-15",
        category="Shopping",
        amount=2800.0,
        payment_method="Credit Card",
        description="Formal Shoes",
        transaction_type="Expense"
    )
    assert up_ok is True
    df_updated = ds.load_transactions(TEST_USER_A)
    assert df_updated[df_updated['id'] == shoe_id].iloc[0]['Amount'] == 2800.0
    assert df_updated[df_updated['id'] == shoe_id].iloc[0]['Description'] == "Formal Shoes"

    # Test Delete
    del_ok, _ = ds.delete_transaction_by_id(TEST_USER_A, shoe_id)
    assert del_ok is True
    df_after_del = ds.load_transactions(TEST_USER_A)
    assert len(df_after_del) == 3


def test_financial_kpi_calculations():
    prof_a = ds.get_user_profile(TEST_USER_A)
    # Baseline income: 80,000, Budget: 55,000
    # Current September 2026 transactions for User A:
    # 1. User A Dinner: Expense 1200
    # 2. Freelance Gig: Income 20000
    # 3. Shoe Refund: Refund 500
    # Expected:
    # Total Income = 80,000 + 20,000 = 100,000
    # Total Spent = Expenses (1200) - Refunds (500) = 700
    # Saved = 100,000 - 700 = 99,300
    # Budget Remaining = 55,000 - 700 = 54,300

    df_a = ds.load_transactions(TEST_USER_A)
    kpis = ds.calculate_kpis(df_a, "September 2026", prof_a)

    assert kpis['income'] == 100000.0
    assert kpis['spent'] == 700.0
    assert kpis['saved'] == 99300.0
    assert kpis['budget_remaining'] == 54300.0
    assert kpis['status_type'] == 'success'


def test_csv_import_validation():
    # Create sample CSV with valid and invalid rows and duplicates
    csv_content = """Date,Category,Amount,Payment Method,Description,Transaction Type
2026-09-18,Groceries,1500.0,UPI,Supermarket,Expense
2026-09-19,Dining,800.0,Cash,Lunch,Expense
invalid-date,Bills,900.0,UPI,Bad Date Row,Expense
2026-09-20,Bills,-400.0,UPI,Negative Amount,Expense
2026-09-18,Groceries,1500.0,UPI,Supermarket,Expense
"""
    import io
    file_obj = io.StringIO(csv_content)
    imported, skipped, errors = ds.import_transactions_csv(TEST_USER_A, file_obj)

    assert imported == 2  # Supermarket + Lunch
    assert skipped == 1   # Duplicate Supermarket
    assert len(errors) == 2  # invalid-date and negative amount


def test_savings_goals():
    # 1. Add Goal
    goals = ds.add_savings_goal(
        username=TEST_USER_A,
        name="Vacation in Japan",
        target_amount=120000.0,
        current_amount=20000.0,
        target_date="May 2027",
        category="Travel"
    )
    assert len(goals) == 1
    g_id = goals[0]['id']

    # 2. Add Contribution
    updated_goals = ds.add_to_goal_savings(TEST_USER_A, g_id, 30000.0)
    assert updated_goals[0]['current_amount'] == 50000.0

    # 3. Delete Goal
    final_goals = ds.delete_savings_goal(TEST_USER_A, g_id)
    assert len(final_goals) == 0


def test_spending_scenarios():
    prof_a = ds.get_user_profile(TEST_USER_A)
    df_a = ds.load_transactions(TEST_USER_A)

    # User A has Dining spending: 1200
    res = ds.calculate_spending_scenario(
        df=df_a,
        month_name="September 2026",
        user_profile=prof_a,
        reductions_pct={"Dining": 25}
    )

    # User A has Dining spending: 1200 (Dinner) + 800 (Lunch) = 2000
    # 25% of 2000 = 500 monthly savings increase
    assert res['category_details']['Dining']['reduction'] == 500.0
    assert res['monthly_savings_increase'] == 500.0
    assert res['annual_savings'] == 6000.0


def test_forecasting():
    prof_a = ds.get_user_profile(TEST_USER_A)
    df_a = ds.load_transactions(TEST_USER_A)

    # User A currently only has 1 month (September 2026)
    fc = ds.get_forecast(df_a, prof_a)
    assert fc['has_sufficient_history'] is False

    # Seed User A with 3 distinct months
    ds.save_new_transaction(TEST_USER_A, "2026-07-15", "Dining", 4000.0, "UPI", "July Dining", "Expense")
    ds.save_new_transaction(TEST_USER_A, "2026-08-15", "Dining", 5000.0, "UPI", "August Dining", "Expense")
    
    df_3m = ds.load_transactions(TEST_USER_A)
    fc_full = ds.get_forecast(df_3m, prof_a)
    assert fc_full['has_sufficient_history'] is True
    assert fc_full['data_months'] >= 3
    assert 'predicted_amount' in fc_full


def test_sensible_anomaly_detection():
    # Add regular small dining expenses
    ds.save_new_transaction(TEST_USER_A, "2026-09-02", "Dining", 350.0, "UPI", "Coffee", "Expense")
    ds.save_new_transaction(TEST_USER_A, "2026-09-03", "Dining", 400.0, "UPI", "Snack", "Expense")
    # Add an extreme outlier expense
    ds.save_new_transaction(TEST_USER_A, "2026-09-05", "Dining", 18500.0, "Credit Card", "Luxury Banquet", "Expense")

    df = ds.load_transactions(TEST_USER_A)
    anomalies = ds.detect_sensible_anomalies(df, "September 2026")

    # High expense flagged
    flagged_descs = [a['description'] for a in anomalies]
    assert "Luxury Banquet" in flagged_descs
    # Normal coffee and snacks must NOT be flagged
    assert "Coffee" not in flagged_descs
    assert "Snack" not in flagged_descs


def test_alert_dismissal_persistence():
    prof_a = ds.get_user_profile(TEST_USER_A)
    df = ds.load_transactions(TEST_USER_A)

    alerts = ds.get_user_alerts(df, "September 2026", prof_a, TEST_USER_A)
    assert len(alerts) > 0

    first_alert_id = alerts[0]['id']
    # Dismiss alert
    ds.dismiss_alert(TEST_USER_A, first_alert_id)

    # Re-fetch alerts; dismissed alert must not be present
    alerts_after = ds.get_user_alerts(df, "September 2026", prof_a, TEST_USER_A)
    remaining_ids = [a['id'] for a in alerts_after]
    assert first_alert_id not in remaining_ids

    # Reset dismissals
    ds.reset_dismissed_alerts(TEST_USER_A)
    alerts_reset = ds.get_user_alerts(df, "September 2026", prof_a, TEST_USER_A)
    reset_ids = [a['id'] for a in alerts_reset]
    assert first_alert_id in reset_ids


def test_ask_smartspend_assistant():
    prof_a = ds.get_user_profile(TEST_USER_A)
    df = ds.load_transactions(TEST_USER_A)

    res_budget = ds.ask_financial_assistant("What is my budget?", df, prof_a, "September 2026")
    assert "55,000" in res_budget['answer'] or "budget" in res_budget['answer'].lower()

    res_afford = ds.ask_financial_assistant("Can I afford a ₹2,000 purchase?", df, prof_a, "September 2026")
    assert "afford" in res_afford['answer'].lower()

    res_breakdown = ds.ask_financial_assistant("Where did my money go?", df, prof_a, "September 2026")
    assert "spending" in res_breakdown['answer'].lower() or "breakdown" in res_breakdown['answer'].lower()
