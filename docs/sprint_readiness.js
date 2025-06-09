const READY_STATUSES = ["Ready for Development", "To Do"];
const NON_READY_STATUSES = ["New", "Grooming", "Backlog"];

function getStoplight(percent) {
  if (percent >= 80) return "images/blinking_green.gif";
  if (percent >= 50) return "images/blinking_yellow.gif";
  return "images/blinking_red.gif";
}

function formatStatus(status, count) {
  const excluded = NON_READY_STATUSES.includes(status);
  return `${excluded ? '<span class="italic-underline">' : ''}${status}: ${count}${excluded ? '</span>' : ''}`;
}

fetch("rascal_data.csv")
  .then(response => response.text())
  .then(csv => {
    const lines = csv.split("\n").map(line => line.split(","));
    const headers = lines[0];

    const statusIdx = headers.indexOf("Status");
    const sprintIdx = headers.indexOf("Sprint");
    const typeIdx = headers.indexOf("Issue Type");
    const comp1Idx = headers.indexOf("Components");
    const comp2Idx = headers.indexOf("Components.1");

    const rows = lines.slice(1).filter(row => row.length >= headers.length);
    const teamMap = {};

    rows.forEach(row => {
      if (row[typeIdx] !== "Story") return;
      const status = row[statusIdx];
      const sprint = row[sprintIdx] || "";

      const teamRaw = row[comp1Idx] || row[comp2Idx] || "Unassigned";
      const team = teamRaw.trim();

      const isFutureSprint = sprint.toLowerCase().includes("sprint");
      if (!isFutureSprint) return;

      if (!teamMap[team]) {
        teamMap[team] = { statuses: {}, total: 0, ready: 0 };
      }

      teamMap[team].statuses[status] = (teamMap[team].statuses[status] || 0) + 1;
      teamMap[team].total++;
      if (READY_STATUSES.includes(status)) teamMap[team].ready++;
    });

    ["Engineering - Product", "Engineering - Platform", "Engineering - AI Ops", "Design", "Data Science"].forEach(team => {
      if (!teamMap[team]) teamMap[team] = { statuses: {}, total: 0, ready: 0 };
    });

    const container = document.getElementById("teamBoxes");
    Object.entries(teamMap).forEach(([team, stats]) => {
      const percent = stats.total > 0 ? Math.round((stats.ready / stats.total) * 100) : 0;
      const stoplight = getStoplight(percent);
      const breakdown = Object.entries(stats.statuses)
        .map(([status, count]) => formatStatus(status, count))
        .join("<br>");

      const box = document.createElement("div");
      box.className = "team-box";
      box.innerHTML = `
        <h3>${team}</h3>
        <img src="${stoplight}" class="stoplight" alt="Stoplight">
        <p><strong>${percent}% Ready</strong></p>
        <div>${breakdown || '<em>No story tickets in future sprints</em>'}</div>
      `;
      container.appendChild(box);
    });
  });
