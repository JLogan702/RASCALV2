
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

def calculate_backlog_health(df):
    healthy_statuses = ["To Do", "Ready for Development"]
    excluded_statuses = ["Done", "Cancelled", "In Progress", "Blocked", "Won't Do"]

    df = df[df["Issue Type"] == "Story"]
    df = df[~df["Status"].isin(excluded_statuses)]

    # Include stories that are in a sprint OR not assigned to any sprint (backlog)
    df = df[df["Sprint"].notna() | df["Sprint"].isna()]

    team_map = {
        "Engineering - Product": "Product",
        "Engineering - Platform": "Platform",
        "Engineering - AI Ops": "AI Ops",
        "Design": "Design",
        "Data Science": "Data Science"
    }

    df["Team"] = df["Components"].map(team_map)
    teams = ["Product", "Platform", "AI Ops", "Design", "Data Science"]

    result = {}
    for team in teams:
        team_df = df[df["Team"] == team]
        total = len(team_df)
        healthy = len(team_df[team_df["Status"].isin(healthy_statuses)])
        percent = round((healthy / total) * 100, 1) if total > 0 else 0
        stoplight = "blinking_green.gif" if percent >= 80 else "blinking_yellow.gif" if percent >= 50 else "blinking_red.gif"

        status_counts = team_df["Status"].value_counts().to_dict()
        result[team] = {
            "total": total,
            "healthy": healthy,
            "percent": percent,
            "stoplight": stoplight,
            "status_counts": status_counts
        }

    return result

def render_html(data):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('backlog_health_template.html')
    output = template.render(teams=data)

    output_path = os.path.join("docs", "backlog_health.html")
    with open(output_path, "w") as f:
        f.write(output)

def main():
    df = pd.read_csv("docs/data/rascal_data.csv")
    team_data = calculate_backlog_health(df)
    render_html(team_data)

if __name__ == "__main__":
    main()
