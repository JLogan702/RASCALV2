// dashboard_logic.js
document.addEventListener('DOMContentLoaded', () => {
    // This dashboardData variable comes from dashboard_data.js
    if (typeof dashboardData === 'undefined') {
        console.error('dashboardData.js not loaded or dashboardData is not defined.');
        return;
    }

    const currentPath = window.location.pathname;
    const pageName = currentPath.substring(currentPath.lastIndexOf('/') + 1);

    // --- Navigation Logic ---
    window.navigateTo = function(value) {
        window.location.href = value;
    };

    // Set correct option in nav menu based on current page
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        for (let i = 0; i < navMenu.options.length; i++) {
            if (navMenu.options[i].value === pageName) {
                navMenu.selectedIndex = i;
                break;
            }
        }
    }

    // Helper to get stoplight image path
    function getStoplightImagePath(color) {
        const imageMap = {
            'green': 'images/green_light.gif',
            'yellow': 'images/yellow_light.gif',
            'red': 'images/red_light.gif'
        };
        return imageMap[color] || 'images/yellow_light.gif'; // Default to yellow
    }

    // Helper to get percentage meaning text
    function getPercentageMeaning(percentage) {
        if (percentage >= 80) {
            return '✅ Green: 80% or more ready';
        } else if (percentage >= 50) {
            return '🟡 Yellow: 50–79% ready';
        } else {
            return '🔴 Red: Less than 50% ready';
        }
    }

    // Helper for overall program status description
    function getOverallProgramStatusDescription(status) {
        switch(status) {
            case 'green':
                return 'The program currently demonstrates strong readiness, healthy backlog, and minimal impediments.';
            case 'yellow':
                return 'The program has some areas requiring attention in readiness, backlog health, or dependencies. Proactive review is recommended.';
            case 'red':
                return 'The program is facing significant challenges in readiness, backlog health, or dependencies that require immediate attention.';
            default:
                return 'Status not available.';
        }
    }


    // --- Click-to-Zoom Overlay Logic ---
    const overlay = document.createElement('div');
    overlay.className = 'overlay';
    document.body.appendChild(overlay);

    const zoomedBox = document.createElement('div');
    zoomedBox.className = 'zoomed-box';
    overlay.appendChild(zoomedBox);

    const closeButton = document.createElement('button');
    closeButton.className = 'close-button';
    closeButton.innerHTML = '&times;'; // 'x' symbol
    zoomedBox.appendChild(closeButton);

    closeButton.addEventListener('click', () => {
        overlay.classList.remove('active');
        zoomedBox.innerHTML = ''; // Clear content
        zoomedBox.appendChild(closeButton); // Re-add close button for next use
    });

    // --- Populate Dashboard Data ---

    // Logic for Program Summary/Overview
    if (pageName === 'index.html') {
        const programSummary = dashboardData.programSummary;
        const sprintReadiness = dashboardData.sprintReadiness.overall;
        const backlogHealth = dashboardData.backlogHealth.overall;
        const dependencies = dashboardData.dependencies;

        document.getElementById('programStatusLight').src = getStoplightImagePath(programSummary.overall_status);
        document.getElementById('programOverallStatusText').textContent = `Overall Status: ${programSummary.overall_status.toUpperCase()}`;
        document.getElementById('reportGenerationDate').textContent = programSummary.generation_date;
        document.getElementById('overallProgramStatusDescription').textContent = getOverallProgramStatusDescription(programSummary.overall_status);


        document.getElementById('summarySprintReadinessLight').src = getStoplightImagePath(sprintReadiness.stoplight);
        document.getElementById('summarySprintReadinessPercentage').textContent = `${sprintReadiness.percentage.toFixed(2)}%`;
        document.getElementById('summarySprintReadinessExplanation').textContent = getPercentageMeaning(sprintReadiness.percentage);


        document.getElementById('summaryBacklogHealthLight').src = getStoplightImagePath(backlogHealth.stoplight);
        document.getElementById('summaryBacklogHealthPercentage').textContent = `${backlogHealth.percentage.toFixed(2)}%`;
        document.getElementById('summaryBacklogHealthExplanation').textContent = getPercentageMeaning(backlogHealth.percentage);


        // Dependencies summary status based on blocked count
        let dependenciesStatusColor = 'green';
        if (dependencies.blocked_epics_count > 5) {
            dependenciesStatusColor = 'red';
        } else if (dependencies.blocked_epics_count > 0 && dependencies.blocked_epics_count <= 5) {
            dependenciesStatusColor = 'yellow';
        }
        document.getElementById('summaryDependenciesLight').src = getStoplightImagePath(dependenciesStatusColor);
        document.getElementById('summaryDependenciesCount').textContent = `${dependencies.blocked_epics_count} Epics`;
        document.getElementById('summaryDependenciesExplanation').textContent = `Fewer blocked Epics indicate smoother cross-team flow.`;


        // Populate Team Health Overview
        const teamOverviewContainer = document.getElementById('teamOverviewContainer');
        if (teamOverviewContainer) {
            const allComponents = new Set([
                ...Object.keys(dashboardData.sprintReadiness.by_component),
                ...Object.keys(dashboardData.backlogHealth.by_component)
            ]);
            
            const sortedComponents = Array.from(allComponents).sort();

            sortedComponents.forEach(component => {
                const sprintData = dashboardData.sprintReadiness.by_component[component] || { percentage: 0, stoplight: 'red' };
                const backlogData = dashboardData.backlogHealth.by_component[component] || { percentage: 0, stoplight: 'red' };

                let componentOverallStatus = 'green';
                if (sprintData.stoplight === 'red' || backlogData.stoplight === 'red') {
                    componentOverallStatus = 'red';
                } else if (sprintData.stoplight === 'yellow' || backlogData.stoplight === 'yellow') {
                    componentOverallStatus = 'yellow';
                }

                const componentBox = document.createElement('div');
                componentBox.className = 'component-box team-summary-box';
                componentBox.setAttribute('data-component', component); // For zoom feature
                componentBox.innerHTML = `
                    <h3>${component}</h3>
                    <img src="${getStoplightImagePath(componentOverallStatus)}" alt="${component} Status" class="stoplight-img-sm">
                    <p>Sprint: ${sprintData.percentage.toFixed(2)}%</p>
                    <p>Backlog: ${backlogData.percentage.toFixed(2)}%</p>
                    <p class="percentage-meaning">${getPercentageMeaning(componentOverallStatus === 'green' ? 80 : componentOverallStatus === 'yellow' ? 50 : 0)}</p>
                `;
                teamOverviewContainer.appendChild(componentBox);
            });
        }
    }

    // Logic for Backlog Health Dashboard
    else if (pageName === 'backlog_health.html') {
        const backlogHealth = dashboardData.backlogHealth;

        // Overall
        document.getElementById('overallBacklogHealthStoplight').src = getStoplightImagePath(backlogHealth.overall.stoplight);
        document.getElementById('overallBacklogHealthPercentage').textContent = `${backlogHealth.overall.percentage.toFixed(2)}%`;
        document.getElementById('overallBacklogHealthCounts').textContent = `${backlogHealth.overall.numerator} Healthy / ${backlogHealth.overall.denominator} Total`;
        document.getElementById('overallBacklogHealthExplanation').textContent = getPercentageMeaning(backlogHealth.overall.percentage);

        // By Component
        const componentContainer = document.getElementById('componentBacklogHealthContainer');
        if (componentContainer) {
            const sortedComponents = Object.keys(backlogHealth.by_component).sort();
            sortedComponents.forEach(component => {
                const data = backlogHealth.by_component[component];
                const componentBox = document.createElement('div');
                componentBox.className = 'component-box';
                componentBox.setAttribute('data-component', component); // For zoom feature

                let statusBreakdownHtml = '';
                const allPossibleStatuses = ['New', 'Grooming', 'Backlog', 'To Do']; // Define order
                statusBreakdownHtml += '<ul class="status-breakdown-list">';
                allPossibleStatuses.forEach(status => {
                    const count = data.status_counts[status] || 0;
                    statusBreakdownHtml += `<li><strong>${status}:</strong> ${count} stories</li>`;
                });
                statusBreakdownHtml += '</ul>';

                componentBox.innerHTML = `
                    <h3>${component}</h3>
                    <img src="${getStoplightImagePath(data.stoplight)}" alt="${component} Status" class="stoplight-img-sm">
                    <p class="percentage">${data.percentage.toFixed(2)}%</p>
                    <p class="count-info">${data.numerator} Healthy / ${data.denominator} Total</p>
                    <p class="percentage-meaning">${getPercentageMeaning(data.percentage)}</p>
                    <p class="box-description">This team's backlog health indicates the percentage of their active backlog stories that are ready for development.</p>
                    ${statusBreakdownHtml}
                `;
                componentContainer.appendChild(componentBox);
            });
        }
    }

    // Logic for Sprint Readiness Dashboard
    else if (pageName === 'sprint_readiness.html') {
        const sprintReadiness = dashboardData.sprintReadiness;

        // Overall
        document.getElementById('overallSprintReadinessStoplight').src = getStoplightImagePath(sprintReadiness.overall.stoplight);
        document.getElementById('overallSprintReadinessPercentage').textContent = `${sprintReadiness.overall.percentage.toFixed(2)}%`;
        document.getElementById('overallSprintReadinessCounts').textContent = `${sprintReadiness.overall.numerator} Ready / ${sprintReadiness.overall.denominator} Total`;
        document.getElementById('overallSprintReadinessExplanation').textContent = getPercentageMeaning(sprintReadiness.overall.percentage);


        // By Component
        const componentContainer = document.getElementById('componentReadinessContainer');
        if (componentContainer) {
            const sortedComponents = Object.keys(sprintReadiness.by_component).sort();
            sortedComponents.forEach(component => {
                const data = sprintReadiness.by_component[component];
                const componentBox = document.createElement('div');
                componentBox.className = 'component-box';
                componentBox.setAttribute('data-component', component); // For zoom feature
                
                let cautionMessage = '';
                let cautionImage = '';
                if (data.numerator < 3) {
                    cautionImage = '<img src="images/warning_yellow.png" alt="Caution" class="caution-icon">';
                    cautionMessage = '<p class="caution-text">Sprint may not be ready: &lt; 3 stories ready.</p>';
                }

                let statusBreakdownHtml = '';
                const allPossibleStatuses = ['New', 'Backlog', 'Grooming', 'To Do']; // Define order
                statusBreakdownHtml += '<ul class="status-breakdown-list">';
                allPossibleStatuses.forEach(status => {
                    const count = data.status_counts[status] || 0;
                    statusBreakdownHtml += `<li><strong>${status}:</strong> ${count} stories</li>`;
                });
                statusBreakdownHtml += '</ul>';

                componentBox.innerHTML = `
                    <h3>${component}</h3>
                    <img src="${getStoplightImagePath(data.stoplight)}" alt="${component} Status" class="stoplight-img-sm">
                    <p class="percentage">${data.percentage.toFixed(2)}%</p>
                    <p class="count-info">${data.numerator} Ready / ${data.denominator} Total</p>
                    <p class="percentage-meaning">${getPercentageMeaning(data.percentage)}</p>
                    <p class="box-description">This team's sprint readiness indicates their preparedness for the upcoming sprint.</p>
                    ${statusBreakdownHtml}
                    ${cautionImage}
                    ${cautionMessage}
                `;
                componentContainer.appendChild(componentBox);
            });
        }
    }

    // Logic for Dependencies Dashboard
    else if (pageName === 'dependencies.html') {
        const dependencies = dashboardData.dependencies;
        const dashboardContainer = document.getElementById('dashboard');
        const blockedEpicsCountElem = document.getElementById('blockedEpicsCount');
        const reportGenerationDateElem = document.getElementById('reportGenerationDate');

        if (blockedEpicsCountElem) {
            blockedEpicsCountElem.textContent = dependencies.blocked_epics_count;
        }

        if (reportGenerationDateElem) {
            reportGenerationDateElem.textContent = dashboardData.programSummary.generation_date;
        }

        if (dashboardContainer) {
            const sortedComponents = Object.keys(dependencies.dependencies_by_component).sort();
            sortedComponents.forEach(component => {
                const teamBox = document.createElement('div');
                teamBox.className = 'team-box';
                teamBox.setAttribute('data-component', component); // For zoom feature

                teamBox.innerHTML = `<h2>${component}</h2><ul></ul>`;
                const ul = teamBox.querySelector('ul');

                dependencies.dependencies_by_component[component].forEach(epic => {
                    const listItem = document.createElement('li');
                    let blocksHtml = epic.blocks.length > 0 ? `🚫 <b>Blocks:</b> ${epic.blocks.join(', ')}<br>` : '';
                    let blockedByHtml = epic.blocked_by.length > 0 ? `⛔ <b>Blocked By:</b> ${epic.blocked_by.join(', ')}<br>` : '';

                    if (blocksHtml || blockedByHtml) {
                        listItem.innerHTML = `
                            <strong>${epic.issue_key}</strong>: ${epic.summary}<br>
                            <span>Status: ${epic.status}</span><br>
                            ${blocksHtml}
                            ${blockedByHtml}
                        `;
                        ul.appendChild(listItem);
                    }
                });
                if (ul.children.length > 0) {
                    dashboardContainer.appendChild(teamBox);
                }
            });
        }
    }

    // --- Click-to-Zoom Event Listeners ---
    document.querySelectorAll('.component-box, .team-box').forEach(box => {
        box.addEventListener('click', function() {
            // Clone the content of the clicked box
            const clonedContent = this.cloneNode(true);
            clonedContent.classList.add('zoomed-content');
            clonedContent.classList.remove('component-box', 'team-summary-box', 'team-box');

            // Clear previous content in zoomedBox and append cloned content
            zoomedBox.innerHTML = '';
            zoomedBox.appendChild(closeButton);
            zoomedBox.appendChild(clonedContent);

            overlay.classList.add('active'); // Show overlay
        });
    });

});
