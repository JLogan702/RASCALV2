import pandas as pd
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

# Constants
CSV_PATH = "docs/jira_data.csv"
TEMPLATE_FILE = "dependencies_template.html"
OUTPUT_FILE = "docs/dependencies.html"


def extract_dependencies(df):
    team_data = defaultdict(lambda: {"inbound": [], "outbound": []})

    for _, row in df.iterrows():
        team = row.get("Components")
        key = row.get("Issue key")
        summary = row.get("Summary")
        inbound = row.get("Inward issue link (Dependency)")
        outbound = row.get("Outward issue link (Dependency)")

        if pd.notna(inbound):
            team_data[team]["inbound"].append({"key": key, "summary": summary, "link": inbound})
        if pd.notna(outbound):
            team_data[team]["outbound"].append({"key": key, "summary": summary, "link": outbound})

    return team_data


def generate_summary(team_data):
    total_inbound = sum(len(data.get("inbound", [])) for data in team_data.values())
    total_outbound = sum(len(data.get("outbound", [])) for data in team_data.values())
    explanation = (
        "This dashboard shows cross-team dependencies based on actual Jira issue links. "
        "Inbound dependencies are those blocking a team's work, while outbound dependencies are "
        "those blocking others. Keeping dependencies visible helps reduce delivery risk."
    )
    return {
        "total_inbound": total_inbound,
        "total_outbound": total_outbound,
        "explanation": explanation
    }


def render_html(team_data, dependency_summary):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(TEMPLATE_FILE)

    for team, data in team_data.items():
        if not isinstance(data.get("inbound"), list):
            data["inbound"] = []
        if not isinstance(data.get("outbound"), list):
            data["outbound"] = []

    output = template.render(
        teams=team_data,
        dependency_summary=dependency_summary,
        title="Dependencies Dashboard"
    )

    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("✅ dependencies.html generated.")


def main():
    df = pd.read_csv(CSV_PATH)
    team_data = extract_dependencies(df)
    summary = generate_summary(team_data)

    print("==== TEAM DATA ====")
    for team, data in team_data.items():
        print(f"Team: {team}")
        print(f"  Inbound: {len(data['inbound'])}")
        print(f"  Outbound: {len(data['outbound'])}")

    print("\n==== SUMMARY ====")
    print(summary)

    render_html(team_data, summary)


if __name__ == "__main__":
    main()

