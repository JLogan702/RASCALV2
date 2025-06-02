import pandas as pd
from jinja2 import Environment, FileSystemLoader

CSV_PATH = "docs/jira_data.csv"
TEMPLATE_PATH = "templates"
OUTPUT_PATH = "docs/sprint_readiness.html"

SPRINT_FIELD = "Sprint"
STATUS_FIELD = "Status"
COMPONENT_FIELD = "Components"
ISSUE_TYPE_FIELD = "Issue Type"

READY_STATUSES = ["To Do", "Ready for Development"]
EXCLUDED_STATUSES = ["Done"]

TEAM_ORDER = [
    "Data Science", "Design", "Engineering - AI Ops", "Engineering - Platform", "Engineering - Product"
]

def prepare_data(df):
    teams = {}
    df = df[df[ISSUE_TYPE_FIELD] == "Story"]
    df = df[~df[STATUS_FIELD].isin(EXCLUDED_STATUSES)]

    for team in TEAM_ORDER:
        team_df = df[df[COMPONENT_FIELD] == team]
        future_df = team_df[team_df[SPRINT_FIELD].notnull()]
        ready = future_df[future_df[STATUS_FIELD].isin(READY_STATUSES)]
        total = len(future_df)
        score = round(len(ready) / total * 100, 1) if total > 0 else 0

        if score >= 80:
            light = "blinking_green.gif"
        elif score >= 50:
            light = "blinking_yellow.gif"
        else:
            light = "blinking_red.gif"

        status_counts = future_df[STATUS_FIELD].value_counts().to_dict()
        teams[team] = {
            "total": total,
            "ready": len(ready),
            "score": score,
            "light": light,
            "statuses": status_counts
        }
    return teams

def render_html(team_data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template("sprint_readiness_template.html")
    output = template.render(team_data=team_data, team_order=TEAM_ORDER)
    with open(OUTPUT_PATH, "w") as f:
        f.write(output)

def main():
    df = pd.read_csv(CSV_PATH)
    team_data = prepare_data(df)
    render_html(team_data)

if __name__ == "__main__":
    main()

