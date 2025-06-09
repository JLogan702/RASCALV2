const TEAM_LIST = [
  "Engineering - Product",
  "Engineering - Platform",
  "Engineering - AI Ops",
  "Design",
  "Data Science"
];

function getStoplightColor(blockedCount) {
  if (blockedCount === 0) return "images/blinking_green.gif";
  if (blockedCount === 1) return "images/blinking_yellow.gif";
  return "images/blinking_red.gif";
}

fetch("dependency_mapping_MarTech1.0 (Evolve24 JIRA).csv")
  .then(response => response.text())
  .then(csv => {
    const lines = csv.split("\n").map(line => line.split(","));
    const headers = lines[0];

    const statusIdx = headers.indexOf("Status");
    const comp1 = headers.indexOf("Components");
    const comp2 = headers.indexOf("Components.1");
    const comp3 = headers.indexOf("Components.2");
    const inwardLinks = headers.filter(h => h.startsWith("Inward issue link (Blocks)"));
    const outwardLinks = headers.filter(h => h.startsWith("Outward issue link (Blocks)"));

    const teamMap = {};

    lines.slice(1).forEach(row => {
      if (!row.length || !row[statusIdx]) return;
      const status = row[statusIdx].toLowerCase();
      if (["done", "cancelled", "closed"].includes(status)) return;

      const team = row[comp1] || row[comp2] || row[comp3] || "Unassigned";
      if (!teamMap[team]) {
        teamMap[team] = {
          blockedBy: new Set(),
          blocking: new Set(),
          totalEpics: 0
        };
      }

      teamMap[team].totalEpics++;

      inwardLinks.forEach(key => {
        const idx = headers.indexOf(key);
        if (row[idx]) teamMap[team].blockedBy.add(row[idx]);
      });

      outwardLinks.forEach(key => {
        const idx = headers.indexOf(key);
        if (row[idx]) teamMap[team].blocking.add(row[idx]);
      });
    });

    const container = document.getElementById("dependencyBoxes");

    TEAM_LIST.forEach(team => {
      const teamData = teamMap[team] || {
        blockedBy: new Set(),
        blocking: new Set(),
        totalEpics: 0
      };

      const blockedList = Array.from(teamData.blockedBy).join(", ") || "None";
      const blockingList = Array.from(teamData.blocking).join(", ") || "None";
      const stoplight = getStoplightColor(teamData.blockedBy.size);

      const box = document.createElement("div");
      box.className = "team-box";
      box.innerHTML = `
        <h3>${team}</h3>
        <img src="${stoplight}" class="stoplight" alt="Stoplight">
        <p><strong>${teamData.totalEpics} Epics</strong></p>
        <p><strong>Blocked By:</strong> ${teamData.blockedBy.size}</p>
        <p><strong>Blocking:</strong> ${teamData.blocking.size}</p>
        <p><strong>Inbound:</strong> ${blockedList}</p>
        <p><strong>Outbound:</strong> ${blockingList}</p>
      `;
      container.appendChild(box);
    });
  });
