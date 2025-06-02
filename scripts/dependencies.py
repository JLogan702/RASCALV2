import pandas as pd
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

CSV_PATH = "docs/jira_data.csv"
TEMPLATE_FILE = "dependencies_template.html"
OUTPUT_FILE = "docs/dependencies.html"
SPRINT_FIELD = "Sprint"
TEAM_FIELD = "Components"
STATUS_FIELD = "Status"
ISSUE_TYPE_FIELD = "Issue Type"
INWARD_FIELD = "Inward issue link (Blocks)"
OUTWARD_FIELD = "Outward issue link (Blocks)"

TEAM_ORDER = [
    "Data Science",
    "Design",
    "Engineering - AI Ops",
    "Engineering - Platform",
    "Engineering - Product"
]

THRESHOLDS = {
    "green": 80,
    "yellow": 50
}

def calculate_dependency_data(df):
    team_data = []
    total_dependencies = 0
    total_tickets_with_links = 0

    for team in TEAM_ORDER:
        team_df = df[df[TEAM_FIELD] == team]
        total = len(team_df)

        team_df[INWARD_FIELD] = team_df[INWARD_FIELD].fillna("")
        team_df[OUTWARD_FIELD] = team_df[OUTWARD_FIELD].fillna("")

        has_dependency = team_df[(team_df[INWARD_FIELD] != "") | (team_df[OUTWARD_FIELD] != "")]
        count_with_dependency = len(has_dependency)

        status_counts = team_df[STATUS_FIELD].value_counts().to_dict()

        percent = round((count_with_dependency / total) * 100, 1) if total > 0 else 0.0

        if percent >= THRESHOLDS["green"]:
            stoplight = "blinking_green.gif"
        elif percent >= THRESHOLDS["yellow"]:
            stoplight = "blinking_yellow.gif"
        else:
            stoplight = "blinking_red.gif"

        explanation = (
            f"{percent}% of {team} story tickets have documented dependencies. "
            f"This metric helps track risk and planning alignment between teams. "
            f"{'Good visibility' if percent >= 80 else 'Moderate tracking' if percent >= 50 else 'Low visibility on blockers'} present."
        )

        team_data.append({
            "team": team,
            "total": total,
            "count_with_dependency": count_with_dependency,
            "percent": percent,
            "stoplight": stoplight,
            "status_counts": status_counts,
            "explanation": explanation
        })

        total_dependencies += count_with_dependency
        total_tickets_with_links += total

    overall_percent = round((total_dependencies / total_tickets_with_links) * 100, 1) if total_tickets_with_links > 0 else 0.0
    overall_explanation = (
        f"Across all teams, {overall_percent}% of story tickets have identified dependencies. "
        "This helps drive proactive risk management and cross-team planning, per Agile best practices (see SAFe 6.0 guidance)."
    )

    summary_data = {
        "total_dependencies": total_dependencies,
        "percent_with_links": overall_percent,
        "explanation": overall_explanation
    }

    return team_data, summary_data

def render_html(team_data, summary_data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(TEMPLATE_FILE)
    output = template.render(teams=team_data, dependency_summary=summary_data)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("✅ dependencies.html generated")

def main():
    df = pd.read_csv(CSV_PATH)
    df = df[(df[ISSUE_TYPE_FIELD] == "Story") & (df[STATUS_FIELD] != "Done")]
    team_data, summary_data = calculate_dependency_data(df)
    render_html(team_data, summary_data)

if __name__ == "__main__":
    main()

