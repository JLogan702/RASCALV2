import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

JQL = """
project in ("Brand Growth Platform")
AND issuetype = Story
AND component in (
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
)
AND (
    sprint IS EMPTY
    OR sprint NOT IN openSprints()
)
AND status != Done
"""

HEADERS = {
    "Authorization": f"Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}",
    "Content-Type": "application/json"
}

def fetch_issues():
    issues = []
    start_at = 0
    max_results = 100

    while True:
        response = requests.get(
            f"{JIRA_DOMAIN}/rest/api/3/search",
            headers=HEADERS,
            params={
                "jql": JQL,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": "summary,status,components,issuetype,sprint,customfield_10020,issuelinks"
            }
        )
        data = response.json()
        issues.extend(data.get("issues", []))

        if start_at + max_results >= data["total"]:
            break
        start_at += max_results

    return issues

def parse_issues(raw_issues):
    rows = []
    for issue in raw_issues:
        fields = issue["fields"]
        components = [comp["name"] for comp in fields.get("components", [])]
        sprint_name = fields.get("customfield_10020", [{}])[0].get("name") if fields.get("customfield_10020") else None
        inward_links = [link["inwardIssue"]["key"] for link in fields.get("issuelinks", []) if "inwardIssue" in link and link.get("type", {}).get("name") == "Blocks"]
        outward_links = [link["outwardIssue"]["key"] for link in fields.get("issuelinks", []) if "outwardIssue" in link and link.get("type", {}).get("name") == "Blocks"]

        rows.append({
            "Issue key": issue["key"],
            "Summary": fields.get("summary", "N/A"),
            "Status": fields.get("status", {}).get("name", "Unknown"),
            "Components": ", ".join(components),
            "Sprint": sprint_name,
            "Inward issue link (Blocks)": ", ".join(inward_links),
            "Outward issue link (Blocks)": ", ".join(outward_links),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("🔄 Fetching Jira issues...")
    issues = fetch_issues()
    df = parse_issues(issues)
    df.to_csv("docs/jira_data.csv", index=False)
    print("✅ jira_data.csv updated.")

