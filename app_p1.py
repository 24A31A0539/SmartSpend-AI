# app.py Part 1
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import data_service as ds
from styles import CUSTOM_CSS

st.set_page_config(
    page_title="SmartSpend AI | Personal Financial Intelligence",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = ds.get_user_profile()
if 'active_page' not in st.session_state:
    st.session_state.active_page = 'Dashboard'
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = 'September 2026'
if 'ask_question_input' not in st.session_state:
    st.session_state.ask_question_input = ''

user = st.session_state.user_profile
curr = user.get('preferred_currency', '₹')

def get_greeting(name):
    hour = datetime.now().hour
    if 5 <= hour < 12:
        part = "Good morning"
    elif 12 <= hour < 17:
        part = "Good afternoon"
    else:
        part = "Good evening"
    return f"{part}, {name}"

def navigate_to(page_name):
    st.session_state.active_page = page_name
    st.rerun()

def render_landing_page():
    nav_col1, nav_col2, nav_col3 = st.columns([4, 4, 3])
    with nav_col1:
        st.markdown("### 💰 **SmartSpend AI**")
    with nav_col3:
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("Sign In", use_container_width=True):
                st.session_state.show_login_modal = True
        with btn_c2:
            if st.button("Get Started", type="primary", use_container_width=True):
                st.session_state.show_login_modal = True

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-hero">
        <div class="landing-title">Understand your spending.<br>Plan your money better.</div>
        <div class="landing-desc">
            SmartSpend AI helps you track your spending, understand your financial habits,
            plan future expenses, and work toward your savings goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1, 1.5])
    with c_btn2:
        if st.button("⚡ Explore Demo Account", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_profile = ds.get_user_profile()
            st.rerun()

    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 1.5rem; color: #0f172a;'>Designed for clarity and peace of mind</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
            <div class="landing-feature-title">Track your money</div>
            <div class="landing-feature-desc">See your income, spending, and savings at a single glance with zero clutter.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎯</div>
            <div class="landing-feature-title">Stay within budget</div>
            <div class="landing-feature-desc">Know exactly how much budget remains this month and prevent surprise overruns.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💡</div>
            <div class="landing-feature-title">Understand spending</div>
            <div class="landing-feature-desc">Instantly identify where your money goes across essential and discretionary categories.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏆</div>
            <div class="landing-feature-title">Track savings goals</div>
            <div class="landing-feature-desc">Set realistic milestones for travel, emergency funds, and major purchases.</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🔮</div>
            <div class="landing-feature-title">Plan ahead</div>
            <div class="landing-feature-desc">Receive reliable next-month spending forecasts based on your actual spending history.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="landing-feature-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💬</div>
            <div class="landing-feature-title">Get answers instantly</div>
            <div class="landing-feature-desc">Ask natural questions about your finances and receive immediate, data-backed answers.</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.get('show_login_modal', False):
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Sign in to SmartSpend AI</h3>", unsafe_allow_html=True)
        l_c1, l_c2, l_c3 = st.columns([1, 1, 1])
        with l_c2:
            u_name = st.text_input("Username", value="janaganika")
            u_pass = st.text_input("Password", value="password123", type="password")
            if st.button("Continue to Dashboard", type="primary", use_container_width=True):
                st.session_state.authenticated = True
                st.session_state.user_profile = ds.get_user_profile()
                st.rerun()

def render_sidebar(df):
    st.sidebar.markdown("### 💰 **SmartSpend AI**")
    st.sidebar.caption("Personal Financial Intelligence")
    st.sidebar.markdown("---")

    available_months = ds.get_available_months(df)
    if st.session_state.selected_month not in available_months and available_months:
        st.session_state.selected_month = available_months[0]
    
    st.sidebar.markdown("<p style='font-size:0.75rem; font-weight:600; color:#64748b; margin-bottom:2px;'>CURRENT PERIOD</p>", unsafe_allow_html=True)
    st.session_state.selected_month = st.sidebar.selectbox(
        "Period",
        options=available_months,
        index=available_months.index(st.session_state.selected_month) if st.session_state.selected_month in available_months else 0,
        label_visibility="collapsed"
    )
    st.sidebar.markdown("---")

    pages = [
        ("HOME", ["Dashboard"]),
        ("MONEY", ["Transactions", "Spending"]),
        ("PLAN", ["Goals", "What-If"]),
        ("INSIGHTS", ["Forecast", "Alerts", "Ask SmartSpend"]),
        ("ACCOUNT", ["Profile", "Settings"])
    ]

    for section, page_list in pages:
        st.sidebar.markdown(f"<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; letter-spacing:0.05em; margin-top:0.6rem; margin-bottom:0.2rem;'>{section}</p>", unsafe_allow_html=True)
        for p in page_list:
            is_active = (st.session_state.active_page == p)
            btn_label = f"▸ {p}" if is_active else f"  {p}"
            btn_type = "primary" if is_active else "secondary"
            if st.sidebar.button(btn_label, key=f"nav_{p}", type=btn_type, use_container_width=True):
                st.session_state.active_page = p
                st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **{user.get('name', 'User')}**")
    st.sidebar.caption(f"{user.get('email', '')}")
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

def render_dashboard(df):
    selected_month = st.session_state.selected_month
    kpis = ds.calculate_kpis(df, selected_month, user)
    
    st.markdown(f"<h1>{get_greeting(user.get('name', 'Janaganika'))}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='page-subtitle'>Here's your financial summary for <strong>{selected_month}</strong>.</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-card-title">Income</div>
            <div class="summary-card-value">{curr}{kpis['income']:,.0f}</div>
            <div class="summary-card-sub">Monthly credit</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-card-title">Spent</div>
            <div class="summary-card-value" style="color:#0f172a;">{curr}{kpis['spent']:,.0f}</div>
            <div class="summary-card-sub">{selected_month}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-card-title">Saved</div>
            <div class="summary-card-value" style="color:#059669;">{curr}{kpis['saved']:,.0f}</div>
            <div class="summary-card-sub">Net surplus</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-card-title">Budget Remaining</div>
            <div class="summary-card-value" style="color:{'#059669' if kpis['budget_remaining']>=0 else '#dc2626'};">{curr}{kpis['budget_remaining']:,.0f}</div>
            <div class="summary-card-sub">Available</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    badge_class = f"badge-{kpis['status_type']}"
    st.markdown(f"""
    <div class="budget-box">
        <div class="budget-header">
            <div>
                <span style="font-weight: 600; font-size: 1.05rem; color: #0f172a;">Monthly Budget</span>
                <span style="margin-left: 0.75rem; color: #64748b; font-size: 0.9rem;">{curr}{kpis['spent']:,.0f} of {curr}{kpis['budget']:,.0f} used</span>
            </div>
            <div>
                <span class="badge {badge_class}">{kpis['status']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(float(kpis['budget_pct'] / 100.0))
    st.caption(f"{round(kpis['budget_pct'])}% used • {curr}{kpis['budget_remaining']:,.0f} remaining")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### Where your money goes")
        cat_breakdown = ds.get_category_breakdown(df, selected_month)
        
        if not cat_breakdown.empty:
            fig, ax = plt.subplots(figsize=(6, 2.8))
            fig.patch.set_facecolor('#ffffff')
            ax.set_facecolor('#ffffff')
            
            categories = cat_breakdown.index.tolist()[:5]
            values = cat_breakdown.values.tolist()[:5]
            colors = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1']
            
            y_pos = np.arange(len(categories))
            ax.barh(y_pos, values, color=colors[:len(categories)], height=0.55, edgecolor='none')
            ax.set_yticks(y_pos)
            ax.set_yticklabels(categories, fontsize=9.5, color='#1e293b')
            ax.invert_yaxis()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#e2e8f0')
            ax.tick_params(axis='x', colors='#64748b', labelsize=8.5)
            ax.xaxis.grid(True, linestyle='--', alpha=0.5, color='#e2e8f0')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            st.markdown("<div style='margin-top: 0.5rem;'>", unsafe_allow_html=True)
            for c_name, c_amt in cat_breakdown.head(5).items():
                st.markdown(f"<span style='color:#334155;'><strong>{c_name}</strong> — {curr}{c_amt:,.0f}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button("View spending →", key="dash_view_spending"):
                navigate_to("Spending")
        else:
            st.info("No spending recorded for this month.")

    with col_right:
        st.markdown("### Things to know")
        insights = ds.get_insights(df, selected_month, user)
        for item in insights:
            border_type = "insight-item-warning" if item.get('type') == 'warning' else "insight-item-success" if item.get('type') == 'success' else "insight-item"
            st.markdown(f"""
            <div class="insight-item {border_type}">
                <div style="font-weight: 600; font-size: 0.95rem; color: #0f172a; margin-bottom: 2px;">{item['title']}</div>
                <div style="font-size: 0.88rem; color: #475569;">{item['text']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        st.markdown("### Needs your attention")
        anomalies = ds.detect_sensible_anomalies(df, selected_month)
        if not anomalies:
            anomalies = ds.detect_sensible_anomalies(df, None)
            
        if anomalies:
            top_a = anomalies[0]
            st.markdown(f"""
            <div class="alert-card">
                <div style="font-weight: 600; color: #991b1b; font-size: 0.92rem;">Unusual {top_a['category']} expense</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 2px 0;">{curr}{top_a['amount']:,.0f}</div>
                <div style="font-size: 0.82rem; color: #64748b;">Typical {top_a['category']} expense is ~{curr}{top_a['typical_amount']:,.0f} • {top_a['date']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Review transaction →", key="dash_review_anomaly"):
                navigate_to("Alerts")
        else:
            st.markdown("""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.75rem 1rem; color:#64748b; font-size:0.88rem;">
                ✅ You're all caught up. No unusual spending detected.
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    c_txns, c_goal = st.columns([1.3, 1])

    with c_txns:
        st.markdown("### Recent transactions")
        month_df = ds.get_month_data(df, selected_month)
        recent = month_df.head(5) if not month_df.empty else df.head(5)
        
        if not recent.empty:
            display_recent = recent[['Date', 'Description', 'Category', 'Amount']].copy()
            display_recent['Date'] = display_recent['Date'].dt.strftime('%d %b')
            display_recent['Amount'] = display_recent['Amount'].apply(lambda x: f"{curr}{x:,.0f}")
            st.dataframe(
                display_recent,
                use_container_width=True,
                hide_index=True
            )
            if st.button("View all transactions →", key="dash_view_all_txns"):
                navigate_to("Transactions")
        else:
            st.info("No transactions found.")

    with c_goal:
        st.markdown("### Savings Goal")
        goals = ds.get_savings_goals()
        if goals:
            primary_goal = goals[0]
            pct = round((primary_goal['current_amount'] / primary_goal['target_amount']) * 100)
            rem_goal = max(0.0, primary_goal['target_amount'] - primary_goal['current_amount'])
            st.markdown(f"""
            <div class="goal-card">
                <div style="font-weight: 600; font-size: 1.05rem; color: #0f172a;">{primary_goal['name']}</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #2563eb; margin: 4px 0;">
                    {curr}{primary_goal['current_amount']:,.0f} <span style="font-size: 0.85rem; font-weight: normal; color: #64748b;">/ {curr}{primary_goal['target_amount']:,.0f}</span>
                </div>
                <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 0.5rem;">
                    {pct}% complete • {curr}{rem_goal:,.0f} remaining • Target: {primary_goal['target_date']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(float(min(100, pct) / 100.0))
            if st.button("View goal →", key="dash_view_goal"):
                navigate_to("Goals")
        else:
            st.markdown("""
            <div class="goal-card">
                <div style="font-weight: 600; color: #0f172a;">Start a savings goal</div>
                <div style="font-size: 0.85rem; color: #64748b; margin: 4px 0 0.75rem 0;">Set a target and track your progress toward your dreams.</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create goal", key="dash_create_goal"):
                navigate_to("Goals")
