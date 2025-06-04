
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the CSV data
df = pd.read_csv("RASCAL_DB_Filter_Evolve24_JIRA.csv")

# Normalize and clean sprint data
df['Sprint'] = df['Sprint'].fillna("Unassigned")
df['Status'] = df['Status'].fillna("Unknown")
df['Components'] = df['Components'].fillna("No Component")

# Filter for story tickets only and future sprints (exclude active sprints logic if needed)
story_df = df[df['Issue Type'] == 'Story']

# Define readiness statuses
readiness_statuses = ['To Do', 'Ready for Development']

# Group by team/component
teams = story_df['Components'].unique()
results = {team: {'total': 0, 'ready': 0, 'statuses': {}} for team in teams}

for _, row in story_df.iterrows():
    team = row['Components']
    status = row['Status']
    sprint = row['Sprint']

    if sprint == "Unassigned":
        continue

    results[team]['total'] += 1
    if status in readiness_statuses:
        results[team]['ready'] += 1

    if status not in results[team]['statuses']:
        results[team]['statuses'][status] = 0
    results[team]['statuses'][status] += 1

# Compute readiness % and stoplight
def get_stoplight(percent):
    if percent >= 80:
        return "images/blinking_green.gif"
    elif percent >= 50:
        return "images/blinking_yellow.gif"
    return "images/blinking_red.gif"

for team in results:
    total = results[team]['total']
    ready = results[team]['ready']
    percent = (ready / total * 100) if total else 0
    results[team]['percent'] = round(percent)
    results[team]['stoplight'] = get_stoplight(percent)

# Render HTML
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('sprint_readiness_template.html')
output = template.render(data=results)

# Save output
with open("docs/sprint_readiness.html", "w") as f:
    f.write(output)

print("✅ Sprint Readiness dashboard generated.")
