import streamlit as st
import os
import sys
from agentic_team_orchestrator.controller import Controller
from dotenv import load_dotenv

# Load env
load_dotenv()

# ---------- UI CONFIG ----------
st.set_page_config(
    page_title="🚀 Multi-Agent Factory",
    layout="wide"
)

# ---------- UI STYLES ----------
st.markdown("""
<style>
.main { background-color: #0e0e0e; }
.agent-card {
    background-color: #1e1e2d;
    border-radius: 12px;
    padding: 20px;
    border-left: 5px solid #3b82f6;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
}
.task-step {
    background-color: #2d2d3d;
    border-radius: 8px;
    padding: 15px;
    margin-top: 10px;
    border: 1px solid #444;
}
.mission-banner {
    background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "controller" not in st.session_state:
    st.session_state.controller = None

if "ui_schema" not in st.session_state:
    st.session_state.ui_schema = []

if "plan" not in st.session_state:
    st.session_state.plan = {}

# ---------- HEADER ----------
st.title("🚀 JIT Multi-Agent Factory")
st.caption("Architect specialized teams and watch them build tools and execute missions.")

# ---------- SIDEBAR ----------
st.sidebar.subheader("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    value=os.getenv("OPENAI_API_KEY", "")
)

# ---------- INPUT ----------
user_prompt = st.text_area(
    "What mission should the factory architect?",
    placeholder="e.g. Conduct a deep research on the current AI chip market and generate a summary report.",
    height=120
)

# ---------- BUILD AGENT ----------
if st.button("🏗️ Architect Mission"):
    if not api_key:
        st.error("❌ API key missing")
        st.stop()

    try:
        st.session_state.controller = Controller(api_key)

        with st.status("🏗️ Architecting Multi-Agent System...") as status:
            st.write("Generating Team Mission and Roles...")
            res = st.session_state.controller.build_agent(user_prompt)
            st.session_state.plan = res
            st.session_state.ui_schema = res["ui_schema"]
            st.write("Developing JIT Tool Code for each agent...")
            status.update(label="✅ Team Architected!", state="complete")

    except Exception as e:
        st.error(f"Error in architecture: {str(e)}")

# ---------- RENDER MISSION ----------
if st.session_state.plan:
    st.markdown(f"""
    <div class="mission-banner">
        <h3>🚀 Automation Objective: {st.session_state.plan['mission']}</h3>
        <p><b>Strategy:</b> {st.session_state.plan.get('execution_strategy', 'Standard Processing')}</p>
        <p><b>Agentic Framework:</b> {st.session_state.plan.get('framework', 'Agno')}</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Agent Team", "🔄 Workflow", "💻 Generated Code"])

    # ---------- TEAM TAB ----------
    with tab1:
        st.subheader("Specialized Agent Team")
        cols = st.columns(len(st.session_state.plan.get("agents", [])))
        for i, agent in enumerate(st.session_state.plan.get("agents", [])):
            with cols[i]:
                st.markdown(f"""
                <div class="agent-card">
                    <h4>{agent.get('name', 'Agent')}</h4>
                    <p><small>{agent.get('role', 'Specialist')}</small></p>
                    <p><b>Goal:</b> {agent.get('goal', 'Execute Mission')}</p>
                    <p><b>Tools:</b> {', '.join(agent.get('tools', []))}</p>
                </div>
                """, unsafe_allow_html=True)

    # ---------- WORKFLOW TAB ----------
    with tab2:
        st.subheader("Multi-Step Task Execution Strategy")
        for task in st.session_state.plan.get("tasks", []):
            st.markdown(f"""
            <div class="task-step">
                <b>Step {task.get('step', 'N/A')}: {task.get('name', 'Task')}</b><br>
                Assigned Agent: <code>{task.get('agent', 'Universal')}</code><br>
                <i>Description: {task.get('description', 'Processing mission strategy...')}</i><br>
                Tools utilized: {', '.join(task.get('tools', []))}
            </div>
            """, unsafe_allow_html=True)

    # ---------- CODE TAB ----------
    with tab3:
        st.subheader("🛠️ Component Source Code")
        st.caption("This is the self-contained Python code for the JIT-generated tools.")
        if "full_code" in st.session_state.plan:
            st.code(st.session_state.plan["full_code"], language="python")
        else:
            st.info("Code not yet architected.")
