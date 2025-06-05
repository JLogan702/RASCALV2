import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Define correct template path
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
env = Environment(loader=FileSystemLoader(template_dir))

print(f"Template search path: {template_dir}")
print(f"Available templates: {os.listdir(template_dir)}")

# Load data
df = pd.read_csv("RASCAL_DB_Filter_Evolve24_JIRA.csv")

# Normalize and clean
df['Sprint'] = df['Sprint'].fillna("Unassigned")
df['Status'] = df['Status'].fillna("Unknown")
df['Components'] = df['Components'].fillna("No Component")

# Filter stories in backlog statuses and future sprints only
story_df = df[
    (df['Issue Type'] == 'Story') &
    (~df['Status'].isin(['Done', 'Cancelled', 'Won\'t Do'])) &
    (df['Sprint'] == 'Unassigned')
]

# Define backlog health statuses
backlog_statuses = ['New', 'Grooming', 'Backlog']

# Aggregate by team
teams = story_df['Components'].unique()
summary = {}

for team in teams:
    team_df = story_df[story_df['Components'] == team]
    total = len(team_df)
    relevant = team_df[team_df['Status'].isin(backlog_statuses)]
    relevant_count = len(relevant)

    summary[team] = {
        "total": total,
        "healthy": relevant_count,
        "statuses": team_df['Status'].value_counts().to_dict(),
        "percent": int((relevant_count / total) * 100) if total > 0 else 0,
        "stoplight": "images/blinking_red.gif"  # default
    }

    percent = summary[team]["percent"]
    if percent >= 80:
        summary[team]["stoplight"] = "images/blinking_green.gif"
    elif percent >= 50:
        summary[team]["stoplight"] = "images/blinking_yellow.gif"

# Render HTML
template = env.get_template("backlog_health_template.html")
html = template.render(summary=summary)

# Output path
with open("docs/backlog_health.html", "w") as f:
    f.write(html)

print("✅ backlog_health.html rendered successfully.")

