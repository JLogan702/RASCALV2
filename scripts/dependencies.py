import pandas as pd
from jinja2 import Environment, FileSystemLoader

df = pd.read_csv("docs/jira_data.csv")
df = df[(df["Issue Type"] == "Story") & (
    df["Inward issue link (Blocks)"].notna() | df["Outward issue link (Blocks)"].notna()
)]

df["Summary"] = df.get("Summary", "N/A").fillna("N/A")

teams = {}
for _, row in df.iterrows():
    team = row.get("Components", "Unknown")
    if team not in teams:
        teams[team] = []
    teams[team].append({
        "key": row["Issue key"],
        "summary": row["Summary"],
        "link": row.get("Inward issue link (Blocks)") or row.get("Outward issue link (Blocks)")
    })

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")
output = template.render(teams=teams)

with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html generated.")

