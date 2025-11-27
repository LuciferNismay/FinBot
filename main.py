import streamlit as st
from nlp_module import analyze_text_local, classify_needs_wants
import json, math, matplotlib.pyplot as plt
from llm_gemini_api import generate_financial_advice
import random

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="FinBot – Your AI Financial Assistant", page_icon="💰", layout="wide")

# -------------------- THEME STATE --------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

dark = st.session_state.theme == "dark"

# -------------------- COLORS --------------------
colors = {
    "bg": "#0E1117" if dark else "#F4F6FA",
    "text": "#EDEDED" if dark else "#111111",
    "accent": "#5B9FFF" if dark else "#2563EB",
    "accent_soft": "#A5B4FC" if dark else "#3B82F6",
    "input_bg": "#1B1E25" if dark else "#FFFFFF",
    "border": "#2C2F36" if dark else "#E0E0E0",
}

# -------------------- STYLING --------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

body, .stApp {{
    background-color: {colors["bg"]};
    color: {colors["text"]};
    font-family: 'Inter', sans-serif;
    transition: all 0.3s ease;
}}

.top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 15px 25px;
    background-color: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid {colors["border"]};
    border-radius: 12px;
    backdrop-filter: blur(10px);
    margin-bottom: 20px;
}}

.logo-space {{
    width: 50px;
    height: 50px;
    border-radius: 10px;
    background-color: rgba(91,159,255,0.15);
    border: 1px solid {colors["accent_soft"]};
    display: flex;
    align-items: center;
    justify-content: center;
    color: {colors["accent"]};
    font-weight: bold;
    font-size: 22px;
}}

.header-title {{
    flex-grow: 1;
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: {colors["accent"]};
    text-shadow: 0 0 10px rgba(91,159,255,0.4);
    animation: glow 4s ease-in-out infinite alternate;
}}
@keyframes glow {{
    from {{ text-shadow: 0 0 8px rgba(91,159,255,0.3); }}
    to {{ text-shadow: 0 0 16px rgba(91,159,255,0.6); }}
}}

.theme-toggle {{
    font-size: 24px;
    cursor: pointer;
    color: {colors["accent"]};
    transition: 0.3s ease;
}}
.theme-toggle:hover {{
    transform: rotate(15deg) scale(1.1);
}}

.section {{
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    border: 1px solid {colors["border"]};
    padding: 25px;
    margin-bottom: 20px;
    backdrop-filter: blur(8px);
}}

.footer {{
    text-align: center;
    margin-top: 40px;
    font-size: 14px;
    color: #9CA3AF;
}}
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
icon = "☀️" if dark else "🌙"
if st.button(icon, key="theme_toggle", help="Switch Theme", use_container_width=False):
    toggle_theme()
    st.rerun()

st.markdown(f"""
<div class="top-bar">
    <div class="logo-space">₹</div>
    <div class="header-title">FinBot – Your AI Financial Assistant</div>
    <div class="theme-toggle">{icon}</div>
</div>
""", unsafe_allow_html=True)

# -------------------- MAIN LAYOUT --------------------
col1, col2 = st.columns([1.3, 1])

# -------------------- LEFT PANEL: AI CHAT --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

with col1:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("💬 FinBot Assistant")

    persona = st.selectbox("👤 Select Persona", ["Student", "Working Professional", "Retiree"])
    question = st.text_area("Ask FinBot a financial question:", height=100, placeholder="e.g., How can I save more each month?")

    if st.button("✨ Get Financial Advice"):
        if question.strip() == "":
            st.warning("Please enter your question.")
        else:
            with st.spinner("FinBot is analyzing your query... 🤖"):
                try:
                    analysis = analyze_text_local(question)
                    advice = generate_financial_advice(question, persona)
                    st.session_state.chat_history.append({"q": question, "a": advice})
                    if len(st.session_state.chat_history) > 3:
                        st.session_state.chat_history.pop(0)
                except Exception as e:
                    st.error(f"Error: {e}")

    if st.session_state.chat_history:
        st.write("### 🧠 Recent Conversations")
        for chat in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {chat['q']}")
            st.markdown(f"**FinBot:** {chat['a']}")
            st.write("---")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- RIGHT PANEL: FINANCIAL DASHBOARD --------------------
with col2:
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📊 Financial Dashboard")

    budget_str = st.text_area(
        "💵 Monthly Budget JSON:",
        '{"income":65000, "expenses":{"food":9000,"shopping":4000,"rent":18000,"transport":3500,"utilities":2500,"investment":6000,"entertainment":2000}}',
        height=120
    )
    goal_amount = st.number_input("🎯 Savings Goal (₹)", min_value=0, step=1000)

    if st.button("💡 Analyze Budget"):
        try:
            budget = json.loads(budget_str)
            income = budget["income"]
            expenses = budget["expenses"]
            total_exp = sum(expenses.values())
            savings = income - total_exp
            savings_rate = (savings / income) * 100

            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Income", f"₹{income:,.0f}")
            c2.metric("💸 Expenses", f"₹{total_exp:,.0f}")
            c3.metric("✅ Savings", f"₹{savings:,.0f}", delta=f"{savings_rate:.1f}%")

            # Financial Health Score
            health = max(30, min(100, int(100 - (total_exp / income) * 80)))
            st.progress(health / 100)
            st.write(f"**Financial Health Score:** {health}/100")

            # Expense Pie Chart
            st.write("### 🥧 Expense Distribution")
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                expenses.values(),
                labels=expenses.keys(),
                autopct="%1.1f%%",
                startangle=90,
                colors=plt.cm.Blues(range(50, 50 + len(expenses)*20, 20))
            )
            for t in autotexts:
                t.set_color("white")
                t.set_fontsize(9)
            ax.axis("equal")
            plt.title("Monthly Spending Overview", fontsize=12, color=colors["text"])
            st.pyplot(fig)

            st.write("### 🧩 Needs vs Wants")
            for category, amount in expenses.items():
                classification = classify_needs_wants(category)
                emoji = "✅" if classification == "Need" else "⚠️"
                st.write(f"• **{category.title()}** → {classification} {emoji} (₹{amount:,.0f})")

            if goal_amount > 0:
                if savings <= 0:
                    st.error("⚠ No savings possible. Try reducing 'Wants'.")
                else:
                    months_needed = math.ceil(goal_amount / savings)
                    st.success(f"📅 You can reach ₹{goal_amount:,.0f} in about {months_needed} months.")
                    if months_needed > 12:
                        st.info("💡 Tip: Reduce discretionary spending or increase investments for faster results.")
        except Exception as e:
            st.error(f"Invalid input: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- PROJECT INFO (COMPACT) --------------------
st.markdown(f"""
<hr style="border: 0; height: 1px; background-color: {colors["border"]}; margin-top: 40px; margin-bottom: 20px;">
<div style="text-align:center; color:{colors["text"]};">
    <h4 style="color:{colors["accent"]}; font-weight:700; margin-bottom:6px;">📘 Project Overview</h4>
    <p style="font-size:13px; color:#9CA3AF;">
        A Major Project submitted in partial fulfillment of the requirements for the degree of
        <b>Bachelor of Engineering (Computer Science & Engineering)</b>.
    </p>
</div>

<div style="display:flex; justify-content:center; gap:18px; flex-wrap:wrap; margin-top:12px;">
    <div style="background-color:rgba(255,255,255,0.05); border:1px solid {colors["border"]};
                border-radius:8px; padding:6px 14px; font-size:12px; color:#AAA;">
        <b>Institution:</b> Navodaya Institute of Technology
    </div>
    <div style="background-color:rgba(255,255,255,0.05); border:1px solid {colors["border"]};
                border-radius:8px; padding:6px 14px; font-size:12px; color:#AAA;">
        <b>Team Members:</b> Mayur, Mohammed Amaanuddin, Mohammed Gouse, Mohammed Kashif Hussain
    </div>
    <div style="background-color:rgba(255,255,255,0.05); border:1px solid {colors["border"]};
                border-radius:8px; padding:6px 14px; font-size:12px; color:#AAA;">
        <b>Guide:</b> Prof. Mahjabeen
    </div>
</div>

<div style="text-align:center; margin-top:12px; font-size:12px; color:#9CA3AF;">
    Developed with ❤️ by <b>Team FinBot</b> | Powered by Streamlit & Hugging Face
</div>
""", unsafe_allow_html=True)
