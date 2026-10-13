# data_service.py
"""
SmartSpend AI - Core Data & Financial Intelligence Service
Handles:
- User authentication with salted password hashing & multi-user isolation
- Transaction management (Expense, Income, Refund, Transfer) with CRUD, search, filter, CSV import/export
- Financial calculations (Income, Spending, Savings, Budget remaining)
- Savings Goals management & contribution tracking
- Spending Scenarios (What-If modeling)
- Spending Forecast (Run-rate velocity + Historical linear trend)
- Explainable, sensible anomaly & alert detection with persistent dismissal
- Grounded Ask SmartSpend AI financial assistant
"""
import os
import json
import uuid
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.linear_model import LinearRegression

DATA_BASE_DIR = 'data'
USERS_BASE_DIR = os.path.join(DATA_BASE_DIR, 'users')
USERS_INDEX_FILE = 'users.json'

os.makedirs(USERS_BASE_DIR, exist_ok=True)

# ============================================================
# PASSWORD SECURITY & AUTHENTICATION
# ============================================================
def _hash_password(password: str, salt: str = None) -> tuple:
    """Hash password with per-user salt using SHA-256."""
    if not salt:
        salt = os.urandom(16).hex()
    hash_obj = hashlib.sha256((salt + password).encode('utf-8'))
    return hash_obj.hexdigest(), salt

def _verify_password(stored_hash: str, salt: str, password_attempt: str) -> bool:
    """Verify password against stored salt and hash."""
    if not salt:
        # Fallback for legacy un-migrated accounts
        return stored_hash == password_attempt
    attempt_hash, _ = _hash_password(password_attempt, salt)
    return attempt_hash == stored_hash

# ============================================================
# USER DIRECTORY & STORAGE MANAGEMENT
# ============================================================
def _get_user_dir(username: str) -> str:
    clean_un = username.lower().strip() if username else 'janaganika'
    user_dir = os.path.join(USERS_BASE_DIR, clean_un)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def _ensure_user_storage(username: str):
    """Ensure user directory and files exist, migrating legacy data if needed."""
    clean_un = username.lower().strip() if username else 'janaganika'
    user_dir = _get_user_dir(clean_un)
    
    tx_file = os.path.join(user_dir, 'transactions.csv')
    goals_file = os.path.join(user_dir, 'goals.json')
    prof_file = os.path.join(user_dir, 'profile.json')
    alerts_file = os.path.join(user_dir, 'alerts_state.json')

    if not os.path.exists(alerts_file):
        with open(alerts_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Seed janaganika default data if fresh
    if clean_un == 'janaganika':
        if not os.path.exists(tx_file) and os.path.exists('sample_expense_data.csv'):
            import shutil
            shutil.copy('sample_expense_data.csv', tx_file)
        if not os.path.exists(goals_file):
            default_goals = [
                {"id": "g-1", "name": "New Laptop", "target_amount": 60000.0, "current_amount": 25000.0, "target_date": "March 2027", "category": "Electronics", "status": "In Progress"},
                {"id": "g-2", "name": "Emergency Fund", "target_amount": 150000.0, "current_amount": 90000.0, "target_date": "December 2027", "category": "Savings", "status": "In Progress"}
            ]
            with open(goals_file, 'w', encoding='utf-8') as f:
                json.dump(default_goals, f, indent=2)
        if not os.path.exists(prof_file):
            h_pwd, salt = _hash_password("password123")
            default_prof = {
                "username": "janaganika",
                "name": "Janaganika",
                "email": "janaganika@smartspend.ai",
                "password_hash": h_pwd,
                "password_salt": salt,
                "monthly_income": 75000.0,
                "monthly_budget": 50000.0,
                "preferred_currency": "₹",
                "member_since": "September 2025",
                "account_status": "Active",
                "onboarding_complete": True
            }
            with open(prof_file, 'w', encoding='utf-8') as f:
                json.dump(default_prof, f, indent=2, ensure_ascii=False)
    else:
        if not os.path.exists(tx_file):
            empty_df = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type'])
            empty_df.to_csv(tx_file, index=False)
        if not os.path.exists(goals_file):
            with open(goals_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

def _load_users_index() -> dict:
    if not os.path.exists(USERS_INDEX_FILE):
        return {}
    try:
        with open(USERS_INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users_index(data: dict):
    with open(USERS_INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ============================================================
# USER AUTHENTICATION & PROFILE APIS
# ============================================================
def signup_user(username, name, email, password, monthly_income, monthly_budget, preferred_currency="₹"):
    clean_un = username.lower().strip()
    if not clean_un or not name.strip() or not email.strip() or not password:
        return None, "All personal fields are required."
    
    users = _load_users_index()
    if clean_un in users or os.path.exists(os.path.join(USERS_BASE_DIR, clean_un, 'profile.json')):
        return None, "This username is already taken. Please choose another one."

    pwd_hash, salt = _hash_password(password)
    user_data = {
        "username": clean_un,
        "name": name.strip(),
        "email": email.strip(),
        "password_hash": pwd_hash,
        "password_salt": salt,
        "monthly_income": float(monthly_income),
        "monthly_budget": float(monthly_budget),
        "preferred_currency": preferred_currency or "₹",
        "member_since": datetime.now().strftime("%B %Y"),
        "account_status": "Active",
        "onboarding_complete": False
    }

    # Save to index
    users[clean_un] = {k: v for k, v in user_data.items() if k not in ['password_salt']}
    _save_users_index(users)

    # Initialize user storage
    user_dir = _get_user_dir(clean_un)
    with open(os.path.join(user_dir, 'profile.json'), 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2, ensure_ascii=False)
    
    empty_df = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type'])
    empty_df.to_csv(os.path.join(user_dir, 'transactions.csv'), index=False)
    
    with open(os.path.join(user_dir, 'goals.json'), 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)

    with open(os.path.join(user_dir, 'alerts_state.json'), 'w', encoding='utf-8') as f:
        json.dump([], f, indent=2)

    return user_data, None

def login_user(username, password):
    clean_un = username.lower().strip()
    if not clean_un or not password:
        return None, "Username and password are required."
    
    _ensure_user_storage(clean_un)
    prof_file = os.path.join(_get_user_dir(clean_un), 'profile.json')
    user_info = None

    if os.path.exists(prof_file):
        try:
            with open(prof_file, 'r', encoding='utf-8') as f:
                user_info = json.load(f)
        except Exception:
            pass
            
    if not user_info:
        users = _load_users_index()
        user_info = users.get(clean_un)

    if not user_info:
        return None, "Invalid username or password."

    stored_hash = user_info.get('password_hash')
    salt = user_info.get('password_salt')
    legacy_pwd = user_info.get('password')

    authenticated = False
    if stored_hash and salt:
        authenticated = _verify_password(stored_hash, salt, password)
    elif legacy_pwd and legacy_pwd == password:
        # Legacy user migration
        new_hash, new_salt = _hash_password(password)
        user_info['password_hash'] = new_hash
        user_info['password_salt'] = new_salt
        user_info.pop('password', None)
        with open(prof_file, 'w', encoding='utf-8') as f:
            json.dump(user_info, f, indent=2, ensure_ascii=False)
        authenticated = True

    if authenticated:
        profile = dict(user_info)
        profile['username'] = clean_un
        # Clean currency encoding if corrupted
        if profile.get('preferred_currency') in ['â‚¹', '', None]:
            profile['preferred_currency'] = '₹'
        return profile, None

    return None, "Invalid username or password. Please check your credentials."

def get_user_profile(username=None):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    prof_file = os.path.join(_get_user_dir(clean_un), 'profile.json')
    if os.path.exists(prof_file):
        try:
            with open(prof_file, 'r', encoding='utf-8') as f:
                p = json.load(f)
                p['username'] = clean_un
                if p.get('preferred_currency') in ['â‚¹', '', None]:
                    p['preferred_currency'] = '₹'
                return p
        except Exception:
            pass
    return {
        "username": clean_un,
        "name": clean_un.capitalize(),
        "email": f"{clean_un}@smartspend.ai",
        "monthly_income": 75000.0,
        "monthly_budget": 50000.0,
        "preferred_currency": "₹",
        "member_since": "September 2026",
        "account_status": "Active",
        "onboarding_complete": True
    }

def update_user_profile(username, updated_dict):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    profile = get_user_profile(clean_un)
    profile.update(updated_dict)
    profile['username'] = clean_un
    
    prof_file = os.path.join(_get_user_dir(clean_un), 'profile.json')
    with open(prof_file, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    users = _load_users_index()
    if clean_un in users:
        users[clean_un].update({k: v for k, v in updated_dict.items() if k not in ['password_salt', 'password_hash']})
        _save_users_index(users)
    return profile

def change_user_password(username, old_password, new_password):
    clean_un = username.lower().strip() if username else 'janaganika'
    profile = get_user_profile(clean_un)
    stored_hash = profile.get('password_hash')
    salt = profile.get('password_salt')
    legacy_pwd = profile.get('password')

    valid_old = False
    if stored_hash and salt:
        valid_old = _verify_password(stored_hash, salt, old_password)
    elif legacy_pwd:
        valid_old = (legacy_pwd == old_password)

    if not valid_old:
        return False, "Current password does not match."
    
    if len(new_password) < 4:
        return False, "New password must be at least 4 characters long."

    new_hash, new_salt = _hash_password(new_password)
    update_user_profile(clean_un, {
        'password_hash': new_hash,
        'password_salt': new_salt
    })
    return True, "Password updated successfully."

# ============================================================
# PER-USER TRANSACTIONS CRUD & IMPORT/EXPORT
# ============================================================
def load_transactions(username=None):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    tx_file = os.path.join(_get_user_dir(clean_un), 'transactions.csv')
    
    empty_df = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type'])
    if not os.path.exists(tx_file):
        return empty_df
    try:
        df = pd.read_csv(tx_file)
        if df.empty or 'Date' not in df.columns or 'Amount' not in df.columns:
            return empty_df
        
        # Ensure stable ID column
        if 'id' not in df.columns:
            df['id'] = [str(uuid.uuid4())[:8] for _ in range(len(df))]
            df.to_csv(tx_file, index=False)
            
        # Ensure Transaction Type column (Expense, Income, Refund, Transfer)
        if 'Transaction Type' not in df.columns:
            df['Transaction Type'] = 'Expense'
            df.to_csv(tx_file, index=False)
        else:
            df['Transaction Type'] = df['Transaction Type'].fillna('Expense')

        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Date', 'Amount']).sort_values(by='Date', ascending=False).reset_index(drop=True)
        if df.empty:
            return empty_df

        df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
        df['MonthName'] = df['Date'].dt.strftime('%B %Y')
        return df
    except Exception:
        return empty_df

def save_new_transaction(username, date_str, category, amount, payment_method, description, transaction_type="Expense"):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    tx_file = os.path.join(_get_user_dir(clean_un), 'transactions.csv')
    
    df = load_transactions(clean_un)
    new_id = str(uuid.uuid4())[:8]
    new_row = pd.DataFrame([{
        'id': new_id,
        'Date': pd.to_datetime(date_str),
        'Category': category,
        'Amount': float(amount),
        'Payment Method': payment_method,
        'Description': description,
        'Transaction Type': transaction_type
    }])
    df = pd.concat([new_row, df], ignore_index=True)
    exp = df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
    exp['Date'] = pd.to_datetime(exp['Date']).dt.strftime('%Y-%m-%d')
    exp.to_csv(tx_file, index=False)
    return df

def update_transaction(username, txn_id, date_str, category, amount, payment_method, description, transaction_type="Expense"):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    tx_file = os.path.join(_get_user_dir(clean_un), 'transactions.csv')
    df = load_transactions(clean_un)
    
    mask = df['id'].astype(str) == str(txn_id)
    if mask.any():
        df.loc[mask, 'Date'] = pd.to_datetime(date_str)
        df.loc[mask, 'Category'] = category
        df.loc[mask, 'Amount'] = float(amount)
        df.loc[mask, 'Payment Method'] = payment_method
        df.loc[mask, 'Description'] = description
        df.loc[mask, 'Transaction Type'] = transaction_type
        
        exp = df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
        exp['Date'] = pd.to_datetime(exp['Date']).dt.strftime('%Y-%m-%d')
        exp.to_csv(tx_file, index=False)
        return True, "Transaction updated successfully."
    return False, "Transaction ID not found."

def delete_transaction_by_id(username, txn_id):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    tx_file = os.path.join(_get_user_dir(clean_un), 'transactions.csv')
    df = load_transactions(clean_un)
    
    initial_len = len(df)
    df = df[df['id'].astype(str) != str(txn_id)].reset_index(drop=True)
    if len(df) < initial_len:
        exp = df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
        exp['Date'] = pd.to_datetime(exp['Date']).dt.strftime('%Y-%m-%d')
        exp.to_csv(tx_file, index=False)
        return True, "Transaction deleted."
    return False, "Transaction not found."

def import_transactions_csv(username, uploaded_file):
    """
    Import transactions from CSV with schema and data validation.
    Returns (imported_count, skipped_count, error_messages)
    """
    clean_un = username.lower().strip() if username else 'janaganika'
    try:
        import_df = pd.read_csv(uploaded_file)
    except Exception as e:
        return 0, 0, [f"Failed to read CSV file: {str(e)}"]

    required_cols = ['Date', 'Category', 'Amount']
    missing_cols = [c for c in required_cols if c not in import_df.columns]
    if missing_cols:
        return 0, 0, [f"Missing required columns in CSV: {', '.join(missing_cols)}. Expected: Date, Category, Amount"]

    existing_df = load_transactions(clean_un)
    existing_signatures = set()
    if not existing_df.empty:
        for _, r in existing_df.iterrows():
            d_str = pd.to_datetime(r['Date']).strftime('%Y-%m-%d') if pd.notna(r['Date']) else ''
            sig = f"{d_str}_{r['Category']}_{float(r['Amount'])}_{str(r.get('Description', ''))}"
            existing_signatures.add(sig)

    valid_rows = []
    errors = []
    skipped_duplicates = 0

    for idx, row in import_df.iterrows():
        row_num = idx + 2
        raw_date = row['Date']
        parsed_date = pd.to_datetime(raw_date, errors='coerce')
        if pd.isna(parsed_date):
            errors.append(f"Row {row_num}: Invalid date format '{raw_date}'.")
            continue

        raw_amt = row['Amount']
        try:
            amt = float(raw_amt)
            if amt <= 0:
                errors.append(f"Row {row_num}: Amount must be positive. Found {amt}.")
                continue
        except (ValueError, TypeError):
            errors.append(f"Row {row_num}: Non-numeric amount '{raw_amt}'.")
            continue

        cat = str(row['Category']).strip() if pd.notna(row['Category']) else 'Other'
        pay = str(row['Payment Method']).strip() if 'Payment Method' in row and pd.notna(row['Payment Method']) else 'Other'
        desc = str(row['Description']).strip() if 'Description' in row and pd.notna(row['Description']) else cat
        ttype = str(row['Transaction Type']).strip() if 'Transaction Type' in row and pd.notna(row['Transaction Type']) else 'Expense'
        if ttype not in ['Expense', 'Income', 'Refund', 'Transfer']:
            ttype = 'Expense'

        sig = f"{parsed_date.strftime('%Y-%m-%d')}_{cat}_{amt}_{desc}"
        if sig in existing_signatures:
            skipped_duplicates += 1
            continue

        existing_signatures.add(sig)
        valid_rows.append({
            'id': str(uuid.uuid4())[:8],
            'Date': parsed_date,
            'Category': cat,
            'Amount': amt,
            'Payment Method': pay,
            'Description': desc,
            'Transaction Type': ttype
        })

    if valid_rows:
        new_valid_df = pd.DataFrame(valid_rows)
        combined_df = pd.concat([new_valid_df, existing_df], ignore_index=True)
        tx_file = os.path.join(_get_user_dir(clean_un), 'transactions.csv')
        exp = combined_df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
        exp['Date'] = pd.to_datetime(exp['Date']).dt.strftime('%Y-%m-%d')
        exp.to_csv(tx_file, index=False)

    return len(valid_rows), skipped_duplicates, errors

# ============================================================
# MONTH / PERIOD HANDLING
# ============================================================
def get_available_months(df):
    current_month = datetime.now().strftime('%B %Y')
    if df.empty:
        return [current_month]
    months = list(dict.fromkeys(df.sort_values(by='Date', ascending=False)['MonthName'].tolist()))
    if current_month not in months:
        months.insert(0, current_month)
    return months

def get_month_data(df, month_name):
    if df.empty:
        return df
    if month_name == 'All' or not month_name:
        return df.copy()
    return df[df['MonthName'] == month_name].copy()

# ============================================================
# FINANCIAL METRICS & CONSISTENT KPIS
# ============================================================
def calculate_kpis(df, month_name, user_profile):
    """
    Consistent financial definitions:
    - Base Income: from profile
    - Additional Income: from transactions with Type == 'Income'
    - Total Income: Base Income + Additional Income
    - Total Spending: (Expense transactions) - (Refund transactions)
    - Savings / Net Balance: Total Income - Total Spending
    - Budget Remaining: Budget - Total Spending
    """
    month_df = get_month_data(df, month_name)
    base_income = float(user_profile.get('monthly_income', 75000.0))
    budget = float(user_profile.get('monthly_budget', 50000.0))

    if month_df.empty:
        return {
            'income': base_income,
            'extra_income': 0.0,
            'spent': 0.0,
            'saved': base_income,
            'budget': budget,
            'budget_remaining': budget,
            'budget_pct': 0.0,
            'status': 'Within budget',
            'status_type': 'success',
            'has_transactions': False
        }

    # Separate by transaction type
    extra_income = float(month_df[month_df['Transaction Type'] == 'Income']['Amount'].sum())
    expenses = float(month_df[month_df['Transaction Type'] == 'Expense']['Amount'].sum())
    refunds = float(month_df[month_df['Transaction Type'] == 'Refund']['Amount'].sum())

    total_income = base_income + extra_income
    total_spent = max(0.0, expenses - refunds)
    saved = total_income - total_spent
    budget_remaining = budget - total_spent
    budget_pct = (total_spent / budget * 100.0) if budget > 0 else 0.0

    if budget_pct <= 80.0:
        status, status_type = 'Within budget', 'success'
    elif budget_pct <= 100.0:
        status, status_type = 'Approaching limit', 'warning'
    else:
        status, status_type = 'Over budget', 'danger'

    return {
        'income': total_income,
        'extra_income': extra_income,
        'spent': total_spent,
        'saved': saved,
        'budget': budget,
        'budget_remaining': budget_remaining,
        'budget_pct': min(100.0, budget_pct),
        'status': status,
        'status_type': status_type,
        'has_transactions': True
    }

def get_category_breakdown(df, month_name):
    """Category breakdown calculating net expenses (Expense minus Refund)."""
    month_df = get_month_data(df, month_name)
    if month_df.empty:
        return pd.Series(dtype=float)
    
    # Filter to expenses and refunds
    expense_df = month_df[month_df['Transaction Type'] == 'Expense']
    refund_df = month_df[month_df['Transaction Type'] == 'Refund']

    cat_exp = expense_df.groupby('Category')['Amount'].sum()
    cat_ref = refund_df.groupby('Category')['Amount'].sum()

    net_series = cat_exp.subtract(cat_ref, fill_value=0.0)
    net_series = net_series[net_series > 0].sort_values(ascending=False)
    return net_series

# ============================================================
# SAVINGS GOALS APIS
# ============================================================
def get_savings_goals(username=None):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    goals_file = os.path.join(_get_user_dir(clean_un), 'goals.json')
    if os.path.exists(goals_file):
        try:
            with open(goals_file, 'r', encoding='utf-8') as f:
                goals = json.load(f)
                for g in goals:
                    if 'status' not in g:
                        g['status'] = 'In Progress'
                return goals
        except Exception:
            return []
    return []

def save_savings_goals(username, goals):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    goals_file = os.path.join(_get_user_dir(clean_un), 'goals.json')
    with open(goals_file, 'w', encoding='utf-8') as f:
        json.dump(goals, f, indent=2)

def add_savings_goal(username, name, target_amount, current_amount, target_date, category='Savings'):
    goals = get_savings_goals(username)
    new_id = f"g-{str(uuid.uuid4())[:6]}"
    goals.append({
        "id": new_id,
        "name": name.strip(),
        "target_amount": float(target_amount),
        "current_amount": float(current_amount),
        "target_date": target_date.strip() if target_date else "Flexible",
        "category": category,
        "status": "In Progress"
    })
    save_savings_goals(username, goals)
    return goals

def update_savings_goal(username, goal_id, name, target_amount, target_date, category, status="In Progress"):
    goals = get_savings_goals(username)
    for g in goals:
        if str(g.get('id')) == str(goal_id):
            g['name'] = name.strip()
            g['target_amount'] = float(target_amount)
            g['target_date'] = target_date.strip()
            g['category'] = category
            g['status'] = status
            break
    save_savings_goals(username, goals)
    return goals

def add_to_goal_savings(username, goal_id, amount):
    goals = get_savings_goals(username)
    for g in goals:
        if str(g.get('id')) == str(goal_id):
            g['current_amount'] = g['current_amount'] + float(amount)
            if g['current_amount'] >= g['target_amount']:
                g['status'] = 'Completed'
            break
    save_savings_goals(username, goals)
    return goals

def delete_savings_goal(username, goal_id):
    goals = [g for g in get_savings_goals(username) if str(g.get('id')) != str(goal_id)]
    save_savings_goals(username, goals)
    return goals

# ============================================================
# SPENDING SCENARIOS (WHAT-IF)
# ============================================================
def calculate_spending_scenario(df, month_name, user_profile, reductions_pct: dict):
    """
    Simulates category-specific spending reductions against actual baseline.
    Returns clear before-and-after comparison.
    """
    kpis = calculate_kpis(df, month_name, user_profile)
    cat_breakdown = get_category_breakdown(df, month_name)
    
    current_spent = kpis['spent']
    current_income = kpis['income']
    current_savings = kpis['saved']
    
    category_diffs = {}
    total_reduction = 0.0

    for cat, pct in reductions_pct.items():
        base_amt = cat_breakdown.get(cat, 0.0)
        reduction_amt = base_amt * (float(pct) / 100.0)
        category_diffs[cat] = {
            'baseline': base_amt,
            'pct': pct,
            'reduction': reduction_amt,
            'projected': base_amt - reduction_amt
        }
        total_reduction += reduction_amt

    simulated_spent = max(0.0, current_spent - total_reduction)
    simulated_savings = current_savings + total_reduction
    annual_savings = total_reduction * 12.0

    return {
        'baseline_month': month_name,
        'current_spending': current_spent,
        'simulated_spending': simulated_spent,
        'monthly_savings_increase': total_reduction,
        'current_savings': current_savings,
        'simulated_savings': simulated_savings,
        'annual_savings': annual_savings,
        'category_details': category_diffs
    }

# ============================================================
# SPENDING FORECAST
# ============================================================
def get_forecast(df, user_profile):
    """
    Honest spending forecast:
    - If < 3 months of data: Returns limited data status.
    - If >= 3 months of data: Uses linear OLS trend line + run-rate analysis.
    """
    if df.empty:
        return None
        
    expense_df = df[df['Transaction Type'] == 'Expense']
    monthly = expense_df.groupby('YearMonth')['Amount'].sum().reset_index()
    
    if len(monthly) < 3:
        return {
            'has_sufficient_history': False,
            'data_months': len(monthly),
            'historical_months': monthly['YearMonth'].tolist() if not monthly.empty else [],
            'historical_amounts': monthly['Amount'].tolist() if not monthly.empty else [],
            'message': f"Only {len(monthly)} month(s) of transaction history available. At least 3 months are needed to calculate historical trends."
        }
        
    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly['Amount'].values
    model = LinearRegression()
    model.fit(X, y)
    
    next_idx = len(monthly)
    pred_amount = max(500.0, round(float(model.predict(np.array([[next_idx]]))[0]), 0))
    
    last_ym = monthly['YearMonth'].iloc[-1]
    next_dt = pd.to_datetime(last_ym + '-01') + pd.DateOffset(months=1)
    
    budget = float(user_profile.get('monthly_budget', 50000.0))
    diff = budget - pred_amount
    r2 = float(model.score(X, y))
    
    recent = monthly['YearMonth'].tail(3).tolist()
    rdf = expense_df[expense_df['YearMonth'].isin(recent)]
    total_recent = rdf['Amount'].sum()
    cat_shares = (rdf.groupby('Category')['Amount'].sum() / total_recent).to_dict() if total_recent > 0 else {}
    proj_cats = {c: round(s * pred_amount, 0) for c, s in sorted(cat_shares.items(), key=lambda x: x[1], reverse=True)}
    
    return {
        'has_sufficient_history': True,
        'next_month': next_dt.strftime('%B %Y'),
        'predicted_amount': pred_amount,
        'budget': budget,
        'expected_difference': abs(round(diff, 0)),
        'under_budget': diff >= 0,
        'historical_months': monthly['YearMonth'].tolist(),
        'historical_amounts': monthly['Amount'].tolist(),
        'r2_score': round(max(0.0, r2), 3),
        'slope': round(float(model.coef_[0]), 2),
        'projected_categories': proj_cats,
        'data_months': len(monthly)
    }

get_spending_forecast = get_forecast

# ============================================================
# ALERTS & ANOMALY DETECTION WITH PERSISTENT DISMISSAL
# ============================================================
def _get_dismissed_alerts(username: str) -> list:
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    alerts_file = os.path.join(_get_user_dir(clean_un), 'alerts_state.json')
    if os.path.exists(alerts_file):
        try:
            with open(alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def dismiss_alert(username: str, alert_id: str):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    dismissed = _get_dismissed_alerts(clean_un)
    if alert_id not in dismissed:
        dismissed.append(alert_id)
        alerts_file = os.path.join(_get_user_dir(clean_un), 'alerts_state.json')
        with open(alerts_file, 'w', encoding='utf-8') as f:
            json.dump(dismissed, f, indent=2)

def reset_dismissed_alerts(username: str):
    clean_un = username.lower().strip() if username else 'janaganika'
    _ensure_user_storage(clean_un)
    alerts_file = os.path.join(_get_user_dir(clean_un), 'alerts_state.json')
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

def detect_sensible_anomalies(df, month_name=None):
    """
    Multi-factor outlier detection:
    Flags ONLY transactions that are significantly higher than historical category baseline.
    Never flags low or ordinary transactions.
    """
    if df.empty:
        return []
        
    expense_df = df[df['Transaction Type'] == 'Expense']
    if expense_df.empty:
        return []

    anomalies = []
    cat_stats = {}
    for cat, group in expense_df.groupby('Category'):
        amounts = group['Amount']
        q3 = amounts.quantile(0.75)
        iqr = q3 - amounts.quantile(0.25)
        median = amounts.median()
        mean = amounts.mean()
        std = amounts.std() if len(amounts) > 1 else 0
        high_threshold = max(q3 + 1.5 * iqr, mean + 2.0 * std, median * 2.5, 3500.0)
        cat_stats[cat] = {'median': median, 'mean': mean, 'threshold': high_threshold}

    target_df = get_month_data(expense_df, month_name) if month_name and month_name != 'All' else expense_df
    for idx, row in target_df.iterrows():
        cat, amt = row['Category'], row['Amount']
        stats = cat_stats.get(cat)
        if stats and amt >= stats['threshold']:
            d_str = row['Date'].strftime('%B %d, %Y') if hasattr(row['Date'], 'strftime') else str(row['Date'])
            anomalies.append({
                'id': f"anom-{str(row.get('id', idx))}",
                'txn_id': str(row.get('id', idx)),
                'date': d_str,
                'category': cat,
                'amount': amt,
                'description': row['Description'] if pd.notna(row['Description']) and row['Description'] else cat,
                'typical_amount': round(stats['median'], 0),
                'difference_pct': round(((amt - stats['median']) / stats['median']) * 100, 0) if stats['median'] > 0 else 0
            })
    anomalies.sort(key=lambda x: x['amount'], reverse=True)
    return anomalies

def detect_recurring_expenses(df):
    """Finds regular monthly subscriptions and recurring commitments."""
    if df.empty or len(df['YearMonth'].unique()) < 2:
        return []
    recurring = []
    expense_df = df[df['Transaction Type'] == 'Expense']
    for (cat, desc), grp in expense_df.groupby(['Category', 'Description']):
        dm = grp['YearMonth'].nunique()
        desc_str = str(desc)
        is_known_kw = any(k in desc_str.lower() for k in ['rent', 'broadband', 'electricity', 'subscription', 'netflix', 'internet', 'gym', 'spotify'])
        if dm >= 3 or is_known_kw:
            avg = grp['Amount'].mean()
            std = grp['Amount'].std() if len(grp) > 1 else 0
            if std < avg * 0.45 or is_known_kw:
                day = grp['Date'].dt.day.mode()[0] if not grp.empty else 1
                recurring.append({
                    'description': desc,
                    'category': cat,
                    'amount': round(avg, 0),
                    'typical_day': int(day),
                    'frequency': 'Monthly',
                    'occurrences': dm
                })
    recurring.sort(key=lambda x: x['amount'], reverse=True)
    return recurring

def get_user_alerts(df, month_name, user_profile, username):
    """Generates all actionable alerts, filtering out dismissed items."""
    dismissed = set(_get_dismissed_alerts(username))
    alerts = []
    curr = user_profile.get('preferred_currency', '₹')

    # 1. Budget Alerts
    kpis = calculate_kpis(df, month_name, user_profile)
    if kpis['budget_pct'] > 100.0:
        b_id = f"b-over-{month_name}"
        if b_id not in dismissed:
            alerts.append({
                'id': b_id,
                'title': f"Budget exceeded in {month_name}",
                'severity': 'danger',
                'message': f"You have spent {curr}{kpis['spent']:,.0f}, exceeding your {curr}{kpis['budget']:,.0f} limit by {curr}{abs(kpis['budget_remaining']):,.0f}.",
                'action_label': "View Transactions",
                'action_target': "Transactions"
            })
    elif kpis['budget_pct'] >= 80.0:
        b_id = f"b-near-{month_name}"
        if b_id not in dismissed:
            alerts.append({
                'id': b_id,
                'title': f"Budget nearing limit in {month_name}",
                'severity': 'warning',
                'message': f"You've used {round(kpis['budget_pct'])}% of your monthly budget. Only {curr}{kpis['budget_remaining']:,.0f} remains.",
                'action_label': "Review Spending",
                'action_target': "Spending"
            })

    # 2. Anomaly Outliers
    anomalies = detect_sensible_anomalies(df, month_name)
    for a in anomalies:
        a_id = f"a-{a['id']}"
        if a_id not in dismissed:
            alerts.append({
                'id': a_id,
                'title': f"Unusually high {a['category']} expense",
                'severity': 'warning',
                'message': f"₹{a['amount']:,.0f} on '{a['description']}' ({a['date']}). Typical spending is ~{curr}{a['typical_amount']:,.0f}.",
                'action_label': "Review Transaction",
                'action_target': "Transactions"
            })

    # 3. Category Increase Alert vs Previous Month
    all_months = get_available_months(df)
    cur_idx = all_months.index(month_name) if month_name in all_months else -1
    if cur_idx != -1 and cur_idx + 1 < len(all_months):
        prev_m = all_months[cur_idx + 1]
        prev_breakdown = get_category_breakdown(df, prev_m)
        curr_breakdown = get_category_breakdown(df, month_name)
        for cat, c_amt in curr_breakdown.items():
            p_amt = prev_breakdown.get(cat, 0.0)
            if p_amt > 1000.0 and c_amt > p_amt * 1.35 and (c_amt - p_amt) >= 2000.0:
                cat_id = f"cat-inc-{cat}-{month_name}"
                if cat_id not in dismissed:
                    diff = c_amt - p_amt
                    alerts.append({
                        'id': cat_id,
                        'title': f"{cat} spending increased significantly",
                        'severity': 'warning',
                        'message': f"{cat} rose by +{curr}{diff:,.0f} compared to {prev_m} ({curr}{c_amt:,.0f} vs {curr}{p_amt:,.0f}).",
                        'action_label': "Inspect Category",
                        'action_target': "Spending"
                    })

    return alerts

def get_insights(df, month_name, user_profile):
    """Generates 2 to 3 concise, meaningful insights for Overview."""
    insights = []
    curr = user_profile.get('preferred_currency', '₹')
    kpis = calculate_kpis(df, month_name, user_profile)
    month_df = get_month_data(df, month_name)

    if month_df.empty:
        insights.append({
            'title': 'Full budget available',
            'text': f"No expenses have been recorded for {month_name} yet. Your entire {curr}{kpis['budget']:,.0f} budget is intact.",
            'type': 'good'
        })
        insights.append({
            'title': 'Savings potential',
            'text': f"Your potential savings this month is {curr}{kpis['income']:,.0f}.",
            'type': 'info'
        })
        return insights

    # Insight 1: Budget status
    if kpis['spent'] <= kpis['budget']:
        insights.append({
            'title': "Within planned budget",
            'text': f"You have {curr}{kpis['budget_remaining']:,.0f} ({100 - round(kpis['budget_pct'])}%) available for the rest of {month_name}.",
            'type': 'good'
        })
    else:
        insights.append({
            'title': "Budget limit exceeded",
            'text': f"You have spent {curr}{abs(kpis['budget_remaining']):,.0f} over your {curr}{kpis['budget']:,.0f} planned limit.",
            'type': 'danger'
        })

    # Insight 2: Top expense category
    cat_breakdown = get_category_breakdown(df, month_name)
    if not cat_breakdown.empty:
        top_cat = cat_breakdown.index[0]
        top_amt = cat_breakdown.iloc[0]
        share = round((top_amt / kpis['spent']) * 100) if kpis['spent'] > 0 else 0
        insights.append({
            'title': f"{top_cat} is your largest expense",
            'text': f"You spent {curr}{top_amt:,.0f} on {top_cat}, representing {share}% of your monthly expenses.",
            'type': 'info'
        })

    # Insight 3: MoM comparison
    all_months = get_available_months(df)
    cur_idx = all_months.index(month_name) if month_name in all_months else -1
    if cur_idx != -1 and cur_idx + 1 < len(all_months):
        prev_m = all_months[cur_idx + 1]
        prev_kpis = calculate_kpis(df, prev_m, user_profile)
        if prev_kpis['spent'] > 0:
            diff = kpis['spent'] - prev_kpis['spent']
            diff_pct = round((abs(diff) / prev_kpis['spent']) * 100, 1)
            if diff < 0:
                insights.append({
                    'title': "Spending decreased vs last month",
                    'text': f"You spent {curr}{abs(diff):,.0f} ({diff_pct}%) less than in {prev_m}.",
                    'type': 'good'
                })
            else:
                insights.append({
                    'title': "Spending increased vs last month",
                    'text': f"You spent {curr}{diff:,.0f} ({diff_pct}%) more than in {prev_m}.",
                    'type': 'warn'
                })

    return insights[:3]

# ============================================================
# GROUNDED ASK SMARTSPEND FINANCIAL ADVISOR
# ============================================================
def ask_financial_assistant(question, df, user_profile, month_name):
    q = question.lower().strip()
    curr = user_profile.get('preferred_currency', '₹')
    user_name = user_profile.get('name', 'User')
    username = user_profile.get('username', 'janaganika')
    
    kpis = calculate_kpis(df, month_name, user_profile)
    spent = kpis['spent']
    income = kpis['income']
    budget = kpis['budget']
    saved = kpis['saved']
    rem_budget = kpis['budget_remaining']
    budget_pct = kpis['budget_pct']
    
    month_df = get_month_data(df, month_name)
    cat_totals = get_category_breakdown(df, month_name).to_dict()
    
    goals = get_savings_goals(username)
    goals_summary = []
    total_goals_target = 0.0
    total_goals_saved = 0.0
    for g in goals:
        g_rem = max(0.0, g['target_amount'] - g['current_amount'])
        g_pct = round((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
        total_goals_target += g['target_amount']
        total_goals_saved += g['current_amount']
        goals_summary.append(f"- **{g['name']}**: {curr}{g['current_amount']:,.0f} of {curr}{g['target_amount']:,.0f} ({g_pct}%, {curr}{g_rem:,.0f} needed by {g['target_date']})")

    recurring = detect_recurring_expenses(df)
    total_recurring = sum(r['amount'] for r in recurring)

    # 1. Greetings & System Identity
    if any(q.startswith(w) for w in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'who are you', 'what can you do', 'help']):
        ans = (f"Hello {user_name}! I am your **SmartSpend AI Financial Advisor**.\n\n"
               f"Here is your real-time summary for **{month_name}**:\n"
               f"- **Income**: {curr}{income:,.0f}\n"
               f"- **Spent**: {curr}{spent:,.0f} ({round(budget_pct)}% of your {curr}{budget:,.0f} budget)\n"
               f"- **Budget Remaining**: {curr}{rem_budget:,.0f}\n"
               f"- **Net Savings**: {curr}{saved:,.0f}\n"
               f"- **Active Goals**: {len(goals)} goal(s) in progress\n\n"
               f"Ask me anything about your transactions, category spending, affordability checks, savings goals, or spending tips!")
        sug = f"You have {curr}{rem_budget:,.0f} remaining in your budget. Try asking 'Can I afford a {curr}3,000 purchase?' or 'Where did most of my money go?'"
        return {"answer": ans, "suggestion": sug}

    # 2. Budget queries
    if any(w in q for w in ['budget', 'remaining', 'how much left', 'limit', 'allowance', 'left']):
        if rem_budget >= 0:
            ans = (f"In **{month_name}**, your monthly spending budget is **{curr}{budget:,.0f}**.\n\n"
                   f"- **Amount Spent**: {curr}{spent:,.0f} ({round(budget_pct, 1)}%)\n"
                   f"- **Budget Remaining**: **{curr}{rem_budget:,.0f}**\n"
                   f"- **Status**: Within budget.")
            daily_pace = max(0.0, rem_budget / 12.0)
            sug = f"To finish {month_name} within budget, aim to pace flexible daily spending at roughly **{curr}{daily_pace:,.0f} per day**."
        else:
            ans = (f"In **{month_name}**, your spending has exceeded your planned budget of **{curr}{budget:,.0f}**.\n\n"
                   f"- **Total Spent**: {curr}{spent:,.0f} ({round(budget_pct, 1)}%)\n"
                   f"- **Over Budget By**: **{curr}{abs(rem_budget):,.0f}**")
            top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else "Expenses"
            sug = f"Your highest expense category is **{top_cat}** ({curr}{cat_totals.get(top_cat, 0):,.0f}). Pausing discretionary spending in {top_cat} will prevent further overruns."
        return {"answer": ans, "suggestion": sug}

    # 3. Affordability checks
    if 'can i afford' in q or 'can i buy' in q or 'can i spend' in q:
        import re
        nums = re.findall(r'\d+', q.replace(',', ''))
        check_amt = float(nums[0]) if nums else 2000.0
        
        if rem_budget >= check_amt:
            new_rem = rem_budget - check_amt
            ans = (f"**Yes, you can afford a {curr}{check_amt:,.0f} purchase.**\n\n"
                   f"- Current remaining budget: **{curr}{rem_budget:,.0f}**\n"
                   f"- Remaining after purchase: **{curr}{new_rem:,.0f}**\n"
                   f"- You will remain within your monthly budget.")
            sug = f"After this purchase, you will have {curr}{new_rem:,.0f} remaining for other discretionary expenses this month."
        else:
            deficit = check_amt - rem_budget
            ans = (f"**Caution**: Spending **{curr}{check_amt:,.0f}** will exceed your monthly budget.\n\n"
                   f"- Current remaining budget: **{curr}{rem_budget:,.0f}**\n"
                   f"- Budget shortfall: **{curr}{deficit:,.0f}**")
            sug = f"Consider postponing this purchase to next month, or shifting funds from another category."
        return {"answer": ans, "suggestion": sug}

    # 4. Savings queries
    if any(w in q for w in ['saving', 'save', 'saved', 'surplus', 'net balance']):
        rate = round((saved / income) * 100, 1) if income > 0 else 0
        ans = (f"Here is your savings analysis for **{month_name}**:\n\n"
               f"- **Monthly Income**: {curr}{income:,.0f}\n"
               f"- **Total Spent**: {curr}{spent:,.0f}\n"
               f"- **Net Savings**: **{curr}{saved:,.0f}**\n"
               f"- **Savings Rate**: **{rate}%**")
        if rate >= 20:
            sug = f"Your {rate}% savings rate meets the recommended 20% savings rule. You can safely allocate {curr}{min(saved, 10000):,.0f} toward your active savings goals."
        else:
            sug = f"To raise your savings rate toward the standard 20% target ({curr}{income * 0.2:,.0f}), explore the **Spending Scenarios** tab to model small reductions."
        return {"answer": ans, "suggestion": sug}

    # 5. Goals queries
    if any(w in q for w in ['goal', 'goals', 'target', 'saving for']):
        if goals:
            ans = (f"You currently have **{len(goals)} active savings goal(s)**:\n\n" +
                   "\n".join(goals_summary) +
                   f"\n\n**Total Saved Across Goals**: {curr}{total_goals_saved:,.0f} of {curr}{total_goals_target:,.0f}")
            sug = f"Contributing {curr}{min(saved, 5000):,.0f} from your current surplus will accelerate your milestone completion."
        else:
            ans = "You haven't set up any savings goals yet. Having a dedicated target helps you build wealth faster."
            sug = "Visit the **Savings Goals** page in the sidebar to create your first goal (e.g. Emergency Fund or Travel)!"
        return {"answer": ans, "suggestion": sug}

    # 6. Category breakdown
    if any(w in q for w in ['where', 'breakdown', 'split', 'distribution', 'categories', 'category']):
        if cat_totals:
            top_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
            lines = [f"Here is your spending breakdown for **{month_name}** ({curr}{spent:,.0f} total):"]
            for c, a in top_cats:
                pct = round((a / spent) * 100, 1) if spent > 0 else 0
                lines.append(f"- **{c}**: {curr}{a:,.0f} ({pct}%)")
            ans = "\n".join(lines)
            top_cat_name, top_cat_val = top_cats[0]
            sug = f"**{top_cat_name}** represents {round((top_cat_val/spent)*100)}% of your expenses. Reviewing transactions under {top_cat_name} is the fastest way to save."
        else:
            ans = f"You haven't recorded any expenses in **{month_name}** yet."
            sug = "Add transactions using the **Transactions** page to start tracking categories."
        return {"answer": ans, "suggestion": sug}

    # 7. Highest/Biggest expenses
    if any(w in q for w in ['biggest', 'highest', 'largest', 'top', 'expensive', 'most']):
        if not month_df.empty:
            expense_only = month_df[month_df['Transaction Type'] == 'Expense']
            top_txns = expense_only.sort_values('Amount', ascending=False).head(5)
            lines = [f"Your highest expenses in **{month_name}**:"]
            for _, r in top_txns.iterrows():
                d_str = r['Date'].strftime('%d %b') if hasattr(r['Date'], 'strftime') else str(r['Date'])
                desc = r['Description'] if pd.notna(r['Description']) and r['Description'] else r['Category']
                lines.append(f"- **{desc}** ({r['Category']}): {curr}{r['Amount']:,.0f} on {d_str}")
            ans = "\n".join(lines)
            max_r = top_txns.iloc[0]
            sug = f"Your single largest purchase was {curr}{max_r['Amount']:,.0f} on '{max_r['Description'] or max_r['Category']}'."
        else:
            ans = "No transactions found for this period."
            sug = "Log transactions to analyze your spending."
        return {"answer": ans, "suggestion": sug}

    # 8. Specific category inquiries
    known_cats = ['dining', 'shopping', 'transport', 'bills', 'rent', 'groceries', 'entertainment', 'health', 'travel', 'utilities']
    for cat in known_cats:
        if cat in q:
            match_cat = cat.capitalize()
            cat_amt = cat_totals.get(match_cat, 0.0)
            pct = round((cat_amt / spent) * 100, 1) if spent > 0 else 0
            
            lines = [f"In **{month_name}**, you spent **{curr}{cat_amt:,.0f}** on **{match_cat}** ({pct}% of total spending)."]
            cat_txns = month_df[month_df['Category'].str.lower() == cat]
            if not cat_txns.empty:
                lines.append("\nRecent items:")
                for _, r in cat_txns.head(4).iterrows():
                    d_str = r['Date'].strftime('%d %b') if hasattr(r['Date'], 'strftime') else ''
                    desc = r['Description'] if pd.notna(r['Description']) and r['Description'] else match_cat
                    lines.append(f"- {desc}: {curr}{r['Amount']:,.0f} ({d_str})")
            ans = "\n".join(lines)
            
            if cat_amt > budget * 0.25:
                sug = f"{match_cat} accounts for over 25% of your budget. A 15% reduction would save {curr}{cat_amt * 0.15:,.0f} per month ({curr}{cat_amt * 0.15 * 12:,.0f}/year)."
            else:
                sug = f"Your {match_cat} spending is within healthy boundaries."
            return {"answer": ans, "suggestion": sug}

    # 9. Specific merchant search
    if not month_df.empty:
        tokens = [t for t in q.split() if len(t) > 3 and t not in ['spend', 'spent', 'much', 'many', 'what', 'where', 'when']]
        matching_txns = month_df[month_df['Description'].astype(str).str.lower().apply(lambda d: any(tok in d for tok in tokens))]
        if not matching_txns.empty:
            m_sum = matching_txns['Amount'].sum()
            lines = [f"Found **{len(matching_txns)} transaction(s)** matching '{tokens[0]}' ({curr}{m_sum:,.0f} total):"]
            for _, r in matching_txns.head(5).iterrows():
                lines.append(f"- **{r['Description']}** ({r['Category']}): {curr}{r['Amount']:,.0f} on {r['Date'].strftime('%d %b')}")
            ans = "\n".join(lines)
            sug = "Every matching record is logged in your Transactions ledger."
            return {"answer": ans, "suggestion": sug}

    # 10. Month over month changes
    if any(w in q for w in ['increase', 'more', 'compare', 'last month', 'trend', 'rose', 'grew']):
        all_m = get_available_months(df)
        ci = all_m.index(month_name) if month_name in all_m else -1
        if ci != -1 and ci + 1 < len(all_m):
            prev_m = all_m[ci + 1]
            prev_kpis = calculate_kpis(df, prev_m, user_profile)
            diff = spent - prev_kpis['spent']
            prev_breakdown = get_category_breakdown(df, prev_m)
            diffs = [(c, cat_totals.get(c, 0) - prev_breakdown.get(c, 0)) for c in cat_totals if cat_totals.get(c, 0) - prev_breakdown.get(c, 0) > 0]
            diffs.sort(key=lambda x: x[1], reverse=True)
            
            if diff > 0:
                ans = f"In **{month_name}**, you spent **{curr}{diff:,.0f} more** than in {prev_m} ({curr}{spent:,.0f} vs {curr}{prev_kpis['spent']:,.0f})."
                if diffs:
                    ans += f"\n\n**Categories with highest growth**:\n" + "\n".join([f"- **{c}**: +{curr}{d:,.0f}" for c, d in diffs[:3]])
                sug = f"The largest rise came from {diffs[0][0] if diffs else 'lifestyle expenses'}. Monitor this category closely over the next two weeks."
            else:
                ans = f"Great progress! In **{month_name}**, you spent **{curr}{abs(diff):,.0f} less** than in {prev_m} ({curr}{spent:,.0f} vs {curr}{prev_kpis['spent']:,.0f})."
                sug = "Your spending discipline is increasing your monthly savings surplus."
            return {"answer": ans, "suggestion": sug}

    # 11. Recurring expenses
    if any(w in q for w in ['recurring', 'subscription', 'bills', 'fixed', 'regular']):
        if recurring:
            lines = [f"Detected **{len(recurring)} regular monthly payment(s)** (~{curr}{total_recurring:,.0f}/month total):"]
            for r in recurring[:5]:
                lines.append(f"- **{r['description']}** ({r['category']}): ~{curr}{r['amount']:,.0f}/month (~day {r['typical_day']})")
            ans = "\n".join(lines)
            sug = f"Fixed commitments account for {round((total_recurring/budget)*100)}% of your monthly budget, leaving {curr}{budget - total_recurring:,.0f} for variable expenses."
        else:
            ans = "No recurring payments detected yet in your history."
            sug = "As you log transactions across consecutive months, recurring payments will be recognized automatically."
        return {"answer": ans, "suggestion": sug}

    # 12. General Financial Advice (50/30/20 rule, budgeting tips)
    if any(w in q for w in ['how to save', 'advice', 'tips', '50/30/20', 'rule', 'plan', 'budget better']):
        needs = income * 0.50
        wants = income * 0.30
        savings_target = income * 0.20
        ans = (f"Here is your personalized **50/30/20 Budget Framework** based on your **{curr}{income:,.0f}** income:\n\n"
               f"- **Needs (50%)**: {curr}{needs:,.0f} (Rent, groceries, utilities, debt)\n"
               f"- **Wants (30%)**: {curr}{wants:,.0f} (Dining, shopping, entertainment)\n"
               f"- **Savings (20%)**: {curr}{savings_target:,.0f} (Emergency fund & financial goals)\n\n"
               f"Your current monthly budget is set to **{curr}{budget:,.0f}**.")
        sug = f"Automate transferring {curr}{savings_target:,.0f} into a savings fund on the day your income arrives."
        return {"answer": ans, "suggestion": sug}

    # 13. Emergency Fund Queries
    if any(w in q for w in ['emergency', 'safety net', 'contingency', 'rainy day']):
        rec_min = spent * 3
        rec_max = spent * 6
        ans = (f"**Emergency Reserve Assessment** based on your **{curr}{spent:,.0f}/month** spending:\n\n"
               f"- **Recommended 3-Month Buffer**: {curr}{rec_min:,.0f}\n"
               f"- **Recommended 6-Month Buffer**: {curr}{rec_max:,.0f}\n"
               f"- **Current Monthly Net Surplus**: {curr}{saved:,.0f}/month\n\n"
               f"At your current savings pace of {curr}{saved:,.0f}/month, you can fully establish a 3-month safety fund in **{max(1, round(rec_min / max(saved, 1)))} months**.")
        sug = "Keep your emergency reserve in a high-yield liquid savings account or short-term fixed deposit for instant accessibility."
        return {"answer": ans, "suggestion": sug}

    # 14. Investment & Wealth Generation Queries
    if any(w in q for w in ['invest', 'investing', 'mutual fund', 'sip', 'stock', 'equity', 'wealth', 'fd', 'fixed deposit']):
        investable = max(0.0, saved * 0.70)
        ans = (f"**Investment Potential for {month_name}**:\n\n"
               f"- **Total Monthly Surplus**: {curr}{saved:,.0f}\n"
               f"- **Suggested Monthly SIP / Investment**: **{curr}{investable:,.0f}** (70% of surplus)\n"
               f"- **Liquid Buffer Retained**: {curr}{saved - investable:,.0f} (30% for short-term goals)\n\n"
               f"Deploying {curr}{investable:,.0f}/month at an assumed 12% annual return would accumulate to approximately **{curr}{investable * 12 * 1.06:,.0f} in 1 year** and **{curr}{investable * 82.5:,.0f} in 5 years**.")
        sug = "Ensure you have a 3-month emergency fund in place first, then automate monthly index fund or mutual fund SIPs."
        return {"answer": ans, "suggestion": sug}

    # 15. Debt & Credit Card Queries
    if any(w in q for w in ['debt', 'credit card', 'loan', 'emi', 'interest']):
        ans = (f"**Debt & Liability Optimization**:\n\n"
               f"- **Credit Utilization Rule**: Keep monthly credit card usage strictly below **30% of your total credit limit**.\n"
               f"- **Repayment Priority**: Pay high-interest credit card dues (36-42% APR) immediately before allocating money to investments.\n"
               f"- **Monthly Surplus Available**: You have **{curr}{saved:,.0f}** in net surplus this month to accelerate debt clearance.")
        sug = "Use the Avalanche Method: pay minimums on all obligations and throw all extra monthly surplus at the debt with the highest interest rate."
        return {"answer": ans, "suggestion": sug}

    # 16. Default synthesis
    top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else 'Expenses'
    top_amt = cat_totals.get(top_cat, 0.0)
    ans = (f"Here is your financial status for **{month_name}**:\n\n"
           f"- **Monthly Income**: {curr}{income:,.0f}\n"
           f"- **Total Spent**: {curr}{spent:,.0f} ({round(budget_pct)}% of {curr}{budget:,.0f} budget)\n"
           f"- **Remaining Budget**: {curr}{rem_budget:,.0f}\n"
           f"- **Net Savings**: {curr}{saved:,.0f}\n"
           f"- **Top Category**: **{top_cat}** ({curr}{top_amt:,.0f})")
    if rem_budget >= 0:
        sug = f"You are on track to stay within your budget. Try asking 'What are my biggest expenses?' or 'Can I afford a {curr}3,000 purchase?'."
    else:
        sug = f"You are {curr}{abs(rem_budget):,.0f} over budget. Review your top category ({top_cat}) to trim non-essential spending."
    return {"answer": ans, "suggestion": sug}
