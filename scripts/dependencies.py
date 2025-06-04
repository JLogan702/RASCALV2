import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the data
csv_path = os.path.join(os.path.dirname(__file__), "../Evolve24 JIRA.csv")
df = pd.read_csv(csv_path)

# Filter for Story tickets and exclude Done/Canceled/Won’t Do
df = df[
    (df["Issue Type"] == "Story") &
    (~df["Status"].isin(["Done", "Canceled", "Won't Do"]))
]

# Clean up and define the mapping
teams = {
    "Engineering - Product": "Product",
    "Engineering - Platform": "Platform",
    "Engineering - AI Ops": "AI Ops",
    "Design": "Design",
    "Data Science": "Data Science"
}

# Prep the data
summary = {}

for comp, team in teams.items():
    team_df = df[df["Components"] == comp]

    inbound = team_df["Inward issue link (Blocks)"].dropna().tolist()
    outbound = team_df["Outward issue link (Blocks)"].dropna().tolist()

    summary[team] = {
        "inbound": inbound,
        "outbound": outbound,
        "in_count": len(inbound),
        "out_count": len(outbound),
        "stoplight": "images/blinking_green.gif" if len(inbound) + len(outbound) < 5
                     else "images/blinking_yellow.gif" if len(inbound) + len(outbound) < 10
                     else "images/blinking_red.gif"
    }

# Total summary
total_in = sum(team["in_count"] for team in summary.values())
total_out = sum(team["out_count"] for team in summary.values())
summary["__totals__"] = {
    "total_inbound": total_in,
    "total_outbound": total_out
}

# Render with Jinja2
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")
output = template.render(dependency_summary=summary["__totals__"], teams=summary)

# Save the file
with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ Dependencies dashboard generated: docs/dependencies.html")

