# 🚨 InfraGuard AI

**InfraGuard AI** is an intelligent infrastructure analysis and incident management system that enhances security and performance across AWS IAM policies, Kafka consumer lag, and Terraform infrastructure changes.

It leverages the **Gemini API** for natural language processing and **Streamlit** for an intuitive UI — automating risk detection, resolution suggestions, and incident tracking.

---

## ✨ Features

- **IAM Policy Analysis:** Detects over-permissive AWS IAM policies and recommends least-privilege alternatives.
- **Kafka Lag Analysis:** Analyzes synthetic Kafka consumer lag data to identify bottlenecks and suggest improvements.
- **Infra Change Analysis:** Flags risky Terraform GitHub PR diffs and suggests secure configurations.
- **Incident Management:** Interactive Streamlit dashboard to track incidents and download logs.
- **Automated Notifications:** Sends alerts to Microsoft Teams for critical actions.
- **Simulation Mode:** One-click full simulation of all analysis modules.

---

## 🧩 Implemented Components

- **Streamlit UI (`app.py`)**: Central dashboard for simulation and incident handling.
- **Database (`infraguard.db`)**: Uses SQLite with SQLAlchemy ORM.
- **Analysis Modules:**
  - `iam_analyzer.py`: IAM policy analysis using `boto3`.
  - `kafka_explainer.py`: Simulated Kafka logs and lag analysis.
  - `infra_summarizer.py`: Terraform diff analysis using `PyGithub`.

> All modules utilize `Langchain`’s `ConversationBufferMemory` for context-aware processing.

- **Decision Engine (`decision_engine.py`)**: Assigns risk scores and actions.
- **Action Generator (`action_generator.py`)**: Prepares PR/ticket messages and Teams notifications.
- **Simulation Orchestrator (`main.py`)**: Runs full simulation across all modules.

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **Streamlit** – Web UI framework
- **Gemini API** – NLP-based analysis
- **SQLAlchemy** – ORM for SQLite
- **boto3** – AWS SDK for IAM analysis
- **PyGithub** – GitHub API client
- **requests** – For Teams webhook alerts
- **pandas** – CSV generation
- **Langchain** – Conversational memory and context handling

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/infraguard-ai.git
cd infraguard-ai


### 2. Install Dependencies

```bash
pip install -r requirements.txt


### 3. Set Env variable

### 4. Run the app - streamlit run app.py



# 🚨 InfraGuard AI

**InfraGuard AI** is an intelligent infrastructure analysis and incident management system that enhances security and performance across AWS IAM policies, Kafka consumer lag, and Terraform infrastructure changes.

It leverages the **Gemini API** for natural language processing and **Streamlit** for an intuitive UI — automating risk detection, resolution suggestions, and incident tracking.

---

## ✨ Features

- **IAM Policy Analysis:** Detects over-permissive AWS IAM policies and recommends least-privilege alternatives.
- **Kafka Lag Analysis:** Analyzes synthetic Kafka consumer lag data to identify bottlenecks and suggest improvements.
- **Infra Change Analysis:** Flags risky Terraform GitHub PR diffs and suggests secure configurations.
- **Incident Management:** Interactive Streamlit dashboard to track incidents and download logs.
- **Automated Notifications:** Sends alerts to Microsoft Teams for critical actions.
- **Simulation Mode:** One-click full simulation of all analysis modules.

---

## 🧩 Implemented Components

- **Streamlit UI (`app.py`)**: Central dashboard for simulation and incident handling.
- **Database (`infraguard.db`)**: Uses SQLite with SQLAlchemy ORM.
- **Analysis Modules:**
  - `iam_analyzer.py`: IAM policy analysis using `boto3`.
  - `kafka_explainer.py`: Simulated Kafka logs and lag analysis.
  - `infra_summarizer.py`: Terraform diff analysis using `PyGithub`.

> All modules utilize `Langchain`’s `ConversationBufferMemory` for context-aware processing.

- **Decision Engine (`decision_engine.py`)**: Assigns risk scores and actions.
- **Action Generator (`action_generator.py`)**: Prepares PR/ticket messages and Teams notifications.
- **Simulation Orchestrator (`main.py`)**: Runs full simulation across all modules.

---

## 🛠️ Technologies Used

- **Python 3.8+**
- **Streamlit** – Web UI framework
- **Gemini API** – NLP-based analysis
- **SQLAlchemy** – ORM for SQLite
- **boto3** – AWS SDK for IAM analysis
- **PyGithub** – GitHub API client
- **requests** – For Teams webhook alerts
- **pandas** – CSV generation
- **Langchain** – Conversational memory and context handling

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/infraguard-ai.git
cd infraguard-ai


### 2. Install Dependencies

```bash
pip install -r requirements.txt


### 3. Set Env variable

### 4. Run the app - streamlit run app.py
