import os
import requests
import csv
from dotenv import load_dotenv

# Load .env file (must contain JIRA_DOMAIN, JIRA_EMAIL, JIRA_TOKEN)
load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

AUTH_HEADER = {
    "Authorization": f"Basic {requests.auth._basic_auth_str(JIRA_EMAIL, JIRA_TOKEN)}",
    "Content-Type": "application/json"
}

JQL_QUERY = """
project = "Brand Growth Platform"
AND issuetype = Story
AND component IN (
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
)
AND (
    customFieldId_10119 IS EMPTY
    OR customFieldId_10119 NOT IN openSprints()
)
AND status NOT IN (Done, Canceled, "Won't Do")
"""

FIELDS = "summary,status,components,customFieldId_10119,issuelinks,issuetype"

def fetch_issues():
    all_issues = []
    max_results = 100
    start_at = 0

    while True:
        params = {
            "jql": JQL_QUERY,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": FIELDS
        }

        response = requests.get(
            f"{JIRA_DOMAIN}/rest/api/3/search",
            headers=AUTH_HEADER,
            params=params
        )

        data = response.json()
        print("🔎 Raw Jira Response:", data)

        if "errorMessages" in data:
            print("❌ Error in Jira API response:", data)
            return []

        issues = data.get("issues", [])
        if not issues:
            break

        all_issues.extend(issues)

        if start_at + max_results >= data.get("total", 0):
            break

        start_at += max_results

    return all_issues

def flatten_issue(issue):
    fields = issue["fields"]
    return {
        "Issue key": issue.get("key"),
        "Summary": fields.get("summary", ""),
        "Status": fields.get("status", {}).get("name", ""),
        "Components": ", ".join([c["name"] for c in fields.get("components", [])]),
        "Sprint": fields.get("customfield_10119", {}).get("name", "") if isinstance(fields.get("customfield_10119"), dict) else "",
        "Inward issue link (Blocks)": extract_link(issue, "blocks", inward=True),
        "Outward issue link (Blocks)": extract_link(issue, "blocks", inward=False)
    }

def extract_link(issue, link_type, inward=True):
    links = issue["fields"].get("issuelinks", [])
    direction = "inwardIssue" if inward else "outwardIssue"
    return ", ".join(
        l[direction]["key"]
        for l in links
        if l.get("type", {}).get("name", "").lower() == link_type and direction in l
    )

def save_to_csv(issues):
    output_path = "docs/jira_data.csv"
    os.makedirs("docs", exist_ok=True)

    if not issues:
        print("⚠️ No issues returned. Skipping CSV write.")
        return

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Issue key", "Summary", "Status", "Components", "Sprint",
            "Inward issue link (Blocks)", "Outward issue link (Blocks)"
        ])
        writer.writeheader()
        for issue in issues:
            writer.writerow(flatten_issue(issue))

    print(f"💾 Saved {len(issues)} issues to {output_path}")

if __name__ == "__main__":
    print("🔄 Fetching Jira issues...")
    issues = fetch_issues()
    print(f"✅ Retrieved {len(issues)} issues.")
    save_to_csv(issues)
    print("✅ Done.")

