from iam_analyzer import analyze_iam
from kafka_explainer import analyze_kafka
from infra_summarizer import summarize_infra
from decision_engine import process_incident
from action_generator import generate_action_content, send_teams_notification

def run_simulation():
    """Run an end-to-end simulation of InfraGuard AI."""
    incidents = [
        {"type": "iam", "params": {"role_names": None}},
        {"type": "kafka", "params": {"num_entries": 10}},
        {"type": "infra", "params": {"repo_name": "user/repo", "pr_number": 1}}
    ]
    results = []
    for incident in incidents:
        if incident["type"] == "iam":
            analysis = analyze_iam(**incident["params"])
        elif incident["type"] == "kafka":
            analysis = analyze_kafka(**incident["params"])
        elif incident["type"] == "infra":
            analysis = summarize_infra(**incident["params"])
        
        decision = process_incident(incident["type"], analysis)
        if decision["action"] == "Execute autonomous action":
            content = generate_action_content(incident["type"], analysis)
            notification = send_teams_notification(content)
            decision["notification"] = notification
        results.append({
            "type": incident["type"],
            "analysis": analysis,
            "decision": decision
        })
    return results