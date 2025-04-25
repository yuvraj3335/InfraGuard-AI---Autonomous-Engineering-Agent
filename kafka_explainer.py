import os
import json
import random
from datetime import datetime, timedelta
from google.generativeai import GenerativeModel, configure

# Configure Gemini API
configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')

def generate_synthetic_kafka_logs(num_entries=10):
    """Generate synthetic Kafka logs."""
    logs = []
    base_time = datetime.now()
    for i in range(num_entries):
        log = {
            "timestamp": (base_time + timedelta(seconds=i)).isoformat(),
            "partition": random.randint(0, 5),
            "offset": i * 10,
            "consumer_offset": i * 10 - random.randint(0, 20)
        }
        logs.append(log)
    return logs

def calculate_synthetic_lag(logs):
    """Calculate lag from synthetic logs."""
    total_lag = 0
    for log in logs:
        lag = log["offset"] - log["consumer_offset"]
        if lag > 0:
            total_lag += lag
    return total_lag

def analyze_kafka_lag(lag, threshold=100):
    """Analyze Kafka lag and generate findings."""
    findings = [f"Total consumer lag: {lag} messages."]
    if lag > threshold:
        findings.append("High lag detected, indicating transaction delays.")
    return findings

def suggest_kafka_resolution(findings):
    """
    Use Gemini API to suggest Kafka lag resolutions.
    Fine-tuned prompt for Kafka performance optimization.
    """
    if not findings or "High lag" not in " ".join(findings):
        return ["Lag within acceptable limits."]
    prompt = (
        "You are a Kafka performance expert. Given the following findings from Kafka consumer lag analysis, "
        "suggest specific, actionable resolutions to reduce lag and optimize performance:\n\n"
        f"{'\n'.join(findings)}\n\n"
        "Provide concise recommendations in plain text, focusing on consumer optimization, partitioning, or scaling."
    )
    response = gemini_model.generate_content(prompt)
    return [response.text]

def analyze_kafka(num_entries=10):
    """
    Main function to analyze Kafka lag using synthetic logs and provide Gemini suggestions.
    """
    logs = generate_synthetic_kafka_logs(num_entries)
    lag = calculate_synthetic_lag(logs)
    findings = analyze_kafka_lag(lag)
    suggestions = suggest_kafka_resolution(findings)
    return {
        "findings": findings,
        "suggestions": suggestions
    }