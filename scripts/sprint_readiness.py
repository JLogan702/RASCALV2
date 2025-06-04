import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Load data
df = pd.read_csv("Evolve24 JIRA.csv")

# Filter to story tickets in a future sprint that are "To Do" or "Ready for Development"
valid_statuses = ["To Do", "Ready for Development"]
df = df[df["Issue Type"] == "Story"]
df = df[df["Sprint"].notna()]

# Group by team/component
components = df["Components"].fillna("Unassigned").unique()
team_data = {}

for comp in components:
    team_df = df[df["Components"] == comp]
    total = len(team_df)
    ready = len(team_df[team_df["Status"].isin(valid_statuses)])
    percent = round((ready / total * 100), 1) if total > 0 else 0

    team_data[comp] = {
        "total": total,
        "ready": ready,
        "percent": percent,
        "stoplight": "blinking_green.gif" if percent >= 80 else "blinking_yellow.gif" if percent >= 50 else "blinking_red.gif"
    }

# Load and render HTML template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sprint_readiness_template.html")
output = template.render(teams=team_data)

# Save HTML
with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ sprint_readiness.html generated")

