import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load Jira CSV
df = pd.read_csv("RASCAL_DB_Filter_Evolve24_JIRA.csv")

# Normalize columns
df['Components'] = df['Components'].fillna("No Component")
df['Inward issue link (Blocks)'] = df['Inward issue link (Blocks)'].fillna("")
df['Outward issue link (Blocks)'] = df['Outward issue link (Blocks)'].fillna("")

# Prepare data per team
teams = sorted(df['Components'].unique())
summary = {}

for team in teams:
    team_df = df[df['Components'] == team]

    inbound = team_df['Inward issue link (Blocks)']
    outbound = team_df['Outward issue link (Blocks)']

    inbound_count = sum(bool(link.strip()) for link in inbound)
    outbound_count = sum(bool(link.strip()) for link in outbound)

    total = len(team_df)

    summary[team] = {
        "total": total,
        "inbound": inbound_count,
        "outbound": outbound_count,
    }

# Setup Jinja2
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template("dependencies_template.html")

# Render HTML
html = template.render(summary=summary)

output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'dependencies.html'))
with open(output_path, "w") as f:
    f.write(html)

print(f"✅ Dependencies dashboard generated at: {output_path}")

