from google.generativeai import GenerativeModel, configure
import os
from langchain.memory import ConversationBufferMemory
import logging

# Configure logging
logging.basicConfig(filename='infraguard.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')


configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')


memory = ConversationBufferMemory(memory_key="chat_history")

# Configuration
CONFIG = {
    "risk_scores": {
        "iam": {"low": 1, "medium": 3, "high": 5},
        "kafka": {"low": 2, "medium": 4, "high": 6},
        "infra": {"low": 1, "medium": 3, "high": 5}
    },
    "execute_threshold": 5,
    "escalate_threshold": 3
}

def score_risk(incident_type, severity):
    """Score the risk of an issue based on type and severity."""
    return CONFIG["risk_scores"].get(incident_type.lower(), {}).get(severity.lower(), 0)

def decide_action(risk_score):
    """Decide action based on risk score."""
    if risk_score >= CONFIG["execute_threshold"]:
        return "Execute autonomous action"
    elif risk_score >= CONFIG["escalate_threshold"]:
        return "Escalate to team"
    return "Suggest action"

def validate_decision(incident_type, analysis, action):
    """
    Use Gemini API to validate the decision logic.
    Fine-tuned prompt for incident response validation.
    """
    prompt = (
        "You are an incident response expert. Given the following incident details and proposed action, "
        "validate if the action is appropriate and suggest improvements if necessary:\n\n"
        f"Incident Type: {incident_type}\nFindings: {', '.join(analysis['findings'])}\n"
        f"Proposed Action: {action}\n\n"
        "Provide a concise validation or correction in plain text."
    )
    response = gemini_model.generate_content(prompt)
    return response.text

def process_incident(incident_type, analysis):
    """Process an incident with memory and decide on an action."""
    # Retrieve past incidents from memory
    past_incidents = memory.load_memory_variables({"incident_type": incident_type}).get("chat_history", "")
    
    # Include past incidents in decision-making
    prompt = (
        f"Given past incidents: {past_incidents}\n"
        f"Current Incident Type: {incident_type}\nFindings: {', '.join(analysis['findings'])}\n"
        f"Suggestions: {', '.join(analysis['suggestions'])}\n"
        "Decide on the best action considering historical context."
    )
    
    # Use Gemini to decide action
    response = gemini_model.generate_content(prompt)
    action = response.text.strip()
    
    # Calculate risk score for consistency
    severity = "high" if any("risk" in f.lower() or "high" in f.lower() for f in analysis["findings"]) else "low"
    risk = score_risk(incident_type, severity)
    validation = validate_decision(incident_type, analysis, action)
    
    # Store the decision in memory
    memory.save_context(
        {"input": prompt},
        {"output": action}
    )
    
    # Log the decision
    logging.info(f"Incident Processed - Type: {incident_type}, Action: {action}, Risk: {risk}")
    
    return {
        "risk_score": risk,
        "action": action,
        "validation": validation
    }
