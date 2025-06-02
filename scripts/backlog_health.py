import pandas as pd
from jinja2 import Environment, FileSystemLoader

CSV_PATH = "docs/jira_data.csv"
TEMPLATE_PATH = "templates"
OUTPUT_PATH = "docs/backlog_health.html"

SPRINT_FIELD = "Sprint"
TEAM_FIELD = "Components"
STATUS_FIELD = "Status"
ISSUE_TYPE_FIELD = "Issue Type"

RELEVANT_STATUSES = ["New", "Grooming", "Backlog"]
EXCLUDED_STATUSES = ["Done"]

THRESHOLDS = {
    "green": 80,
    "yellow": 50
}

TEAM_ORDER = [
    "Data Science", "Design", "Engineering - AI Ops", "Engineering - Platform", "Engineering - Product"
]

def prepare_data(df):
    teams = {}
    df = df[(df[ISSUE_TYPE_FIELD] == "Story") & (~df[STATUS_FIELD].isin(EXCLUDED_STATUSES))]

    for team in TEAM_ORDER:
        team_df = df[df[TEAM_FIELD] == team]
        backlog_df = team_df[(team_df[SPRINT_FIELD].isnull()) | (~team_df[SPRINT_FIELD].str.contains("open", na=False))]
        status_counts = backlog_df[STATUS_FIELD].value_counts().to_dict()
        total = len(backlog_df)
        relevant_count = sum([status_counts.get(s, 0) for s in RELEVANT_STATUSES])
        score = round((relevant_count / total) * 100, 1) if total > 0 else 0

        if score >= THRESHOLDS["green"]:
            light = "blinking_green.gif"
        elif score >= THRESHOLDS["yellow"]:
            light = "blinking_yellow.gif"
        else:
            light = "blinking_red.gif"

        teams[team] = {
            "total": total,
            "relevant": relevant_count,
            "score": score,
            "light": light,
            "status_counts": status_counts
        }
    return teams

def render_html(team_data):
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
    template = env.get_template("backlog_health_template.html")
    output = template.render(team_data=team_data, team_order=TEAM_ORDER)
    with open(OUTPUT_PATH, "w") as f:
        f.write(output)

def main():
    df = pd.read_csv(CSV_PATH)
    team_data = prepare_data(df)
    render_html(team_data)

if __name__ == "__main__":
    main()

