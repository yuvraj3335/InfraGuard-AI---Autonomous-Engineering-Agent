InfraGuard AI
InfraGuard AI is an intelligent infrastructure analysis and incident management system that enhances security and performance across AWS IAM policies, Kafka consumer lag, and Terraform infrastructure changes. It uses the Gemini API for natural language processing and Streamlit for an intuitive UI, automating risk detection, resolution suggestions, and incident tracking.
Features

IAM Policy Analysis: Identifies over-permissive AWS IAM policies and suggests least-privilege alternatives.
Kafka Lag Analysis: Analyzes synthetic Kafka consumer lag data to detect bottlenecks and recommend optimizations.
Infra Change Analysis: Reviews Terraform diffs from GitHub PRs to flag risks and suggest secure configurations.
Incident Management: Tracks and manages incidents via a Streamlit dashboard with downloadable logs.
Automated Notifications: Sends alerts to Microsoft Teams for critical actions.
Simulation Mode: Runs a full analysis across all modules with one click.

Implemented Components

Streamlit UI (app.py): Central dashboard for simulations and incident management.
Database (infraguard.db): SQLite with SQLAlchemy for incident storage.
Analysis Modules:
iam_analyzer.py: IAM policy analysis using boto3.
kafka_explainer.py: Synthetic Kafka log generation and lag analysis.
infra_summarizer.py: Terraform diff analysis via PyGithub.
Each of them uses Lanchain memory ConversationBufferMemory for maintaing the conversation Context.


Decision Engine (decision_engine.py): Risk scoring and action decisions.
Action Generator (action_generator.py): Creates PR/ticket content and Teams notifications.
Simulation Orchestrator (main.py): Coordinates full simulations.

Technologies Used

Python 3.8+
Streamlit: Web UI framework.
Gemini API: NLP for suggestions and validations.
SQLAlchemy: ORM for SQLite.
boto3: AWS SDK for IAM.
PyGithub: GitHub API for PR diffs.
requests: Teams webhook notifications.
pandas: CSV generation for incident logs.
Langchain: for conversational context.

Setup Instructions

Clone the Repository:
git clone https://github.com/your-repo/infraguard-ai.git
cd infraguard-ai


Install Dependencies:
pip install -r requirements.txt

Requires: streamlit, sqlalchemy, boto3, google-generativeai, PyGithub, requests, pandas.

Set Environment Variables:

GEMINI_API_KEY: Gemini API key.
AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY: AWS credentials.
GITHUB_TOKEN: GitHub API token.
TEAMS_WEBHOOK_URL: Teams webhook URL.


Run the Application:
streamlit run app.py



Usage

Login: Use admin/password to access the dashboard.
Run Simulations: Click "Run Full Simulation" for a complete analysis.
Individual Analysis: Use expanders for IAM, Kafka, or Infra with custom inputs.
Manage Incidents: Approve/decline incidents and download logs as CSV.

Incident Workflow

Detection: Modules identify issues.
Decision: Risk scores trigger "Execute," "Escalate," or "Suggest" actions.
Notification: "Execute" actions send Teams alerts.
Management: Incidents are logged and managed in the dashboard.

Logging

Actions are logged to infraguard.log for auditing.

Future Enhancements

Implement real Kafka metrics.
Replace hardcoded login with OAuth.
Optimize for large-scale incident handling.

