import sys
import os

# Write the complete app.py for SmartSpend AI
APP_CODE = r'''# app.py - SmartSpend AI - Modern Financial Intelligence
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

import data_service as ds
from styles import CUSTOM_CSS

st.set_page_config(
    page_title="SmartSpend AI",
    page_icon="\U0001f4b0",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = ds.get_user_profile()
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Dashboard'
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = 'September 2026'

user = st.session_state.user_profile
curr = user.get('preferred_currency', '\u20b9')

def get_greeting(name):
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return f"Good morning, {name}"
    elif 12 <= hour < 17:
        return f"Good afternoon, {name}"
    return f"Good evening, {name}"

def navigate_to(page):
    st.session_state.active_page = page
    st.rerun()


# ============================================================
# LANDING PAGE
# ============================================================
def render_landing_page():
    nc1, nc2, nc3 = st.columns([4, 4, 3])
    with nc1:
        st.markdown("### \U0001f4b0 **SmartSpend AI**")
    with nc3:
        b1, b2 = st.columns(2)
        with b1:
            if st.button("Sign In", use_container_width=True):
                st.session_state.show_login = True
        with b2:
            if st.button("Get Started", type="primary", use_container_width=True):
                st.session_state.show_login = True

    st.markdown("""
    <div class="landing-hero">
        <div class="landing-title">Understand your spending.<br>Plan your money better.</div>
        <div class="landing-desc">SmartSpend AI helps you track your spending, understand your financial habits, plan future expenses, and work toward your savings goals.</div>
    </div>
    """, unsafe_allow_html=True)

    _, cb, _ = st.columns([1.5, 1, 1.5])
    with cb:
        if st.button("\u26a1 Explore Demo Account", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_profile = ds.get_user_profile()
            st.rerun()

    st.markdown("<h3 style='text-align:center;margin:2rem 0 1.5rem;color:#0f172a;'>Designed for clarity and peace of mind</h3>", unsafe_allow_html=True)
    features = [
        ("\U0001f4ca", "Track your money", "See income, spending, and savings at a glance."),
        ("\U0001f4a1", "Understand spending", "Know where your money goes across categories."),
        ("\U0001f52e", "Plan ahead", "Get next-month spending forecasts from your history."),
        ("\U0001f3af", "Stay within budget", "Know how much budget remains each month."),
        ("\U0001f3c6", "Track savings goals", "Set milestones for purchases and emergency funds."),
        ("\U0001f4ac", "Get answers instantly", "Ask questions and get data-backed answers."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""<div class="landing-feature-card"><div style="font-size:1.5rem;margin-bottom:0.5rem;">{icon}</div><div class="landing-feature-title">{title}</div><div class="landing-feature-desc">{desc}</div></div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    if st.session_state.get('show_login', False):
        st.markdown("<hr style='margin:2rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>Sign in to SmartSpend AI</h3>", unsafe_allow_html=True)
        _, lc, _ = st.columns([1, 1, 1])
        with lc:
            st.text_input("Username", value="janaganika", key="login_user")
            st.text_input("Password", value="password123", type="password", key="login_pass")
            if st.button("Continue to Dashboard", type="primary", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_profile = ds.get_user_profile()
                st.rerun()


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar(df):
    st.sidebar.markdown("### \U0001f4b0 **SmartSpend AI**")
    st.sidebar.caption("Personal Financial Intelligence")
    st.sidebar.markdown("---")

    available = ds.get_available_months(df)
    if st.session_state.selected_month not in available and available:
        st.session_state.selected_month = available[0]
    st.sidebar.markdown("<p style='font-size:0.75rem;font-weight:600;color:#64748b;'>CURRENT PERIOD</p>", unsafe_allow_html=True)
    st.session_state.selected_month = st.sidebar.selectbox("Period", available,
        index=available.index(st.session_state.selected_month) if st.session_state.selected_month in available else 0,
        label_visibility="collapsed")
    st.sidebar.markdown("---")

    pages = [("HOME", ["Dashboard"]), ("MONEY", ["Transactions", "Spending"]),
             ("PLAN", ["Goals", "What-If"]), ("INSIGHTS", ["Forecast", "Alerts", "Ask SmartSpend"]),
             ("ACCOUNT", ["Profile", "Settings"])]
    for section, plist in pages:
        st.sidebar.markdown(f"<p style='font-size:0.75rem;font-weight:700;color:#94a3b8;letter-spacing:0.05em;margin-top:0.6rem;margin-bottom:0.2rem;'>{section}</p>", unsafe_allow_html=True)
        for p in plist:
            active = st.session_state.active_page == p
            label = f"\u25b8 {p}" if active else f"  {p}"
            btype = "primary" if active else "secondary"
            if st.sidebar.button(label, key=f"nav_{p}", type=btype, use_container_width=True):
                st.session_state.active_page = p
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"\U0001f464 **{user.get('name', 'User')}**")
    st.sidebar.caption(user.get('email', ''))
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================
def render_dashboard(df):
    sm = st.session_state.selected_month
    kpis = ds.calculate_kpis(df, sm, user)

    st.markdown(f"<h1>{get_greeting(user.get('name', 'Janaganika'))}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>Here's your financial summary for <strong>{sm}</strong>.</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val, sub, color in [
        (c1, "Income", kpis['income'], "Monthly credit", "#0f172a"),
        (c2, "Spent", kpis['spent'], sm, "#0f172a"),
        (c3, "Saved", kpis['saved'], "Net surplus", "#059669"),
        (c4, "Budget Remaining", kpis['budget_remaining'], "Available", "#059669" if kpis['budget_remaining'] >= 0 else "#dc2626"),
    ]:
        with col:
            st.markdown(f'<div class="summary-card"><div class="summary-card-title">{lbl}</div><div class="summary-card-value" style="color:{color};">{curr}{val:,.0f}</div><div class="summary-card-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem;'></div>", unsafe_allow_html=True)

    badge_cls = f"badge-{kpis['status_type']}"
    st.markdown(f'<div class="budget-box"><div class="budget-header"><div><span style="font-weight:600;font-size:1.05rem;color:#0f172a;">Monthly Budget</span> <span style="margin-left:0.75rem;color:#64748b;font-size:0.9rem;">{curr}{kpis["spent"]:,.0f} of {curr}{kpis["budget"]:,.0f} used</span></div><div><span class="badge {badge_cls}">{kpis["status"]}</span></div></div></div>', unsafe_allow_html=True)
    st.progress(float(kpis['budget_pct'] / 100.0))
    st.caption(f"{round(kpis['budget_pct'])}% used \u2022 {curr}{kpis['budget_remaining']:,.0f} remaining")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### Where your money goes")
        cat_b = ds.get_category_breakdown(df, sm)
        if not cat_b.empty:
            fig, ax = plt.subplots(figsize=(6, 2.8))
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            top = cat_b.head(5)
            colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1']
            yp = np.arange(len(top))
            ax.barh(yp, top.values, color=colors[:len(top)], height=0.55)
            ax.set_yticks(yp)
            ax.set_yticklabels(top.index, fontsize=9.5, color='#1e293b')
            ax.invert_yaxis()
            for s in ['top', 'right', 'left']:
                ax.spines[s].set_visible(False)
            ax.spines['bottom'].set_color('#e2e8f0')
            ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#e2e8f0')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            for cn, ca in cat_b.head(5).items():
                st.markdown(f"**{cn}** \u2014 {curr}{ca:,.0f}")
            if st.button("View spending \u2192", key="dash_spending"):
                navigate_to("Spending")
        else:
            st.info("No spending recorded for this month.")

    with col_right:
        st.markdown("### Things to know")
        insights = ds.get_insights(df, sm, user)
        for item in insights:
            bt = "insight-item-warning" if item.get('type') == 'warning' else ("insight-item-success" if item.get('type') == 'success' else "")
            st.markdown(f'<div class="insight-item {bt}"><div style="font-weight:600;font-size:0.95rem;color:#0f172a;margin-bottom:2px;">{item["title"]}</div><div style="font-size:0.88rem;color:#475569;">{item["text"]}</div></div>', unsafe_allow_html=True)

        st.markdown("### Needs your attention")
        anomalies = ds.detect_sensible_anomalies(df, sm)
        if not anomalies:
            anomalies = ds.detect_sensible_anomalies(df, None)
        if anomalies:
            a = anomalies[0]
            st.markdown(f'<div class="alert-card"><div style="font-weight:600;color:#991b1b;">Unusual {a["category"]} expense</div><div style="font-size:1.15rem;font-weight:700;color:#0f172a;margin:2px 0;">{curr}{a["amount"]:,.0f}</div><div style="font-size:0.82rem;color:#64748b;">Typical ~{curr}{a["typical_amount"]:,.0f} \u2022 {a["date"]}</div></div>', unsafe_allow_html=True)
            if st.button("Review transaction \u2192", key="dash_review"):
                navigate_to("Alerts")
        else:
            st.markdown('<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:0.75rem 1rem;color:#64748b;">\u2705 All caught up. No unusual spending.</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    ct, cg = st.columns([1.3, 1])
    with ct:
        st.markdown("### Recent transactions")
        mdf = ds.get_month_data(df, sm)
        recent = mdf.head(5) if not mdf.empty else df.head(5)
        if not recent.empty:
            dr = recent[['Date', 'Description', 'Category', 'Amount']].copy()
            dr['Date'] = dr['Date'].dt.strftime('%d %b')
            dr['Amount'] = dr['Amount'].apply(lambda x: f"{curr}{x:,.0f}")
            st.dataframe(dr, use_container_width=True, hide_index=True)
            if st.button("View all transactions \u2192", key="dash_txns"):
                navigate_to("Transactions")
        else:
            st.info("No transactions yet.")

    with cg:
        st.markdown("### Savings Goal")
        goals = ds.get_savings_goals()
        if goals:
            g = goals[0]
            pct = round((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
            rem = max(0.0, g['target_amount'] - g['current_amount'])
            st.markdown(f'<div class="goal-card"><div style="font-weight:600;font-size:1.05rem;color:#0f172a;">{g["name"]}</div><div style="font-size:1.3rem;font-weight:700;color:#2563eb;margin:4px 0;">{curr}{g["current_amount"]:,.0f} <span style="font-size:0.85rem;font-weight:normal;color:#64748b;">/ {curr}{g["target_amount"]:,.0f}</span></div><div style="font-size:0.82rem;color:#64748b;">{pct}% complete \u2022 {curr}{rem:,.0f} remaining \u2022 Target: {g["target_date"]}</div></div>', unsafe_allow_html=True)
            st.progress(float(min(100, pct) / 100.0))
            if st.button("View goal \u2192", key="dash_goal"):
                navigate_to("Goals")
        else:
            st.markdown('<div class="goal-card"><div style="font-weight:600;color:#0f172a;">Start a savings goal</div><div style="font-size:0.85rem;color:#64748b;">Set a target and track your progress.</div></div>', unsafe_allow_html=True)
            if st.button("Create goal", key="dash_new_goal"):
                navigate_to("Goals")


# ============================================================
# TRANSACTIONS
# ============================================================
def render_transactions(df):
    st.markdown("<h1>Transactions</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Manage your financial activity.</div>", unsafe_allow_html=True)

    tc1, tc2, tc3 = st.columns([1.2, 1.2, 3])
    with tc1:
        show_add = st.button("+ Add Transaction", type="primary", use_container_width=True)
    with tc2:
        exp = df[['Date', 'Category', 'Amount', 'Payment Method', 'Description']].copy()
        exp['Date'] = exp['Date'].dt.strftime('%Y-%m-%d')
        st.download_button("Export CSV", exp.to_csv(index=False).encode('utf-8'), "smartspend_transactions.csv", "text/csv", use_container_width=True)

    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False
    if show_add:
        st.session_state.show_add_form = not st.session_state.show_add_form

    if st.session_state.show_add_form:
        st.markdown("##### New Transaction")
        f1, f2, f3 = st.columns(3)
        with f1:
            nd = st.date_input("Date", value=datetime.now())
            nc = st.selectbox("Category", ["Dining", "Shopping", "Bills", "Transport", "Other", "Entertainment", "Groceries", "Health"])
        with f2:
            na = st.number_input(f"Amount ({curr})", min_value=1.0, value=500.0, step=50.0)
            np_ = st.selectbox("Payment Method", ["UPI", "Credit Card", "Debit Card", "Bank Transfer", "Cash"])
        with f3:
            ndesc = st.text_input("Description", value="")
            st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Save Transaction", type="primary", use_container_width=True):
                ds.save_new_transaction(nd.strftime('%Y-%m-%d'), nc, na, np_, ndesc)
                st.success("Transaction saved!")
                st.session_state.show_add_form = False
                st.rerun()

    st.markdown("<hr style='margin:1.25rem 0;'>", unsafe_allow_html=True)
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        fm = st.selectbox("Month", ["All Months"] + ds.get_available_months(df))
    with fc2:
        fcat = st.selectbox("Category Filter", ["All Categories"] + sorted(df['Category'].unique().tolist()))
    with fc3:
        fpay = st.selectbox("Payment Method Filter", ["All Methods"] + sorted(df['Payment Method'].unique().tolist()))
    with fc4:
        fsearch = st.text_input("Search", placeholder="e.g. Swiggy")

    filt = df.copy()
    if fm != "All Months":
        filt = filt[filt['MonthName'] == fm]
    if fcat != "All Categories":
        filt = filt[filt['Category'] == fcat]
    if fpay != "All Methods":
        filt = filt[filt['Payment Method'] == fpay]
    if fsearch:
        filt = filt[filt['Description'].str.contains(fsearch, case=False, na=False)]

    st.caption(f"Showing {len(filt)} transactions")
    if not filt.empty:
        tbl = filt[['Date', 'Description', 'Category', 'Payment Method', 'Amount']].copy()
        tbl['Date'] = tbl['Date'].dt.strftime('%Y-%m-%d')
        tbl['Amount'] = tbl['Amount'].apply(lambda x: f"{curr}{x:,.2f}")
        st.dataframe(tbl, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions match your filters.")


# ============================================================
# SPENDING
# ============================================================
def render_spending(df):
    sm = st.session_state.selected_month
    mdf = ds.get_month_data(df, sm)
    total = mdf['Amount'].sum() if not mdf.empty else 0.0

    st.markdown("<h1>Spending</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Understand where your money goes.</div>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="summary-card"><div class="summary-card-title">Total Spending</div><div class="summary-card-value">{curr}{total:,.0f}</div><div class="summary-card-sub">{sm}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="summary-card"><div class="summary-card-title">Categories</div><div class="summary-card-value">{mdf["Category"].nunique() if not mdf.empty else 0}</div><div class="summary-card-sub">Active groups</div></div>', unsafe_allow_html=True)
    with m3:
        avg = mdf['Amount'].mean() if not mdf.empty else 0.0
        st.markdown(f'<div class="summary-card"><div class="summary-card-title">Average Transaction</div><div class="summary-card-value">{curr}{avg:,.0f}</div><div class="summary-card-sub">Per transaction</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Spending by Category")
    cat_b = ds.get_category_breakdown(df, sm)
    if not cat_b.empty:
        cl, cr = st.columns([1.2, 1])
        with cl:
            fig, ax = plt.subplots(figsize=(7, 3.2))
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            ax.barh(np.arange(len(cat_b)), cat_b.values, color='#2563eb', height=0.55)
            ax.set_yticks(np.arange(len(cat_b)))
            ax.set_yticklabels(cat_b.index, fontsize=9.5, color='#1e293b')
            ax.invert_yaxis()
            for s in ['top', 'right', 'left']:
                ax.spines[s].set_visible(False)
            ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#e2e8f0')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        with cr:
            rows = [{"Category": n, "Amount": f"{curr}{a:,.0f}", "Share": f"{round((a/total)*100,1)}%"} for n, a in cat_b.items()]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### Essential vs Discretionary")
        essentials = ['Bills', 'Rent', 'Groceries', 'Utilities', 'Health']
        ess = mdf[mdf['Category'].isin(essentials)]['Amount'].sum()
        disc = total - ess
        ec1, ec2 = st.columns(2)
        with ec1:
            ep = round((ess / total) * 100, 1) if total > 0 else 0
            st.markdown(f'<div class="smart-card"><div style="font-weight:600;color:#0f172a;">Essential</div><div style="font-size:1.6rem;font-weight:700;color:#2563eb;margin:4px 0;">{curr}{ess:,.0f} <span style="font-size:0.9rem;color:#64748b;">({ep}%)</span></div><div style="font-size:0.85rem;color:#64748b;">Rent, bills, groceries, utilities, healthcare.</div></div>', unsafe_allow_html=True)
        with ec2:
            dp = round((disc / total) * 100, 1) if total > 0 else 0
            st.markdown(f'<div class="smart-card"><div style="font-weight:600;color:#0f172a;">Discretionary</div><div style="font-size:1.6rem;font-weight:700;color:#059669;margin:4px 0;">{curr}{disc:,.0f} <span style="font-size:0.9rem;color:#64748b;">({dp}%)</span></div><div style="font-size:0.85rem;color:#64748b;">Dining, shopping, entertainment, travel.</div></div>', unsafe_allow_html=True)
    else:
        st.info("No spending data for this month.")


# ============================================================
# FORECAST
# ============================================================
def render_forecast(df):
    st.markdown("<h1>Spending Forecast</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>What might your future spending look like?</div>", unsafe_allow_html=True)

    fc = ds.get_forecast(df, user)
    if fc:
        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown(f'<div class="summary-card"><div class="summary-card-title">Expected {fc["next_month"]}</div><div class="summary-card-value" style="color:#2563eb;">{curr}{fc["predicted_amount"]:,.0f}</div><div class="summary-card-sub">Projection</div></div>', unsafe_allow_html=True)
        with f2:
            st.markdown(f'<div class="summary-card"><div class="summary-card-title">Your Budget</div><div class="summary-card-value">{curr}{fc["budget"]:,.0f}</div><div class="summary-card-sub">Monthly limit</div></div>', unsafe_allow_html=True)
        with f3:
            sc = "#059669" if fc['under_budget'] else "#dc2626"
            sl = "under budget" if fc['under_budget'] else "over budget"
            st.markdown(f'<div class="summary-card"><div class="summary-card-title">Expected Difference</div><div class="summary-card-value" style="color:{sc};">{curr}{fc["expected_difference"]:,.0f}</div><div class="summary-card-sub">{sl}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### Projected spending contributors")
        pc1, pc2 = st.columns([1.2, 1])
        with pc1:
            fig, ax = plt.subplots(figsize=(7, 3.2))
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            hx = np.arange(len(fc['historical_months']))
            ax.plot(hx, fc['historical_amounts'], marker='o', color='#2563eb', linewidth=2, label='Actual')
            ni = len(hx)
            ax.scatter([ni], [fc['predicted_amount']], color='#ef4444', s=70, zorder=5, label='Projected')
            ax.plot([hx[-1], ni], [fc['historical_amounts'][-1], fc['predicted_amount']], '--', color='#94a3b8')
            labels = [m.split('-')[1] for m in fc['historical_months']] + [fc['next_month'].split(' ')[0][:3]]
            ax.set_xticks(list(hx) + [ni])
            ax.set_xticklabels(labels, fontsize=8.5, color='#64748b')
            for s in ['top', 'right']:
                ax.spines[s].set_visible(False)
            ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#e2e8f0')
            ax.legend(frameon=False, fontsize=8.5)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        with pc2:
            rows = [{"Category": c, "Expected": f"{curr}{a:,.0f}"} for c, a in list(fc['projected_categories'].items())[:5]]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.expander("How does this forecast work?"):
            st.markdown(f"- **Model**: Linear OLS Regression over monthly totals.\n- **Slope**: {fc['slope']} {curr}/month.\n- **R\u00b2**: {fc['r2_score']}")
    else:
        st.warning("We don't have enough transaction history to provide a useful forecast yet. Add more transaction history to unlock spending forecasts.")


# ============================================================
# ALERTS
# ============================================================
def render_alerts(df):
    st.markdown("<h1>Alerts</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>What needs your attention?</div>", unsafe_allow_html=True)

    st.markdown("### Unusual spending")
    anomalies = ds.detect_sensible_anomalies(df, None)
    if anomalies:
        for a in anomalies[:4]:
            st.markdown(f'<div class="alert-card"><div style="font-weight:700;color:#991b1b;font-size:1.05rem;">Unusual {a["category"]} expense</div><div style="font-size:1.35rem;font-weight:700;color:#0f172a;margin:4px 0;">{curr}{a["amount"]:,.0f}</div><div style="font-size:0.88rem;color:#475569;">{a["description"]} \u2022 {a["date"]}</div><div style="font-size:0.82rem;color:#64748b;">Your usual {a["category"]} spending is around {curr}{a["typical_amount"]:,.0f}.</div></div>', unsafe_allow_html=True)
    else:
        st.success("No unusual spending detected. All transactions are within normal bounds.")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Budget alerts")
    kpis = ds.calculate_kpis(df, st.session_state.selected_month, user)
    if kpis['budget_pct'] >= 85:
        st.markdown(f'<div class="insight-item insight-item-warning"><div style="font-weight:600;color:#92400e;">Budget approaching limit</div><div style="font-size:0.88rem;color:#475569;">You have {curr}{kpis["budget_remaining"]:,.0f} remaining.</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="insight-item insight-item-success"><div style="font-weight:600;color:#065f46;">Budget healthy</div><div style="font-size:0.88rem;color:#475569;">{round(kpis["budget_pct"])}% of monthly budget used.</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Regular payments")
    rec = ds.detect_recurring_expenses(df)
    if rec:
        rows = [{"Description": r['description'], "Category": r['category'], "Amount": f"{curr}{r['amount']:,.0f}", "Day": f"~Day {r['typical_day']}", "Frequency": r['frequency']} for r in rec]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No recurring payments detected yet.")

    with st.expander("How unusual spending is detected"):
        st.markdown("- **Algorithm**: IQR + Standard Deviation multi-factor outlier detection.\n- Only genuinely high outliers are flagged. Low/normal amounts are never flagged.")


# ============================================================
# GOALS
# ============================================================
def render_goals():
    st.markdown("<h1>Savings Goals</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>What am I saving for?</div>", unsafe_allow_html=True)

    if 'show_goal_form' not in st.session_state:
        st.session_state.show_goal_form = False
    gc1, _ = st.columns([1.5, 4])
    with gc1:
        if st.button("+ Create Goal", type="primary", use_container_width=True):
            st.session_state.show_goal_form = not st.session_state.show_goal_form

    if st.session_state.show_goal_form:
        st.markdown("##### New Goal")
        g1, g2, g3 = st.columns(3)
        with g1:
            gn = st.text_input("Goal Name", value="New Laptop")
            gcat = st.selectbox("Goal Category", ["Electronics", "Savings", "Travel", "Vehicle", "Home", "General"])
        with g2:
            gt = st.number_input(f"Target ({curr})", min_value=1000.0, value=60000.0, step=5000.0)
            gc_ = st.number_input(f"Current ({curr})", min_value=0.0, value=0.0, step=1000.0)
        with g3:
            gd = st.text_input("Target Date", value="March 2027")
            st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Save Goal", type="primary", use_container_width=True):
                ds.add_savings_goal(gn, gt, gc_, gd, gcat)
                st.success(f"Goal '{gn}' created!")
                st.session_state.show_goal_form = False
                st.rerun()

    st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)
    goals = ds.get_savings_goals()
    if goals:
        for g in goals:
            pct = round((g['current_amount'] / g['target_amount']) * 100) if g['target_amount'] > 0 else 0
            rem = max(0, g['target_amount'] - g['current_amount'])
            cc, ca = st.columns([3, 1])
            with cc:
                st.markdown(f'<div class="goal-card"><div style="display:flex;justify-content:space-between;"><span style="font-weight:700;font-size:1.15rem;color:#0f172a;">{g["name"]}</span><span class="badge badge-neutral">{g.get("category","General")}</span></div><div style="font-size:1.5rem;font-weight:700;color:#2563eb;margin:6px 0;">{curr}{g["current_amount"]:,.0f} <span style="font-size:0.95rem;font-weight:normal;color:#64748b;">/ {curr}{g["target_amount"]:,.0f}</span></div><div style="font-size:0.85rem;color:#64748b;"><strong>{pct}% complete</strong> \u2022 {curr}{rem:,.0f} remaining \u2022 Target: {g["target_date"]}</div></div>', unsafe_allow_html=True)
                st.progress(float(min(100, pct) / 100.0))
            with ca:
                add_a = st.number_input(f"+ Add ({curr})", min_value=500.0, value=2000.0, step=500.0, key=f"gi_{g['id']}")
                if st.button("Deposit", key=f"gd_{g['id']}", use_container_width=True):
                    ds.add_to_goal_savings(g['id'], add_a)
                    st.success(f"Added {curr}{add_a:,.0f}!")
                    st.rerun()
    else:
        st.markdown('<div style="background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:2rem;text-align:center;color:#64748b;"><p style="font-weight:600;color:#1e293b;">You don\'t have a savings goal yet.</p><p>Create one to start tracking your progress.</p></div>', unsafe_allow_html=True)


# ============================================================
# WHAT-IF
# ============================================================
def render_whatif(df):
    st.markdown("<h1>What-If</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>See how changing your spending could affect your savings.</div>", unsafe_allow_html=True)

    sm = st.session_state.selected_month
    mdf = ds.get_month_data(df, sm)
    cat_b = ds.get_category_breakdown(df, sm)
    income = float(user.get('monthly_income', 75000.0))
    spent = float(mdf['Amount'].sum()) if not mdf.empty else 0.0
    savings = max(0.0, income - spent)

    cs, cr = st.columns([1.2, 1])
    reductions = {}
    with cs:
        st.markdown("### Adjust your spending")
        for cat in ['Dining', 'Shopping', 'Transport', 'Other']:
            cv = cat_b.get(cat, 0.0)
            reductions[cat] = st.slider(f"{cat} reduction ({curr}{cv:,.0f})", 0, 50, 0, step=5, format="%d%%")

    total_diff = sum(cat_b.get(c, 0.0) * (p / 100.0) for c, p in reductions.items())
    pot_savings = savings + total_diff

    with cr:
        st.markdown("### Projected Impact")
        st.markdown(f'<div class="smart-card"><div style="color:#64748b;font-size:0.85rem;text-transform:uppercase;">Current Savings</div><div style="font-size:1.4rem;font-weight:700;color:#0f172a;">{curr}{savings:,.0f}/month</div><hr style="margin:0.75rem 0;border:none;border-top:1px solid #e2e8f0;"><div style="color:#64748b;font-size:0.85rem;text-transform:uppercase;">Potential Savings</div><div style="font-size:1.75rem;font-weight:700;color:#059669;">{curr}{pot_savings:,.0f}/month</div><hr style="margin:0.75rem 0;border:none;border-top:1px solid #e2e8f0;"><div style="color:#64748b;font-size:0.85rem;text-transform:uppercase;">Monthly Increase</div><div style="font-size:1.3rem;font-weight:700;color:#2563eb;">+{curr}{total_diff:,.0f}/month</div><div style="font-size:0.82rem;color:#64748b;">+{curr}{total_diff*12:,.0f} projected over 12 months</div></div>', unsafe_allow_html=True)
        st.caption("Scenario only \u2014 actual savings may vary.")


# ============================================================
# ASK SMARTSPEND
# ============================================================
def render_ask(df):
    st.markdown("<h1>Ask SmartSpend</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Ask questions about your own financial data.</div>", unsafe_allow_html=True)

    quick = [
        "Where did most of my money go?", "Why did I spend more this month?",
        "What are my biggest expenses?", "Which category increased the most?",
        "What recurring payments do I have?", "How much did I spend on dining?",
        "How much am I saving?", "What if I reduce shopping by 20%?"
    ]
    st.markdown("##### Quick Questions")
    cols = st.columns(4)
    sel = None
    for i, q in enumerate(quick):
        with cols[i % 4]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                sel = q

    uq = st.text_input("Ask a custom question", value=sel if sel else "", placeholder="e.g. Where did most of my money go?")
    if uq:
        ans = ds.ask_financial_assistant(uq, df, user, st.session_state.selected_month)
        st.markdown(f'<div class="smart-card" style="border-left:4px solid #2563eb;"><div style="font-weight:600;font-size:1rem;color:#0f172a;margin-bottom:0.5rem;">Answer</div><div style="color:#334155;line-height:1.6;">{ans}</div></div>', unsafe_allow_html=True)


# ============================================================
# PROFILE
# ============================================================
def render_profile():
    st.markdown("<h1>Profile</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Your account information.</div>", unsafe_allow_html=True)

    cl, cr = st.columns(2)
    with cl:
        st.markdown(f'<div class="smart-card"><h4>Personal Information</h4><p style="color:#64748b;">Name: <strong style="color:#0f172a;">{user.get("name","")}</strong></p><p style="color:#64748b;">Email: <strong style="color:#0f172a;">{user.get("email","")}</strong></p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="smart-card"><h4>Financial Information</h4><p style="color:#64748b;">Currency: <strong style="color:#0f172a;">{curr}</strong></p><p style="color:#64748b;">Monthly Income: <strong style="color:#0f172a;">{curr}{user.get("monthly_income",75000):,.0f}</strong></p><p style="color:#64748b;">Monthly Budget: <strong style="color:#0f172a;">{curr}{user.get("monthly_budget",50000):,.0f}</strong></p></div>', unsafe_allow_html=True)
    with cr:
        goals = ds.get_savings_goals()
        ts = sum(g['current_amount'] for g in goals)
        st.markdown(f'<div class="smart-card"><h4>Savings</h4><p style="color:#64748b;">Active Goals: <strong style="color:#0f172a;">{len(goals)}</strong></p><p style="color:#64748b;">Total In Goals: <strong style="color:#0f172a;">{curr}{ts:,.0f}</strong></p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="smart-card"><h4>Account</h4><p style="color:#64748b;">Member Since: <strong style="color:#0f172a;">{user.get("member_since","2025")}</strong></p><p style="color:#64748b;">Status: <span class="badge badge-success">{user.get("account_status","Active")}</span></p></div>', unsafe_allow_html=True)

    if 'edit_profile' not in st.session_state:
        st.session_state.edit_profile = False
    if st.button("Edit Profile", type="primary"):
        st.session_state.edit_profile = not st.session_state.edit_profile

    if st.session_state.edit_profile:
        st.markdown("##### Edit Details")
        e1, e2, e3 = st.columns(3)
        with e1:
            en = st.text_input("Name", value=user.get('name', ''))
            ee = st.text_input("Email", value=user.get('email', ''))
        with e2:
            ei = st.number_input(f"Income ({curr})", min_value=1000.0, value=float(user.get('monthly_income', 75000)), step=5000.0)
            eb = st.number_input(f"Budget ({curr})", min_value=1000.0, value=float(user.get('monthly_budget', 50000)), step=5000.0)
        with e3:
            ec = st.selectbox("Currency", ["\u20b9", "$", "\u20ac", "\u00a3"], index=0)
            st.markdown("<div style='height:1.7rem;'></div>", unsafe_allow_html=True)
            if st.button("Save Changes", type="primary", use_container_width=True):
                up = ds.update_user_profile({'name': en, 'email': ee, 'monthly_income': ei, 'monthly_budget': eb, 'preferred_currency': ec})
                st.session_state.user_profile = up
                st.session_state.edit_profile = False
                st.success("Profile updated!")
                st.rerun()


# ============================================================
# SETTINGS
# ============================================================
def render_settings(df):
    st.markdown("<h1>Settings</h1>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Application preferences.</div>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown("### Preferences")
        st.selectbox("Currency", ["\u20b9 (INR)", "$ (USD)", "\u20ac (EUR)", "\u00a3 (GBP)"])
        st.selectbox("Date Format", ["YYYY-MM-DD", "DD/MM/YYYY"])
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("### Notifications")
        st.checkbox("Budget limit alerts", value=True)
        st.checkbox("Unusual spending alerts", value=True)
        st.checkbox("Recurring payment reminders", value=True)
    with s2:
        st.markdown("### Data Management")
        exp = df[['Date', 'Category', 'Amount', 'Payment Method', 'Description']].copy()
        exp['Date'] = exp['Date'].dt.strftime('%Y-%m-%d')
        st.download_button("Export All Data (CSV)", exp.to_csv(index=False).encode('utf-8'), "smartspend_export.csv", "text/csv", use_container_width=True)
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("### Privacy & Security")
        st.markdown('<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:1rem;font-size:0.88rem;color:#475569;">All calculations run locally. No data is sent to external servers.</div>', unsafe_allow_html=True)


# ============================================================
# MAIN
# ============================================================
def main():
    if not st.session_state.authenticated:
        render_landing_page()
    else:
        df = ds.load_transactions()
        render_sidebar(df)
        p = st.session_state.active_page
        if p == "Dashboard":
            render_dashboard(df)
        elif p == "Transactions":
            render_transactions(df)
        elif p == "Spending":
            render_spending(df)
        elif p == "Forecast":
            render_forecast(df)
        elif p == "Alerts":
            render_alerts(df)
        elif p == "Goals":
            render_goals()
        elif p == "What-If":
            render_whatif(df)
        elif p == "Ask SmartSpend":
            render_ask(df)
        elif p == "Profile":
            render_profile()
        elif p == "Settings":
            render_settings(df)
        else:
            render_dashboard(df)

if __name__ == "__main__":
    main()
'''

with open(os.path.join(os.path.dirname(__file__), 'app.py'), 'w', encoding='utf-8') as f:
    f.write(APP_CODE)
print("app.py written successfully!")
