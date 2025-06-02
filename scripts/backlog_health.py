import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re

CSV_PATH = "docs/jira_data.csv"
TEMPLATE_FILE = "backlog_health_template.html"
OUTPUT_FILE = "docs/backlog_health.html"
SPRINT_FIELD = "Sprint"
TEAM_FIELD = "Components"
STATUS_FIELD = "Status"
ISSUE_TYPE_FIELD = "Issue Type"

BACKLOG_STATUSES = ["New", "Grooming", "Backlog"]

TEAM_ORDER = [
    "Data Science",
    "Design",
    "Engineering - AI Ops",
    "Engineering - Platform",
    "Engineering - Product"
]

THRESHOLDS = {
    "green": 80,
    "yellow": 50
}

def extract_end_date(sprint_str):
    if pd.isna(sprint_str):
        return None
    date_matches = re.findall(r"(\d{1,2})[\/-](\d{1,2})", sprint_str)
    if date_matches:
        try:
            month, day = map(int, date_matches[-1])
            year = datetime.now().year
            return datetime(year, month, day)
        except ValueError:
            return None
    return None

def calculate_team_data(df):
    data = []
    today = datetime.now()

    for team in TEAM_ORDER:
        team_df = df[df[TEAM_FIELD] == team]

        # Consider only tickets NOT assigned to a future sprint
        backlog_df = team_df[team_df[SPRINT_FIELD].apply(
            lambda s: extract_end_date(s) is None or extract_end_date(s) <= today)]

        total = len(backlog_df)
        relevant = backlog_df[backlog_df[STATUS_FIELD].isin(BACKLOG_STATUSES)]
        status_counts = backlog_df[STATUS_FIELD].value_counts().to_dict()

        if total > 0:
            percent = round((len(relevant) / total) * 100, 1)
        else:
            percent = 0.0

        if percent >= THRESHOLDS["green"]:
            stoplight = "blinking_green.gif"
        elif percent >= THRESHOLDS["yellow"]:
            stoplight = "blinking_yellow.gif"
        else:
            stoplight = "blinking_red.gif"

        data.append({
            "team": team,
            "total": total,
            "relevant": len(relevant),
            "percent": percent,
            "stoplight": stoplight,
            "status_counts": status_counts
        })

    return data

def render_html(team_data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(TEMPLATE_FILE)
    output = template.render(teams=team_data)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("✅ backlog_health.html generated")

def main():
    df = pd.read_csv(CSV_PATH)
    df = df[(df[ISSUE_TYPE_FIELD] == "Story") & (df[STATUS_FIELD] != "Done")]
    team_data = calculate_team_data(df)
    render_html(team_data)

if __name__ == "__main__":
    main()

