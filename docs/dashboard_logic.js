// dashboard_logic.js

// Define health thresholds
const GREEN_THRESHOLD = 80;
const YELLOW_THRESHOLD = 50;

const healthyStatuses = ["Ready for Development", "To Do"];
const nonCountedStatuses = ["New", "Grooming", "Backlog"];

function getStoplightImage(percent) {
  if (percent >= GREEN_THRESHOLD) return "images/blinking_green.gif";
  if (percent >= YELLOW_THRESHOLD) return "images/blinking_yellow.gif";
  return "images/blinking_red.gif";
}

function formatStatus(status, count) {
  const isExcluded = nonCountedStatuses.includes(status);
  return `${isExcluded ? '<span class="italic-underline">' : ''}${status}: ${count}${isExcluded ? '</span>' : ''}`;
}

fetch("rascal_data.csv")
  .then(response => response.text())
  .then(csv => {
    const lines = csv.split("\n").map(l => l.split(","));
    const headers = lines[0];

    const statusIdx = headers.indexOf("Status");
    const teamIdx = headers.indexOf("Components");
    const sprintIdx = headers.indexOf("Sprint");
    const issueTypeIdx = headers.indexOf("Issue Type");

    const data = lines.slice(1).filter(row => row.length >= headers.length);

    const teamMap = {};

    data.forEach(row => {
      if (row[issueTypeIdx] !== "Story") return;
      const team = row[teamIdx] || "Unassigned";
      const sprint = row[sprintIdx] || "";
      const status = row[statusIdx];

      const isFuture = sprint.toLowerCase().includes("sprint");
      if (!isFuture) return;

      if (!teamMap[team]) {
        teamMap[team] = {
          statuses: {},
          total: 0,
          healthy: 0
        };
      }

      teamMap[team].statuses[status] = (teamMap[team].statuses[status] || 0) + 1;
      teamMap[team].total++;
      if (healthyStatuses.includes(status)) teamMap[team].healthy++;
    });

    // Ensure all 5 teams exist even with 0 tickets
    ["Engineering - Product", "Engineering - Platform", "Engineering - AI Ops", "Design", "Data Science"].forEach(team => {
      if (!teamMap[team]) {
        teamMap[team] = { statuses: {}, total: 0, healthy: 0 };
      }
    });

    const container = document.getElementById("teamBoxes");
    Object.entries(teamMap).forEach(([team, stats]) => {
      const percent = stats.total > 0 ? Math.round((stats.healthy / stats.total) * 100) : 0;
      const stoplight = getStoplightImage(percent);

      const statusList = Object.entries(stats.statuses).map(
        ([status, count]) => formatStatus(status, count)
      ).join("<br>");

      const box = document.createElement("div");
      box.className = "team-box";
      box.innerHTML = `
        <h3>${team}</h3>
        <img src="${stoplight}" class="stoplight" alt="Stoplight">
        <p><strong>${percent}% Ready</strong></p>
        <div>${statusList || '<em>No story tickets in future sprints</em>'}</div>
      `;
      container.appendChild(box);
    });
  });
