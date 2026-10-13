# styles.py — SmartSpend AI Executive Blue Fintech Theme

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Complete removal of Streamlit default Header, Toolbar, Decoration and Deploy button */
    header, [data-testid="stHeader"], .stAppDeployButton, [data-testid="stAppDeployButton"], 
    [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0F172A;
        -webkit-font-smoothing: antialiased;
    }

    /* Executive Blue UI Background - Rich, Crisp, Modern Fintech Blue */
    .stApp {
        background-color: #EBF4FC !important;
        background-image: 
            radial-gradient(at 0% 0%, #DBEAFE 0px, transparent 55%),
            radial-gradient(at 100% 100%, #BFDBFE 0px, transparent 50%),
            radial-gradient(at 50% 25%, #E2F0FD 0px, transparent 65%) !important;
        background-attachment: fixed !important;
    }

    /* Top padding correction to eliminate extra space gap */
    .main .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px !important;
    }

    /* Headings & Typography */
    h1 {
        color: #1E3A8A;
        font-weight: 800;
        letter-spacing: -0.035em;
        font-size: 2rem;
        margin-bottom: 0.2rem;
        margin-top: 0 !important;
    }
    h2 {
        color: #1E40AF;
        font-weight: 700;
        letter-spacing: -0.025em;
        font-size: 1.45rem;
    }
    h3 {
        color: #1E3A8A;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    h4 {
        color: #334155;
        font-weight: 600;
        font-size: 1.05rem;
    }

    .page-subtitle {
        color: #64748B;
        font-size: 0.98rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* Polished, Elevated White Surface Cards */
    .surface-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.4rem 1.65rem;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
        margin-bottom: 1rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    }
    .surface-card:hover {
        border-color: #BFDBFE;
        box-shadow: 0 8px 26px -4px rgba(37, 99, 235, 0.08);
    }

    /* Metric KPI Cards with Top Accent & Click Interaction */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #2563EB;
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05);
        margin-bottom: 0.85rem;
        transition: all 0.2s ease;
    }
    .metric-card.active-kpi {
        border: 2px solid #2563EB !important;
        border-top: 4px solid #1D4ED8 !important;
        background: #F8FAFC !important;
        box-shadow: 0 10px 28px -4px rgba(37, 99, 235, 0.15) !important;
        transform: translateY(-2px);
    }
    .metric-card.income { border-top-color: #0284C7; }
    .metric-card.spent  { border-top-color: #2563EB; }
    .metric-card.saved  { border-top-color: #059669; }
    .metric-card.budget { border-top-color: #10B981; }
    .metric-card.alert  { border-top-color: #DC2626; }

    .metric-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 0.35rem;
    }

    /* Structured Detail Drawer on Metric Click */
    .detail-drawer {
        background: #FFFFFF;
        border: 1.5px solid #BFDBFE;
        border-radius: 16px;
        padding: 1.4rem 1.65rem;
        box-shadow: 0 8px 26px -4px rgba(37, 99, 235, 0.1);
        margin-bottom: 1.4rem;
    }
    .detail-drawer-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #EFF6FF;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
    }
    .detail-drawer-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #1E3A8A;
    }

    /* Budget Progress Box */
    .budget-section {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.4rem 1.65rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05);
    }
    .budget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    /* Badges & Status Indicators */
    .badge {
        display: inline-block;
        padding: 0.32rem 0.85rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-success { background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }
    .badge-warning { background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }
    .badge-danger  { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
    .badge-neutral { background: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; }
    .badge-blue    { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }

    /* Category Spending Bar */
    .cat-row { margin-bottom: 0.85rem; }
    .cat-meta { display: flex; justify-content: space-between; margin-bottom: 0.35rem; }
    .cat-name { font-size: 0.92rem; font-weight: 600; color: #1E293B; }
    .cat-amount { font-size: 0.92rem; font-weight: 700; color: #0F172A; }
    .cat-bar-bg { background: #E2E8F0; border-radius: 8px; height: 10px; overflow: hidden; }
    .cat-bar-fill { height: 100%; border-radius: 8px; transition: width 0.3s ease; }

    /* Trajectory Visual Cards for Forecast */
    .trajectory-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.15rem 1.3rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .trajectory-card:hover {
        border-color: #93C5FD;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.08);
    }
    .trajectory-period {
        font-weight: 700;
        font-size: 0.96rem;
        color: #1E293B;
    }
    .trajectory-amount {
        font-weight: 800;
        font-size: 1.15rem;
        color: #0F172A;
    }

    /* Scenario Executive Gradient Box */
    .scenario-gradient-card {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        color: #FFFFFF;
        box-shadow: 0 10px 26px -4px rgba(37, 99, 235, 0.3);
        margin-bottom: 1.2rem;
    }
    .scenario-gradient-label {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #BFDBFE;
        margin-bottom: 0.3rem;
    }
    .scenario-gradient-val {
        font-size: 2.1rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .scenario-gradient-sub {
        font-size: 0.88rem;
        color: #DBEAFE;
        margin-top: 0.35rem;
    }

    /* Insight Banner */
    .insight-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4.5px solid #2563EB;
        border-radius: 0 12px 12px 0;
        padding: 0.95rem 1.25rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }
    .insight-item.warn { border-left-color: #D97706; }
    .insight-item.good { border-left-color: #059669; }
    .insight-item.danger { border-left-color: #DC2626; }

    /* Alert Banner */
    .alert-banner {
        background: #FFFFFF;
        border: 1px solid #FED7AA;
        border-left: 4.5px solid #EA580C;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.3rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(234, 88, 12, 0.05);
    }
    .alert-banner.danger {
        border-color: #FECACA;
        border-left-color: #DC2626;
    }

    /* Transaction Row */
    .txn-item {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 0.85rem 1.2rem;
        margin-bottom: 0.55rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.02);
    }

    /* AI Response Card */
    .ai-response-card {
        background: #FFFFFF;
        border: 1.5px solid #BFDBFE;
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-top: 1rem;
        box-shadow: 0 6px 22px rgba(37, 99, 235, 0.08);
    }
    .ai-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 0.85rem;
        font-weight: 700;
        color: #1E3A8A;
        font-size: 1.02rem;
    }
    .ai-body {
        color: #334155;
        line-height: 1.7;
        font-size: 0.96rem;
    }
    .ai-suggestion {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 12px;
        padding: 0.95rem 1.25rem;
        margin-top: 1.1rem;
        color: #1E40AF;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    /* Empty state */
    .empty-state-box {
        background: #FFFFFF;
        border: 2px dashed #CBD5E1;
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 1.25rem;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
    }
    .empty-state-title { font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-bottom: 0.4rem; }
    .empty-state-desc { font-size: 0.94rem; color: #64748B; margin-bottom: 1.35rem; }

    /* Executive High-Contrast Buttons */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.92rem;
        padding: 0.5rem 1.25rem;
        transition: all 0.15s ease;
        border: 1px solid #CBD5E1;
        background-color: #FFFFFF;
        color: #0F172A;
    }
    div.stButton > button:hover {
        border-color: #2563EB;
        background-color: #EFF6FF;
        color: #1D4ED8;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28);
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
        border-color: #1E40AF !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.38);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F0F6FC !important;
        border-right: 1.5px solid #BFDBFE !important;
        box-shadow: 2px 0 16px rgba(37, 99, 235, 0.08) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.88rem;
    }
    section[data-testid="stSidebar"] div.stButton > button {
        background-color: #FFFFFF !important;
        border: 1px solid #BFDBFE !important;
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background-color: #DBEAFE !important;
        border-color: #2563EB !important;
        color: #1D4ED8 !important;
    }
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    /* Landing Container */
    .landing-container {
        text-align: center;
        padding: 3.5rem 1rem 2.5rem;
        max-width: 740px;
        margin: 0 auto;
    }
    .landing-brand {
        font-size: 1.05rem;
        font-weight: 800;
        color: #2563EB;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.85rem;
    }
    .landing-headline {
        font-size: 3rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.15;
        letter-spacing: -0.035em;
        margin-bottom: 1.2rem;
    }
    .landing-sub {
        font-size: 1.15rem;
        color: #475569;
        line-height: 1.65;
        margin-bottom: 2.5rem;
    }

    /* Streamlit Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #2563EB 0%, #059669 100%);
    }

    /* Prevent any accidental pre/code rendering */
    pre, code {
        background: transparent !important;
    }
</style>
"""
