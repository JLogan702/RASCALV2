
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def load_data(file_path):
    df = pd.read_csv(file_path)
    # Filter for Epics that are blocking or blocked
    deps = df[(df["Issue Type"] == "Epic") & (
        df["Outward issue link (Blocks)"].notna() | df["Inward issue link (Blocks)"].notna()
    )]
    return deps

def process_dependencies(df):
    grouped = {}
    for _, row in df.iterrows():
        team = row["Components"] if pd.notna(row["Components"]) else "Unassigned"
        if team not in grouped:
            grouped[team] = []

        grouped[team].append({
            "key": row["Issue key"],
            "summary": row["Summary"],
            "status": row["Status"],
            "blocks": row.get("Outward issue link (Blocks)", ""),
            "blocked_by": row.get("Inward issue link (Blocks)", "")
        })
    return grouped

def render_html(data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("dependencies_template.html")
    today = datetime.now().strftime("%B %d, %Y")
    output = template.render(dependencies=data, today=today)

    with open("docs/dependencies.html", "w") as f:
        f.write(output)

def main():
    file_path = "docs/data/rascal_data.csv"
    df = load_data(file_path)
    data = process_dependencies(df)
    render_html(data)

if __name__ == "__main__":
    main()
