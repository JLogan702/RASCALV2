import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the CSV data
csv_path = os.path.join(os.path.dirname(__file__), "../Evolve24 JIRA.csv")
df = pd.read_csv(csv_path)

# Filter for Story tickets only, excluding Done/Canceled/Won’t Do
df = df[
    (df["Issue Type"] == "Story") &
    (~df["Status"].isin(["Done", "Canceled", "Won't Do"]))
]

# Define relevant statuses and teams
readiness_statuses = ["Ready for Development", "To Do"]
teams = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

team_data = {}

for comp, team in teams.items():
    team_df = df[df["Components"] == comp]

    future_sprint_df = team_df[team_df["Sprint"].notnull()]
    total = len(future_sprint_df)
    ready = len(future_sprint_df[future_sprint_df["Status"].isin(readiness_statuses)])

    status_counts = future_sprint_df["Status"].value_counts().to_dict()
    readiness_pct = round((ready / total) * 100, 1) if total > 0 else 0

    if readiness_pct >= 80:
        stoplight = "images/blinking_green.gif"
    elif readiness_pct >= 50:
        stoplight = "images/blinking_yellow.gif"
    else:
        stoplight = "images/blinking_red.gif"

    team_data[team] = {
        "total": total,
        "ready": ready,
        "percent": readiness_pct,
        "stoplight": stoplight,
        "statuses": status_counts
    }

# Load and render the template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sprint_readiness_template.html")
output = template.render(teams=team_data)

# Save the rendered HTML
with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ Sprint Readiness dashboard generated: docs/sprint_readiness.html")

