import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load data
csv_path = os.path.join(os.path.dirname(__file__), "../Evolve24 JIRA.csv")
df = pd.read_csv(csv_path)

# Filter for Story tickets and exclude Done/Canceled/Won’t Do
df = df[
    (df["Issue Type"] == "Story") &
    (~df["Status"].isin(["Done", "Canceled", "Won't Do"]))
]

# Define backlog statuses and team mapping
backlog_statuses = ["New", "Grooming", "Backlog"]
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

    backlog_df = team_df[
        (team_df["Sprint"].isnull()) |
        (team_df["Sprint"].str.strip() == "")
    ]

    total = len(backlog_df)
    healthy = len(backlog_df[backlog_df["Status"].isin(backlog_statuses)])
    status_counts = backlog_df["Status"].value_counts().to_dict()

    health_pct = round((healthy / total) * 100, 1) if total > 0 else 0

    if health_pct >= 80:
        stoplight = "images/blinking_green.gif"
    elif health_pct >= 50:
        stoplight = "images/blinking_yellow.gif"
    else:
        stoplight = "images/blinking_red.gif"

    team_data[team] = {
        "total": total,
        "healthy": healthy,
        "percent": health_pct,
        "stoplight": stoplight,
        "statuses": status_counts
    }

# Load and render the template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("backlog_health_template.html")
output = template.render(teams=team_data)

# Save the rendered HTML
with open("docs/backlog_health.html", "w") as f:
    f.write(output)

print("✅ Backlog Health dashboard generated: docs/backlog_health.html")

