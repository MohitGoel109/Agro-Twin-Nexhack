# Agro-Twin — Predictive Maintenance Digital Twin for Farm Machinery

> **NexHack 2.0** (Geeta University, Panipat) | **Track:** AI in Agriculture — **Problem Statement 08**  
> **Team:** Deadline Dominators (Vansh, Kunal, Mohit, Shashi)

**Agro-Twin** is an explainable, leak-free predictive maintenance digital twin for shared agricultural machinery fleets. During short sowing and harvesting windows, an unexpected tractor or harvester breakdown can stall multiple farms at once—while fixed calendar-based servicing wastes scarce technicians and spare parts on healthy equipment.

Agro-Twin replays hourly farm machinery telemetry, separates real developing faults from noisy or missing sensor data, quantifies prediction uncertainty, prioritizes constrained maintenance under limited technicians and spare parts, and proves its impact against a fair calendar-only servicing baseline.

---

## Key Capabilities (Mapped to Problem Statement 08)

| PS 08 Requirement | How Agro-Twin Solves It |
|---|---|
| **Reconstruct Machine Condition** | Starts with a 6-machine farm fleet (`TR-101`, `HV-202`, `TR-103`, `SD-304`, `TR-105`, `HV-206`) and supports adding, editing, or removing units during a 120-hour harvest replay. |
| **Live Fleet Management** | Creates deterministic telemetry for new machines, applies condition modes and harvest criticality, keeps fleet selectors and AI recognition in sync, and releases reserved resources when a unit is removed. |
| **Leak-Free Fault Detection** | Trains a 50-tree Random Forest strictly on backward sliding windows (`[t-5 .. t]`) to predict failure within the next 24 hours. Future failure timestamps never enter prediction inputs. |
| **Uncertainty & Data Quality** | Computes uncertainty from ensemble tree disagreement plus missing-sensor penalties. A 3-hour rolling median filter isolates single-hour sensor spikes (`SENSOR_NOISE_FILTERED` on `SD-304`) and holds alarms during dropouts (`MISSING_DATA_HOLD` on `TR-105`). |
| **Plain-English Explainability** | Every alert lists the top-3 human-readable sensor deviations (e.g., Engine Temperature above baseline, Oil Pressure drop, Vibration trend) alongside risk score and confidence bounds. |
| **Constrained Scheduling** | Ranks repairs by fault risk, confidence, and harvest criticality under scarce technician slots and spare-part stock. Tracks alert acknowledgements, work-order lifecycles (`WO-001`, ...), and transparently marks stockouts as `DEFERRED_SCARCITY`. |
| **Fair Baseline Comparison** | Replays the exact same 120-hour harvest scenario under **Calendar-Only Servicing** vs. **Agro-Twin AI**, comparing availability, downtime, unplanned breakdowns, and warning lead time side-by-side. |

---

## Verified Impact (120-Hour Harvest Scenario)

Measured directly by `ops/verify_ops.py` on identical fleet telemetry:

| Metric | Calendar-Only Baseline | Agro-Twin AI | Net Improvement |
|---|---:|---:|---:|
| **Fleet Availability** | `92.22%` | **`98.33%`** | **`+6.11%`** |
| **Total Fleet Downtime** | `56 hrs` | **`12 hrs`** | **`44 hrs saved`** |
| **Unplanned Breakdowns** | `2` | **`0`** | **`2 avoided`** |
| **Avg. Fault-Warning Lead Time** | `0.0 hrs` | **`18.3 hrs`** | **`+18.3 hrs early`** |
| **Noisy / Missing Telemetry Holds** | N/A | **`13 held`** | **Zero false dispatches** |

---

## System Architecture

```text
+-----------------------------+       +-----------------------------+
| frontend/ Streamlit + Plotly|--HTTP>| backend/ FastAPI            |
| 5 pages | 5 themes          |       | REST API | TwinStateManager  |
+-----------------------------+       +--------------+--------------+
+-----------------------------+                      |
| web/ Flask segmented site   |--direct state calls--+
| Fleet Manager | AI Guide    |                      |
+-----------------------------+                      |
                                          +----------v----------+
                                          | ml/       | ops/    |
                                          | AI engine | Scheduler|
                                          +-----------+---------+
```

The Streamlit dashboard can use the FastAPI service or its offline fallback. The Flask website calls the shared `TwinStateManager` in-process.

---

## Repository Structure

```text
.
├── README.md                  # Project overview, setup, and demo walkthrough
├── requirements.txt           # Shared Python dependencies
├── .gitignore                 # Excludes cache, virtualenvs, and local artifacts
├── ml/                        # Member 1 (Vansh) — AI & Explainability Lead
│   ├── __init__.py
│   ├── ml_engine.py           # Leak-free ML predictor, noise filter, uncertainty & explainability
│   └── verify_ml.py           # Standalone verification tests for ml/
├── ops/                       # Member 2 (Kunal) — Fleet Operations & Optimization Lead
│   ├── __init__.py
│   ├── scheduler.py           # Constrained maintenance scheduler, work orders & baseline replay
│   └── verify_ops.py          # Integration tests for ops/ + ml/
├── backend/                   # Member 3 (Mohit) — Backend & Twin State Architect
│   ├── __init__.py
│   ├── state.py               # Unified Digital Twin state controller
│   ├── app.py                 # FastAPI fleet CRUD, simulation, and operations APIs
│   └── verify_backend.py      # Integration tests for backend/ + ops/ + ml/
├── frontend/                  # Streamlit/Plotly dashboard
│   ├── __init__.py
│   ├── api_client.py          # Dual-mode API client (FastAPI + offline-safe local fallback)
│   ├── charts.py              # Interactive Plotly visualizations
│   ├── dashboard.py           # Multi-page command center with five selectable themes
│   ├── dashboard_shared.py    # Shared state and presentation helpers
│   ├── app_pages/             # Fleet, telemetry, performance, work orders, operations
│   └── verify_frontend.py     # Streamlit dashboard verification
├── web/                       # Flask website, fleet manager, and AI guide
│   ├── app.py                 # Flask routes and live fleet CRUD API
│   ├── ai_assistant.py        # Live fleet-aware assistant with strict off-topic guardrail
│   ├── templates/             # Segmented website
│   ├── static/                # Website JavaScript and styling
│   └── verify_web.py          # Flask UI/API and assistant verification
└── render.yaml                # Render Blueprint for the public Flask website
```

---

## Quick Start (Local Setup)

### 1. Clone the Repository & Install Dependencies
```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
pip install -r requirements.txt
```

### 2. Run Full-Stack Verification (Optional)
Confirm all four layers (`ml/`, `ops/`, `backend/`, `frontend/`) work together cleanly:
```bash
python frontend/verify_frontend.py
```

You can also run each module's individual check:
```bash
python ml/verify_ml.py
python ops/verify_ops.py
python backend/verify_backend.py
python web/verify_web.py
```

### 3. Launch the Backend API (Terminal 1)
```bash
uvicorn backend.app:app --reload --port 8000
```
* Interactive Swagger API docs: **`http://localhost:8000/docs`**
* Optional standalone FastAPI service start command:
  ```bash
  uvicorn backend.app:app --host 0.0.0.0 --port $PORT
  ```

### 4. Launch the Digital Twin Dashboard (Terminal 2)
```bash
streamlit run frontend/dashboard.py
```
* Dashboard URL: **`http://localhost:8501`**
* *Resilience Note:* If the FastAPI server is offline, `AgroTwinClient` automatically falls back to **Direct Twin Mode** so the live demo remains 100% functional without network errors.

### 5. Launch the Flask Website (Optional)
```bash
python web/app.py
```
* Website URL: **`http://localhost:5000`**
* Segment 04 includes the Fleet Manager for adding, editing, and deleting machines.

---

## Public Deployment (Recommended: Render)

Render is the best fit for the Flask website because it runs as a conventional Python web service and keeps the in-memory simulation state available to visitors while the instance is running. The repository includes [`render.yaml`](./render.yaml) as a Render Blueprint:

1. Push the repository to GitHub.
2. In Render, choose **New → Blueprint**, connect the repository, and approve the `agro-twin-web` service.
3. Wait for the build and deploy to finish. Render uses `gunicorn` and checks `/api/health`.
4. Open the public `onrender.com` URL shown on the service page.

The free Render plan may sleep when idle, and an instance restart or redeploy resets the demo's in-memory fleet, work orders, and webhook log. This is a shareable demo, not durable fleet storage. The public demo API has no authentication; avoid entering private data or configuring a secret webhook URL on a publicly shared instance.

**Vercel is not recommended** for this single stateful Python app: its serverless execution model is a poor match for an in-memory Flask simulation. If the UI and API are later separated and simulation state moves to persistent storage, that deployment choice can be revisited.

---

## Live Demo Walkthrough (2 Minutes)

1. **Inspect Fleet at Hour 35 (Default View):**
   * `TR-101` (Tractor Alpha) displays `CRITICAL_WARNING` with plain-English root causes **11 hours before** its scheduled Hour 46 breakdown.
   * `SD-304` (Seed Drill Delta) displays `SENSOR_NOISE_FILTERED`, proving isolated sensor spikes do not trigger false dispatches.
   * `TR-105` (Tractor Echo) displays `MISSING_DATA_HOLD` with widened uncertainty error bars.
2. **Execute a Closed-Loop Intervention (Tab 1):**
   * Click **Acknowledge Alert** and **Schedule 4h Service** for `TR-101`.
   * Jump to **Hr 48: Saved!** in the sidebar to see `TR-101` transition to `SERVICED_READY` instead of suffering an 18-hour field breakdown.
3. **Audit Sensor Telemetry & Noise Handling (Tab 2):**
   * Inspect the 4-sensor history plots for `SD-304` and `TR-105` to verify spikes and missing gaps alongside leak-free feature guarantees.
4. **Compare Fair Baseline Outcomes (Tab 3):**
   * Review the side-by-side **Calendar-Only vs. Agro-Twin AI** charts showing availability (`92.22%` to `98.33%`), downtime saved (`44 hrs`), and lead time (`18.3 hrs`).
5. **Test Scarcity & Live Fault Injection (Sidebar):**
   * Adjust available technicians or spare parts to observe `DEFERRED_SCARCITY`, inject a live fault into healthy harvester `HV-206`, or click **Reset Entire Demo** to rewind cleanly to Hour 0.

---

## Tech Stack

* **Machine Learning & Data:** Python, NumPy, pandas, scikit-learn (Random Forest Ensemble)
* **Optimization & Simulation:** Custom priority-weighted constrained scheduler & work-order state machine
* **Backend API:** FastAPI, Uvicorn, Pydantic
* **Frontend & Visualization:** Streamlit, Plotly, Requests

---

## Team — Deadline Dominators

| Member | Role | Module |
|---|---|---|
| **Vansh** | AI & Explainability Lead | `ml/` |
| **Kunal** | Fleet Operations & Optimization Lead | `ops/` |
| **Mohit** | Backend & Twin State Architect | `backend/` |
| **Shashi** | Dashboard UI & Pitch Lead | `frontend/` |