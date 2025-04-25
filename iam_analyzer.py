import boto3
import json
import os
from google.generativeai import GenerativeModel, configure

# Configure Gemini API
configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = GenerativeModel('gemini-2.0-flash')

def fetch_iam_policies(role_names=None):
    """
    Fetch IAM policies from AWS for specified roles or all roles if none specified.
    Returns None if the fetch fails.
    """
    try:
        iam = boto3.client(
            'iam',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        policies = []
        if role_names:
            for role_name in role_names:
                attached_policies = iam.list_attached_role_policies(RoleName=role_name)
                for policy in attached_policies['AttachedPolicies']:
                    policy_version = iam.get_policy_version(
                        PolicyArn=policy['PolicyArn'],
                        VersionId=policy['DefaultVersionId']
                    )
                    policies.append(policy_version['PolicyVersion']['Document'])
        else:
            paginator = iam.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page['Roles']:
                    attached_policies = iam.list_attached_role_policies(RoleName=role['RoleName'])
                    for policy in attached_policies['AttachedPolicies']:
                        policy_version = iam.get_policy_version(
                            PolicyArn=policy['PolicyArn'],
                            VersionId=policy['DefaultVersionId']
                        )
                        policies.append(policy_version['PolicyVersion']['Document'])
        return policies
    except Exception as e:
        print(f"Failed to fetch IAM policies: {e}")
        return None

def analyze_iam_policies(policies):
    """
    Analyze IAM policies for over-permissive actions.
    Include the full statement in findings for detailed analysis.
    """
    findings = []
    for policy in policies:
        for statement in policy.get('Statement', []):
            if statement['Effect'] == 'Allow' and '*' in statement.get('Resource', []):
                findings.append(f"High risk: Over-permissive statement: {json.dumps(statement)}")
    return findings

def suggest_least_privilege_policy(findings):
    """
    Use Gemini API to suggest least-privilege policy changes based on detailed findings.
    Returns original policy, suggested policy, and reasoning.
    """
    if not findings:
        return ["No changes needed."]
    prompt = (
        "You are an AWS IAM security expert. Below are findings from IAM policy analysis, each describing an over-permissive statement in JSON format. "
        "For each finding, provide the following:\n"
        "1. The original policy statement (as provided in the finding).\n"
        "2. A suggested policy statement with a more restrictive resource specification, adhering to the principle of least privilege.\n"
        "3. An explanation of why this change is necessary.\n\n"
        "Format your response clearly, referencing each finding. Here are the findings:\n\n"
        + "\n\n".join(findings)
    )
    response = gemini_model.generate_content(prompt)
    return [response.text]

# Hardcoded fallback policy
SAMPLE_IAM_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "*"
        }
    ]
}

def analyze_iam(role_names=None):
    """
    Main function to analyze IAM policies with fallback and Gemini suggestions.
    """
    policies = fetch_iam_policies(role_names)
    if policies is None:
        print("AWS fetch failed. Falling back to hardcoded sample policy.")
        policies = [SAMPLE_IAM_POLICY]
    findings = analyze_iam_policies(policies)
    suggestions = suggest_least_privilege_policy(findings)
    return {
        "findings": findings or ["No issues found."],
        "suggestions": suggestions
    }