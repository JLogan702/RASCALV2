import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re

CSV_PATH = "docs/jira_data.csv"
TEMPLATE_FILE = "dependencies_template.html"
OUTPUT_FILE = "docs/dependencies.html"
SPRINT_FIELD = "Sprint"
TEAM_FIELD = "Components"
STATUS_FIELD = "Status"
ISSUE_TYPE_FIELD = "Issue Type"
INWARD_FIELD = "Inward issue link (Blocks)"
OUTWARD_FIELD = "Outward issue link (Blocks)"

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

def calculate_dependencies(df):
    data = []

    for team in TEAM_ORDER:
        team_df = df[df[TEAM_FIELD] == team]

        blockers = team_df[INWARD_FIELD].dropna()
        blockees = team_df[OUTWARD_FIELD].dropna()

        total = len(team_df)
        blocking_count = len(blockers) + len(blockees)

        if total > 0:
            score = round(((total - blocking_count) / total) * 100, 1)
        else:
            score = 0.0

        if score >= THRESHOLDS["green"]:
            stoplight = "blinking_green.gif"
        elif score >= THRESHOLDS["yellow"]:
            stoplight = "blinking_yellow.gif"
        else:
            stoplight = "blinking_red.gif"

        explanation = (
            f"{score}% of this team's story tickets are not blocked by or blocking other tickets. "
            f"This is a proxy for overall delivery independence. {blocking_count} total dependencies were detected."
        )

        data.append({
            "team": team,
            "total": total,
            "blocking": blocking_count,
            "score": score,
            "stoplight": stoplight,
            "explanation": explanation
        })

    return data

def render_html(team_data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(TEMPLATE_FILE)
    output = template.render(teams=team_data)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("✅ dependencies.html generated")

def main():
    df = pd.read_csv(CSV_PATH)
    df = df[(df[ISSUE_TYPE_FIELD] == "Story") & (df[STATUS_FIELD] != "Done")]
    team_data = calculate_dependencies(df)
    render_html(team_data)

if __name__ == "__main__":
    main()

