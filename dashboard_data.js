const dashboardData = {
  "sprintReadiness": {
    "overall": {
      "numerator": 4,
      "denominator": 26,
      "percentage": 15.38,
      "stoplight": "red"
    },
    "by_component": {
      "Engineering - Product": {
        "numerator": 2,
        "denominator": 19,
        "percentage": 10.53,
        "stoplight": "red",
        "status_counts": {
          "New": 13,
          "Grooming": 4,
          "To Do": 2
        }
      },
      "Engineering - AI Ops": {
        "numerator": 0,
        "denominator": 2,
        "percentage": 0.0,
        "stoplight": "red",
        "status_counts": {
          "New": 2
        }
      },
      "Engineering - Platform": {
        "numerator": 0,
        "denominator": 0,
        "percentage": 0,
        "stoplight": "red",
        "status_counts": {}
      },
      "Data Science": {
        "numerator": 0,
        "denominator": 0,
        "percentage": 0,
        "stoplight": "red",
        "status_counts": {}
      },
      "Design": {
        "numerator": 2,
        "denominator": 5,
        "percentage": 40.0,
        "stoplight": "red",
        "status_counts": {
          "New": 3,
          "To Do": 2
        }
      }
    }
  },
  "backlogHealth": {
    "overall": {
      "numerator": 32,
      "denominator": 88,
      "percentage": 36.36,
      "stoplight": "red"
    },
    "by_component": {
      "Engineering - Product": {
        "numerator": 3,
        "denominator": 29,
        "percentage": 10.34,
        "stoplight": "red",
        "status_counts": {
          "New": 19,
          "Grooming": 7,
          "To Do": 3
        }
      },
      "Engineering - AI Ops": {
        "numerator": 2,
        "denominator": 17,
        "percentage": 11.76,
        "stoplight": "red",
        "status_counts": {
          "New": 9,
          "Backlog": 5,
          "To Do": 2,
          "Grooming": 1
        }
      },
      "Engineering - Platform": {
        "numerator": 15,
        "denominator": 23,
        "percentage": 65.22,
        "stoplight": "yellow",
        "status_counts": {
          "To Do": 15,
          "New": 7,
          "Backlog": 1
        }
      },
      "Data Science": {
        "numerator": 3,
        "denominator": 4,
        "percentage": 75.0,
        "stoplight": "yellow",
        "status_counts": {
          "To Do": 3,
          "Backlog": 1
        }
      },
      "Design": {
        "numerator": 9,
        "denominator": 15,
        "percentage": 60.0,
        "stoplight": "yellow",
        "status_counts": {
          "To Do": 9,
          "New": 4,
          "Grooming": 2
        }
      }
    }
  },
  "dependencies": {
    "dependencies_by_component": {
      "Engineering - AI Ops": [
        {
          "issue_key": "CLP-840",
          "summary": "Eng: Data Integration - Recommendations (Strategies)",
          "status": "New",
          "blocks": [],
          "blocked_by": [
            "CLP-116"
          ]
        },
        {
          "issue_key": "CLP-113",
          "summary": "Eng: Data Integration - Emotion/Risk Perception",
          "status": "In Progress",
          "blocks": [],
          "blocked_by": [
            "CLP-86"
          ]
        },
        {
          "issue_key": "CLP-112",
          "summary": "Eng: Data Integration - Resonance",
          "status": "In Progress",
          "blocks": [],
          "blocked_by": [
            "CLP-84"
          ]
        },
        {
          "issue_key": "CLP-75",
          "summary": "DS+ Eng: Context Area Setup for MVP",
          "status": "In Progress",
          "blocks": [],
          "blocked_by": [
            "CLP-538"
          ]
        },
        {
          "issue_key": "CLP-14",
          "summary": "Eng: Data Integration - Psychographics/Communities",
          "status": "In Progress",
          "blocks": [
            "CLP-52"
          ],
          "blocked_by": [
            "CLP-85"
          ]
        }
      ],
      "Data Science": [
        {
          "issue_key": "CLP-126",
          "summary": "QA and E2E Testing ",
          "status": "To Do",
          "blocks": [
            "CLP-127"
          ],
          "blocked_by": []
        }
      ],
      "Design": []
    },
    "blocked_epics_count": 5
  },
  "programSummary": {
    "overall_status": "red",
    "generation_date": "June 10, 2025"
  }
};