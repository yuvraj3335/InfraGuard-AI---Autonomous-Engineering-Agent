import os
import requests
from google.generativeai import GenerativeModel, configure
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
from main import run_simulation
from iam_analyzer import analyze_iam
from kafka_explainer import analyze_kafka
from infra_summarizer import summarize_infra, simulate_pr_review
from decision_engine import process_incident
from action_generator import generate_action_content, send_teams_notification
import pandas as pd

# Configure Gemini API
configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')

# Database setup
Base = declarative_base()
class Incident(Base):
    __tablename__ = 'incidents'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    findings = Column(String)
    suggestions = Column(String)
    action = Column(String)
    status = Column(String, default='pending')

engine = create_engine('sqlite:///infraguard.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit UI
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("InfraGuard AI Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "yuvraj" and password == "password":  
            st.session_state.authenticated = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials")
else:
    st.title("InfraGuard AI - Dashboard")

    # Service descriptions for hover tooltips
    service_descriptions = {
        "IAM Policy Analysis": "Analyzes AWS IAM policies for security issues and suggests improvements.",
        "Kafka Lag Analysis": "Analyzes Kafka consumer lag using synthetic data and provides optimization suggestions.",
        "Infra Change Analysis": "Analyzes Terraform diffs from GitHub PRs for potential risks and suggests resolutions.",
        "PR Simulation": "Simulates PR reviews with memory and logging for historical context."
    }

    # Run Simulation
    if st.button("Run Full Simulation"):
        results = run_simulation()
        for result in results:
            incident = Incident(
                type=result['type'],
                findings=json.dumps(result['analysis']['findings']),
                suggestions=json.dumps(result['analysis']['suggestions']),
                action=result['decision']['action']
            )
            session.add(incident)
            session.commit()
            st.subheader(f"Incident Type: {result['type']}")
            st.markdown("**Findings:**")
            for finding in result['analysis']['findings']:
                st.markdown(f"- {finding}")
            st.markdown("**Suggestions:**")
            for suggestion in result['analysis']['suggestions']:
                st.markdown(f"- {suggestion}")
            st.markdown(f"**Action:** {result['decision']['action']}")
            if "notification" in result['decision']:
                st.markdown(f"**Notification:** {result['decision']['notification']}")

    # IAM Analysis Section
    with st.expander("IAM Policy Analysis"):
        st.markdown(
            f'<span title="{service_descriptions["IAM Policy Analysis"]}">IAM Policy Analysis</span>',
            unsafe_allow_html=True
        )
        role_name = st.text_input(
            "IAM Role Name (blank for all)",
            help="Enter a specific IAM role name or leave blank to analyze all roles.",
            key="iam_role"
        )
        if st.button("Analyze IAM"):
            analysis = analyze_iam([role_name] if role_name else None)
            decision = process_incident("iam", analysis)
            incident = Incident(
                type="iam",
                findings=json.dumps(analysis['findings']),
                suggestions=json.dumps(analysis['suggestions']),
                action=decision['action']
            )
            session.add(incident)
            session.commit()
            st.markdown("**Findings:**")
            for finding in analysis['findings']:
                st.markdown(f"- {finding}")
            st.markdown("**Suggestions:**")
            for suggestion in analysis['suggestions']:
                st.markdown(f"- {suggestion}")
            st.markdown(f"**Action:** {decision['action']}")
            st.markdown(f"**Validation:** {decision['validation']}")

    # Kafka Analysis Section
    with st.expander("Kafka Lag Analysis"):
        st.markdown(
            f'<span title="{service_descriptions["Kafka Lag Analysis"]}">Kafka Lag Analysis</span>',
            unsafe_allow_html=True
        )
        num_entries = st.number_input(
            "Number of synthetic log entries",
            min_value=1,
            value=10,
            help="Specify the number of synthetic Kafka log entries to generate for analysis."
        )
        if st.button("Analyze Kafka"):
            analysis = analyze_kafka(num_entries)
            decision = process_incident("kafka", analysis)
            incident = Incident(
                type="kafka",
                findings=json.dumps(analysis['findings']),
                suggestions=json.dumps(analysis['suggestions']),
                action=decision['action']
            )
            session.add(incident)
            session.commit()
            st.markdown("**Findings:**")
            for finding in analysis['findings']:
                st.markdown(f"- {finding}")
            st.markdown("**Suggestions:**")
            for suggestion in analysis['suggestions']:
                st.markdown(f"- {suggestion}")
            st.markdown(f"**Action:** {decision['action']}")
            st.markdown(f"**Validation:** {decision['validation']}")

    # Infra Analysis Section
    with st.expander("Infra Change Analysis"):
        st.markdown(
            f'<span title="{service_descriptions["Infra Change Analysis"]}">Infra Change Analysis</span>',
            unsafe_allow_html=True
        )
        repo_name = st.text_input(
            "GitHub Repo (e.g., user/repo)",
            help="Enter the GitHub repository name in the format 'user/repo'.",
            key="infra_repo"
        )
        pr_number = st.number_input(
            "PR Number",
            min_value=1,
            step=1,
            help="Enter the pull request number to analyze."
        )
        if st.button("Analyze Infra"):
            analysis = summarize_infra(repo_name, pr_number)
            decision = process_incident("infra", analysis)
            incident = Incident(
                type="infra",
                findings=json.dumps(analysis['findings']),
                suggestions=json.dumps(analysis['suggestions']),
                action=decision['action']
            )
            session.add(incident)
            session.commit()
            st.markdown("**Findings:**")
            for finding in analysis['findings']:
                st.markdown(f"- {finding}")
            st.markdown("**Suggestions:**")
            for suggestion in analysis['suggestions']:
                st.markdown(f"- {suggestion}")
            st.markdown(f"**Action:** {decision['action']}")
            st.markdown(f"**Validation:** {decision['validation']}")

    # PR Simulation Section
    with st.expander("PR Simulation"):
        st.markdown(
            f'<span title="{service_descriptions["PR Simulation"]}">PR Simulation</span>',
            unsafe_allow_html=True
        )
        pr_repo_name = st.text_input(
            "GitHub Repo (e.g., user/repo)",
            help="Enter the GitHub repository name for PR simulation.",
            key="pr_repo"
        )
        pr_number_sim = st.number_input(
            "PR Number for Simulation",
            min_value=1,
            step=1,
            help="Enter the pull request number to simulate."
        )
        if st.button("Simulate PR Review"):
            review_response = simulate_pr_review(pr_repo_name, pr_number_sim)
            st.write(f"**Review Response:** {review_response}")
            with open('infraguard.log', 'r') as log_file:
                st.text("**Log Output:**\n" + log_file.read())

    # Incident Dashboard
    st.subheader("Incident Dashboard")

    # Download Incident Log
    all_incidents = session.query(Incident).all()
    incident_data = []
    for inc in all_incidents:
        incident_data.append({
            "ID": inc.id,
            "Type": inc.type,
            "Timestamp": inc.timestamp.isoformat(),
            "Findings": inc.findings,
            "Suggestions": inc.suggestions,
            "Action": inc.action,
            "Status": inc.status
        })
    df = pd.DataFrame(incident_data)
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download Incident Log",
        data=csv,
        file_name="incident_log.csv",
        mime="text/csv"
    )

    # Display Pending Incidents
    incidents = session.query(Incident).filter(Incident.status == 'pending').all()
    for inc in incidents:
        st.markdown(f"**ID:** {inc.id} | **Type:** {inc.type} | **Action:** {inc.action} | **Status:** {inc.status}")
        if st.button("Approve", key=f"approve_{inc.id}"):
            inc.status = "approved"
            session.commit()
            st.success(f"Incident {inc.id} approved")
        if inc.action == "Suggest action":
            if st.button("Decline", key=f"decline_{inc.id}"):
                inc.status = "declined"
                session.commit()
                st.success(f"Incident {inc.id} declined")