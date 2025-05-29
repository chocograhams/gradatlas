
# GradAtlas Test Plan

_A Living Document for Ensuring Quality & Performance_

## Purpose

This test plan outlines how GradAtlas, a lightweight event discovery tool for Seattle-based graduate students, will be tested and maintained to ensure its usability, reliability, and performance. It is intended to guide ongoing development, issue detection, and continuous improvement.

---

## Test Categories

### 1. Functional Tests

| Feature | Test Case | Expected Result | Method |
|--------|-----------|-----------------|--------|
| Search Filters | Search by tag/location/name/description | Only relevant results appear | Manual input testing |
| CSV Export | Select and export events | CSV file contains selected events with accurate formatting | Functional click test |
| Page Load | Search page opens in browser | Loads with logo, search filters, and welcome message | Browser test |
| JSON Data Load | meetups-list.json loads into page | All events display with correct metadata | Console + UI test |
| REST API | `GET /meetups` returns data | Valid JSON list of events | `curl` / Postman test |
| Add Event (if enabled) | `POST /add` adds a new event | JSON file updates and displays new item | Manual post request |

---

### 2. Performance Tests

| Metric | Goal | Method | Alert Threshold |
|--------|------|--------|-----------------|
| Page Load Time | < 2 seconds | Browser DevTools | > 3 seconds |
| API Response Time | < 500ms | Postman Benchmark | > 1 second |
| CSV Download | < 1 second | Manual + Timer | > 2 seconds |
| Uptime (deployed version) | > 99% | Monitor via Render/Vercel logs | Email alert on downtime |

---

## Alarms & Monitoring

| Trigger | Action |
|--------|--------|
| 404 or 500 server error | Auto-log to `error.log` and notify dev |
| API failure or malformed JSON | Return graceful error message + log issue |
| Broken CSV download | Disable button + prompt retry |
| Unexpected downtime | Alert via hosting platform (Render, Vercel) |
| Duplicate or corrupted data | Run nightly JSON validator |

---

## Maintenance & Continuous Improvement

- **Weekly QA Audit:** Manually test all search filters and CSV export.
- **Nightly Data Check:** Validate `meetups-list.json` for malformed entries.
- **Monthly Performance Review:** Check logs for errors and slow endpoints.
- **User Feedback Loop:** Implement user suggestion collection and prioritize fixes based on usability pain points.

---

## Sample Test Snippet

```bash
# Functional API Test
curl http://127.0.0.1:5002/meetups

# Should return a JSON array of events:
[
  {
    "event_name": "Board Game Night",
    "date": "2024-06-01T18:00:00",
    "location": "Capitol Hill",
    ...
  }
]
```

---

## Quality Goals Summary

| Attribute | Goal |
|-----------|------|
| Usability | Easy for first-time users to filter and export events |
| Performance | Smooth interaction under normal user load |
| Data Accuracy | Consistent, well-formatted event listings |
| Maintainability | Easy to update and validate JSON data |
| Accessibility | Works on desktop and mobile browsers |

---

## Contributors

Christine Chen & Yue Liu  
MSIM | University of Washington

---

## Related Files

- `meetup_api3.py` — Flask API logic  
- `meetups-list.json` — Event data store  
- `search_meetups_with_export_logo_welcome.html` — UI template

---

This test plan serves as a foundation and should evolve as GradAtlas scales or adds features like login, admin controls, or date filtering.
