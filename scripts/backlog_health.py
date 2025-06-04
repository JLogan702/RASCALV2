import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Load data
df = pd.read_csv("Evolve24 JIRA.csv")

# Filter to story tickets in the backlog
df = df[df["Issue Type"] == "Story"]
df = df[df["Sprint"].isna()]

# Backlog statuses considered groomed
groomed_statuses = ["New", "Grooming", "Backlog"]

components = df["Components"].fillna("Unassigned").unique()
team_data = {}

for comp in components:
    team_df = df[df["Components"] == comp]
    total = len(team_df)
    groomed = len(team_df[team_df["Status"].isin(groomed_statuses)])
    percent = round((groomed / total * 100), 1) if total > 0 else 0

    team_data[comp] = {
        "total": total,
        "groomed": groomed,
        "percent": percent,
        "stoplight": "blinking_green.gif" if percent >= 80 else "blinking_yellow.gif" if percent >= 50 else "blinking_red.gif"
    }

# Load and render HTML
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("backlog_health_template.html")
output = template.render(teams=team_data)

with open("docs/backlog_health.html", "w") as f:
    f.write(output)

print("✅ backlog_health.html generated")

