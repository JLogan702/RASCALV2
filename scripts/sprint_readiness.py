import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Set up Jinja2 environment
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
env = Environment(loader=FileSystemLoader(template_dir))

# Load CSV data
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'RASCAL_DB_Filter_Evolve24_JIRA.csv'))
df = pd.read_csv(csv_path)

# Prepare data
df['Sprint'] = df['Sprint'].fillna("Unassigned")
df['Status'] = df['Status'].fillna("Unknown")
df['Components'] = df['Components'].fillna("No Component")

# Filter for story tickets only
story_df = df[df['Issue Type'] == 'Story']
future_sprints = story_df[story_df['Sprint'].str.contains("Sprint", case=False, na=False)]

# Define readiness statuses
ready_statuses = ['To Do', 'Ready for Development']

# Group by team
teams = future_sprints['Components'].unique()
results = {}

for team in teams:
    team_df = future_sprints[future_sprints['Components'] == team]
    total = len(team_df)
    ready = team_df['Status'].isin(ready_statuses).sum()

    if total == 0:
        percent = 0
    else:
        percent = round((ready / total) * 100, 1)

    # Stoplight
    if percent >= 80:
        stoplight = "images/blinking_green.gif"
    elif percent >= 50:
        stoplight = "images/blinking_yellow.gif"
    else:
        stoplight = "images/blinking_red.gif"

    # Count per status
    status_counts = team_df['Status'].value_counts().to_dict()

    results[team] = {
        "total": total,
        "ready": ready,
        "percent": percent,
        "stoplight": stoplight,
        "status_counts": status_counts
    }

# DEBUG: You can print this if needed
# print(json.dumps(results, indent=2))

# Render template
template = env.get_template("sprint_readiness_template.html")
output = template.render(teams=results)

with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ Sprint Readiness page generated.")

