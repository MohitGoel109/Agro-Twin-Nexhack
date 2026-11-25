# 🚜 Agro-Twin — Predictive Maintenance Digital Twin for Farm Machinery

> **NexHack 2.0** (Geeta University, Panipat) | **Track:** AI in Agriculture — **Problem Statement 08**  
> **Team:** Deadline Dominators (Vansh, Kunal, Mohit, Shashi)

**Repository:** [MohitGoel109/Agro-Twin-Nexhack](https://github.com/MohitGoel109/Agro-Twin-Nexhack)

**Agro-Twin** is an explainable predictive-maintenance digital-twin demonstration for shared agricultural machinery fleets. It combines deterministic synthetic telemetry, a leak-free sliding-window ML model, constrained maintenance scheduling, a Flask website, a Streamlit dashboard, and FastAPI services.

Agro-Twin replays hourly simulated telemetry, separates noisy or missing sensor data, quantifies ensemble uncertainty, prioritizes maintenance under limited technicians and spare parts, and compares an AI replay with the repository's calendar-only baseline. The metrics below are generated from the project's 120-hour demo scenario; they are not results from real farm deployments.

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
├── Dockerfile                 # Non-root production image for the Flask website
├── .github/workflows/ci.yml   # Tests, verification, and Docker image build
└── render.yaml                # Render Blueprint for the public Flask website
```

---

## Quick Start (Local Setup)

### 1. Prerequisites
- Python **3.12** (CI uses Python 3.12)
- Git
- Optional: Docker Desktop for container checks
- Optional: Chrome or Edge for browser speech recognition

### 2. Clone and create an isolated environment

**Windows PowerShell**
```bash
git clone https://github.com/MohitGoel109/Agro-Twin-Nexhack.git
cd Agro-Twin-Nexhack
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
```

**macOS/Linux**
```bash
git clone https://github.com/MohitGoel109/Agro-Twin-Nexhack.git
cd Agro-Twin-Nexhack
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
```

### 3. Verify the repository

Run the complete test suite:
```bash
python -m pytest tests -q
```

Then run the standalone verifiers:
```bash
python ml/verify_ml.py
python ops/verify_ops.py
python backend/verify_backend.py
python web/verify_web.py
python frontend/verify_frontend.py
```

At the current code state, the pytest suite and verifier scripts can be run independently. If an optional environment is missing, install the dependencies in `requirements.txt` before retrying.

### 4. Launch the Flask website

The Flask application is the recommended demo entry point:

```bash
python web/app.py
```

Open:
- **Home:** http://localhost:5000/
- **Machines:** http://localhost:5000/machines
- **Machine Picture:** http://localhost:5000/picture
- **Money Saved:** http://localhost:5000/savings
- **Repairs:** http://localhost:5000/repairs
- **Farmer Check-up:** http://localhost:5000/checkup

All state is in memory. Restarting or redeploying resets the demo fleet, work orders, check-ups, and webhook log.

### 5. Launch the FastAPI service

In another terminal:
```bash
uvicorn backend.app:app --reload --port 8000
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Check-up routes: `/questions`, `/machines/{machine_id}/farmer-report`, and `/machines/{machine_id}/report`

FastAPI CORS is closed by default. To allow a separate browser origin, set a comma-separated allowlist before startup:

**Windows PowerShell**
```powershell
$env:AGRO_TWIN_CORS_ORIGINS="http://localhost:8501"
uvicorn backend.app:app --reload --port 8000
```

**macOS/Linux**
```bash
AGRO_TWIN_CORS_ORIGINS="http://localhost:8501" uvicorn backend.app:app --reload --port 8000
```

Do not add `*` as a production origin.

### 6. Launch the Streamlit dashboard

In another terminal:
```bash
streamlit run frontend/dashboard.py
```

- Dashboard: http://localhost:8501
- The API client can fall back to direct local twin state if FastAPI is unavailable.

---

## Implementation Status

| Feature | Repository support | Important limitation |
|---|---|---|
| 120-hour digital-twin replay | Implemented | Synthetic/demo telemetry, not live field data |
| 6-machine baseline fleet | Implemented | Fleet starts at Hour 35; can be managed at runtime |
| Dynamic fleet add/edit/delete | Implemented | State is in memory and resets on restart |
| Noise and missing-data handling | Implemented | Demonstrated on generated sensor values |
| Calendar vs. AI comparison | Implemented | Verification metrics come from the bundled scenario |
| Flask segmented website | Implemented | `/`, `/machines`, `/picture`, `/savings`, `/repairs`, `/checkup` |
| Farmer check-up | Implemented | Rule-based, English/Hindi UI, printable reports and English PDF |
| Bulk simulated ML model | Implemented | Trained only on synthetic assumptions; not validated on real tractors |
| AI4I public benchmark | Implemented with a precomputed report | The CSV is not committed; live rerun requires downloaded `data/ai4i2020.csv` |
| FastAPI Swagger routes | Implemented | FastAPI check-up routes are separately mounted under the backend app |
| Browser voice recognition | Implemented | Requires compatible browser permissions and is not available in every environment |
| SMS job-card generation | Implemented | Creates text/cards locally; no SMS provider is contacted |
| Webhook dispatch | Implemented | Sends to a user-configured HTTP endpoint; no default third-party webhook |
| Authentication | Not implemented | Public demo is unauthenticated |
| Persistent storage | Not implemented | No database or durable fleet-state storage |
| Real tractor training data | Not implemented | Do not interpret model scores as real-world approval or certification |

## Docker

Build and run the Flask demo on Windows, macOS, or Linux:

```bash
docker build -t agro-twin-web .
docker run --rm -p 5000:5000 agro-twin-web
```

Open http://localhost:5000. GitHub Actions builds the image on pushes and pull requests. Docker Desktop must be running for local Docker commands.

---

## Public Deployment (Recommended: Render)

**Optional public website:** [agro-twin-web.onrender.com](https://agro-twin-web.onrender.com)

This URL is only available when the corresponding Render service is deployed and running. It is a demo environment and resets when the instance restarts.

Render is the best fit for the Flask website because it runs as a conventional Python web service and keeps the in-memory simulation state available to visitors while the instance is running. The repository includes [`render.yaml`](./render.yaml) as a Render Blueprint. Render builds the repository's Docker image and waits for GitHub Actions checks to pass before deploying:

1. Push the repository to GitHub.
2. For a new service, choose **New → Blueprint** and connect the repository. For an existing service, sync the updated Blueprint to switch it to the Docker runtime.
3. Ensure the repository's GitHub Actions workflow is enabled. Render deploys only after the checks pass and checks `/api/health`.
4. Open the public `onrender.com` URL shown on the service page.

To build and run the same container locally:
```bash
docker build -t agro-twin-web .
docker run --rm -p 5000:5000 agro-twin-web
```

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

## Farmer Check-up

Owner form + sound/smell/smoke/look/feel questions -> rule-based scoring (rules of thumb, NOT machine learning)
-> verdict (OK / WATCH / SERVICE SOON / STOP NOW) -> downloadable report (English PDF, English/Hindi printable page).
Open `/checkup` on the website. The advice text needs a mechanic's review and the Hindi needs a native speaker's review.

## Training data and validation (bulk, SIMULATED)

`python ml/bulk_data.py --n 5000 --seed 42` generates a simulated fleet (data/bulk_fleet.csv, not committed).
`python ml/train_bulk.py --n 5000 --seed 42` trains a Random Forest (fault by system) and a Random Forest regressor
(hours until failure) on 3,500 machines and tests on 1,500 machines never seen in training (split by machine id).
Results are in `ml/bulk_report.json` (see the table printed by the script). We compare against a fixed-interval service rule.

## Public benchmark (UCI AI4I 2020)

`python ml/benchmark_ai4i.py` (needs `data/ai4i2020.csv`, not committed) trains a Random Forest per failure type on 70% of
the 10,000 records and tests on the other 30%. Any-failure F1 0.89 vs 0.20 for the rule "tool wear > 200 min". Results in
`ml/ai4i_report.json`. This is a different machine type (milling) and itself synthetic: it shows the method works on a
public benchmark, not that it works on tractors. Tool-wear failures are predicted poorly and random failures not at all.

## Limitations

- All data is simulated from our own assumptions (wear model + placeholder service intervals). High scores show the method
  works, not that it is accurate on real tractors. Next step: validation on real pilot-pool logs.
- Service intervals in `checkup/service_intervals.json` are placeholders until checked against the manufacturer's manual.
- The symptom and idle-damage rules are expert rules of thumb, not validated on real data.
- The existing sensor model and the calendar-vs-Agro-Twin comparison (92.22% vs 98.33%) are unchanged by the bulk model.
