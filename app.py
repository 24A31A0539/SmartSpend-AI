# app.py
"""
SmartSpend AI - Personal Financial Intelligence Platform
Full-stack implementation featuring:
- Sage Green & Warm White Design System
- Multi-User Isolated Storage & Secure Password Hashing
- Structured Navigation: YOUR MONEY, YOUR PLANS, YOUR INSIGHTS, YOUR ACCOUNT
- Financial Calculations supporting Expenses, Incomes, Refunds, and Transfers
- Full Transaction Management (CRUD, Search, Filter, Sort, CSV Import/Export)
- Spending Intelligence with Category Drill-Down
- Savings Goals with Contributions & Milestone Progress
- Spending Scenarios (What-If modeling against actual baselines)
- Spending Forecast (Historical Trend & Velocity with honest uncertainty)
- Actionable Alerts with Persistent Dismissal
- Grounded Ask SmartSpend AI Financial Assistant
- Profile & Settings Management
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import io
import textwrap

import data_service as ds
from styles import CUSTOM_CSS

# ============================================================
# HELPER RENDERING FUNCTIONS (NO INDENTED CODE BLOCK ARTIFACTS)
# ============================================================
def render_html(content: str):
    """Safely renders HTML without Markdown converting indented lines or blank lines to pre/code blocks."""
    cleaned = chr(10).join(line.strip() for line in content.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

def render_sidebar_html(content: str):
    """Safely renders HTML in sidebar without Markdown code block artifacts."""
    cleaned = chr(10).join(line.strip() for line in content.splitlines() if line.strip())
    st.sidebar.markdown(cleaned, unsafe_allow_html=True)
# ============================================================
# PAGE CONFIGURATION & STYLING
# ============================================================
st.set_page_config(
    page_title="SmartSpend AI — Personal Financial Intelligence",
        layout="wide",
    initial_sidebar_state="expanded"
)
render_html(CUSTOM_CSS)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
state_defaults = {
    'authenticated': False,
    'user_profile': None,
    'auth_view': 'landing',      # 'landing', 'signup', 'login', 'onboarding'
    'active_page': 'Overview',   # Default landing page
    'selected_month': datetime.now().strftime('%B %Y'),
    'chat_history': [],
    'editing_txn_id': None,
    'editing_goal_id': None,
    'confirm_delete_txn_id': None,
    'confirm_delete_goal_id': None,
    'scenario_adjustments': {},
    'active_ai_query': '',
    'active_kpi_tab': 'spent',
}
for k, v in state_defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def nav(page_name):
    st.session_state.active_page = page_name
    st.rerun()

def get_time_greeting(name):
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return f"Good morning, {name}"
    elif 12 <= hour < 17:
        return f"Good afternoon, {name}"
    return f"Good evening, {name}"

# ============================================================
# 1. LANDING PAGE
# ============================================================
def render_landing():
    col_logo, col_actions = st.columns([5, 3])
    with col_logo:
        render_html("<h3 style='margin-top:0.2rem; color:#0F172A; font-weight:800; letter-spacing:-0.03em;'>SmartSpend AI</h3>")
    with col_actions:
        b_in, b_start = st.columns(2)
        with b_in:
            if st.button("Sign In", use_container_width=True):
                st.session_state.auth_view = 'login'
                st.rerun()
        with b_start:
            if st.button("Get Started", type="primary", use_container_width=True):
                st.session_state.auth_view = 'signup'
                st.rerun()

    render_html("""
    <div class="landing-container">
        <div class="landing-brand">SmartSpend AI</div>
        <div class="landing-headline">Understand your spending.<br>Plan your money better.</div>
        <div class="landing-sub">
            Track expenses and income, stay within your monthly budget, model future scenarios, and achieve your savings goals with complete clarity.
        </div>
    </div>
    """)

    c_left, c_center, c_right = st.columns([1.5, 1.3, 1.5])
    with c_center:
        if st.button("Get Started — Create Account", type="primary", use_container_width=True, key="hero_start_btn"):
            st.session_state.auth_view = 'signup'
            st.rerun()
        render_html("<div style='text-align:center; margin-top:0.6rem;'><span style='color:#5C6E64; font-size:0.88rem;'>Already using SmartSpend?</span></div>")
        if st.button("Sign In to Account", use_container_width=True, key="hero_signin_btn"):
            st.session_state.auth_view = 'login'
            st.rerun()

# ============================================================
# 2. SIGN UP EXPERIENCE
# ============================================================
def render_signup():
    c_back, _ = st.columns([2, 6])
    with c_back:
        if st.button("← Back to Home", key="back_home_signup"):
            st.session_state.auth_view = 'landing'
            st.rerun()

    render_html("""
    <div style="max-width: 540px; margin: 1rem auto 0; text-align: center;">
        <h2 style="margin-bottom: 0.25rem;">Create your account</h2>
        <p style="color: #5C6E64; font-size: 0.95rem;">Set up your private personal finance profile.</p>
    </div>
    """)

    _, col_form, _ = st.columns([1, 2.2, 1])
    with col_form:
        with st.form("signup_form"):
            render_html("#### Personal Details")
            f_name = st.text_input("Full Name", placeholder="Enter your full name")
            f_username = st.text_input("Username", placeholder="Choose a username")
            f_email = st.text_input("Email", placeholder="Enter your email address")
            f_password = st.text_input("Password", type="password", placeholder="Create a secure password")

            render_html("<div style='height:0.6rem;'></div>")
            render_html("#### Financial Baseline")
            st.caption("We use these values to establish your monthly budget and savings baseline.")
            
            f_curr = st.selectbox("Preferred Currency", ["₹ (INR)", "$ (USD)", "€ (EUR)", "£ (GBP)"], index=0)
            curr_symbol = f_curr.split()[0]
            
            f_income = st.number_input(
                f"Monthly Income ({curr_symbol})",
                min_value=0.0,
                value=75000.0,
                step=5000.0,
                help="Your typical take-home income per month"
            )
            f_budget = st.number_input(
                f"Monthly Spending Budget ({curr_symbol})",
                min_value=0.0,
                value=50000.0,
                step=5000.0,
                help="Your planned monthly spending limit"
            )

            render_html("<div style='height:0.8rem;'></div>")
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if submit:
                if not f_name.strip() or not f_username.strip() or not f_email.strip() or not f_password:
                    st.error("Please fill in all personal details.")
                elif f_income <= 0:
                    st.error("Monthly income must be greater than 0.")
                elif f_budget <= 0:
                    st.error("Monthly budget must be greater than 0.")
                else:
                    profile, err = ds.signup_user(
                        username=f_username,
                        name=f_name,
                        email=f_email,
                        password=f_password,
                        monthly_income=f_income,
                        monthly_budget=f_budget,
                        preferred_currency=curr_symbol
                    )
                    if profile:
                        st.session_state.authenticated = True
                        st.session_state.user_profile = profile
                        st.session_state.auth_view = 'onboarding'
                        st.rerun()
                    else:
                        st.error(err)

        render_html("<div style='text-align:center; margin-top:1rem;'><span style='color:#5C6E64;'>Already have an account?</span></div>")
        if st.button("Sign In Instead", use_container_width=True, key="su_to_login_btn"):
            st.session_state.auth_view = 'login'
            st.rerun()

# ============================================================
# 3. SIGN IN EXPERIENCE
# ============================================================
def render_login():
    c_back, _ = st.columns([2, 6])
    with c_back:
        if st.button("← Back to Home", key="back_home_login_btn"):
            st.session_state.auth_view = 'landing'
            st.rerun()

    render_html("""
    <div style="max-width: 480px; margin: 1.5rem auto 0; text-align: center;">
        <h2 style="margin-bottom: 0.25rem;">Sign in to SmartSpend AI</h2>
        <p style="color: #5C6E64; font-size: 0.95rem;">Access your personal financial intelligence.</p>
    </div>
    """)

    _, col_form, _ = st.columns([1, 1.8, 1])
    with col_form:
        with st.form("login_form"):
            l_un = st.text_input("Username", placeholder="Enter your username")
            l_pw = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submit:
                if not l_un.strip() or not l_pw:
                    st.error("Please enter both username and password.")
                else:
                    profile, err = ds.login_user(l_un.strip(), l_pw)
                    if profile:
                        st.session_state.authenticated = True
                        st.session_state.user_profile = profile
                        if not profile.get('onboarding_complete', True):
                            st.session_state.auth_view = 'onboarding'
                        else:
                            st.session_state.auth_view = 'landing'
                        st.rerun()
                    else:
                        st.error(err)

        render_html("<div style='text-align:center; margin-top:1rem;'><span style='color:#5C6E64;'>New to SmartSpend AI?</span></div>")
        if st.button("Create an Account", use_container_width=True, key="login_to_su_btn"):
            st.session_state.auth_view = 'signup'
            st.rerun()

# ============================================================
# 4. ONBOARDING
# ============================================================
def render_onboarding():
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')

    render_html(f"""
    <div style="max-width: 600px; margin: 1.5rem auto 0; text-align: center;">
        <h2>Welcome to SmartSpend AI, {user.get('name', 'User')}!</h2>
        <p style="color: #5C6E64; font-size: 1rem; margin-top: 0.5rem; line-height: 1.5;">
            Let's configure your financial view. These settings establish your budget thresholds and savings pace.
        </p>
    </div>
    """)

    _, col_card, _ = st.columns([1, 2.2, 1])
    with col_card:
        with st.form("onboarding_form"):
            render_html("#### Confirm Financial Setup")
            o_income = st.number_input(
                f"Monthly Income ({curr})",
                min_value=1000.0,
                value=float(user.get('monthly_income', 75000.0)),
                step=5000.0
            )
            o_budget = st.number_input(
                f"Monthly Budget ({curr})",
                min_value=1000.0,
                value=float(user.get('monthly_budget', 50000.0)),
                step=5000.0
            )

            render_html("<hr style='margin:1.25rem 0; border:none; border-top:1px solid #E2E7DF;'>")
            render_html("#### Set an Initial Savings Goal (Optional)")
            st.caption("Having a dedicated target increases savings discipline.")

            o_goal_name = st.text_input("Goal Name", placeholder="What are you saving for? (e.g. Emergency Fund, Travel)")
            o_goal_target = st.number_input(f"Target Amount ({curr})", min_value=0.0, value=50000.0, step=5000.0)
            o_goal_date = st.text_input("Target Date", value="December 2027")

            render_html("<div style='height:0.8rem;'></div>")
            complete = st.form_submit_button("Continue to Overview →", type="primary", use_container_width=True)

            if complete:
                updated = ds.update_user_profile(user['username'], {
                    'monthly_income': o_income,
                    'monthly_budget': o_budget,
                    'onboarding_complete': True
                })
                st.session_state.user_profile = updated

                if o_goal_name.strip() and o_goal_target > 0:
                    ds.add_savings_goal(
                        username=user['username'],
                        name=o_goal_name.strip(),
                        target_amount=o_goal_target,
                        current_amount=0.0,
                        target_date=o_goal_date.strip() if o_goal_date.strip() else "December 2027",
                        category="Savings"
                    )

                st.session_state.auth_view = 'landing'
                st.session_state.active_page = 'Overview'
                st.rerun()

# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================
def render_sidebar(df):
    user = st.session_state.user_profile
    render_sidebar_html("""
    <div style="padding: 0.2rem 0 0.8rem 0;">
        <div style="font-size: 1.45rem; font-weight: 800; color: #1E3A8A; letter-spacing: -0.035em; line-height: 1.15;">SmartSpend AI</div>
        <div style="font-size: 0.78rem; font-weight: 700; color: #2563EB; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 3px;">Financial Intelligence</div>
    </div>
    """)
    st.sidebar.markdown("---")

    # Viewing Period Selector
    avail_months = ds.get_available_months(df)
    if st.session_state.selected_month not in avail_months and avail_months:
        st.session_state.selected_month = avail_months[0]

    render_sidebar_html("<p style='font-size:0.75rem; font-weight:700; color:#6A7C72; letter-spacing:0.05em; margin-bottom:2px;'>VIEWING PERIOD</p>")
    st.session_state.selected_month = st.sidebar.selectbox(
        "Period",
        options=avail_months,
        index=avail_months.index(st.session_state.selected_month) if st.session_state.selected_month in avail_months else 0,
        label_visibility="collapsed"
    )
    render_sidebar_html("---")

    # Mandatory exact user-facing sidebar navigation structure
    nav_structure = [
        ("YOUR MONEY", [
            ("Overview", "📊"),
            ("Transactions", "💳"),
            ("Spending", "📈")
        ]),
        ("YOUR PLANS", [
            ("Savings Goals", "🎯"),
            ("Spending Scenarios", "💡")
        ]),
        ("YOUR INSIGHTS", [
            ("Spending Forecast", "🔮"),
            ("Alerts", "🔔"),
            ("Ask SmartSpend", "💬")
        ]),
        ("YOUR ACCOUNT", [
            ("Profile", "👤"),
            ("Settings", "⚙️")
        ])
    ]

    # Calculate active un-dismissed alert count
    alerts_list = ds.get_user_alerts(df, st.session_state.selected_month, user, user['username'])
    alert_count = len(alerts_list)

    for section_title, page_items in nav_structure:
        render_sidebar_html(f"<p style='font-size:0.72rem; font-weight:700; color:#85998D; letter-spacing:0.06em; margin-top:0.6rem; margin-bottom:0.2rem;'>{section_title}</p>")
        for page_name, icon in page_items:
            active = (st.session_state.active_page == page_name)
            label = f"{icon} {page_name}"
            if page_name == "Alerts" and alert_count > 0:
                label = f"{icon} Alerts ({alert_count})"

            b_type = "primary" if active else "secondary"
            if st.sidebar.button(label, key=f"nav_btn_{page_name}", type=b_type, use_container_width=True):
                st.session_state.active_page = page_name
                st.rerun()

    # User footer & logout
    render_sidebar_html("---")
    if st.sidebar.button("Log out", use_container_width=True, key="sidebar_logout_btn"):
        st.session_state.authenticated = False
        st.session_state.user_profile = None
        st.session_state.auth_view = 'landing'
        st.session_state.active_page = 'Overview'
        st.rerun()

# ============================================================
# 6. OVERVIEW — THE FINANCIAL HOMEPAGE
# ============================================================
def render_overview(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    top_c1, top_c2 = st.columns([4, 1.2])
    with top_c1:
        render_html(f"<h1>{get_time_greeting(user.get('name', 'User'))}</h1>")
        render_html(f"<div class='page-subtitle'>Financial summary and intelligence for <strong>{sm}</strong>.</div>")
    with top_c2:
        if st.button("➕ Add Transaction", type="primary", use_container_width=True, key="overview_add_txn_btn"):
            st.session_state.active_page = "Transactions"
            st.session_state.show_add_modal = True
            st.rerun()

    kpis = ds.calculate_kpis(df, sm, user)
    active_kpi = st.session_state.get('active_kpi_tab', 'spent')

    # 4 Premium Interactive KPI Cards with Click Selection
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        is_active = (active_kpi == 'income')
        active_cls = " active-kpi" if is_active else ""
        render_html(f"""
        <div class="metric-card income{active_cls}">
            <div class="metric-label">Income</div>
            <div class="metric-value">{curr}{kpis['income']:,.0f}</div>
            <div class="metric-sub">Monthly Inflow</div>
        </div>
        """)
        if st.button("💵 Income Details", key="kpi_btn_income", use_container_width=True):
            st.session_state.active_kpi_tab = 'income'
            st.rerun()

    with c2:
        is_active = (active_kpi == 'spent')
        active_cls = " active-kpi" if is_active else ""
        render_html(f"""
        <div class="metric-card spent{active_cls}">
            <div class="metric-label">Spent</div>
            <div class="metric-value">{curr}{kpis['spent']:,.0f}</div>
            <div class="metric-sub">Net Expenses in {sm}</div>
        </div>
        """)
        if st.button("💳 Spent Details", key="kpi_btn_spent", use_container_width=True):
            st.session_state.active_kpi_tab = 'spent'
            st.rerun()

    with c3:
        is_active = (active_kpi == 'saved')
        active_cls = " active-kpi" if is_active else ""
        save_color = "#059669" if kpis['saved'] >= 0 else "#DC2626"
        render_html(f"""
        <div class="metric-card saved{active_cls}">
            <div class="metric-label">Saved / Net Balance</div>
            <div class="metric-value" style="color:{save_color};">{curr}{kpis['saved']:,.0f}</div>
            <div class="metric-sub">Net Savings Surplus</div>
        </div>
        """)
        if st.button("📈 Savings Details", key="kpi_btn_saved", use_container_width=True):
            st.session_state.active_kpi_tab = 'saved'
            st.rerun()

    with c4:
        is_active = (active_kpi == 'budget')
        active_cls = " active-kpi" if is_active else ""
        rem_color = "#059669" if kpis['budget_remaining'] >= 0 else "#DC2626"
        render_html(f"""
        <div class="metric-card budget{active_cls}">
            <div class="metric-label">Budget Remaining</div>
            <div class="metric-value" style="color:{rem_color};">{curr}{kpis['budget_remaining']:,.0f}</div>
            <div class="metric-sub">Limit: {curr}{kpis['budget']:,.0f}</div>
        </div>
        """)
        if st.button("🎯 Budget Details", key="kpi_btn_budget", use_container_width=True):
            st.session_state.active_kpi_tab = 'budget'
            st.rerun()

    render_html("<div style='height: 0.5rem;'></div>")

    # Structured Interactive Detail Drawer for Clicked KPI
    month_df = ds.get_month_data(df, sm)
    expense_txns = month_df[month_df['Transaction Type'] == 'Expense'] if not month_df.empty else pd.DataFrame()
    income_txns = month_df[month_df['Transaction Type'] == 'Income'] if not month_df.empty else pd.DataFrame()

    if active_kpi == 'spent':
        top_cat_data = ds.get_category_breakdown(df, sm)
        top_c = top_cat_data.index[0] if not top_cat_data.empty else "N/A"
        top_c_amt = top_cat_data.iloc[0] if not top_cat_data.empty else 0.0
        largest_txn = expense_txns.sort_values(by='Amount', ascending=False).iloc[0] if not expense_txns.empty else None
        largest_desc = f"{largest_txn['Description'] or largest_txn['Category']} ({curr}{largest_txn['Amount']:,.0f})" if largest_txn is not None else "None recorded"
        daily_pace = kpis['spent'] / 30.0

        render_html(f"""
        <div class="detail-drawer">
            <div class="detail-drawer-header">
                <div>
                    <span class="detail-drawer-title">💳 Spending Intelligence & Outflow Breakdown — {sm}</span>
                </div>
                <span class="badge badge-blue">Active Deep-Dive: Spent</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 0.8rem;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Top Category</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#1E3A8A; margin-top:2px;">{top_c}</div>
                    <div style="font-size:0.8rem; color:#64748B;">{curr}{top_c_amt:,.0f} ({round((top_c_amt/kpis['spent'])*100) if kpis['spent']>0 else 0}% of expenses)</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Daily Burn Pace</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#2563EB; margin-top:2px;">{curr}{daily_pace:,.0f} / day</div>
                    <div style="font-size:0.8rem; color:#64748B;">Average run-rate over 30 days</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Largest Single Expense</div>
                    <div style="font-size:1.05rem; font-weight:800; color:#0F172A; margin-top:2px;">{largest_desc}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Highest logged line-item</div>
                </div>
            </div>
        </div>
        """)
    elif active_kpi == 'income':
        savings_rate = round((kpis['saved'] / kpis['income'] * 100), 1) if kpis['income'] > 0 else 0
        render_html(f"""
        <div class="detail-drawer">
            <div class="detail-drawer-header">
                <div>
                    <span class="detail-drawer-title">💵 Inflow & Income Structure — {sm}</span>
                </div>
                <span class="badge badge-blue">Active Deep-Dive: Income</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 0.8rem;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Monthly Inflow</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0284C7; margin-top:2px;">{curr}{kpis['income']:,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Total deposits in {sm}</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Savings Retention</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#059669; margin-top:2px;">{savings_rate}% retained</div>
                    <div style="font-size:0.8rem; color:#64748B;">Surplus: {curr}{kpis['saved']:,.0f}</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Baseline Target</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-top:2px;">{curr}{user.get('monthly_income', 75000.0):,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Configured profile baseline</div>
                </div>
            </div>
        </div>
        """)
    elif active_kpi == 'saved':
        goals_data = ds.get_savings_goals(user['username'])
        total_goal_saved = sum(g['current_amount'] for g in goals_data)
        render_html(f"""
        <div class="detail-drawer">
            <div class="detail-drawer-header">
                <div>
                    <span class="detail-drawer-title">📈 Net Savings & Wealth Generation — {sm}</span>
                </div>
                <span class="badge badge-blue">Active Deep-Dive: Saved</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 0.8rem;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Net Surplus</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#059669; margin-top:2px;">{curr}{kpis['saved']:,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Inflow minus total expenses</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Active Goals Reserve</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#1E3A8A; margin-top:2px;">{curr}{total_goal_saved:,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Across {len(goals_data)} active goals</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Recommended SIP</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#2563EB; margin-top:2px;">{curr}{max(0, kpis['saved']*0.5):,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Suggested wealth investment</div>
                </div>
            </div>
        </div>
        """)
    elif active_kpi == 'budget':
        safe_daily = max(0.0, kpis['budget_remaining']) / 30.0
        render_html(f"""
        <div class="detail-drawer">
            <div class="detail-drawer-header">
                <div>
                    <span class="detail-drawer-title">🎯 Monthly Budget Runway & Limits — {sm}</span>
                </div>
                <span class="badge badge-blue">Active Deep-Dive: Budget</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 0.8rem;">
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Spending Limit</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#10B981; margin-top:2px;">{curr}{kpis['budget']:,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Configured monthly threshold</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Remaining Buffer</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#059669; margin-top:2px;">{curr}{kpis['budget_remaining']:,.0f}</div>
                    <div style="font-size:0.8rem; color:#64748B;">{round(100 - kpis['budget_pct'])}% buffer remaining</div>
                </div>
                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:0.85rem 1rem;">
                    <div style="font-size:0.75rem; font-weight:700; color:#64748B; text-transform:uppercase;">Safe Daily Spend</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#2563EB; margin-top:2px;">{curr}{safe_daily:,.0f} / day</div>
                    <div style="font-size:0.8rem; color:#64748B;">Safe allowance to stay on track</div>
                </div>
            </div>
        </div>
        """)

    # Monthly Budget Progress
    badge_cls = f"badge-{kpis['status_type']}"
    render_html(f"""
    <div class="budget-section">
        <div class="budget-header">
            <div>
                <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">Monthly Spending Budget</span>
                <span style="margin-left: 0.85rem; color: #64748B; font-size: 0.9rem;">
                    {curr}{kpis['spent']:,.0f} of {curr}{kpis['budget']:,.0f} used
                </span>
            </div>
            <div>
                <span class="badge {badge_cls}">{kpis['status']}</span>
            </div>
        </div>
    </div>
    """)
    st.progress(float(min(100.0, kpis['budget_pct']) / 100.0))
    st.caption(f"{round(kpis['budget_pct'])}% used • {curr}{kpis['budget_remaining']:,.0f} remaining")

    render_html("<div style='height: 1.25rem;'></div>")

    if month_df.empty:
        render_html(f"""
        <div class="empty-state-box">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div class="empty-state-title">Your money dashboard is ready</div>
            <div class="empty-state-desc">Add your first transaction for {sm} to start tracking categories and spending velocity.</div>
        </div>
        """)
        _, c_btn1, c_btn2, _ = st.columns([1.5, 1.2, 1.2, 1.5])
        with c_btn1:
            if st.button("➕ Add Transaction", type="primary", use_container_width=True, key="empty_add_txn_btn"):
                st.session_state.active_page = "Transactions"
                st.session_state.show_add_modal = True
                st.rerun()
        with c_btn2:
            if st.button("📥 Import CSV", use_container_width=True, key="empty_import_btn"):
                st.session_state.active_page = "Transactions"
                st.rerun()
    else:
        # Category Breakdown & Insights
        col_cat, col_insights = st.columns([1.2, 1])
        with col_cat:
            render_html("### Where your money went")
            cat_totals = ds.get_category_breakdown(df, sm)
            if not cat_totals.empty:
                blue_palette = ['#1D4ED8', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
                for i, (c_name, c_amt) in enumerate(cat_totals.head(5).items()):
                    pct = (c_amt / kpis['spent'] * 100) if kpis['spent'] > 0 else 0
                    color = blue_palette[i % len(blue_palette)]
                    render_html(f"""
                    <div class="cat-row">
                        <div class="cat-meta">
                            <span class="cat-name">{c_name}</span>
                            <span class="cat-amount">{curr}{c_amt:,.0f} ({round(pct)}%)</span>
                        </div>
                        <div class="cat-bar-bg">
                            <div class="cat-bar-fill" style="width: {pct}%; background: {color};"></div>
                        </div>
                    </div>
                    """)
                if st.button("View Full Spending Breakdown →", key="dash_view_spend_btn"):
                    nav("Spending")
            else:
                st.info("No expense transactions recorded.")

        with col_insights:
            render_html("### Things to know")
            insights = ds.get_insights(df, sm, user)
            for item in insights:
                css_t = item.get('type', 'info')
                render_html(f"""
                <div class="insight-item {css_t}">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #1E3A8A; margin-bottom: 2px;">{item['title']}</div>
                    <div style="font-size: 0.86rem; color: #475569;">{item['text']}</div>
                </div>
                """)

            active_alerts = ds.get_user_alerts(df, sm, user, user['username'])
            if active_alerts:
                top_alert = active_alerts[0]
                render_html("<div style='height:0.3rem;'></div>")
                render_html("### Needs your attention")
                render_html(f"""
                <div class="alert-banner {'danger' if top_alert['severity']=='danger' else ''}">
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.92rem;">{top_alert['title']}</div>
                    <div style="font-size: 0.86rem; color: #334155; margin: 3px 0;">{top_alert['message']}</div>
                </div>
                """)
                if st.button(f"{top_alert['action_label']} →", key="dash_alert_action_btn"):
                    nav(top_alert['action_target'])

    render_html("<div style='height: 1.5rem;'></div>")

    # Recent Transactions & Savings Goal Progress
    col_rec, col_g = st.columns([1.3, 1])
    with col_rec:
        render_html("### Recent transactions")
        recent_txns = month_df.head(5) if not month_df.empty else df.head(5)
        if not recent_txns.empty:
            for _, r in recent_txns.iterrows():
                d_str = r['Date'].strftime('%d %b') if hasattr(r['Date'], 'strftime') else str(r['Date'])
                desc = r['Description'] if pd.notna(r['Description']) and r['Description'] else r['Category']
                ttype = r.get('Transaction Type', 'Expense')
                t_badge_cls = 'badge-success' if ttype == 'Income' else ('badge-warning' if ttype == 'Refund' else 'badge-neutral')
                render_html(f"""
                <div class="txn-item">
                    <div>
                        <span style="font-weight: 600; color: #0F172A;">{desc}</span>
                        <span class="badge {t_badge_cls}" style="margin-left: 6px;">{ttype}</span><br>
                        <span style="font-size: 0.78rem; color: #64748B;">{r['Category']} • {d_str}</span>
                    </div>
                    <div style="font-weight: 700; color: #0F172A;">{curr}{r['Amount']:,.0f}</div>
                </div>
                """)
            if st.button("View All Transactions →", key="dash_all_txns_btn"):
                nav("Transactions")
        else:
            render_html("""
            <div class="surface-card" style="text-align: center; color: #64748B; padding: 1.5rem;">
                No transactions recorded yet.
            </div>
            """)

    with col_g:
        render_html("### Savings goal progress")
        goals = ds.get_savings_goals(user['username'])
        if goals:
            g = goals[0]
            pct = round((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
            rem = max(0.0, g['target_amount'] - g['current_amount'])
            render_html(f"""
            <div class="surface-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">{g['name']}</span>
                    <span class="badge badge-neutral">{g.get('category', 'Savings')}</span>
                </div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #059669; margin: 4px 0;">
                    {curr}{g['current_amount']:,.0f} <span style="font-size: 0.85rem; font-weight: normal; color: #64748B;">/ {curr}{g['target_amount']:,.0f}</span>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 0.6rem;">
                    {pct}% complete • {curr}{rem:,.0f} remaining • Target: {g['target_date']}
                </div>
            </div>
            """)
            st.progress(float(min(100, pct) / 100.0))
            if st.button("Manage Goals →", key="dash_manage_goals_btn"):
                nav("Savings Goals")
        else:
            render_html("""
            <div class="surface-card">
                <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">Create your first savings goal</div>
                <div style="font-size: 0.85rem; color: #64748B; margin-bottom: 0.8rem;">Define a target amount and date to track your savings progress.</div>
            </div>
            """)
            if st.button("➕ Create a Goal", key="dash_create_goal_btn"):
                nav("Savings Goals")


# ============================================================
# 7. TRANSACTIONS MANAGEMENT
# ============================================================
def render_transactions(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    render_html("<h1>Transactions</h1>")
    render_html("<div class='page-subtitle'>Add, search, filter, edit, import, and export your financial records.</div>")

    # Top Actions Bar
    col_a1, col_a2, col_a3, _ = st.columns([1.3, 1.3, 1.3, 3])
    with col_a1:
        if st.button("➕ Add Transaction", type="primary", use_container_width=True, key="tx_open_add_btn"):
            st.session_state.show_add_modal = not st.session_state.get('show_add_modal', False)
            st.session_state.editing_txn_id = None
    with col_a2:
        if st.button("📥 Import CSV", use_container_width=True, key="tx_open_import_btn"):
            st.session_state.show_import_panel = not st.session_state.get('show_import_panel', False)
    with col_a3:
        if not df.empty:
            exp_csv = df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
            exp_csv['Date'] = exp_csv['Date'].dt.strftime('%Y-%m-%d')
            st.download_button(
                "📤 Export CSV",
                exp_csv.to_csv(index=False).encode('utf-8'),
                "smartspend_transactions.csv",
                "text/csv",
                use_container_width=True
            )

    # Add / Edit Transaction Form
    if st.session_state.get('show_add_modal', False) or st.session_state.get('editing_txn_id'):
        is_editing = bool(st.session_state.get('editing_txn_id'))
        edit_row = None
        if is_editing:
            found = df[df['id'].astype(str) == str(st.session_state.editing_txn_id)]
            if not found.empty:
                edit_row = found.iloc[0]

        with st.container():
            render_html(f"##### {'Edit Transaction' if is_editing else 'New Transaction'}")
            with st.form("txn_form"):
                f1, f2, f3 = st.columns(3)
                with f1:
                    init_date = edit_row['Date'].to_pydatetime() if is_editing and pd.notna(edit_row['Date']) else datetime.now()
                    t_date = st.date_input("Date", value=init_date)
                    cats_list = ["Dining", "Shopping", "Bills", "Transport", "Other", "Groceries", "Entertainment", "Health", "Rent", "Salary", "Investment"]
                    init_cat = edit_row['Category'] if is_editing and edit_row['Category'] in cats_list else "Dining"
                    t_cat = st.selectbox("Category", cats_list, index=cats_list.index(init_cat) if init_cat in cats_list else 0)
                with f2:
                    init_amt = float(edit_row['Amount']) if is_editing else 500.0
                    t_amt = st.number_input(f"Amount ({curr})", min_value=1.0, value=init_amt, step=50.0)
                    pays_list = ["UPI", "Credit Card", "Debit Card", "Bank Transfer", "Cash", "Other"]
                    init_pay = edit_row['Payment Method'] if is_editing and edit_row['Payment Method'] in pays_list else "UPI"
                    t_pay = st.selectbox("Payment Method", pays_list, index=pays_list.index(init_pay) if init_pay in pays_list else 0)
                with f3:
                    types_list = ["Expense", "Income", "Refund", "Transfer"]
                    init_type = edit_row.get('Transaction Type', 'Expense') if is_editing else "Expense"
                    t_type = st.selectbox("Transaction Type", types_list, index=types_list.index(init_type) if init_type in types_list else 0)
                    init_desc = edit_row['Description'] if is_editing and pd.notna(edit_row['Description']) else ""
                    t_desc = st.text_input("Merchant / Description", value=init_desc, placeholder="e.g. Swiggy, Amazon, Groceries")

                render_html("<div style='height:0.8rem;'></div>")
                btn_lbl = "Update Transaction" if is_editing else "Save Transaction"
                submit_txn = st.form_submit_button(btn_lbl, type="primary", use_container_width=True)

                if submit_txn:
                    final_desc = t_desc.strip() if t_desc.strip() else t_cat
                    if is_editing:
                        ds.update_transaction(
                            username=user['username'],
                            txn_id=st.session_state.editing_txn_id,
                            date_str=t_date.strftime('%Y-%m-%d'),
                            category=t_cat,
                            amount=t_amt,
                            payment_method=t_pay,
                            description=final_desc,
                            transaction_type=t_type
                        )
                        st.success("Transaction updated successfully!")
                        st.session_state.editing_txn_id = None
                        st.session_state.show_add_modal = False
                        st.rerun()
                    else:
                        ds.save_new_transaction(
                            username=user['username'],
                            date_str=t_date.strftime('%Y-%m-%d'),
                            category=t_cat,
                            amount=t_amt,
                            payment_method=t_pay,
                            description=final_desc,
                            transaction_type=t_type
                        )
                        st.success("Transaction added successfully!")
                        st.session_state.show_add_modal = False
                        st.rerun()

    # Import CSV Panel
    if st.session_state.get('show_import_panel', False):
        with st.container():
            render_html("##### Import Transactions from CSV")
            st.caption("Upload a CSV file containing at least columns: Date, Category, Amount. Optional: Payment Method, Description, Transaction Type.")
            uploaded_file = st.file_uploader("Choose CSV file", type=['csv'], key="csv_import_uploader")
            if uploaded_file:
                imported, skipped, errors = ds.import_transactions_csv(user['username'], uploaded_file)
                if imported > 0:
                    st.success(f"Successfully imported {imported} transaction(s)! {f'({skipped} duplicates skipped)' if skipped else ''}")
                    st.session_state.show_import_panel = False
                    st.rerun()
                elif skipped > 0 and imported == 0:
                    st.info(f"All {skipped} row(s) were recognized as duplicates and skipped.")
                if errors:
                    st.error("Validation issues encountered:")
                    for err in errors[:5]:
                        st.write(f"- {err}")

    render_html("<hr style='margin:1.25rem 0; border:none; border-top:1px solid #E2E7DF;'>")

    # Search & Filtering
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        months_opt = ["All Months"] + ds.get_available_months(df)
        filt_m = st.selectbox("Month Filter", months_opt, index=0)
    with f2:
        cats_opt = ["All Categories"] + sorted(df['Category'].unique().tolist()) if not df.empty else ["All Categories"]
        filt_c = st.selectbox("Category Filter", cats_opt, index=0)
    with f3:
        pays_opt = ["All Methods"] + sorted(df['Payment Method'].unique().tolist()) if not df.empty else ["All Methods"]
        filt_p = st.selectbox("Payment Method", pays_opt, index=0)
    with f4:
        types_opt = ["All Types", "Expense", "Income", "Refund", "Transfer"]
        filt_t = st.selectbox("Type Filter", types_opt, index=0)
    with f5:
        sort_opt = st.selectbox("Sort By", ["Date (Newest First)", "Date (Oldest First)", "Amount (Highest First)", "Amount (Lowest First)"])

    search_query = st.text_input("🔍 Search transactions by merchant, description, or category", placeholder="e.g. Swiggy, Fuel, Amazon...")

    # Apply filters
    filt_df = df.copy() if not df.empty else pd.DataFrame()
    if not filt_df.empty:
        if filt_m != "All Months":
            filt_df = filt_df[filt_df['MonthName'] == filt_m]
        if filt_c != "All Categories":
            filt_df = filt_df[filt_df['Category'] == filt_c]
        if filt_p != "All Methods":
            filt_df = filt_df[filt_df['Payment Method'] == filt_p]
        if filt_t != "All Types":
            filt_df = filt_df[filt_df['Transaction Type'] == filt_t]
        if search_query.strip():
            sq = search_query.strip().lower()
            filt_df = filt_df[
                filt_df['Description'].astype(str).str.lower().str.contains(sq) |
                filt_df['Category'].astype(str).str.lower().str.contains(sq)
            ]

        # Sorting
        if sort_opt == "Date (Newest First)":
            filt_df = filt_df.sort_values(by='Date', ascending=False)
        elif sort_opt == "Date (Oldest First)":
            filt_df = filt_df.sort_values(by='Date', ascending=True)
        elif sort_opt == "Amount (Highest First)":
            filt_df = filt_df.sort_values(by='Amount', ascending=False)
        elif sort_opt == "Amount (Lowest First)":
            filt_df = filt_df.sort_values(by='Amount', ascending=True)

    # Render Transaction Ledger
    st.caption(f"Showing {len(filt_df)} transaction(s)")
    if not filt_df.empty:
        for _, r in filt_df.iterrows():
            txn_id = r['id']
            d_str = r['Date'].strftime('%d %b %Y') if hasattr(r['Date'], 'strftime') else str(r['Date'])
            desc = r['Description'] if pd.notna(r['Description']) and r['Description'] else r['Category']
            ttype = r.get('Transaction Type', 'Expense')
            badge_cls = 'badge-success' if ttype == 'Income' else ('badge-warning' if ttype == 'Refund' else 'badge-neutral')

            row_c1, row_c2, row_c3 = st.columns([5, 1.8, 1.2])
            with row_c1:
                render_html(f"""
                <div style="padding: 0.35rem 0;">
                    <span style="font-weight: 600; font-size: 0.95rem; color: #1C2826;">{desc}</span>
                    <span class="badge {badge_cls}" style="margin-left: 6px;">{ttype}</span><br>
                    <span style="font-size: 0.8rem; color: #6A7C72;">{r['Category']} • {r['Payment Method']} • {d_str}</span>
                </div>
                """)
            with row_c2:
                amt_color = "#2E7D47" if ttype == 'Income' else ("#C97A2B" if ttype == 'Refund' else "#1C2826")
                render_html(f"<div style='font-size:1.1rem; font-weight:700; color:{amt_color}; padding-top:0.5rem;'>{curr}{r['Amount']:,.0f}</div>")
            with row_c3:
                btn_edit, btn_del = st.columns(2)
                with btn_edit:
                    if st.button("✏️", key=f"edit_btn_{txn_id}", help="Edit Transaction"):
                        st.session_state.editing_txn_id = txn_id
                        st.session_state.show_add_modal = True
                        st.rerun()
                with btn_del:
                    if st.button("🗑️", key=f"del_btn_{txn_id}", help="Delete Transaction"):
                        ds.delete_transaction_by_id(user['username'], txn_id)
                        st.success("Deleted!")
                        st.rerun()
            render_html("<hr style='margin:0.2rem 0; border:none; border-top:1px solid #EEF2EB;'>")
    else:
        render_html("""
        <div class="surface-card" style="text-align: center; padding: 2.5rem; color: #5C6E64;">
            <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">💳</div>
            <div style="font-weight: 600; color: #1C2826; font-size: 1.05rem;">No matching transactions found</div>
            <div>Try adjusting your filters, or record a new transaction using the button above.</div>
        </div>
        """)

# ============================================================
# 8. SPENDING INTELLIGENCE WITH DRILL-DOWN
# ============================================================
def render_spending(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    render_html("<h1>Spending</h1>")
    render_html(f"<div class='page-subtitle'>Understand where your money goes in <strong>{sm}</strong>.</div>")

    kpis = ds.calculate_kpis(df, sm, user)
    total_spent = kpis['spent']

    # KPI Banner
    top_s1, top_s2, top_s3 = st.columns(3)
    with top_s1:
        render_html(f"""
        <div class="metric-card">
            <div class="metric-label">Total Net Spending</div>
            <div class="metric-value">{curr}{total_spent:,.0f}</div>
            <div class="metric-sub">In {sm}</div>
        </div>
        """)
    with top_s2:
        cat_breakdown = ds.get_category_breakdown(df, sm)
        top_cat = cat_breakdown.index[0] if not cat_breakdown.empty else "N/A"
        top_amt = cat_breakdown.iloc[0] if not cat_breakdown.empty else 0.0
        render_html(f"""
        <div class="metric-card">
            <div class="metric-label">Top Expense Category</div>
            <div class="metric-value">{top_cat}</div>
            <div class="metric-sub">{curr}{top_amt:,.0f} ({round((top_amt/total_spent)*100) if total_spent>0 else 0}%)</div>
        </div>
        """)
    with top_s3:
        m_txns = ds.get_month_data(df, sm)
        expense_count = len(m_txns[m_txns['Transaction Type'] == 'Expense']) if not m_txns.empty else 0
        render_html(f"""
        <div class="metric-card">
            <div class="metric-label">Active Categories</div>
            <div class="metric-value">{len(cat_breakdown)}</div>
            <div class="metric-sub">{expense_count} total expenses</div>
        </div>
        """)

    render_html("<div style='height: 1rem;'></div>")

    if not cat_breakdown.empty:
        col_bars, col_details = st.columns([1.2, 1])
        with col_bars:
            render_html("### Category breakdown")
            sage_palette = ['#4A6B53', '#5D8567', '#739E7D', '#8CB396', '#A6C7AF', '#C0DBC8', '#D8E9DD']
            for i, (c_name, c_amt) in enumerate(cat_breakdown.items()):
                pct = (c_amt / total_spent * 100) if total_spent > 0 else 0
                color = sage_palette[i % len(sage_palette)]
                render_html(f"""
                <div class="cat-row">
                    <div class="cat-meta">
                        <span class="cat-name">{c_name}</span>
                        <span class="cat-amount">{curr}{c_amt:,.0f} ({round(pct, 1)}%)</span>
                    </div>
                    <div class="cat-bar-bg">
                        <div class="cat-bar-fill" style="width: {pct}%; background: {color};"></div>
                    </div>
                </div>
                """)

        with col_details:
            render_html("### Period Comparison")
            all_m = ds.get_available_months(df)
            cur_idx = all_m.index(sm) if sm in all_m else -1
            if cur_idx != -1 and cur_idx + 1 < len(all_m):
                prev_m = all_m[cur_idx + 1]
                prev_kpis = ds.calculate_kpis(df, prev_m, user)
                if prev_kpis['spent'] > 0:
                    diff = total_spent - prev_kpis['spent']
                    diff_pct = round(abs(diff) / prev_kpis['spent'] * 100, 1)
                    if diff > 0:
                        render_html(f"""
                        <div class="insight-item warn">
                            <div style="font-weight:600; color:#1C2826;">Spending increased by {curr}{diff:,.0f} (+{diff_pct}%)</div>
                            <div style="font-size:0.85rem; color:#4D5E54;">Compared to {prev_m} ({curr}{prev_kpis['spent']:,.0f}).</div>
                        </div>
                        """)
                    else:
                        render_html(f"""
                        <div class="insight-item good">
                            <div style="font-weight:600; color:#1C2826;">Spending decreased by {curr}{abs(diff):,.0f} (-{diff_pct}%)</div>
                            <div style="font-size:0.85rem; color:#4D5E54;">Discipline improved compared to {prev_m}.</div>
                        </div>
                        """)
            else:
                st.info("No prior month on record for comparison.")

        # Interactive Category Drill-Down
        render_html("<div style='height: 1.5rem;'></div>")
        render_html("### Category Drill-Down")
        drill_cat = st.selectbox("Select a category to view its underlying transactions:", cat_breakdown.index.tolist())
        if drill_cat:
            cat_txns = m_txns[m_txns['Category'] == drill_cat].sort_values(by='Amount', ascending=False)
            st.caption(f"Showing {len(cat_txns)} transaction(s) in {drill_cat}")
            for _, r in cat_txns.iterrows():
                d_str = r['Date'].strftime('%d %b %Y') if hasattr(r['Date'], 'strftime') else str(r['Date'])
                render_html(f"""
                <div class="txn-item">
                    <div>
                        <span style="font-weight: 500; color: #1C2826;">{r['Description']}</span><br>
                        <span style="font-size: 0.78rem; color: #788A80;">{r['Payment Method']} • {d_str}</span>
                    </div>
                    <div style="font-weight: 600; color: #1C2826;">{curr}{r['Amount']:,.0f}</div>
                </div>
                """)
    else:
        render_html(f"""
        <div class="surface-card" style="text-align:center; padding:2.5rem; color:#5C6E64;">
            No spending records exist for {sm}.
        </div>
        """)

# ============================================================
# 9. SAVINGS GOALS
# ============================================================
def render_goals():
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')

    render_html("<h1>Savings Goals</h1>")
    render_html("<div class='page-subtitle'>Define clear savings targets, record contributions, and track milestones.</div>")

    if st.button("➕ Create Savings Goal", type="primary", key="open_create_goal_btn"):
        st.session_state.show_goal_form = not st.session_state.get('show_goal_form', False)

    if st.session_state.get('show_goal_form', False):
        with st.container():
            render_html("##### New Savings Goal")
            with st.form("add_goal_form"):
                g1, g2, g3 = st.columns(3)
                with g1:
                    gn = st.text_input("Goal Name", placeholder="e.g. Emergency Fund, New Laptop, Vacation")
                    gcat = st.selectbox("Category", ["Savings", "Electronics", "Travel", "Vehicle", "Home", "Education", "Other"])
                with g2:
                    gt = st.number_input(f"Target Amount ({curr})", min_value=1000.0, value=50000.0, step=5000.0)
                    gc = st.number_input(f"Current Amount Saved ({curr})", min_value=0.0, value=0.0, step=1000.0)
                with g3:
                    gd = st.text_input("Target Date", value="December 2027", placeholder="e.g. March 2027")
                    render_html("<div style='height:1.7rem;'></div>")
                    submit_g = st.form_submit_button("Save Goal", type="primary", use_container_width=True)

                if submit_g:
                    if gn.strip():
                        ds.add_savings_goal(user['username'], gn.strip(), gt, gc, gd, gcat)
                        st.session_state.show_goal_form = False
                        st.success("Savings Goal created!")
                        st.rerun()
                    else:
                        st.error("Please enter a goal name.")

    render_html("<hr style='margin:1.25rem 0; border:none; border-top:1px solid #E2E7DF;'>")

    goals = ds.get_savings_goals(user['username'])
    if goals:
        for g in goals:
            gid = g['id']
            pct = round((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
            rem = max(0.0, g['target_amount'] - g['current_amount'])
            status = g.get('status', 'In Progress')
            badge_cls = 'badge-success' if status == 'Completed' else 'badge-sage'

            c_info, c_action = st.columns([3, 1.2])
            with c_info:
                render_html(f"""
                <div class="surface-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-weight:700; font-size:1.1rem; color:#1C2826;">{g['name']}</span>
                        <span>
                            <span class="badge badge-neutral" style="margin-right:4px;">{g.get('category', 'Savings')}</span>
                            <span class="badge {badge_cls}">{status}</span>
                        </span>
                    </div>
                    <div style="font-size:1.45rem; font-weight:700; color:#4A6B53; margin:4px 0;">
                        {curr}{g['current_amount']:,.0f} <span style="font-size:0.9rem; font-weight:normal; color:#6A7C72;">/ {curr}{g['target_amount']:,.0f}</span>
                    </div>
                    <div style="font-size:0.83rem; color:#5C6E64;">
                        <strong>{pct}% completed</strong> • {curr}{rem:,.0f} remaining • Target: {g['target_date']}
                    </div>
                </div>
                """)
                st.progress(float(min(100, pct) / 100.0))
            with c_action:
                add_val = st.number_input(f"+ Record Contribution ({curr})", min_value=100.0, value=1000.0, step=500.0, key=f"contrib_val_{gid}")
                if st.button("Deposit Funds", key=f"contrib_btn_{gid}", use_container_width=True):
                    ds.add_to_goal_savings(user['username'], gid, add_val)
                    st.success(f"Added {curr}{add_val:,.0f} to {g['name']}!")
                    st.rerun()
                if st.button("Delete Goal", key=f"del_goal_btn_{gid}", use_container_width=True):
                    ds.delete_savings_goal(user['username'], gid)
                    st.rerun()
            render_html("<div style='height:0.75rem;'></div>")
    else:
        render_html("""
        <div class="surface-card" style="text-align:center; padding:2.5rem; color:#5C6E64;">
            <div style="font-size: 1.8rem; margin-bottom: 0.4rem;">🎯</div>
            <div style="font-weight:600; color:#1C2826;">You don't have an active savings goal</div>
            <div>Define what you are saving for and watch your progress build over time.</div>
        </div>
        """)

# ============================================================
# 10. SPENDING SCENARIOS (WHAT-IF MODELING)
# ============================================================
def render_scenarios(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    render_html("<h1>Spending Scenarios</h1>")
    render_html(f"<div class='page-subtitle'>Interactive scenario simulator — test how trimming non-essential expenses in <strong>{sm}</strong> puts money directly back into your pocket.</div>")

    cat_breakdown = ds.get_category_breakdown(df, sm)
    if cat_breakdown.empty:
        st.info(f"No expense transactions recorded in {sm} to model scenarios. Please select a period with active spending.")
        return

    # Quick Simulation Preset Buttons
    st.markdown("#### Quick Simulation Presets")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    with p_col1:
        if st.button("⚡ Light Trim (5%)", use_container_width=True, key="sc_pre_5"):
            for c in cat_breakdown.index:
                st.session_state.scenario_adjustments[c] = 5
            st.rerun()
    with p_col2:
        if st.button("🎯 Balanced (15%)", use_container_width=True, key="sc_pre_15"):
            for c in cat_breakdown.index:
                st.session_state.scenario_adjustments[c] = 15
            st.rerun()
    with p_col3:
        if st.button("🚀 Aggressive (25%)", use_container_width=True, key="sc_pre_25"):
            for c in cat_breakdown.index:
                st.session_state.scenario_adjustments[c] = 25
            st.rerun()
    with p_col4:
        if st.button("🔄 Reset Reductions", use_container_width=True, key="sc_pre_0"):
            st.session_state.scenario_adjustments = {}
            st.rerun()

    render_html("<div style='height:0.75rem;'></div>")

    col_sliders, col_result = st.columns([1.2, 1])
    active_reductions = {}

    with col_sliders:
        st.markdown("### Adjust Spending Reductions")
        st.caption("Select categories where you can reduce discretionary spending:")
        for cat_name, cat_val in cat_breakdown.head(6).items():
            prev_slider = st.session_state.scenario_adjustments.get(cat_name, 0)
            chosen_pct = st.slider(
                f"{cat_name} (Current: {curr}{cat_val:,.0f})",
                min_value=0,
                max_value=50,
                value=prev_slider,
                step=5,
                format="%d%%",
                key=f"scenario_sl_{cat_name}"
            )
            active_reductions[cat_name] = chosen_pct
            st.session_state.scenario_adjustments[cat_name] = chosen_pct
            saved_cat_amt = (cat_val * chosen_pct) / 100.0
            if chosen_pct > 0:
                st.caption(f"💡 Saves {curr}{saved_cat_amt:,.0f}/month in {cat_name}")

    scenario_res = ds.calculate_spending_scenario(df, sm, user, active_reductions)

    with col_result:
        st.markdown("### Projected Financial Impact")
        render_html(f"""
        <div class="scenario-gradient-card">
            <div class="scenario-gradient-label">Monthly Savings Increase</div>
            <div class="scenario-gradient-val">+{curr}{scenario_res['monthly_savings_increase']:,.0f} / mo</div>
            <div class="scenario-gradient-sub">+{curr}{scenario_res['annual_savings']:,.0f} potential savings over 12 months</div>
        </div>
        <div class="surface-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.75rem;">
                <span style="font-size:0.85rem; font-weight:700; color:#64748B; text-transform:uppercase;">Baseline Spending ({sm})</span>
                <span style="font-weight:700; color:#0F172A;">{curr}{scenario_res['current_spending']:,.0f}</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.75rem;">
                <span style="font-size:0.85rem; font-weight:700; color:#64748B; text-transform:uppercase;">Projected Spending</span>
                <span style="font-weight:800; color:#2563EB;">{curr}{scenario_res['simulated_spending']:,.0f}</span>
            </div>
            <hr style="margin:0.75rem 0; border:none; border-top:1px solid #E2E8F0;">
            <div style="display:flex; justify-content:space-between;">
                <span style="font-size:0.85rem; font-weight:700; color:#64748B; text-transform:uppercase;">New Monthly Net Savings</span>
                <span style="font-weight:800; color:#059669; font-size:1.15rem;">{curr}{scenario_res['simulated_savings']:,.0f} / mo</span>
            </div>
        </div>
        """)
        st.caption("Hypothetical simulation based on your verified baseline spending records.")


# ============================================================
# 11. SPENDING FORECAST
# ============================================================
def render_forecast(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')

    render_html("<h1>Spending Forecast</h1>")
    render_html("<div class='page-subtitle'>Data-driven trajectory modeling and intelligent velocity projection.</div>")

    fc = ds.get_forecast(df, user)

    if not fc or not fc.get('has_sufficient_history', False):
        msg = fc.get('message', 'Log at least 3 months of transactions to generate trend forecasts.') if fc else 'Log at least 3 months of transactions to generate trend forecasts.'
        render_html(f"""
        <div class="surface-card" style="padding: 2.5rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔮</div>
            <div style="font-weight: 700; font-size: 1.15rem; color: #1E3A8A; margin-bottom: 0.4rem;">
                {msg}
            </div>
            <div style="font-size: 0.88rem; color: #64748B;">
                As you continue to log your monthly expenses, trend lines and projected run-rates will unlock automatically.
            </div>
        </div>
        """)
        return

    # Top Forecast KPI Banner
    f1, f2, f3 = st.columns(3)
    with f1:
        render_html(f"""
        <div class="metric-card spent">
            <div class="metric-label">Expected in {fc['next_month']}</div>
            <div class="metric-value" style="color:#2563EB;">{curr}{fc['predicted_amount']:,.0f}</div>
            <div class="metric-sub">Linear Trend Projection</div>
        </div>
        """)
    with f2:
        render_html(f"""
        <div class="metric-card budget">
            <div class="metric-label">Monthly Spending Budget</div>
            <div class="metric-value">{curr}{fc['budget']:,.0f}</div>
            <div class="metric-sub">Target Spending Threshold</div>
        </div>
        """)
    with f3:
        sc_col = "#059669" if fc['under_budget'] else "#DC2626"
        sc_txt = "under budget" if fc['under_budget'] else "over budget"
        render_html(f"""
        <div class="metric-card saved">
            <div class="metric-label">Expected Difference</div>
            <div class="metric-value" style="color:{sc_col};">{curr}{abs(fc['expected_difference']):,.0f} {sc_txt}</div>
            <div class="metric-sub">Forecasted Buffer</div>
        </div>
        """)

    render_html("<div style='height: 1rem;'></div>")

    # Visual Historical Monthly Trajectory & Projected Category Impact
    c_hist, c_shares = st.columns([1.2, 1])
    with c_hist:
        st.markdown("### Historical Spending Trajectory")
        hist_months = fc['historical_months']
        hist_amounts = fc['historical_amounts']
        
        for i, (m_period, m_amt) in enumerate(zip(hist_months, hist_amounts)):
            pct_used = min(100.0, (m_amt / fc['budget']) * 100) if fc['budget'] > 0 else 0
            # calculate delta from previous
            delta_str = ""
            if i > 0 and hist_amounts[i-1] > 0:
                diff_pct = round(((m_amt - hist_amounts[i-1]) / hist_amounts[i-1]) * 100, 1)
                delta_sign = "+" if diff_pct > 0 else ""
                delta_badge_cls = "badge-danger" if diff_pct > 0 else "badge-success"
                delta_str = f'<span class="badge {delta_badge_cls}" style="margin-left:8px;">{delta_sign}{diff_pct}%</span>'

            status_cls = "badge-success" if m_amt <= fc['budget'] else "badge-danger"
            status_txt = "Within Budget" if m_amt <= fc['budget'] else "Over Budget"

            render_html(f"""
            <div class="trajectory-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <div>
                        <span class="trajectory-period">{m_period}</span>
                        {delta_str}
                    </div>
                    <span class="trajectory-amount">{curr}{m_amt:,.0f}</span>
                </div>
                <div class="cat-bar-bg" style="height:8px; margin-bottom:0.35rem;">
                    <div class="cat-bar-fill" style="width:{pct_used}%; background:#2563EB;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#64748B;">
                    <span>{round(pct_used)}% of monthly budget</span>
                    <span class="badge {status_cls}">{status_txt}</span>
                </div>
            </div>
            """)

    with c_shares:
        st.markdown("### Projected Category Contributors")
        tot_proj = sum(fc['projected_categories'].values()) if fc['projected_categories'] else 1.0
        blue_pal = ['#1D4ED8', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD']
        
        for idx, (cat_n, cat_val) in enumerate(list(fc['projected_categories'].items())[:5]):
            pct_share = round((cat_val / tot_proj) * 100)
            bar_color = blue_pal[idx % len(blue_pal)]
            render_html(f"""
            <div class="cat-row">
                <div class="cat-meta">
                    <span class="cat-name">{cat_n}</span>
                    <span class="cat-amount">{curr}{cat_val:,.0f} ({pct_share}%)</span>
                </div>
                <div class="cat-bar-bg">
                    <div class="cat-bar-fill" style="width: {pct_share}%; background: {bar_color};"></div>
                </div>
            </div>
            """)

        # SmartSpend Forecast Verdict Callout Box
        render_html(f"""
        <div style="background:#EFF6FF; border:1.5px solid #BFDBFE; border-radius:14px; padding:1.25rem 1.4rem; margin-top:1.1rem;">
            <div style="font-weight:800; color:#1E3A8A; font-size:1.02rem;">SmartSpend Projection Summary</div>
            <div style="color:#1E40AF; font-size:0.9rem; margin-top:4px; line-height:1.55;">
                Based on your verified {fc['data_months']}-month financial run-rate, your expected spending for {fc['next_month']} is <strong>{curr}{fc['predicted_amount']:,.0f}</strong>. You are on track to stay <strong>{curr}{abs(fc['expected_difference']):,.0f} under budget</strong>.
            </div>
        </div>
        """)

    render_html("<div style='height: 0.5rem;'></div>")
    with st.expander("How SmartSpend calculates this forecast"):
        st.markdown(f"""
        - **Modeling Approach**: Ordinary Least Squares (OLS) Linear Regression fitted over {fc['data_months']} months of historical spending totals.
        - **Trend Velocity**: {curr}{fc['slope']:,.0f} change per month.
        - **Goodness of Fit (R²)**: {fc['r2_score']}
        - **Guidance Note**: Projections reflect historical patterns and provide honest bounds to plan ahead with discipline.
        """)


# ============================================================
# 12. ALERTS (ACTIONABLE & PERSISTENT DISMISSAL)
# ============================================================
def render_alerts(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    render_html("<h1>Alerts</h1>")
    render_html("<div class='page-subtitle'>Contextual notifications that highlight meaningful financial events.</div>")

    alerts = ds.get_user_alerts(df, sm, user, user['username'])

    top_c, _ = st.columns([2, 5])
    with top_c:
        if st.button("Reset Dismissed Alerts", key="reset_alerts_btn"):
            ds.reset_dismissed_alerts(user['username'])
            st.success("Dismissed alerts have been restored.")
            st.rerun()

    render_html("<div style='height: 0.5rem;'></div>")

    if alerts:
        for a in alerts:
            aid = a['id']
            b_class = 'danger' if a['severity'] == 'danger' else ''
            
            c_text, c_btn = st.columns([5, 1.5])
            with c_text:
                render_html(f"""
                <div class="alert-banner {b_class}">
                    <div style="font-weight: 700; color: #1C2826; font-size: 1rem;">{a['title']}</div>
                    <div style="font-size: 0.88rem; color: #2D3E36; margin: 3px 0;">{a['message']}</div>
                </div>
                """)
            with c_btn:
                if st.button(f"{a['action_label']}", key=f"act_alert_{aid}", use_container_width=True):
                    nav(a['action_target'])
                if st.button("Dismiss", key=f"dis_alert_{aid}", use_container_width=True):
                    ds.dismiss_alert(user['username'], aid)
                    st.rerun()
    else:
        render_html("""
        <div class="surface-card" style="padding: 2.25rem; text-align: center; color: #2E7D47;">
            <div style="font-size: 2rem; margin-bottom: 0.35rem;">✅</div>
            <div style="font-weight: 600; font-size: 1.1rem; color: #1C2826;">You're all caught up</div>
            <div style="color: #5C6E64; font-size: 0.92rem;">No alerts require your attention right now. All expenses and budget metrics look healthy.</div>
        </div>
        """)

# ============================================================
# 13. ASK SMARTSPEND AI FINANCIAL ASSISTANT
# ============================================================
def render_ask(df):
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')
    sm = st.session_state.selected_month

    render_html("<h1>Ask SmartSpend</h1>")
    render_html(f"<div class='page-subtitle'>Personalized financial Q&A grounded directly in your verified records for <strong>{sm}</strong>.</div>")

    prompts = [
        "Where did most of my money go?",
        "Am I over budget this month?",
        "How much can I safely invest?",
        "What is my emergency fund buffer?",
        "Can I afford a ₹5,000 expense?",
        "What are my savings goals?",
        "What was my largest purchase?",
        "Give me a 50/30/20 budget plan"
    ]

    render_html("<p style='font-size:0.82rem; font-weight:700; color:#6A7C72; letter-spacing:0.04em;'>POPULAR QUESTIONS</p>")
    cols = st.columns(4)
    selected_p = None
    for i, p_txt in enumerate(prompts):
        with cols[i % 4]:
            if st.button(p_txt, key=f"ask_chip_{i}", use_container_width=True):
                selected_p = p_txt

    if selected_p:
        st.session_state.active_ai_query = selected_p

    with st.form("ask_form"):
        user_q = st.text_input(
            "Ask a financial question",
            value=st.session_state.active_ai_query,
            placeholder="e.g. Can I afford a ₹5,000 dinner? or What is my savings rate?",
            key="user_ask_input"
        )
        send_btn = st.form_submit_button("Ask SmartSpend", type="primary", use_container_width=True)

    if send_btn and user_q.strip():
        res = ds.ask_financial_assistant(user_q.strip(), df, user, sm)
        st.session_state.chat_history.insert(0, {
            'query': user_q.strip(),
            'answer': res.get('answer', ''),
            'suggestion': res.get('suggestion', '')
        })

    # Render Chat History
    if st.session_state.chat_history:
        for item in st.session_state.chat_history:
            render_html(f"""
            <div class="ai-response-card">
                <div class="ai-header">
                    <span>💬</span>
                    <span>Question: {item['query']}</span>
                </div>
                <div class="ai-body">
                    {item['answer'].replace(chr(10), '<br>')}
                </div>
                {"<div class='ai-suggestion'>" + item['suggestion'].replace(chr(10), '<br>') + "</div>" if item['suggestion'] else ""}
            </div>
            """)

# ============================================================
# 14. PROFILE
# ============================================================
def render_profile():
    user = st.session_state.user_profile
    curr = user.get('preferred_currency', '₹')

    render_html("<h1>Profile</h1>")
    render_html("<div class='page-subtitle'>View and update your personal and financial profile.</div>")

    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        with c1:
            render_html("#### Personal Details")
            p_name = st.text_input("Full Name", value=user.get('name', ''))
            p_email = st.text_input("Email Address", value=user.get('email', ''))
            st.text_input("Username", value=user.get('username', ''), disabled=True, help="Username cannot be altered.")
        with c2:
            st.markdown("#### Financial Setup")
            p_income = st.number_input(f"Monthly Income ({curr})", min_value=1000.0, value=float(user.get('monthly_income', 75000.0)), step=5000.0)
            p_budget = st.number_input(f"Monthly Spending Budget ({curr})", min_value=1000.0, value=float(user.get('monthly_budget', 50000.0)), step=5000.0)
            curr_opts = ["₹", "$", "€", "£"]
            p_curr = st.selectbox("Preferred Currency", curr_opts, index=curr_opts.index(curr) if curr in curr_opts else 0)

        render_html("<div style='height:0.8rem;'></div>")
        save_prof = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

        if save_prof:
            if p_name.strip() and p_email.strip():
                up = ds.update_user_profile(user['username'], {
                    'name': p_name.strip(),
                    'email': p_email.strip(),
                    'monthly_income': p_income,
                    'monthly_budget': p_budget,
                    'preferred_currency': p_curr
                })
                st.session_state.user_profile = up
                st.success("Profile updated successfully!")
                st.rerun()
            else:
                st.error("Name and Email cannot be empty.")

# ============================================================
# 15. SETTINGS
# ============================================================
def render_settings(df):
    user = st.session_state.user_profile
    render_html("<h1>Settings</h1>")
    render_html("<div class='page-subtitle'>Preferences, security credentials, and data management.</div>")

    s1, s2 = st.columns(2)
    with s1:
        render_html("### Security")
        with st.form("pwd_form"):
            st.caption("Change account password:")
            cur_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            btn_pwd = st.form_submit_button("Update Password", type="primary")

            if btn_pwd:
                ok, msg = ds.change_user_password(user['username'], cur_pwd, new_pwd)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        render_html("<div style='height:1rem;'></div>")
        render_html("### Privacy & Infrastructure")
        render_html("""
        <div class="surface-card" style="font-size: 0.88rem; color: #4D5E54; line-height: 1.6;">
            <strong>Local Data Isolation:</strong> Your transaction records and financial targets are stored privately inside your dedicated account space. No data is shared with third-party advertising networks.
        </div>
        """)

    with s2:
        render_html("### Data Management")
        if not df.empty:
            exp_data = df[['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type']].copy()
            exp_data['Date'] = exp_data['Date'].dt.strftime('%Y-%m-%d')
            st.download_button(
                "📤 Export Complete Financial Records (CSV)",
                exp_data.to_csv(index=False).encode('utf-8'),
                "smartspend_complete_export.csv",
                "text/csv",
                use_container_width=True
            )
        else:
            st.info("No transaction data available to export.")

        render_html("<div style='height:1rem;'></div>")
        st.markdown("### Danger Zone")
        with st.expander("Reset or Clear Account"):
            st.caption("Permanently clears your transaction data:")
            if st.button("Clear All Transactions", key="clear_all_txns_btn"):
                empty_df = pd.DataFrame(columns=['id', 'Date', 'Category', 'Amount', 'Payment Method', 'Description', 'Transaction Type'])
                u_dir = ds._get_user_dir(user['username'])
                empty_df.to_csv(os.path.join(u_dir, 'transactions.csv'), index=False)
                st.success("All transactions cleared.")
                st.rerun()

# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================
def main():
    if not st.session_state.authenticated:
        view = st.session_state.auth_view
        if view == 'signup':
            render_signup()
        elif view == 'login':
            render_login()
        else:
            render_landing()
    else:
        if st.session_state.auth_view == 'onboarding':
            render_onboarding()
        else:
            user = st.session_state.user_profile
            df = ds.load_transactions(user['username'])
            render_sidebar(df)

            p = st.session_state.active_page
            if p == "Overview":
                render_overview(df)
            elif p == "Transactions":
                render_transactions(df)
            elif p == "Spending":
                render_spending(df)
            elif p == "Savings Goals":
                render_goals()
            elif p == "Spending Scenarios":
                render_scenarios(df)
            elif p == "Spending Forecast":
                render_forecast(df)
            elif p == "Alerts":
                render_alerts(df)
            elif p == "Ask SmartSpend":
                render_ask(df)
            elif p == "Profile":
                render_profile()
            elif p == "Settings":
                render_settings(df)
            else:
                render_overview(df)

if __name__ == "__main__":
    main()
