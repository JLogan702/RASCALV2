import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load CSV
csv_path = os.path.join(os.path.dirname(__file__), "../Evolve24 JIRA.csv")
df = pd.read_csv(csv_path)

# Filter: only stories, exclude Done/Canceled/Won't Do
df = df[
    (df["Issue Type"] == "Story") &
    (~df["Status"].isin(["Done", "Canceled", "Won't Do"]))
]

# Define component-to-team mapping
teams = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

# Prep counters
readiness_statuses = ["Ready for Development", "To Do"]
backlog_statuses = ["New", "Grooming", "Backlog"]
summary = {}

for comp, team in teams.items():
    team_df = df[df["Components"] == comp]

    # Sprint Readiness: only count stories in future sprints
    future_sprint_df = team_df[team_df["Sprint"].notna()]
    readiness_total = len(future_sprint_df)
    readiness_ready = len(future_sprint_df[future_sprint_df["Status"].isin(readiness_statuses)])
    readiness_pct = round((readiness_ready / readiness_total) * 100, 1) if readiness_total else 0

    # Backlog Health: only backlog stories NOT in active sprints
    backlog_df = team_df[team_df["Sprint"].isna()]
    backlog_total = len(backlog_df)
    backlog_groomed = len(backlog_df[backlog_df["Status"].isin(backlog_statuses)])
    backlog_pct = round((backlog_groomed / backlog_total) * 100, 1) if backlog_total else 0

    # Average of the two for program health
    score = round((readiness_pct + backlog_pct) / 2, 1)

    # Stoplight
    stoplight = "images/blinking_green.gif" if score >= 80 else \
                "images/blinking_yellow.gif" if score >= 50 else \
                "images/blinking_red.gif"

    summary[team] = {
        "readiness_pct": readiness_pct,
        "backlog_pct": backlog_pct,
        "combined_score": score,
        "stoplight": stoplight
    }

# Program-level roll-up
overall_score = round(sum(t["combined_score"] for t in summary.values()) / len(summary), 1)
overall_stoplight = "images/blinking_green.gif" if overall_score >= 80 else \
                    "images/blinking_yellow.gif" if overall_score >= 50 else \
                    "images/blinking_red.gif"

# Final output dict
render_data = {
    "summary": summary,
    "overall_score": overall_score,
    "overall_stoplight": overall_stoplight
}

# Jinja2 render
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("program_summary_template.html")
output = template.render(data=render_data)

# Save to file
with open("docs/index.html", "w") as f:
    f.write(output)

print("✅ Program Summary dashboard generated: docs/index.html")

