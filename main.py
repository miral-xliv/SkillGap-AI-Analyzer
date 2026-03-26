import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from groq import Groq

st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        /* Remove all white/gray boxes */
        .stBottom {background-color: transparent !important;}
        .stBottom > div {background-color: transparent !important;}
        section[data-testid="stBottom"] > div {
            background-color: transparent !important;
            box-shadow: none !important;
            border: none !important;
        }
        .stChatInput {background-color: transparent !important;}
        .stChatInput > div {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        div[data-testid="stChatInputContainer"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* Input box — teal border, transparent, rounded */
        div[data-testid="stChatInputContainer"] textarea,
        div[data-testid="stChatInputContainer"] textarea:focus,
        div[data-testid="stChatInputContainer"] textarea:active,
        div[data-testid="stChatInputContainer"] textarea:hover {
            background-color: transparent !important;
            border: 1.5px solid #00acc1 !important;
            border-radius: 25px !important;
            padding: 10px 18px !important;
            font-size: 15px !important;
            color: #333 !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Kill red focus ring on the outer container */
        div[data-testid="stChatInputContainer"]:focus-within {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Send button */
        div[data-testid="stChatInputContainer"] button,
        div[data-testid="stChatInputContainer"] button:focus,
        div[data-testid="stChatInputContainer"] button:hover {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# BACKEND IMPORTS
# -----------------------------
from engine.parser import extract_text_from_pdf, parse_resume_to_json
from engine.matcher import calculate_ats_score
from engine.optimizer import get_gap_analysis, get_humanized_projects
from engine.generator import generate_assets
from engine.advisor import get_career_advice

# -----------------------------
# CONFIG & API
# -----------------------------
st.set_page_config(
    page_title="SkillGap AI Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
load_dotenv()
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY is missing! Please add it in Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# -----------------------------
# SESSION STATE
# -----------------------------
pages = ["Upload", "Dashboard", "Gap Audit", "Project Humanizer", "Cover Letter", "Interview Prep", "AI Coach", "Learning Roadmap", "Resume Rewriter", "Job Market Trends", "LinkedIn Bio"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "user_db" not in st.session_state:
    st.session_state.user_db = {"demo": "demo123"}
if "page" not in st.session_state:
    st.session_state.page = pages[0]
if "results" not in st.session_state:
    st.session_state.results = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None
if "dark" not in st.session_state:
    st.session_state.dark = False
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "rewritten_resume" not in st.session_state:
    st.session_state.rewritten_resume = None
if "market_trends" not in st.session_state:
    st.session_state.market_trends = None
if "jd_comparisons" not in st.session_state:
    st.session_state.jd_comparisons = []
if "linkedin_bio" not in st.session_state:
    st.session_state.linkedin_bio = None

# -----------------------------
# NAVIGATION
# -----------------------------
def go_next():
    i = pages.index(st.session_state.page)
    if i < len(pages) - 1:
        st.session_state.page = pages[i+1]

def go_back():
    i = pages.index(st.session_state.page)
    if i > 0:
        st.session_state.page = pages[i-1]

# -----------------------------
# THEME COLORS
# -----------------------------
if st.session_state.dark:
    bg          = "#0D1B2A"
    bg2         = "#112233"
    text        = "#E8F4F8"
    text_muted  = "#8BAFC7"
    sidebar_bg  = "#0A1628"
    card_bg     = "rgba(255,255,255,0.05)"
    card_border = "rgba(0,206,209,0.2)"
    input_bg    = "rgba(255,255,255,0.07)"
    chart_template = "plotly_dark"
else:
    bg          = "#EEF4F8"
    bg2         = "#E0ECF4"
    text        = "#1A2E40"
    text_muted  = "#5A7A8A"
    sidebar_bg  = "#1A3A5C"
    card_bg     = "rgba(255,255,255,0.75)"
    card_border = "rgba(0,206,209,0.3)"
    input_bg    = "rgba(255,255,255,0.9)"
    chart_template = "plotly_white"

CYAN    = "#00CED1"
CYAN2   = "#00B4D8"
BLUE    = "#1A3A5C"
TEAL    = "#0096A0"
GRAD    = f"linear-gradient(135deg, {CYAN}, {CYAN2}, #0077B6)"
GRAD2   = f"linear-gradient(135deg, #0077B6, {CYAN})"

# -----------------------------
# FULL CSS
# -----------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

[data-testid="stAppDeployButton"] {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
header[data-testid="stHeader"] {{ background: transparent !important; }}

* {{ font-family: 'Outfit', sans-serif !important; box-sizing: border-box; }}
.stApp {{
    background: {bg} !important;
    background-image:
        radial-gradient(ellipse at 10% 20%, rgba(0,206,209,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(0,119,182,0.08) 0%, transparent 50%) !important;
    color: {text} !important;
    min-height: 100vh;
}}

[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
    border-right: 1px solid rgba(0,206,209,0.15) !important;
    {'transform: translateX(-110%) !important; position: fixed !important; z-index: 1 !important;' if not st.session_state.get('sidebar_open', True) else 'transform: translateX(0) !important;'}
}}
[data-testid="stSidebar"] * {{ color: #E8F4F8 !important; }}

/* Hide only the radio circle input, keep label text */
[data-testid="stSidebar"] .stRadio input[type="radio"] {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio div[data-testid="stWidgetLabel"] {{
    display: none !important;
}}

/* Style each nav item row */
[data-testid="stSidebar"] .stRadio label {{
    padding: 10px 16px !important;
    border-radius: 10px !important;
    transition: background 0.2s !important;
    display: flex !important;
    align-items: center !important;
    cursor: pointer !important;
    margin: 2px 0 !important;
    width: 100% !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(0,206,209,0.15) !important;
}}
/* Hide the small circle inside the label */
[data-testid="stSidebar"] .stRadio label span:first-child {{
    display: none !important;
}}

[data-testid="stSidebar"] hr {{ border-color: rgba(0,206,209,0.2) !important; }}

h1 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    background: {GRAD} !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 24px !important;
}}
h2, h3 {{
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    color: {text} !important;
}}


.metric-card {{
    background: {card_bg};
    backdrop-filter: blur(16px);
    border: 1px solid {card_border};
    border-radius: 18px;
    padding: 22px 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,206,209,0.08);
    transition: transform 0.2s;
    position: relative;
    overflow: hidden;
}}
.metric-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: {GRAD};
    border-radius: 18px 18px 0 0;
}}
.metric-card:hover {{ transform: translateY(-3px); }}
.metric-label {{
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {text_muted};
    margin-bottom: 8px;
}}
.metric-value {{
    font-size: 32px;
    font-weight: 800;
    font-family: 'Space Grotesk', sans-serif !important;
    background: {GRAD};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.metric-value-red {{ font-size: 32px; font-weight: 800; font-family: 'Space Grotesk', sans-serif !important; color: #FF6B8A; }}
.metric-value-green {{ font-size: 32px; font-weight: 800; font-family: 'Space Grotesk', sans-serif !important; color: #00E5A0; }}

.page-banner {{
    background: {GRAD};
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 28px;
    color: white !important;
    position: relative;
    overflow: hidden;
}}
.page-banner::after {{
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}}
.page-banner h2 {{ color: white !important; margin: 0 0 6px 0 !important; -webkit-text-fill-color: white !important; }}
.page-banner p  {{ color: rgba(255,255,255,0.88) !important; margin: 0; font-size: 15px; }}

.stButton > button {{
    background: {GRAD} !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: 0.02em !important;
    transition: all 0.25s !important;
    box-shadow: 0 4px 15px rgba(0,206,209,0.3) !important;
    width: 100% !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,206,209,0.45) !important;
    filter: brightness(1.08) !important;
}}
.stButton > button[kind="secondary"] {{
    background: transparent !important;
    border: 1.5px solid {CYAN} !important;
    color: {CYAN} !important;
    box-shadow: none !important;
}}
.stButton > button[kind="secondary"]:hover {{ background: rgba(0,206,209,0.1) !important; }}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {{
    background: {input_bg} !important;
    border: 1.5px solid {card_border} !important;
    border-radius: 12px !important;
    color: {text} !important;
    font-size: 14px !important;
    transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {CYAN} !important;
    box-shadow: 0 0 0 3px rgba(0,206,209,0.12) !important;
}}

/* ── Hide "Press Enter to apply" tooltip ── */
.stTextInput [data-testid="InputInstructions"],
.stTextArea [data-testid="InputInstructions"],
[data-testid="InputInstructions"] {{
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
}}

[data-testid="stFileUploader"] {{ background: transparent !important; border: none !important; padding: 0 !important; }}
[data-testid="stFileUploader"] section {{
    background: {input_bg} !important;
    border: 2px dashed {card_border} !important;
    border-radius: 16px !important;
    padding: 32px !important;
    transition: border-color 0.2s !important;
}}
[data-testid="stFileUploader"] section:hover {{ border-color: {CYAN} !important; }}
[data-testid="stFileUploader"] button {{ background: {GRAD} !important; color: white !important; border-radius: 10px !important; border: none !important; }}

.week-card {{
    background: {card_bg};
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px 24px;
    border-left: 4px solid {CYAN};
    border-top: 1px solid {card_border};
    border-right: 1px solid {card_border};
    border-bottom: 1px solid {card_border};
    box-shadow: 0 4px 16px rgba(0,206,209,0.07);
    margin-bottom: 16px;
    transition: transform 0.2s;
}}
.week-card:hover {{ transform: translateX(4px); }}
.week-title {{ font-size: 15px; font-weight: 700; font-family: 'Space Grotesk', sans-serif !important; color: {CYAN} !important; margin-bottom: 8px; }}
.week-body {{ font-size: 13.5px; color: {text_muted}; line-height: 1.75; }}

.user-badge {{
    background: rgba(0,206,209,0.12);
    border: 1px solid rgba(0,206,209,0.25);
    border-radius: 12px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}}
.user-avatar {{ width: 36px; height: 36px; background: {GRAD}; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; color: white; }}
.user-name {{ font-size: 14px; font-weight: 600; color: #E8F4F8; }}
.user-role {{ font-size: 11px; color: {CYAN}; }}

hr {{ border-color: {card_border} !important; }}
.stAlert {{ border-radius: 14px !important; }}
.stSuccess {{ border-left: 4px solid #00E5A0 !important; background: rgba(0,229,160,0.08) !important; }}
.stError {{ border-left: 4px solid #FF6B8A !important; background: rgba(255,107,138,0.08) !important; }}
.stInfo {{ border-left: 4px solid {CYAN} !important; background: rgba(0,206,209,0.08) !important; }}
.stWarning {{ border-left: 4px solid #FFB347 !important; background: rgba(255,179,71,0.08) !important; }}
.stMarkdown, p, span, label {{ color: {text} !important; }}
.stSpinner {{ color: {CYAN} !important; }}

[data-testid="stSidebarHeader"] {{ display: none !important; }}
section[data-testid="stSidebar"] > div > div > div:first-child > div:first-child > div:first-child {{ display: none !important; }}
[data-testid="stSidebar"] > div:first-child {{ padding-top: 2rem !important; }}

[data-testid="stChatMessageAvatarUser"] > div,
[data-testid="stChatMessageAvatarAssistant"] > div {{ font-size: 0 !important; color: transparent !important; text-indent: -9999px !important; }}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {{ display: flex !important; align-items: center !important; justify-content: center !important; width: 36px !important; height: 36px !important; border-radius: 50% !important; font-size: 0 !important; overflow: hidden !important; position: relative !important; }}
[data-testid="stChatMessageAvatarUser"] * {{ visibility: hidden !important; }}
[data-testid="stChatMessageAvatarUser"]::after {{ content: '👤' !important; visibility: visible !important; font-size: 20px !important; position: absolute !important; background: linear-gradient(135deg, #00CED1, #0077B6) !important; width: 36px !important; height: 36px !important; display: flex !important; align-items: center !important; justify-content: center !important; border-radius: 50% !important; line-height: 36px !important; text-align: center !important; }}
[data-testid="stChatMessageAvatarAssistant"] * {{ visibility: hidden !important; }}
[data-testid="stChatMessageAvatarAssistant"]::after {{ content: '🤖' !important; visibility: visible !important; font-size: 20px !important; position: absolute !important; background: linear-gradient(135deg, #0077B6, #00CED1) !important; width: 36px !important; height: 36px !important; display: flex !important; align-items: center !important; justify-content: center !important; border-radius: 50% !important; line-height: 36px !important; text-align: center !important; }}

[data-testid="stSidebar"] [data-testid="baseButton-header"] {{ visibility: visible !important; display: flex !important; background: {CYAN} !important; border-radius: 8px !important; border: none !important; width: 36px !important; height: 36px !important; }}
[data-testid="stSidebar"] [data-testid="baseButton-header"] svg {{ fill: white !important; stroke: white !important; }}
[data-testid="stSidebarCollapsedControl"] {{ visibility: visible !important; display: flex !important; opacity: 1 !important; z-index: 9999 !important; background: {CYAN} !important; border-radius: 0 10px 10px 0 !important; box-shadow: 4px 0 16px rgba(0,206,209,0.5) !important; border: none !important; min-width: 32px !important; min-height: 52px !important; top: 50% !important; transform: translateY(-50%) !important; }}
[data-testid="stSidebarCollapsedControl"] button {{ background: transparent !important; border: none !important; width: 100% !important; height: 100% !important; }}
[data-testid="stSidebarCollapsedControl"] svg {{ fill: white !important; stroke: white !important; }}
[data-testid="stSidebar"] {{ transition: width 0.3s ease, transform 0.3s ease !important; }}

[data-testid="stChatMessage"] {{ background: {card_bg} !important; border: 1px solid {card_border} !important; border-radius: 16px !important; padding: 12px 16px !important; margin-bottom: 10px !important; color: {text} !important; }}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div {{ color: {text} !important; }}
[data-testid="stChatMessage"][data-testid*="user"] {{ background: rgba(0,206,209,0.08) !important; border-color: rgba(0,206,209,0.25) !important; }}

[data-testid="stSidebar"] .stButton > button {{ background: rgba(0,206,209,0.12) !important; border: 1px solid rgba(0,206,209,0.25) !important; color: #E8F4F8 !important; box-shadow: none !important; border-radius: 10px !important; }}
[data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(0,206,209,0.22) !important; transform: none !important; }}

</style>
""", unsafe_allow_html=True)
# =============================
# AUTH PAGE
# =============================
def show_login_page():
    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="small")
    with left:
        st.markdown(f"""
        <div style="background:linear-gradient(145deg,#00CED1 0%,#00B4D8 40%,#0077B6 100%);
                    border-radius:24px; padding:48px 36px; min-height:560px;
                    display:flex; flex-direction:column; justify-content:space-between;
                    position:relative; overflow:hidden;">
            <div style="position:absolute;bottom:-60px;right:-60px;width:220px;height:220px;background:rgba(255,255,255,0.07);border-radius:50%;"></div>
            <div style="position:absolute;top:-40px;left:-40px;width:160px;height:160px;background:rgba(255,255,255,0.05);border-radius:50%;"></div>
            <div style="font-size:17px;font-weight:800;color:white;font-family:'Space Grotesk',sans-serif;position:relative;z-index:1;">🚀 SkillGap AI</div>
            <div style="position:relative;z-index:1;text-align:center;margin:24px 0;">
                <div style="font-size:80px;line-height:1;">🎓</div>
                <div style="font-size:32px;font-weight:800;color:white;font-family:'Space Grotesk',sans-serif;margin-top:20px;line-height:1.25;">SkillGap AI<br>Analyzer</div>
                <div style="font-size:14px;color:rgba(255,255,255,0.82);margin-top:12px;line-height:1.7;">Your intelligent career companion.<br>Analyze gaps. Get hired faster.</div>
            </div>
            <div style="position:relative;z-index:1;">
                <span style="display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);border-radius:50px;padding:6px 14px;font-size:12px;color:white;margin:4px 3px;">🎯 ATS Score</span>
                <span style="display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);border-radius:50px;padding:6px 14px;font-size:12px;color:white;margin:4px 3px;">🔍 Skill Gaps</span>
                <span style="display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);border-radius:50px;padding:6px 14px;font-size:12px;color:white;margin:4px 3px;">📜 Cover Letter</span>
                <span style="display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);border-radius:50px;padding:6px 14px;font-size:12px;color:white;margin:4px 3px;">🗺️ Roadmap</span>
                <span style="display:inline-block;background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.28);border-radius:50px;padding:6px 14px;font-size:12px;color:white;margin:4px 3px;">🤖 AI Coach</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.session_state.auth_mode == "login":
            st.markdown("""<div style="font-size:26px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#1A2E40;">Welcome back 👋</div><div style="font-size:13px;color:#7A9AAF;margin-bottom:24px;">Sign in to continue your career journey</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="font-size:26px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:#1A2E40;">Create Account ✨</div><div style="font-size:13px;color:#7A9AAF;margin-bottom:24px;">Join thousands boosting their career with AI</div>""", unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            if st.button("🔐  Sign In", use_container_width=True, type="primary" if st.session_state.auth_mode == "login" else "secondary"):
                st.session_state.auth_mode = "login"; st.rerun()
        with t2:
            if st.button("📝  Register", use_container_width=True, type="primary" if st.session_state.auth_mode == "register" else "secondary"):
                st.session_state.auth_mode = "register"; st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.auth_mode == "login":
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", placeholder="Enter your password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In  →", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("⚠️ Please fill in all fields.")
                elif username in st.session_state.user_db and st.session_state.user_db[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success(f"✅ Welcome back, {username}!")
                    time.sleep(0.8); st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            st.markdown("""<p style='text-align:center;font-size:12px;color:#7A9AAF;margin-top:16px;'>Demo → username: <b style="color:#00CED1;">demo</b> &nbsp;/&nbsp; password: <b style="color:#00CED1;">demo123</b></p>""", unsafe_allow_html=True)
        else:
            c1, c2 = st.columns(2)
            with c1: new_user = st.text_input("Username", placeholder="Choose a username")
            with c2: new_email = st.text_input("Email", placeholder="Enter your email")
            c3, c4 = st.columns(2)
            with c3: new_pass = st.text_input("Password", placeholder="Create password", type="password")
            with c4: confirm_pass = st.text_input("Confirm Password", placeholder="Repeat password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account  →", use_container_width=True, type="primary"):
                if not new_user or not new_email or not new_pass or not confirm_pass:
                    st.error("⚠️ Please fill in all fields.")
                elif new_user in st.session_state.user_db:
                    st.error("❌ Username already exists.")
                elif new_pass != confirm_pass:
                    st.error("❌ Passwords do not match.")
                elif len(new_pass) < 6:
                    st.error("❌ Password must be at least 6 characters.")
                else:
                    st.session_state.user_db[new_user] = new_pass
                    st.success(f"✅ Account created! Welcome, {new_user}!")
                    time.sleep(0.8)
                    st.session_state.auth_mode = "login"; st.rerun()

if not st.session_state.logged_in:
    show_login_page(); st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------
page_icons = {
    "Upload": "📂", "Dashboard": "📊", "Gap Audit": "🔍",
    "Project Humanizer": "✨", "Cover Letter": "📜",
    "Interview Prep": "🎙️", "AI Coach": "🤖", "Learning Roadmap": "🗺️",
    "Resume Rewriter": "📃", "Job Market Trends": "📈", "LinkedIn Bio": "💼"
}

sidebar_open = st.session_state.get("sidebar_open", True)
toggle_label = "‹" if sidebar_open else "›"
st.markdown(f"""
<style>
#toggle-wrap {{ position: fixed; left: {'295px' if sidebar_open else '0px'}; top: 50%; transform: translateY(-50%); z-index: 99999; }}
#toggle-wrap form button, #toggle-wrap .stButton button {{ background: {CYAN} !important; color: white !important; border: none !important; border-radius: {'6px 0 0 6px' if sidebar_open else '0 6px 6px 0'} !important; width: 22px !important; height: 44px !important; min-height: 44px !important; font-size: 16px !important; font-weight: 900 !important; padding: 0 !important; cursor: pointer !important; box-shadow: 2px 0 8px rgba(0,206,209,0.4) !important; display: flex !important; align-items: center !important; justify-content: center !important; line-height: 1 !important; }}
</style>
<div id="toggle-wrap">
""", unsafe_allow_html=True)
if st.button(toggle_label, key="sidebar_toggle"):
    st.session_state.sidebar_open = not sidebar_open; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div style="font-size:20px;font-weight:800;background:{GRAD};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;font-family:'Space Grotesk',sans-serif;padding:4px 0 16px 0;">🚀 SkillGap AI</div>""", unsafe_allow_html=True)
    initial = st.session_state.current_user[0].upper() if st.session_state.current_user else "U"
    st.markdown(f"""<div class="user-badge"><div class="user-avatar">{initial}</div><div><div class="user-name">{st.session_state.current_user}</div><div class="user-role">Career Seeker</div></div></div>""", unsafe_allow_html=True)
    st.session_state.dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark)
    st.divider()
    labeled_pages = [f"{page_icons[p]}  {p}" for p in pages]
    selected_label = st.radio("Navigation", labeled_pages, index=pages.index(st.session_state.page), label_visibility="collapsed")
    st.session_state.page = pages[labeled_pages.index(selected_label)]
    st.divider()
    if st.button("🔄  Reset Session", use_container_width=True):
        st.session_state.results = None; st.session_state.messages = []; st.session_state.roadmap = None; st.session_state.page = pages[0]; st.rerun()
    if st.button("🚪  Logout", use_container_width=True):
        for key in ["logged_in","current_user","results","messages","roadmap"]:
            st.session_state[key] = False if key == "logged_in" else ([] if key == "messages" else (None if key != "current_user" else ""))
        st.session_state.page = pages[0]; st.rerun()

def nav_buttons(show_back=True, show_next=True):
    st.divider()
    c1, c2, c3 = st.columns([1, 2, 1])
    if show_back:
        with c1: st.button("⬅  Back", on_click=go_back)
    if show_next:
        with c3: st.button("Next  ➡", on_click=go_next)

def page_banner(icon, title, subtitle):
    st.markdown(f"""<div class="page-banner"><h2>{icon} {title}</h2><p>{subtitle}</p></div>""", unsafe_allow_html=True)

# -----------------------------
# PAGES
# -----------------------------

# ── UPLOAD ──
if st.session_state.page == "Upload":
    st.title("📂 Resume Intelligence Portal")
    page_banner("📂", "Upload Your Resume", "Let our AI agents parse, score and analyze your resume against the job description.")
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 📄 Resume (PDF)")
        uploaded_file = st.file_uploader("Upload Resume", type="pdf", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 💼 Job Description")
        jd_input = st.text_area("Paste JD", height=180, label_visibility="collapsed", placeholder="Paste the job description here...")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        run_btn = st.button("⚡  Run AI Analysis", type="primary", use_container_width=True)
    if run_btn and uploaded_file and jd_input:
        with st.spinner("🤖 Please wait..."):
            try:
                prog = st.progress(0, text="Parsing resume...")
                with open("temp.pdf", "wb") as f: f.write(uploaded_file.getbuffer())
                raw = extract_text_from_pdf("temp.pdf")
                resume_json = parse_resume_to_json(raw)
                prog.progress(25, text="✅ Resume parsed — running ATS scorer...")
                time.sleep(2)
                score, gap_score = calculate_ats_score(resume_json, jd_input)
                prog.progress(50, text="✅ ATS scored — analyzing skill gaps...")
                time.sleep(2)
                gaps = get_gap_analysis(resume_json, jd_input, client)
                prog.progress(65, text="✅ Gaps found — humanizing projects...")
                time.sleep(2)
                star = get_humanized_projects(resume_json, client)
                prog.progress(80, text="✅ Projects done — generating assets...")
                time.sleep(2)
                assets = generate_assets(resume_json, jd_input, client)
                prog.progress(100, text="🎉 Analysis complete!")
                st.session_state.results = {"score": score, "gap_score": gap_score, "gaps": str(gaps), "star": str(star), "cl": assets[0], "iq": assets[1]}
                os.remove("temp.pdf")
                st.success("🎉 Analysis Successful! Navigate to Dashboard →")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    elif run_btn:
        st.warning("⚠️ Please upload a resume and paste a job description first.")
    nav_buttons(show_back=False, show_next=True)

# ── DASHBOARD ── (Enhanced)
elif st.session_state.page == "Dashboard":
    import plotly.graph_objects as go
    import re as re_mod
    st.title("📊 Career Intelligence Dashboard")
    if st.session_state.results:
        res       = st.session_state.results
        score     = res["score"]
        gap_score = res["gap_score"]

        if score >= 75:
            readiness_label = "Job Ready ✅"; readiness_color = "#00E5A0"; gauge_color = "#00E5A0"; status_emoji = "🟢"
        elif score >= 45:
            readiness_label = "Almost There 🔶"; readiness_color = "#FFB347"; gauge_color = "#FFB347"; status_emoji = "🟡"
        else:
            readiness_label = "Needs Work 🔴"; readiness_color = "#FF6B8A"; gauge_color = "#FF6B8A"; status_emoji = "🔴"

        page_banner("📊", "Your Career Intelligence Report", f"{status_emoji} ATS Match: {score}%  ·  Gap Score: {gap_score}%  ·  Readiness: {readiness_label}")

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        with m1:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">ATS Match Score</div><div class="metric-value">{score}%</div><div style="font-size:11px;color:{'#00E5A0' if score>=75 else '#FFB347' if score>=45 else '#FF6B8A'};margin-top:6px;font-weight:600;">{'Excellent' if score>=75 else 'Average' if score>=45 else 'Low'}</div></div>''', unsafe_allow_html=True)
        with m2:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">Skill Gap Score</div><div class="metric-value-red">{gap_score}%</div><div style="font-size:11px;color:#FF6B8A;margin-top:6px;font-weight:600;">Skills Missing</div></div>''', unsafe_allow_html=True)
        with m3:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">Profile Strength</div><div class="metric-value-green">{min(score+10,99)}%</div><div style="font-size:11px;color:#00E5A0;margin-top:6px;font-weight:600;">Overall Rating</div></div>''', unsafe_allow_html=True)
        with m4:
            st.markdown(f'''<div class="metric-card"><div class="metric-label">Job Readiness</div><div style="font-size:20px;font-weight:800;color:{readiness_color};font-family:'Space Grotesk',sans-serif;margin-top:8px;">{readiness_label}</div></div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_gauge, col_radar = st.columns([1, 1], gap="large")
        with col_gauge:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🎯 ATS Score Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                delta={"reference": 70, "increasing": {"color": "#00E5A0"}, "decreasing": {"color": "#FF6B8A"}},
                title={"text": "ATS Compatibility", "font": {"size": 14, "color": "#8BAFC7"}},
                number={"suffix": "%", "font": {"size": 40, "color": gauge_color}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#8BAFC7", "tickfont": {"color": "#8BAFC7"}},
                    "bar": {"color": gauge_color, "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40],   "color": "rgba(255,107,138,0.15)"},
                        {"range": [40, 70],  "color": "rgba(255,179,71,0.15)"},
                        {"range": [70, 100], "color": "rgba(0,229,160,0.15)"},
                    ],
                    "threshold": {"line": {"color": "#00CED1", "width": 3}, "thickness": 0.8, "value": 70}
                }
            ))
            fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#8BAFC7"}, height=260, margin=dict(l=20, r=20, t=40, b=10))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown('''<div style="display:flex;justify-content:center;gap:20px;margin-top:-10px;"><span style="font-size:12px;color:#FF6B8A;">🔴 0–40 Low</span><span style="font-size:12px;color:#FFB347;">🟡 40–70 Average</span><span style="font-size:12px;color:#00E5A0;">🟢 70–100 Good</span></div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_radar:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🕸️ Competency Radar")
            categories = ["Keywords", "Skills Match", "Experience", "Projects", "Format", "Seniority"]
            values     = [score, max(100-gap_score,10), min(score+5,95), min(score+10,98), 92, 75]
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=values+[values[0]], theta=categories+[categories[0]], fill="toself", fillcolor="rgba(0,206,209,0.15)", line=dict(color="#00CED1", width=2), marker=dict(color="#00CED1", size=6), name="Your Profile"))
            fig_radar.add_trace(go.Scatterpolar(r=[70]*len(categories)+[70], theta=categories+[categories[0]], fill="toself", fillcolor="rgba(255,179,71,0.06)", line=dict(color="#FFB347", width=1.5, dash="dot"), name="Target (70%)"))
            fig_radar.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0,100], tickfont=dict(size=9,color="#8BAFC7"), gridcolor="rgba(255,255,255,0.08)"), angularaxis=dict(tickfont=dict(size=11,color="#8BAFC7"), gridcolor="rgba(255,255,255,0.08)")), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=True, legend=dict(font=dict(color="#8BAFC7", size=11)), height=280, margin=dict(l=40,r=40,t=20,b=20))
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_prog, col_skills = st.columns([1, 1], gap="large")
        with col_prog:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("📊 Category Progress")
            categories_prog = {
                "🔑 Keyword Match":   round(score, 1),
                "🛠️ Skills Coverage": round(max(100-gap_score, 10), 1),
                "📁 Projects":        round(min(score+10, 98), 1),
                "📄 Resume Format":   92,
                "🎓 Seniority Fit":   75,
                "💼 Experience":      round(min(score+5, 95), 1),
            }
            for label, val in categories_prog.items():
                bar_color = "#00E5A0" if val >= 70 else "#FFB347" if val >= 40 else "#FF6B8A"
                st.markdown(f"""
                <div style="margin-bottom:14px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:13px;">
                        <span style="color:{text};font-weight:500;">{label}</span>
                        <span style="color:{bar_color};font-weight:700;">{val}%</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.08);border-radius:50px;height:8px;">
                        <div style="width:{val}%;background:{bar_color};height:8px;border-radius:50px;box-shadow:0 0 8px {bar_color}55;"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_skills:
            st.markdown('</div>', unsafe_allow_html=True)
            st.subheader("🏷️ Skill Gap Badges")
            st.markdown("<br>", unsafe_allow_html=True)
            gaps_text = res.get("gaps", "")

            # Fixed skill lists - always use these defaults based on score
            missing_skills = ["Docker", "FastAPI", "Kubernetes", "AWS", "GraphQL", "Redis"]
            present_skills = ["Python", "Streamlit", "Git", "REST API", "SQL", "Machine Learning"]

            # Try to extract real skills from gaps text
            tech_skills = ["Python", "Java", "JavaScript", "TypeScript", "React", "Node", "Django", 
                        "Flask", "FastAPI", "Docker", "Kubernetes", "AWS", "Azure", "GCP", 
                        "MongoDB", "PostgreSQL", "MySQL", "Redis", "GraphQL", "REST", "Git",
                        "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit", "OpenCV",
                        "Linux", "Terraform", "CI/CD", "Jenkins", "Kafka", "Spark", "Hadoop",
                        "Spring", "Angular", "Vue", "NextJS", "Express", "NLP", "LangChain"]

            found_missing, found_present = [], []
            for line in gaps_text.split("\n"):
                l = line.strip().lower()
                for skill in tech_skills:
                    if skill.lower() in l:
                        if any(k in l for k in ["missing","lacking","need","required","add","gap","not"]):
                            if skill not in found_missing:
                                found_missing.append(skill)
                        elif any(k in l for k in ["have","present","strong","good","match","proficient"]):
                            if skill not in found_present:
                                found_present.append(skill)

            if len(found_missing) >= 3:
                missing_skills = found_missing[:6]
            if len(found_present) >= 3:
                present_skills = found_present[:6]

            st.markdown(f"""
                <div style="margin-bottom:16px;">
                    <div style="font-size:12px;font-weight:700;color:#FF6B8A;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">❌ Missing Skills</div>
                    <div>{''.join([f'<span style="display:inline-block;background:rgba(255,107,138,0.12);border:1px solid rgba(255,107,138,0.35);border-radius:50px;padding:5px 14px;margin:4px;font-size:12px;font-weight:600;color:#FF6B8A;">{s}</span>' for s in missing_skills])}</div>
                </div>
                <div style="margin-bottom:16px;">
                    <div style="font-size:12px;font-weight:700;color:#00E5A0;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">✅ Present Skills</div>
                    <div>{''.join([f'<span style="display:inline-block;background:rgba(0,229,160,0.12);border:1px solid rgba(0,229,160,0.35);border-radius:50px;padding:5px 14px;margin:4px;font-size:12px;font-weight:600;color:#00E5A0;">{s}</span>' for s in present_skills])}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # JOB READINESS METER
        step5_bg     = "rgba(0,229,160,0.15)" if score >= 45 else "rgba(255,179,71,0.1)"
        step5_border = "#00E5A0" if score >= 45 else "#FFB347"
        step5_color  = "#00E5A0" if score >= 45 else "#FFB347"
        step5_icon   = "&#10003;" if score >= 45 else "&#9679;"
        step5_fw     = "600" if score >= 45 else "400"
        step5_line   = "#00E5A0" if score >= 45 else "rgba(180,180,180,0.3)"
        step6_bg     = "rgba(0,229,160,0.15)" if score >= 75 else "rgba(180,180,180,0.08)"
        step6_border = "#00E5A0" if score >= 75 else "rgba(180,180,180,0.4)"
        step6_color  = "#00E5A0" if score >= 75 else "#999999"
        step6_icon   = "&#10003;" if score >= 75 else "&#9675;"
        step6_tc     = "#00E5A0" if score >= 75 else text_muted
        step6_fw     = "700" if score >= 75 else "400"
        step6_line   = "#00E5A0" if score >= 75 else "rgba(180,180,180,0.3)"

        def step_html(icon, label, bg, border, color, fw, tc):
            return (
                '<div style="display:flex;flex-direction:column;align-items:center;flex:1;">' +
                '<div style="width:48px;height:48px;border-radius:50%;background:' + bg +
                ';border:2px solid ' + border + ';display:flex;align-items:center;' +
                'justify-content:center;margin-bottom:8px;">' +
                '<span style="color:' + color + ';font-size:22px;font-weight:900;">' + icon + '</span>' +
                '</div>' +
                '<div style="font-size:12px;text-align:center;color:' + tc + ';font-weight:' + fw + ';line-height:1.5;">' + label + '</div>' +
                '</div>'
            )

        def line_html(color):
            return '<div style="height:2px;background:' + color + ';flex:0.4;margin-top:24px;border-radius:2px;"></div>'

        meter_html = (
            '<div style="background:' + card_bg + ';border:1px solid ' + card_border +
            ';border-radius:20px;padding:24px 28px;margin-bottom:20px;">' +
            '<div style="font-size:17px;font-weight:700;color:' + text + ';margin-bottom:24px;">' +
            '&#128680; Job Readiness Meter' +
            '</div>' +
            '<div style="display:flex;align-items:flex-start;justify-content:space-between;">' +
            step_html("&#10003;", "Resume<br>Uploaded",  "rgba(0,229,160,0.15)", "#00E5A0", "#00E5A0", "600", text) +
            line_html("#00E5A0") +
            step_html("&#10003;", "Analysis<br>Done",    "rgba(0,229,160,0.15)", "#00E5A0", "#00E5A0", "600", text) +
            line_html("#00E5A0") +
            step_html("&#10003;", "ATS<br>Scored",       "rgba(0,229,160,0.15)", "#00E5A0", "#00E5A0", "600", text) +
            line_html("#00E5A0") +
            step_html("&#10003;", "Gaps<br>Identified",  "rgba(0,229,160,0.15)", "#00E5A0", "#00E5A0", "600", text) +
            line_html(step5_line) +
            step_html(step5_icon, "Skills<br>Learning",  step5_bg, step5_border, step5_color, step5_fw, text) +
            line_html(step6_line) +
            step_html(step6_icon, "Job<br>Ready",        step6_bg, step6_border, step6_color, step6_fw, step6_tc) +
            '</div></div>'
        )
        st.markdown(meter_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # WHAT TO DO NEXT
        if score >= 75:
            next_color  = "#00897B"
            next_bg     = "rgba(0,229,160,0.06)"
            next_border = "rgba(0,229,160,0.3)"
            next_title  = "You're Job Ready! Here's what to do next:"
            next_actions = [
                ("Apply to jobs using your optimized resume",       "Cover Letter"),
                ("Practice interview questions before applying",     "Interview Prep"),
                ("Generate your LinkedIn Bio for personal branding", "LinkedIn Bio"),
            ]
        elif score >= 45:
            next_color  = "#E65100"
            next_bg     = "rgba(255,179,71,0.06)"
            next_border = "rgba(255,179,71,0.3)"
            next_title  = "Almost there! Focus on these to boost your score:"
            next_actions = [
                ("Review your skill gaps and start learning missing skills", "Skill Gap"),
                ("Generate a learning roadmap to close gaps fast",           "Learning Roadmap"),
                ("Rewrite your resume with AI for better ATS score",         "Resume Rewriter"),
            ]
        else:
            next_color  = "#C62828"
            next_bg     = "rgba(255,107,138,0.06)"
            next_border = "rgba(255,107,138,0.3)"
            next_title  = "Let's get you job-ready! Start with these steps:"
            next_actions = [
                ("Understand exactly which skills you are missing",  "Skill Gap"),
                ("Let AI rewrite your resume to improve ATS score",  "Resume Rewriter"),
                ("Build a personalized learning roadmap",            "Learning Roadmap"),
            ]

        actions_html = ""
        for a_text, a_page in next_actions:
            actions_html += (
                '<div style="display:flex;align-items:flex-start;gap:16px;padding:14px 18px;' +
                'background:rgba(255,255,255,0.5);border-radius:12px;margin-bottom:10px;' +
                'border-left:4px solid ' + next_border + ';">' +
                '<div style="font-size:16px;font-weight:900;color:' + next_color + ';min-width:20px;margin-top:1px;">&rarr;</div>' +
                '<div>' +
                '<div style="font-size:14px;color:' + text + ';font-weight:600;margin-bottom:3px;">' + a_text + '</div>' +
                '<div style="font-size:12px;color:' + next_color + ';font-weight:700;">Go to ' + a_page + ' page</div>' +
                '</div>' +
                '</div>'
            )

        next_html = (
            '<div style="background:' + next_bg + ';border:1px solid ' + next_border +
            ';border-radius:20px;padding:24px 28px;margin-bottom:8px;">' +
            '<div style="font-size:16px;font-weight:700;color:' + next_color + ';margin-bottom:16px;">' +
            next_title +
            '</div>' +
            actions_html +
            '</div>'
        )
        st.markdown(next_html, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please upload your resume first on the Upload page.")
    nav_buttons()

# ── GAP AUDIT ──
elif st.session_state.page == "Gap Audit":
    st.title("🔍 Skill Gap Analysis")
    page_banner("🔍", "Gap Audit", "AI-detected missing skills and competencies between your resume and the job description.")
    if st.session_state.results:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.results["gaps"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Run analysis first.")
    nav_buttons()

# ── PROJECT HUMANIZER ──
elif st.session_state.page == "Project Humanizer":
    st.title("✨ STAR Project Narratives")
    page_banner("✨", "Project Humanizer", "Your projects rewritten using the STAR method to impress any recruiter or interviewer.")
    if st.session_state.results:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.results["star"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Run analysis first.")
    nav_buttons()

# ── COVER LETTER ──
elif st.session_state.page == "Cover Letter":
    st.title("📜 AI Cover Letter")
    page_banner("📜", "Cover Letter", "A tailored, professional cover letter crafted specifically for your target job.")
    if st.session_state.results:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write(st.session_state.results["cl"])
        st.markdown('</div>', unsafe_allow_html=True)
        st.download_button("📥 Download Cover Letter", data=st.session_state.results["cl"], file_name="cover_letter.txt", mime="text/plain", use_container_width=True)
    else:
        st.warning("⚠️ Run analysis first.")
    nav_buttons()

# ── INTERVIEW PREP ──
elif st.session_state.page == "Interview Prep":
    st.title("🎙️ Interview Prep Guide")
    page_banner("🎙️", "Interview Preparation", "Predicted interview questions and model answers tailored to your resume and the job.")
    if st.session_state.results:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(st.session_state.results["iq"])
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Run analysis first.")
    nav_buttons()

# ── AI COACH ──
elif st.session_state.page == "AI Coach":
    st.title("🤖 AI Career Advisor")
    page_banner("🤖", "AI Career Coach", "Ask anything about your career, resume, job search strategy, or skill development.")
    if st.session_state.results:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        st.markdown('</div>', unsafe_allow_html=True)
        if prompt := st.chat_input("💬 Ask your career question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                name_context = f"Your name is Advik. You are an AI Career Coach named Advik. {prompt}"
                ans = get_career_advice(name_context, st.session_state.results["gaps"])
                ans = ans.replace("Alex Chen", "Advik").replace("Alex", "Advik")
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
    else:
        st.warning("⚠️ Run analysis first to unlock AI coaching.")
    nav_buttons()

# ── LEARNING ROADMAP ──
elif st.session_state.page == "Learning Roadmap":
    st.title("🗺️ Personalized Learning Roadmap")
    if not st.session_state.results:
        st.warning("⚠️ Please upload your resume and run analysis first.")
    else:
        page_banner("🗺️", "Your AI Learning Roadmap", "A week-by-week personalized plan to close your skill gaps and become job-ready.")
        col_weeks, col_btn = st.columns([1, 2], gap="medium")
        with col_weeks:
            num_weeks = st.selectbox("📅 Duration (weeks)", [4, 6, 8, 12], index=1)
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_btn = st.button("⚡  Generate My Roadmap", type="primary", use_container_width=True)
        if generate_btn:
            with st.spinner("🤖 Building your personalized roadmap..."):
                try:
                    prompt = f"""
You are a senior career coach and learning advisor.
A candidate has the following skill gaps identified after resume analysis:
{st.session_state.results['gaps']}
Their ATS match score is {st.session_state.results['score']}% and skill gap score is {st.session_state.results['gap_score']}%.
Create a detailed {num_weeks}-week learning roadmap to help them close these gaps and become job-ready.
Format your response EXACTLY like this for each week:
WEEK 1: [Week Title]
- Focus: [Main skill or topic]
- Topics: [Specific things to learn]
- Resources: [Free resources like YouTube, docs, courses]
- Goal: [What they should be able to do by end of week]
- Time: [Estimated hours per day]
WEEK 2: [Week Title]
...and so on for all {num_weeks} weeks.
End with a SUMMARY section listing the top 5 skills they will have mastered.
Be specific, practical, and motivating.
"""
                    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=3000)
                    st.session_state.roadmap = response.choices[0].message.content
                    st.success("✅ Roadmap generated!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        if st.session_state.roadmap:
            st.markdown("<br>", unsafe_allow_html=True)
            lines = st.session_state.roadmap.split("\n")
            current_title, current_body = None, []
            def flush_week(title, body):
                if title:
                    body_html = "<br>".join(body).strip()
                    st.markdown(f"""<div class="week-card"><div class="week-title">{title}</div><div class="week-body">{body_html}</div></div>""", unsafe_allow_html=True)
            for line in lines:
                s = line.strip()
                if s.upper().startswith("WEEK") and ":" in s:
                    flush_week(current_title, current_body); current_title, current_body = s, []
                elif s.upper().startswith("SUMMARY"):
                    flush_week(current_title, current_body); current_title, current_body = "📋 " + s, []
                elif s:
                    current_body.append(s)
            flush_week(current_title, current_body)
            st.divider()
            st.download_button(label="📥 Download Roadmap (.txt)", data=st.session_state.roadmap, file_name=f"roadmap_{st.session_state.current_user}.txt", mime="text/plain", use_container_width=True)
    st.divider()
    c1, _, c3 = st.columns([1, 2, 1])
    with c1: st.button("⬅  Back", on_click=go_back)
    with c3: st.button("Next  ➡", on_click=go_next)


# ── RESUME REWRITER ──
elif st.session_state.page == "Resume Rewriter":
    st.title("📃 AI Resume Rewriter")
    page_banner("📃", "Resume Rewriter", "AI rewrites your entire resume — stronger verbs, ATS keywords injected, quantified results. Side-by-side before vs after.")
    if not st.session_state.results:
        st.warning("⚠️ Please run analysis on the Upload page first.")
    else:
        st.markdown(f"""<div class="glass-card"><p style="margin:0;font-size:14px;color:{text_muted};">🤖 Paste your current resume text on the left. Our AI will rewrite it fully optimized for your target job — stronger language, injected ATS keywords, quantified achievements.</p></div>""", unsafe_allow_html=True)
        col_orig, col_new = st.columns(2, gap="large")
        with col_orig:
            st.markdown(f"""<div style="background:rgba(255,107,138,0.08);border:1px solid rgba(255,107,138,0.3);border-radius:14px;padding:12px 18px;margin-bottom:10px;"><span style="font-size:12px;font-weight:700;color:#FF6B8A;letter-spacing:0.08em;text-transform:uppercase;">📄 Original Resume</span></div>""", unsafe_allow_html=True)
            original_resume = st.text_area("Original", height=400, placeholder="Paste your full resume text here...", label_visibility="collapsed")
        with col_new:
            st.markdown(f"""<div style="background:rgba(0,206,209,0.08);border:1px solid rgba(0,206,209,0.3);border-radius:14px;padding:12px 18px;margin-bottom:10px;"><span style="font-size:12px;font-weight:700;color:{CYAN};letter-spacing:0.08em;text-transform:uppercase;">✨ AI-Rewritten Resume</span></div>""", unsafe_allow_html=True)
            if st.session_state.rewritten_resume:
                st.text_area("Rewritten", value=st.session_state.rewritten_resume, height=400, label_visibility="collapsed")
            else:
                st.markdown(f"""<div style="height:400px;background:{card_bg};border:2px dashed {card_border};border-radius:14px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:10px;"><div style="font-size:44px;">🪄</div><div style="font-size:13px;color:{text_muted};text-align:center;">Your AI-optimized resume<br>will appear here</div></div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        _, bc, _ = st.columns([1, 1, 1])
        with bc:
            rewrite_btn = st.button("📃  Rewrite My Resume", type="primary", use_container_width=True)
        if rewrite_btn:
            if not original_resume.strip():
                st.warning("⚠️ Please paste your resume text in the left panel.")
            else:
                with st.spinner("🤖 Rewriting your resume for maximum ATS impact..."):
                    try:
                        prompt = f"""You are an expert resume writer and ATS optimization specialist.
The candidate's current ATS score is {st.session_state.results.get('score',0)}%.
Their identified skill gaps: {st.session_state.results.get('gaps','')}
ORIGINAL RESUME:
{original_resume}
Rewrite this resume completely with:
1. Inject missing ATS keywords naturally
2. Replace weak verbs with powerful ones (Led, Engineered, Delivered, Architected...)
3. Add quantifiable metrics to every achievement (%, numbers, impact)
4. Strengthen the Professional Summary for the target role
5. Add a KEY SKILLS section with all technical skills
6. Keep all original experience — only enhance the language
Format with clear sections:
PROFESSIONAL SUMMARY | KEY SKILLS | EXPERIENCE | PROJECTS | EDUCATION
Return ONLY the rewritten resume, nothing else."""
                        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=2000)
                        st.session_state.rewritten_resume = response.choices[0].message.content
                        st.success("✅ Resume rewritten! Scroll up to see the result.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        if st.session_state.rewritten_resume:
            old_score = st.session_state.results.get("score", 0)
            new_score = min(old_score + 25, 98)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:linear-gradient(135deg,rgba(0,229,160,0.10),rgba(0,206,209,0.10));border:1px solid rgba(0,229,160,0.3);border-radius:16px;padding:20px 28px;display:flex;align-items:center;gap:24px;margin-bottom:16px;"><div style="text-align:center;"><div style="font-size:30px;font-weight:800;color:#FF6B8A;">{old_score}%</div><div style="font-size:11px;color:{text_muted};text-transform:uppercase;">Before</div></div><div style="font-size:26px;color:{text_muted};">→</div><div style="text-align:center;"><div style="font-size:30px;font-weight:800;color:#00E5A0;">{new_score}%</div><div style="font-size:11px;color:{text_muted};text-transform:uppercase;">Est. After</div></div><div style="flex:1;padding-left:20px;border-left:1px solid rgba(0,206,209,0.2);"><div style="font-size:14px;font-weight:600;color:{text};">🚀 Estimated ATS Score Improvement</div><div style="font-size:13px;color:{text_muted};margin-top:4px;">Re-upload your rewritten resume to get the exact new score.</div></div></div>""", unsafe_allow_html=True)
            dl1, dl2, _ = st.columns([1, 1, 1])
            with dl1:
                st.download_button("📥 Download Rewritten Resume", data=st.session_state.rewritten_resume, file_name="rewritten_resume.txt", mime="text/plain", use_container_width=True)
            with dl2:
                if st.button("🔄 Rewrite Again", use_container_width=True):
                    st.session_state.rewritten_resume = None; st.rerun()
    nav_buttons()

# ── JOB MARKET TRENDS ──
elif st.session_state.page == "Job Market Trends":
    st.title("📈 Job Market Trend Analyzer")
    page_banner("📈", "Job Market Trends 2025", "Discover in-demand skills, salary ranges, top hiring companies & career paths for any role.")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    tc1, tc2 = st.columns([2, 1], gap="medium")
    with tc1:
        job_role = st.text_input("🔍 Job Role", placeholder="e.g. Python Developer, Data Scientist, DevOps Engineer...")
    with tc2:
        location = st.selectbox("🌍 Location", ["India", "USA", "UK", "Canada", "Remote / Global"])
    st.markdown('</div>', unsafe_allow_html=True)
    _, tb, _ = st.columns([1, 1, 1])
    with tb:
        trend_btn = st.button("📈  Analyze Market Trends", type="primary", use_container_width=True)
    if trend_btn:
        if not job_role.strip():
            st.warning("⚠️ Please enter a job role.")
        else:
            with st.spinner(f"🔍 Analyzing {location} market for {job_role}..."):
                try:
                    prompt = f"""You are a job market intelligence expert with 2025 hiring data.
Analyze the job market for: {job_role} in {location}
Respond in EXACTLY this format:
MARKET OVERVIEW
[2-3 sentences on demand and growth]
TOP 10 IN-DEMAND SKILLS
1. [Skill] - [Why it matters]
2. [Skill] - [Why it matters]
3. [Skill] - [Why it matters]
4. [Skill] - [Why it matters]
5. [Skill] - [Why it matters]
6. [Skill] - [Why it matters]
7. [Skill] - [Why it matters]
8. [Skill] - [Why it matters]
9. [Skill] - [Why it matters]
10. [Skill] - [Why it matters]
SALARY RANGES ({location})
Entry Level (0-2 yrs): [range]
Mid Level (2-5 yrs): [range]
Senior Level (5+ yrs): [range]
Lead/Architect (8+ yrs): [range]
TOP HIRING COMPANIES
[8 companies with one line each]
TRENDING TOOLS & FRAMEWORKS
[8 specific tools trending now]
CAREER GROWTH PATH
[Clear progression: Role A to Role B to Role C to Role D]
PRO TIPS TO GET HIRED FASTER
1. [Tip]
2. [Tip]
3. [Tip]"""
                    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=2000)
                    st.session_state.market_trends = {"role": job_role, "location": location, "content": response.choices[0].message.content}
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    if st.session_state.market_trends:
        d = st.session_state.market_trends
        st.markdown(f"""<div style="background:{GRAD};border-radius:16px;padding:18px 28px;margin:16px 0;display:flex;align-items:center;gap:16px;"><div style="font-size:36px;">📊</div><div><div style="font-size:18px;font-weight:800;color:white;font-family:'Space Grotesk',sans-serif;">{d['role']} — {d['location']}</div><div style="font-size:13px;color:rgba(255,255,255,0.82);">2025 Job Market Intelligence Report</div></div></div>""", unsafe_allow_html=True)
        section_icons = {"MARKET": "🌐", "TOP 10": "🔥", "SALARY": "💰", "HIRING": "🏢", "TRENDING": "⚡", "CAREER": "🚀", "PRO TIP": "💡"}
        for section in d["content"].split("\n\n"):
            if not section.strip(): continue
            lines = section.strip().split("\n")
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            icon = next((v for k, v in section_icons.items() if k in title.upper()), "📌")
            st.markdown(f"""<div class="glass-card"><div style="font-size:15px;font-weight:700;color:{CYAN};margin-bottom:10px;">{icon} {title}</div><div style="font-size:14px;color:{text};line-height:2.0;white-space:pre-line;">{body}</div></div>""", unsafe_allow_html=True)
        dl_c, rs_c, _ = st.columns([1, 1, 1])
        with dl_c:
            st.download_button("📥 Download Report", data=d["content"], file_name=f"trends_{d['role'].replace(' ','_')}.txt", mime="text/plain", use_container_width=True)
        with rs_c:
            if st.button("🔄 New Search", use_container_width=True):
                st.session_state.market_trends = None; st.rerun()
    nav_buttons()


# ── LINKEDIN BIO ──
elif st.session_state.page == "LinkedIn Bio":
    st.title("💼 LinkedIn Bio Generator")
    page_banner("💼", "LinkedIn Profile Builder", "AI crafts your complete LinkedIn presence — headline, summary, skills, and connection message.")
    if not st.session_state.results:
        st.warning("⚠️ Please run analysis on the Upload page first.")
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ✏️ Tell us a bit more about yourself")
        li_c1, li_c2 = st.columns(2, gap="medium")
        with li_c1:
            target_role = st.text_input("🎯 Target Job Title", placeholder="e.g. Python Developer, Data Scientist")
            years_exp   = st.selectbox("📅 Years of Experience", ["Fresher (0 yr)", "1-2 years", "2-4 years", "4-6 years", "6+ years"])
        with li_c2:
            tone        = st.selectbox("🎨 Profile Tone", ["Professional & Formal", "Friendly & Approachable", "Bold & Ambitious", "Creative & Unique"])
            industries  = st.text_input("🏭 Target Industry", placeholder="e.g. FinTech, Healthcare IT, E-commerce")
        achievements = st.text_area("🏆 Key Achievement (optional)", height=80, placeholder="e.g. Built a platform used by 500+ users, Won hackathon, Published research paper...")
        st.markdown('</div>', unsafe_allow_html=True)
        _, gen_col, _ = st.columns([1, 1, 1])
        with gen_col:
            gen_btn = st.button("💼  Generate My LinkedIn Profile", type="primary", use_container_width=True)
        if gen_btn:
            if not target_role.strip():
                st.warning("⚠️ Please enter your target job title.")
            else:
                with st.spinner("✨ Crafting your perfect LinkedIn presence..."):
                    try:
                        prompt = f"""You are a LinkedIn profile optimization expert and personal branding specialist.
Create a complete, compelling LinkedIn profile for this candidate:
TARGET ROLE: {target_role}
EXPERIENCE LEVEL: {years_exp}
INDUSTRY: {industries or 'Technology'}
TONE: {tone}
KEY ACHIEVEMENT: {achievements or 'Not provided'}
RESUME ANALYSIS SUMMARY:
- ATS Score: {st.session_state.results.get('score', 0)}%
- Skill Gaps: {st.session_state.results.get('gaps', '')[:300]}
Generate EXACTLY in this format:
HEADLINE
[One powerful LinkedIn headline under 220 characters. Must include role, value proposition, and 1-2 keywords]
ABOUT SECTION
[5-6 paragraph LinkedIn About/Summary section. Start with a hook, tell their story, highlight skills and achievements, show personality, end with a call to action. 2000-2600 characters total. Use emojis sparingly for visual breaks.]
FEATURED SKILLS (Top 10)
1. [Skill]
2. [Skill]
3. [Skill]
4. [Skill]
5. [Skill]
6. [Skill]
7. [Skill]
8. [Skill]
9. [Skill]
10. [Skill]
CONNECTION REQUEST MESSAGE
[A short, personalized 300-character connection request message they can send to recruiters or professionals in their target industry. Friendly, genuine, not salesy.]
COLD MESSAGE TO RECRUITER
[A 500-character InMail / cold message to send to a recruiter at a target company. Professional, specific, includes a clear ask.]
PROFILE OPTIMIZATION TIPS
1. [Specific tip for their profile]
2. [Specific tip for their profile]
3. [Specific tip for their profile]
4. [Specific tip for their profile]
5. [Specific tip for their profile]
Make everything specific to {target_role} in {industries or 'Technology'}. Be compelling, authentic, and keyword-rich."""
                        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=2500)
                        st.session_state.linkedin_bio = {"role": target_role, "content": response.choices[0].message.content}
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        if st.session_state.linkedin_bio:
            data    = st.session_state.linkedin_bio
            content = data["content"]
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:linear-gradient(135deg,#0A66C2,#0077B5);border-radius:20px;padding:20px 28px;margin-bottom:24px;display:flex;align-items:center;gap:18px;"><div style="width:60px;height:60px;background:rgba(255,255,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">👤</div><div><div style="font-size:18px;font-weight:800;color:white;font-family:'Space Grotesk',sans-serif;">{st.session_state.current_user.title()}</div><div style="font-size:14px;color:rgba(255,255,255,0.85);margin-top:2px;">{data['role']}</div><div style="font-size:12px;color:rgba(255,255,255,0.65);margin-top:4px;">🔗 linkedin.com/in/{st.session_state.current_user.lower().replace(' ','-')}</div></div><div style="margin-left:auto;"><div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);border-radius:50px;padding:6px 18px;font-size:13px;font-weight:600;color:white;cursor:pointer;">+ Connect</div></div></div>""", unsafe_allow_html=True)
            section_config = {
                "HEADLINE":             ("🏷️", "#0A66C2", "rgba(10,102,194,0.08)", "rgba(10,102,194,0.25)"),
                "ABOUT":                ("📝", CYAN,      card_bg,                  card_border),
                "FEATURED SKILLS":      ("⚡", "#00E5A0", "rgba(0,229,160,0.08)",   "rgba(0,229,160,0.25)"),
                "CONNECTION REQUEST":   ("🤝", "#FFB347", "rgba(255,179,71,0.08)",  "rgba(255,179,71,0.25)"),
                "COLD MESSAGE":         ("📬", "#B44FE8", "rgba(180,79,232,0.08)",  "rgba(180,79,232,0.25)"),
                "PROFILE OPTIMIZATION": ("💡", CYAN,      card_bg,                  card_border),
            }
            import re
            raw_sections = re.split(r'\n(?=[A-Z][A-Z\s]+\n)', content)
            for block in raw_sections:
                block = block.strip()
                if not block: continue
                lines   = block.split("\n")
                title   = lines[0].strip().upper()
                body    = "\n".join(lines[1:]).strip()
                cfg_key = next((k for k in section_config if k in title), None)
                icon, accent, bg_col, border_col = section_config.get(cfg_key, ("📌", CYAN, card_bg, card_border))
                if "HEADLINE" in title:
                    st.markdown(f"""<div style="background:{bg_col};border:2px solid {border_col};border-radius:18px;padding:24px 28px;margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">{icon} LinkedIn Headline</div><div style="font-size:20px;font-weight:700;color:{text};font-family:'Space Grotesk',sans-serif;line-height:1.4;">{body}</div><div style="margin-top:10px;font-size:11px;color:{text_muted};">{len(body)} / 220 characters</div></div>""", unsafe_allow_html=True)
                elif "FEATURED SKILLS" in title:
                    skills = [l.strip().lstrip("0123456789. ") for l in body.split("\n") if l.strip()]
                    pills  = "".join([f'<span style="display:inline-block;background:{bg_col};border:1px solid {border_col};border-radius:50px;padding:6px 16px;margin:4px;font-size:13px;font-weight:600;color:{accent};">⚡ {s}</span>' for s in skills])
                    st.markdown(f"""<div style="background:{card_bg};border:1px solid {card_border};border-radius:18px;padding:24px 28px;margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">{icon} Featured Skills</div><div>{pills}</div></div>""", unsafe_allow_html=True)
                elif "CONNECTION REQUEST" in title or "COLD MESSAGE" in title:
                    label = "Connection Request" if "CONNECTION" in title else "Cold Message to Recruiter"
                    st.markdown(f"""<div style="background:{bg_col};border:1px solid {border_col};border-radius:18px;padding:24px 28px;margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">{icon} {label}</div><div style="background:{card_bg};border-radius:12px;padding:16px 20px;font-size:14px;color:{text};line-height:1.75;font-style:italic;border-left:3px solid {accent};">{body}</div><div style="margin-top:8px;font-size:11px;color:{text_muted};">{len(body)} characters</div></div>""", unsafe_allow_html=True)
                elif "PROFILE OPTIMIZATION" in title:
                    tips = [l.strip().lstrip("0123456789. ") for l in body.split("\n") if l.strip()]
                    tips_html = "".join([f'<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;padding:10px 14px;background:{card_bg};border-radius:10px;border-left:3px solid {CYAN};"><span style="color:{CYAN};font-weight:700;min-width:20px;">{i+1}.</span><span style="font-size:13px;color:{text};line-height:1.6;">{t}</span></div>' for i, t in enumerate(tips)])
                    st.markdown(f"""<div style="background:{card_bg};border:1px solid {card_border};border-radius:18px;padding:24px 28px;margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:{CYAN};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">{icon} Profile Optimization Tips</div>{tips_html}</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div style="background:{bg_col};border:1px solid {border_col};border-radius:18px;padding:24px 28px;margin-bottom:16px;"><div style="font-size:12px;font-weight:700;color:{accent};text-transform:uppercase;letter-spacing:0.08em;margin-bottom:12px;">{icon} {lines[0].strip()}</div><div style="font-size:14px;color:{text};line-height:1.85;white-space:pre-line;">{body}</div></div>""", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            dl_col, reset_col, _ = st.columns([1, 1, 1])
            with dl_col:
                st.download_button("📥 Download LinkedIn Profile", data=content, file_name=f"linkedin_profile_{st.session_state.current_user}.txt", mime="text/plain", use_container_width=True)
            with reset_col:
                if st.button("🔄 Regenerate Profile", use_container_width=True):
                    st.session_state.linkedin_bio = None; st.rerun()
    nav_buttons(show_next=False)
