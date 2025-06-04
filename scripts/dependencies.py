import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Load Jira CSV
df = pd.read_csv("Evolve24 JIRA.csv")

# Filter to Stories only
df = df[df["Issue Type"] == "Story"]

# Clean nulls
df["Inward issue link (Blocks)"] = df["Inward issue link (Blocks)"].fillna("")
df["Outward issue link (Blocks)"] = df["Outward issue link (Blocks)"].fillna("")

# Teams
teams = df["Components"].dropna().unique()
summary = {}
total_inbound = 0
total_outbound = 0

for team in teams:
    team_df = df[df["Components"] == team]
    
    inbound = team_df[team_df["Inward issue link (Blocks)"] != ""].copy()
    outbound = team_df[team_df["Outward issue link (Blocks)"] != ""].copy()

    total_inbound += len(inbound)
    total_outbound += len(outbound)

    summary[team] = {
        "inbound": [
            {
                "key": row["Issue key"],
                "summary": row["Summary"],
                "link": row["Inward issue link (Blocks)"]
            }
            for _, row in inbound.iterrows()
        ],
        "outbound": [
            {
                "key": row["Issue key"],
                "summary": row["Summary"],
                "link": row["Outward issue link (Blocks)"]
            }
            for _, row in outbound.iterrows()
        ]
    }

# Load and render HTML
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")
output = template.render(
    dependency_summary={"total_inbound": total_inbound, "total_outbound": total_outbound},
    teams=summary
)

with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html generated")

