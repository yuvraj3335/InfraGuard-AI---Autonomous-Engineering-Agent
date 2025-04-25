import os
from github import Github
from google.generativeai import GenerativeModel, configure
from langchain.memory import ConversationBufferMemory
import logging

# Configure logging
logging.basicConfig(filename='infraguard.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Configure Gemini API
configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')

# Initialize LangChain memory for PR reviews
pr_memory = ConversationBufferMemory(memory_key="pr_history")

# Hardcoded fallback diff
SAMPLE_TERRAFORM_DIFF = """
+ resource "aws_security_group" "example" {
+   ingress {
+     from_port   = 22
+     to_port     = 22
+     protocol    = "tcp"
+     cidr_blocks = ["0.0.0.0/0"]
+   }
- resource "aws_security_group" "old" {
-   ingress {
-     from_port   = 80
-     to_port     = 80
-     protocol    = "tcp"
-     cidr_blocks = ["10.0.0.0/16"]
-   }
"""

def fetch_terraform_diffs(repo_name, pr_number):
    """
    Fetch Terraform diffs from a GitHub PR.
    Returns None if the fetch fails.
    """
    try:
        g = Github(os.getenv('GITHUB_TOKEN'))
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        files = pr.get_files()
        diffs = [file.patch for file in files if file.filename.endswith('.tf')]
        return diffs
    except Exception as e:
        print(f"Failed to fetch Terraform diffs: {e}")
        return None

def analyze_diff(diff_text):
    """
    Analyze Terraform diff by collecting both added and removed lines.
    Returns findings including the full diff text for further analysis.
    """
    lines = diff_text.split('\n')
    added_lines = [line for line in lines if line.strip().startswith('+')]
    removed_lines = [line for line in lines if line.strip().startswith('-')]
    findings = [
        f"Added: {len(added_lines)} lines.",
        f"Removed: {len(removed_lines)} lines.",
        "Diff content:",
        diff_text
    ]
    return findings

def suggest_diff_resolution(findings):
    """
    Use Gemini API to suggest Terraform diff resolutions based on full diff.
    Updated prompt to consider both added and removed lines.
    """
    diff_text = "\n".join(findings[2:])  # Extract diff content from findings
    prompt = (
        "You are a Terraform security expert. Analyze the following Terraform diff, which includes both added and removed lines. "
        "The lines starting with '-' were removed, and those starting with '+' were added in their place. "
        "Identify any potential risks or issues introduced by these changes, and evaluate how the new changes might affect "
        "the previous configurations. Suggest specific, actionable resolutions to mitigate any risks found:\n\n"
        f"{diff_text}\n\n"
        "Provide concise recommendations in plain text, focusing on secure configuration."
    )
    response = gemini_model.generate_content(prompt)
    return [response.text]

def summarize_infra(repo_name, pr_number):
    """
    Main function to summarize Terraform diffs with fallback and Gemini suggestions.
    """
    diffs = fetch_terraform_diffs(repo_name, pr_number)
    if diffs is None:
        print("GitHub fetch failed. Falling back to hardcoded diff.")
        diffs = [SAMPLE_TERRAFORM_DIFF]
    if not diffs:
        return {
            "findings": ["No Terraform changes detected."],
            "suggestions": ["No suggestions needed."]
        }
    findings = []
    for diff in diffs:
        findings.extend(analyze_diff(diff))
    suggestions = suggest_diff_resolution(findings)
    return {
        "findings": findings[:2] + ["See diff content below analyzed by Gemini."],
        "suggestions": suggestions
    }

def simulate_pr_review(repo_name, pr_number):
    """
    Simulate a PR review with memory and logging.
    """
    # Analyze the PR diff
    analysis = summarize_infra(repo_name, pr_number)
    
    # Retrieve past PR reviews from memory
    past_reviews = pr_memory.load_memory_variables({"repo_name": repo_name}).get("pr_history", "")
    
    # Simulate review with memory
    prompt = (
        f"Past PR Reviews: {past_reviews}\n"
        f"Review this PR:\n"
        f"Findings: {', '.join(analysis['findings'])}\n"
        f"Suggestions: {', '.join(analysis['suggestions'])}\n"
        "Provide a review comment considering past PR reviews."
    )
    
    # Use Gemini to generate review response
    response = gemini_model.generate_content(prompt)
    review_response = response.text.strip()
    
    # Log the review
    logging.info(f"PR Review Simulated - Repo: {repo_name}, PR: {pr_number}, Response: {review_response}")
    
    # Store in memory
    pr_memory.save_context(
        {"input": prompt},
        {"output": review_response}
    )
    
    return review_response