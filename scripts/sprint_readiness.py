
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

def calculate_sprint_readiness(df):
    ready_statuses = ["To Do", "Ready for Development"]
    excluded_statuses = ["Done", "Cancelled", "In Progress", "Blocked", "Won't Do"]

    df = df[df["Issue Type"] == "Story"]
    df = df[~df["Status"].isin(excluded_statuses)]
    df = df[df["Sprint"].notna()]
    df = df[df["Status"].isin(ready_statuses)]

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
        ready = total  # All tickets in this filtered df are "ready"
        percent = round((ready / total) * 100, 1) if total > 0 else 0

        # Apply threshold logic
        if total < 3:
            stoplight = "blinking_red.gif"
            warning = "⚠️ Fewer than 3 stories in future sprint — sprint not sufficiently planned"
        elif percent >= 80:
            stoplight = "blinking_green.gif"
            warning = ""
        elif percent >= 50:
            stoplight = "blinking_yellow.gif"
            warning = ""
        else:
            stoplight = "blinking_red.gif"
            warning = ""

        status_counts = team_df["Status"].value_counts().to_dict()
        result[team] = {
            "total": total,
            "ready": ready,
            "percent": percent,
            "stoplight": stoplight,
            "status_counts": status_counts,
            "warning": warning
        }

    return result

def render_html(data):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('sprint_readiness_template.html')
    output = template.render(teams=data)

    output_path = os.path.join("docs", "sprint_readiness.html")
    with open(output_path, "w") as f:
        f.write(output)

def main():
    df = pd.read_csv("docs/data/rascal_data.csv")
    team_data = calculate_sprint_readiness(df)
    render_html(team_data)

if __name__ == "__main__":
    main()
