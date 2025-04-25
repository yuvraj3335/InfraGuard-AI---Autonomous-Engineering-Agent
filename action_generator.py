import os
import requests
from google.generativeai import GenerativeModel, configure
import logging

# Configure logging
logging.basicConfig(filename='infraguard.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Configure Gemini API
configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')

def generate_action_content(incident_type, analysis):
    """
    Generate PR or ticket content using Gemini for formatting.
    Fine-tuned prompt for actionable incident reports.
    """
    prompt = (
        "You are an incident response specialist. Given the following incident details, "
        "generate a concise, human-readable description for a pull request or ticket:\n\n"
        f"Incident Type: {incident_type}\nFindings: {', '.join(analysis['findings'])}\n"
        f"Suggestions: {', '.join(analysis['suggestions'])}\n\n"
        "Format the output as a plain text description."
    )
    response = gemini_model.generate_content(prompt)
    content = response.text
    logging.info(f"Action Content Generated - Type: {incident_type}, Content: {content}")
    return content

def send_teams_notification(content):
    """
    Send notification to Microsoft Teams.
    Falls back to console output if the webhook fails.
    """
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
    try:
        payload = {"text": content}
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            logging.info(f"Teams Notification Sent - Content: {content}")
            return {"status": "Notification sent", "content": content}
        else:
            logging.warning(f"Teams Webhook Failed - Status: {response.status_code}, Content: {content}")
            print(f"Teams webhook failed: {response.status_code}. Falling back to console.")
            print(f"Teams Notification:\n{content}")
            return {"status": "Console fallback", "content": content}
    except Exception as e:
        logging.error(f"Teams Notification Error - Exception: {e}, Content: {content}")
        print(f"Teams notification error: {e}. Falling back to console.")
        print(f"Teams Notification:\n{content}")
        return {"status": "Console fallback", "content": content}