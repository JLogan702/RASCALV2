import pandas as pd
import jinja2
import os

# Load the data
csv_path = "../RASCAL_DB_Filter (Evolve24 JIRA).csv"
df = pd.read_csv(csv_path)

# Clean whitespace and ensure required columns exist
df.columns = df.columns.str.strip()
df['Status'] = df['Status'].fillna("").str.strip()
df['Sprint'] = df['Sprint'].fillna("").astype(str).str.strip()
df['Components'] = df['Components'].fillna("").str.strip()

# Define teams and statuses
teams = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

backlog_statuses = {"New", "Grooming", "Backlog"}
all_statuses_to_track = backlog_statuses.union({
    "To Do", "Ready for Development", "Blocked", "In Progress",
    "Ready for Review", "Ready for Acceptance", "Ready to Deploy",
    "UAT Testing", "IN CODE REVIEW", "Canceled", "Won't Do"
})

# Prepare data
summary = {}
for component, team_name in teams.items():
    team_df = df[df["Components"] == component]
    status_counts = team_df["Status"].value_counts().to_dict()

    total_backlog = sum(
        count for status, count in status_counts.items()
        if status in all_statuses_to_track and team_df[team_df["Status"] == status]["Sprint"].str.strip().eq("").sum() > 0
    )

    valid_backlog = sum(
        count for status, count in status_counts.items()
        if status in backlog_statuses and team_df[team_df["Status"] == status]["Sprint"].str.strip().eq("").sum() > 0
    )

    percent = (valid_backlog / total_backlog) * 100 if total_backlog > 0 else 0

    if percent >= 80:
        stoplight = "blinking_green.gif"
    elif percent >= 50:
        stoplight = "blinking_yellow.gif"
    else:
        stoplight = "blinking_red.gif"

    summary[team_name] = {
        "total_backlog": total_backlog,
        "valid_backlog": valid_backlog,
        "percent": round(percent, 1),
        "stoplight": stoplight,
        "status_counts": status_counts
    }

# Set up Jinja2 environment
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape()
)

template = env.get_template("backlog_health_template.html")

output = template.render(
    summary=summary,
    best_practices_url="https://www.scrum.org/resources/blog/how-manage-product-backlog",
    report_title="Backlog Health Dashboard",
    explanation=(
        "Backlog Health reflects the percentage of story tickets in acceptable pre-sprint statuses (New, Grooming, Backlog) "
        "that are not assigned to any active or future sprint. This aligns with Agile readiness principles that encourage clear "
        "prioritization before sprint planning."
    )
)

# Write to file
os.makedirs("docs", exist_ok=True)
with open("docs/backlog_health.html", "w") as f:
    f.write(output)

print("✅ backlog_health.html generated.")

