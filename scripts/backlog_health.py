import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the Jira CSV
df = pd.read_csv("RASCAL_DB_Filter_Evolve24_JIRA.csv")

# Normalize key fields
df['Sprint'] = df['Sprint'].fillna("Unassigned")
df['Status'] = df['Status'].fillna("Unknown")
df['Components'] = df['Components'].fillna("No Component")

# Filter to Story tickets only
df = df[df['Issue Type'] == 'Story']

# Backlog statuses considered healthy
healthy_statuses = ["New", "Grooming", "Backlog"]

summary = {}

# Iterate over teams/components
for team in sorted(df['Components'].unique()):
    team_df = df[df['Components'] == team]

    # Filter to future/backlog (non-active sprints or unassigned)
    backlog_df = team_df[(team_df['Sprint'] == "Unassigned") | (~team_df['Sprint'].str.contains("active", case=False))]

    total = len(backlog_df)
    healthy = len(backlog_df[backlog_df['Status'].isin(healthy_statuses)])
    percent = int((healthy / total) * 100) if total > 0 else 0
    status_counts = backlog_df['Status'].value_counts().to_dict()

    # Determine stoplight
    def stoplight(percent):
        if percent >= 80:
            return "images/blinking_green.gif"
        elif percent >= 50:
            return "images/blinking_yellow.gif"
        return "images/blinking_red.gif"

    summary[team] = {
        "total": total,
        "healthy": healthy,
        "percent": percent,
        "stoplight": stoplight(percent),
        "status_counts": status_counts,  # 🔥 Must match template!
    }

# Jinja2 setup
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("backlog_health_template.html")

# Render and write to HTML
html = template.render(summary=summary)

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'backlog_health.html'))
with open(output_path, "w") as f:
    f.write(html)

print(f"✅ Backlog Health dashboard generated at: {output_path}")

