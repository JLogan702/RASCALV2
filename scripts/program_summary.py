import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Load CSV
df = pd.read_csv("Evolve24 JIRA.csv")

# Filter only stories
df = df[df["Issue Type"] == "Story"]

# Define core teams
core_teams = [
    "Engineering - Product",
    "Engineering - Platform",
    "Engineering - AI Ops",
    "Design",
    "Data Science"
]

# Backlog Health statuses
groomed_statuses = {"New", "Grooming", "Backlog"}
# Sprint Readiness statuses
ready_statuses = {"To Do", "Ready for Development"}

# Define scoring function
def calculate_scores(team_name):
    team_df = df[df["Components"] == team_name]
    future_sprints = team_df[team_df["Sprint"].notna()]

    # Sprint Readiness
    readiness_df = future_sprints[future_sprints["Status"].isin(ready_statuses)]
    readiness_score = (len(readiness_df) / len(future_sprints)) * 100 if len(future_sprints) > 0 else 0

    # Backlog Health
    backlog_df = team_df[team_df["Status"].isin(groomed_statuses)]
    backlog_score = (len(backlog_df) / len(team_df)) * 100 if len(team_df) > 0 else 0

    return readiness_score, backlog_score

# Collect scores
scores = []
for team in core_teams:
    readiness, backlog = calculate_scores(team)
    scores.append({
        "team": team,
        "readiness": readiness,
        "backlog": backlog
    })

# Average program scores
avg_readiness = round(sum(s["readiness"] for s in scores) / len(scores), 1)
avg_backlog = round(sum(s["backlog"] for s in scores) / len(scores), 1)
overall_score = round((avg_readiness + avg_backlog) / 2, 1)

# Determine stoplight
if overall_score >= 80:
    stoplight = "blinking_green.gif"
elif overall_score >= 50:
    stoplight = "blinking_yellow.gif"
else:
    stoplight = "blinking_red.gif"

# Render template
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("program_summary_template.html")

output = template.render(
    data={
        "readiness": avg_readiness,
        "backlog": avg_backlog,
        "overall": overall_score,
        "stoplight": stoplight
    }
)

with open("docs/index.html", "w") as f:
    f.write(output)

print("✅ index.html (Program Summary) generated")

