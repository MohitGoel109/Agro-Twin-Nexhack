/* Agro-Twin Interactive Flask Frontend: Calm Canvas Motion, Segmented Views, Live Plotly & On-Topic AI Guide */

const STATUS_META = {
    HEALTHY: { label: "Healthy", color: "#4e7a5c", cls: "" },
    SERVICED_READY: { label: "Serviced & ready", color: "#5b9a6f", cls: "saved" },
    SERVICING: { label: "In service", color: "#6e8898", cls: "saved" },
    DATA_CHECK: { label: "Data hold", color: "#6e8898", cls: "hold" },
    EARLY_WARNING: { label: "Early warning", color: "#b87b28", cls: "urgent" },
    CRITICAL_WARNING: { label: "Critical fault", color: "#d9534f", cls: "urgent" },
    BROKEN_DOWN: { label: "Broken down", color: "#a83834", cls: "urgent" },
};

const SENSOR_LABELS = {
    CLEAN: "Clean feed",
    SENSOR_NOISE_FILTERED: "Spike filtered",
    MISSING_DATA_HOLD: "Missing telemetry",
};

const STATE = {
    step: 35,
    calendarInterval: 72,
    selectedTelemetryUnit: "TR-101",
    fleet: null,
    health: null,
    bgMotionEnabled: true,
};

/* ---------------- 1. Calm Topographic Field Contour Background ---------------- */
function initAmbientCanvas() {
    const canvas = document.getElementById("ambient-bg");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) STATE.bgMotionEnabled = false;

    let width = 0;
    let height = 0;
    let t = 0;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    function drawFrame() {
        ctx.clearRect(0, 0, width, height);

        // Ultra-subtle warm charcoal dot grid
        ctx.fillStyle = "rgba(243, 239, 230, 0.035)";
        const gap = 46;
        for (let x = 24; x < width; x += gap) {
            for (let y = 24; y < height; y += gap) {
                ctx.fillRect(x, y, 1.2, 1.2);
            }
        }

        // Slow drifting agricultural contour lines (very low opacity — never flashy)
        const lineCount = 6;
        for (let i = 0; i < lineCount; i++) {
            ctx.beginPath();
            const baseY = (height / (lineCount + 1)) * (i + 1);
            const isAmber = i === 2 || i === 4;
            ctx.strokeStyle = isAmber
                ? "rgba(229, 154, 50, 0.065)"
                : "rgba(243, 239, 230, 0.04)";
            ctx.lineWidth = 1.1;

            for (let x = 0; x <= width; x += 28) {
                const wave =
                    Math.sin(x * 0.0028 + t * 0.45 + i * 1.1) * 22 +
                    Math.cos(x * 0.0014 - t * 0.25 + i * 0.7) * 14;
                const y = baseY + wave;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        if (STATE.bgMotionEnabled) {
            t += 0.008;
        }
        requestAnimationFrame(drawFrame);
    }

    requestAnimationFrame(drawFrame);

    const toggleBtn = document.getElementById("btn-toggle-bg");
    if (toggleBtn) {
        toggleBtn.textContent = STATE.bgMotionEnabled ? "Motion: On" : "Motion: Off";
        toggleBtn.addEventListener("click", () => {
            STATE.bgMotionEnabled = !STATE.bgMotionEnabled;
            canvas.classList.toggle("paused", !STATE.bgMotionEnabled);
            toggleBtn.textContent = STATE.bgMotionEnabled ? "Motion: On" : "Motion: Off";
        });
    }
}

/* ---------------- 2. Gentle Scroll Reveal & Segment Switcher ---------------- */
function initRevealAndSegments() {
    const sections = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window) {
        const obs = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("visible");
                    }
                });
            },
            { threshold: 0.06 }
        );
        sections.forEach((s) => obs.observe(s));
    } else {
        sections.forEach((s) => s.classList.add("visible"));
    }

    // Topbar segment filter (view All Segments or isolate one cleanly)
    const navButtons = document.querySelectorAll(".nav-link");
    const toggleableSegs = ["seg-fleet", "seg-telemetry", "seg-compare", "seg-ops"];

    navButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            navButtons.forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            const target = btn.dataset.segment;

            toggleableSegs.forEach((id) => {
                const el = document.getElementById(id);
                if (!el) return;
                if (target === "all" || target === id) {
                    el.classList.remove("hidden-seg");
                    el.classList.add("visible");
                } else {
                    el.classList.add("hidden-seg");
                }
            });

            if (target !== "all") {
                const el = document.getElementById(target);
                if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
            } else {
                window.scrollTo({ top: 0, behavior: "smooth" });
            }

            // Resize Plotly charts cleanly when revealed
            setTimeout(() => {
                if (window.Plotly) {
                    ["chart-risk", "chart-telemetry", "chart-compare-avail", "chart-compare-bar"].forEach((cid) => {
                        const node = document.getElementById(cid);
                        if (node && node.data) Plotly.Plots.resize(node);
                    });
                }
            }, 120);
        });
    });
}

/* ---------------- 3. Toast Helper & Fetch Wrapper ---------------- */
let toastTimer = null;
function showToast(msg, kind = "info") {
    const el = document.getElementById("toast-banner");
    if (!el) return;
    el.textContent = msg;
    el.className = `toast ${kind}`;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.add("hidden"), 4200);
}

async function apiJson(url, options = {}) {
    const resp = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    return await resp.json();
}

/* ---------------- 4. Render KPIs, Fleet Cards, Priority Queue & Work Orders ---------------- */
function unitHeadline(m, currentStep) {
    const st = m.status;
    if (st === "SERVICED_READY") {
        return "4-hour preventive repair completed early — 18-hour harvest breakdown prevented.";
    }
    if (st === "SERVICING") return m.recommended_action;
    if (st === "BROKEN_DOWN") {
        return "Unplanned breakdown in field. Unit unavailable for 18 hours during harvest window.";
    }
    if (m.sensor_status === "SENSOR_NOISE_FILTERED") {
        return "Isolated 1-hour sensor spike rejected by 3h rolling median filter. No technician dispatched.";
    }
    if (m.sensor_status === "MISSING_DATA_HOLD") {
        return "Telemetry dropout raised uncertainty band. Holding repair until clean sensor feed returns.";
    }
    if (st === "CRITICAL_WARNING" || st === "EARLY_WARNING") {
        const lead =
            m.actual_breakdown_step && m.actual_breakdown_step > currentStep
                ? `Breakdown in ~${m.actual_breakdown_step - currentStep} hrs if unserviced. `
                : "";
        const stock =
            m.part_in_stock > 0
                ? `${m.part_in_stock}x ${m.part_needed} on shelf.`
                : `${m.part_needed} out of stock.`;
        return `${lead}${stock}`;
    }
    return "Operating inside baseline tolerances across all four sensors.";
}

function renderLedger(fleet) {
    document.getElementById("kpi-hour").textContent = `Hr ${fleet.step}`;
    document.getElementById("kpi-readiness").textContent = `${fleet.fleet_readiness_pct}%`;
    document.getElementById("kpi-active").textContent = `${fleet.machines_available} of ${fleet.machines_total} units active`;
    document.getElementById("kpi-prevented").textContent = `${fleet.breakdowns_prevented}`;
    document.getElementById("kpi-downtime").textContent = `${fleet.total_downtime_hours} hrs total downtime`;
    document.getElementById("kpi-workorders").textContent = `${fleet.open_work_orders_count}`;
    document.getElementById("kpi-flagged").textContent = `${fleet.priority_queue.length} unit(s) flagged`;
    document.getElementById("kpi-techs").textContent = `${fleet.resources.technicians_available} / ${fleet.resources.technicians_total}`;
    document.getElementById("kpi-techs-busy").textContent = `${fleet.resources.technicians_busy} assigned to bay`;

    document.getElementById("step-slider").value = fleet.step;
    document.getElementById("slider-readout").textContent = `Hr ${fleet.step}`;

    // Sync scarcity form inputs with live inventory
    document.getElementById("inp-techs").value = fleet.resources.technicians_total;
    document.getElementById("inp-cp").value = fleet.resources.parts_inventory["Coolant Pump"] ?? 0;
    document.getElementById("inp-hv").value = fleet.resources.parts_inventory["Hydraulic Valve"] ?? 0;
    document.getElementById("inp-db").value = fleet.resources.parts_inventory["Drive Bearing"] ?? 0;
}

function renderRiskChart(machines) {
    const el = document.getElementById("chart-risk");
    if (!el) return;

    if (!window.Plotly) {
        el.innerHTML = `<div style="padding:16px;color:#a8a296;font-size:13px;">Offline chart fallback: ${machines
            .map((m) => `${m.machine_id}: ${(m.fault_probability * 100).toFixed(0)}% (±${(m.uncertainty * 100).toFixed(0)}%)`)
            .join(" | ")}</div>`;
        return;
    }

    const x = machines.map((m) => m.machine_id);
    const y = machines.map((m) => Number((m.fault_probability * 100).toFixed(1)));
    const err = machines.map((m) => Number((m.uncertainty * 100).toFixed(1)));
    const colors = machines.map((m) => {
        if (m.status === "CRITICAL_WARNING" || m.status === "BROKEN_DOWN") return "#e59a32";
        if (m.status === "EARLY_WARNING") return "#b87b28";
        if (m.status === "DATA_CHECK") return "#6e8898";
        if (m.status === "SERVICED_READY" || m.status === "SERVICING") return "#5b9a6f";
        return "#3f3d37";
    });
    const hover = machines.map((m) => {
        const meta = STATUS_META[m.status] || { label: m.status };
        return (
            `<b>${m.machine_id} — ${m.name}</b><br>` +
            `State: ${meta.label}<br>` +
            `Risk: ${(m.fault_probability * 100).toFixed(1)}% (±${(m.uncertainty * 100).toFixed(1)}%)<br>` +
            `Confidence: ${(m.confidence * 100).toFixed(0)}%<br>` +
            `Feed: ${SENSOR_LABELS[m.sensor_status] || m.sensor_status}<br>` +
            `Finding: ${m.reasons[0]}`
        );
    });

    const trace = {
        type: "bar",
        x,
        y,
        width: 0.5,
        marker: { color: colors },
        error_y: { type: "data", array: err, visible: true, color: "#d6d0c4", thickness: 1.6, width: 5 },
        text: y.map((v) => `${Math.round(v)}%`),
        textposition: "outside",
        textfont: { family: "IBM Plex Mono, monospace", size: 11, color: "#f3efe6" },
        hovertext: hover,
        hoverinfo: "text",
    };

    const layout = {
        title: {
            text: "Fault risk by unit with ensemble + missing-data uncertainty bands",
            x: 0,
            font: { family: "IBM Plex Sans, sans-serif", size: 14, color: "#f3efe6" },
        },
        paper_bgcolor: "#161513",
        plot_bgcolor: "#161513",
        font: { family: "IBM Plex Mono, monospace", size: 11, color: "#9c968a" },
        margin: { l: 48, r: 20, t: 48, b: 36 },
        height: 330,
        xaxis: { showgrid: false, linecolor: "#2c2a25" },
        yaxis: { title: "Risk (%)", range: [0, 118], gridcolor: "#26241f", zerolinecolor: "#2c2a25" },
        shapes: [
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 70, y1: 70, line: { color: "#e59a32", width: 1.2, dash: "dot" } },
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 40, y1: 40, line: { color: "#5c5850", width: 1, dash: "dot" } },
        ],
    };

    Plotly.react(el, [trace], layout, { displayModeBar: false, responsive: true });
}

function renderFleetCards(fleet) {
    const grid = document.getElementById("fleet-cards-grid");
    grid.innerHTML = "";

    fleet.machines.forEach((m, idx) => {
        const meta = STATUS_META[m.status] || { label: m.status, color: "#524f47", cls: "" };
        const riskPct = Math.round(m.fault_probability * 100);
        const uncPct = Math.round(m.uncertainty * 100);
        const confPct = Math.round(m.confidence * 100);
        const feedLabel = SENSOR_LABELS[m.sensor_status] || m.sensor_status;
        const ackTag = m.acknowledged ? " · Acknowledged" : "";

        const card = document.createElement("div");
        card.className = `unit-card ${meta.cls}`;
        card.style.animationDelay = `${idx * 40}ms`;

        let actionHtml = "";
        if (m.status === "CRITICAL_WARNING" || m.status === "EARLY_WARNING") {
            actionHtml = `
                <div class="unit-actions">
                    <button class="btn btn-amber" data-schedule="${m.machine_id}">Schedule 4h service (${m.part_needed})</button>
                    ${!m.acknowledged ? `<button class="btn btn-subtle" data-ack="${m.machine_id}">Acknowledge</button>` : ""}
                </div>
            `;
        } else if (m.status === "DATA_CHECK" && !m.acknowledged) {
            actionHtml = `
                <div class="unit-actions">
                    <button class="btn btn-subtle" data-ack="${m.machine_id}">Log sensor check</button>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="unit-top">
                <div>
                    <span class="unit-id">${m.machine_id}</span>
                    <span class="unit-name">${m.name}</span>
                </div>
                <span class="status-tag" style="background:${meta.color};">${meta.label}</span>
            </div>
            <div class="unit-summary">${unitHeadline(m, fleet.step)}</div>
            <div class="risk-meter">
                <div class="risk-meter-fill" style="width:${riskPct}%; background:${meta.color};"></div>
            </div>
            <div class="unit-metrics">
                Risk ${riskPct}% (±${uncPct}%) &nbsp;|&nbsp; Confidence ${confPct}% &nbsp;|&nbsp; ${feedLabel}${ackTag}
            </div>
            <div class="unit-reasons">${m.reasons.join(" · ")}</div>
            ${actionHtml}
        `;

        grid.appendChild(card);
    });

    // Attach live action listeners
    grid.querySelectorAll("[data-schedule]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.schedule;
            const res = await apiJson("/api/schedule", {
                method: "POST",
                body: JSON.stringify({ machine_id: id, step: STATE.step }),
            });
            showToast(res.message || "Scheduled.", res.ok ? "success" : "warning");
            await refreshAll();
        });
    });

    grid.querySelectorAll("[data-ack]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.ack;
            const res = await apiJson("/api/acknowledge", {
                method: "POST",
                body: JSON.stringify({ machine_id: id, step: STATE.step }),
            });
            showToast(res.message || "Acknowledged.", "info");
            await refreshAll();
        });
    });
}

function renderPriorityQueue(fleet) {
    const tbody = document.getElementById("priority-tbody");
    if (!fleet.priority_queue.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="color:#787368;">No units require urgent maintenance at Hour ${fleet.step}.</td></tr>`;
        return;
    }

    tbody.innerHTML = fleet.priority_queue
        .map((p) => {
            const meta = STATUS_META[p.status] || { label: p.status };
            return `
                <tr>
                    <td style="font-family:'IBM Plex Mono',monospace;">${p.machine_id}</td>
                    <td>${p.name}</td>
                    <td>${meta.label}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;color:#e59a32;">${p.priority_score}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${Math.round(p.fault_probability * 100)}%</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${Math.round(p.confidence * 100)}%</td>
                    <td>${p.part_needed} (${p.part_in_stock})</td>
                    <td style="color:#a8a296;">${p.recommended_action}</td>
                </tr>
            `;
        })
        .join("");
}

function renderWorkOrdersAndLog(fleet) {
    const woBody = document.getElementById("wo-tbody");
    if (!fleet.work_orders.length) {
        woBody.innerHTML = `<tr><td colspan="6" style="color:#787368;">No work orders yet. Schedule a 4-hour service on TR-101 in Segment 01 to track its lifecycle here.</td></tr>`;
    } else {
        woBody.innerHTML = fleet.work_orders
            .map(
                (w) => `
                <tr>
                    <td style="font-family:'IBM Plex Mono',monospace;">${w.wo_id}</td>
                    <td>${w.machine_id} — ${w.machine_name}</td>
                    <td>${w.part_needed}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;color:#e59a32;">${w.status}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${
                        w.scheduled_start !== null ? `Hr ${w.scheduled_start}–${w.completion_step}` : "Deferred"
                    }</td>
                    <td style="color:#a8a296;">${w.reason}</td>
                </tr>
            `
            )
            .join("");
    }

    const logBox = document.getElementById("event-log-list");
    if (!fleet.recent_events.length) {
        logBox.innerHTML = `<div class="audit-item">No operator actions recorded yet. Acknowledgements, dispatches, and scarcity edits appear here live.</div>`;
    } else {
        logBox.innerHTML = [...fleet.recent_events]
            .reverse()
            .map((e) => {
                const stepStr = e.step !== undefined ? `[Hr ${e.step}] ` : "";
                const target = e.machine_id ? ` · ${e.machine_id}` : "";
                const wo = e.wo_id ? ` · ${e.wo_id}` : "";
                return `<div class="audit-item">${stepStr}<strong style="color:#f3efe6;">${e.event}</strong>${target}${wo}</div>`;
            })
            .join("");
    }
}

/* ---------------- 5. Telemetry & Explainability Segment ---------------- */
async function refreshTelemetry() {
    const unitId = STATE.selectedTelemetryUnit;
    const detail = await apiJson(`/api/machines/${unitId}/history?up_to_step=${STATE.step}`);
    if (!detail.ok) return;

    const m = detail.machine;
    const meta = STATUS_META[m.status] || { label: m.status };

    document.getElementById("telemetry-explain-box").innerHTML = `
        <div><strong>Unit:</strong> ${m.machine_id} — ${m.name}</div>
        <div><strong>State:</strong> ${meta.label} &nbsp;|&nbsp; <strong>Feed:</strong> ${SENSOR_LABELS[m.sensor_status] || m.sensor_status}</div>
        <div><strong>Fault Risk:</strong> ${(m.fault_probability * 100).toFixed(1)}% (±${(m.uncertainty * 100).toFixed(1)}% uncertainty) &nbsp;|&nbsp; <strong>Confidence:</strong> ${(m.confidence * 100).toFixed(0)}%</div>
        <div><strong>Findings:</strong><br>${m.reasons.map((r) => `• ${r}`).join("<br>")}</div>
    `;

    if (STATE.health && STATE.health.model_info) {
        const info = STATE.health.model_info;
        document.getElementById("model-rules-box").innerHTML = `
            <div><strong>Model:</strong> ${info.model_type}</div>
            <div><strong>Noise Filter:</strong> ${info.noise_filter}</div>
            <div><strong>Leak-Free Guarantee:</strong> ${info.leak_free_guarantee}</div>
            <div><strong>Uncertainty Method:</strong> ${info.uncertainty_method}</div>
        `;
    }

    const el = document.getElementById("chart-telemetry");
    if (!window.Plotly) {
        el.innerHTML = `<div style="padding:16px;color:#a8a296;">Telemetry points loaded: ${detail.history.length} hours for ${unitId}.</div>`;
        return;
    }

    const hist = detail.history;
    const steps = hist.map((h) => h.step);
    const traces = [
        { x: steps, y: hist.map((h) => h.engine_temp), name: "Engine Temp (C)", mode: "lines+markers", line: { color: "#e59a32", width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x", yaxis: "y" },
        { x: steps, y: hist.map((h) => h.vibration), name: "Vibration (mm/s)", mode: "lines+markers", line: { color: "#d97736", width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x2", yaxis: "y2" },
        { x: steps, y: hist.map((h) => h.oil_pressure), name: "Oil Pressure (PSI)", mode: "lines+markers", line: { color: "#6e8898", width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x3", yaxis: "y3" },
        { x: steps, y: hist.map((h) => h.rpm_variance), name: "RPM Variance (RPM)", mode: "lines+markers", line: { color: "#5b9a6f", width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x4", yaxis: "y4" },
    ];

    const layout = {
        title: {
            text: `Raw hourly telemetry — ${unitId} (gaps = missing readings, baseline dashed)`,
            x: 0,
            font: { family: "IBM Plex Sans, sans-serif", size: 14, color: "#f3efe6" },
        },
        grid: { rows: 2, columns: 2, pattern: "independent", roworder: "top to bottom" },
        paper_bgcolor: "#161513",
        plot_bgcolor: "#161513",
        font: { family: "IBM Plex Mono, monospace", size: 10, color: "#9c968a" },
        height: 430,
        showlegend: false,
        margin: { l: 48, r: 20, t: 54, b: 36 },
        yaxis: { title: "Temp (C)", gridcolor: "#26241f" },
        yaxis2: { title: "Vib (mm/s)", gridcolor: "#26241f" },
        yaxis3: { title: "Oil (PSI)", gridcolor: "#26241f" },
        yaxis4: { title: "RPM Var", gridcolor: "#26241f" },
        xaxis: { showgrid: false },
        xaxis2: { showgrid: false },
        xaxis3: { showgrid: false, title: "Harvest hour" },
        xaxis4: { showgrid: false, title: "Harvest hour" },
    };

    Plotly.react(el, traces, layout, { displayModeBar: false, responsive: true });
}

/* ---------------- 6. Fair Baseline Comparison Segment ---------------- */
async function refreshComparison() {
    const comp = await apiJson(`/api/compare?calendar_interval=${STATE.calendarInterval}`);
    const cal = comp.calendar_only;
    const ai = comp.ai_twin;
    const imp = comp.improvement;

    document.getElementById("cmp-avail").textContent = `${ai.fleet_availability_pct}%`;
    document.getElementById("cmp-avail-gain").textContent = `+${imp.availability_gain_pct}% over calendar (${cal.fleet_availability_pct}%)`;
    document.getElementById("cmp-saved").textContent = `${imp.downtime_hours_saved} hrs`;
    document.getElementById("cmp-downtime-split").textContent = `${ai.total_downtime_hours}h AI vs. ${cal.total_downtime_hours}h calendar`;
    document.getElementById("cmp-breakdowns").textContent = `${ai.unplanned_breakdowns}`;
    document.getElementById("cmp-breakdowns-note").textContent = `${imp.breakdowns_avoided} avoided (vs. ${cal.unplanned_breakdowns} calendar)`;
    document.getElementById("cmp-lead").textContent = `${ai.avg_warning_lead_time_hours} hrs`;
    document.getElementById("cmp-holds").textContent = `${ai.noisy_or_missing_alerts_held} noisy/missing alerts held`;

    if (!window.Plotly) return;

    const steps = comp.hourly_series.map((p) => p.step);
    const availTraces = [
        {
            x: steps,
            y: comp.hourly_series.map((p) => p.calendar_availability_pct),
            name: "Calendar-only",
            mode: "lines",
            line: { color: "#8c867a", width: 2, dash: "dash" },
        },
        {
            x: steps,
            y: comp.hourly_series.map((p) => p.ai_twin_availability_pct),
            name: "Agro-Twin AI",
            mode: "lines",
            line: { color: "#e59a32", width: 2.8 },
            fill: "tonexty",
            fillcolor: "rgba(229, 154, 50, 0.12)",
        },
    ];

    Plotly.react(
        "chart-compare-avail",
        availTraces,
        {
            title: { text: "Hourly availability (120h harvest)", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: "#f3efe6" } },
            paper_bgcolor: "#161513",
            plot_bgcolor: "#161513",
            font: { family: "IBM Plex Mono, monospace", size: 11, color: "#9c968a" },
            height: 330,
            margin: { l: 48, r: 16, t: 50, b: 40 },
            xaxis: { title: "Harvest hour", showgrid: false },
            yaxis: { title: "Available (%)", range: [45, 105], gridcolor: "#26241f" },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" },
        },
        { displayModeBar: false, responsive: true }
    );

    const barCats = ["Downtime (hrs)", "Unplanned breakdowns", "Warning lead (hrs)"];
    const barTraces = [
        {
            type: "bar",
            name: "Calendar-only",
            x: barCats,
            y: [cal.total_downtime_hours, cal.unplanned_breakdowns, cal.avg_warning_lead_time_hours],
            marker: { color: "#524f47" },
            text: [`${cal.total_downtime_hours}h`, `${cal.unplanned_breakdowns}`, `${cal.avg_warning_lead_time_hours}h`],
            textposition: "outside",
        },
        {
            type: "bar",
            name: "Agro-Twin AI",
            x: barCats,
            y: [ai.total_downtime_hours, ai.unplanned_breakdowns, ai.avg_warning_lead_time_hours],
            marker: { color: "#e59a32" },
            text: [`${ai.total_downtime_hours}h`, `${ai.unplanned_breakdowns}`, `${ai.avg_warning_lead_time_hours}h`],
            textposition: "outside",
        },
    ];

    Plotly.react(
        "chart-compare-bar",
        barTraces,
        {
            title: { text: "Measured outcome comparison", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: "#f3efe6" } },
            barmode: "group",
            paper_bgcolor: "#161513",
            plot_bgcolor: "#161513",
            font: { family: "IBM Plex Mono, monospace", size: 11, color: "#9c968a" },
            height: 330,
            margin: { l: 44, r: 16, t: 50, b: 40 },
            xaxis: { showgrid: false },
            yaxis: { gridcolor: "#26241f" },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" },
        },
        { displayModeBar: false, responsive: true }
    );
}

/* ---------------- 7. Populate Dropdowns & Refresh Master State ---------------- */
let dropdownsInitialized = false;
function syncMachineSelects(machines) {
    if (dropdownsInitialized) return;
    dropdownsInitialized = true;

    const telSel = document.getElementById("telemetry-unit-select");
    const injSel = document.getElementById("inj-machine");

    machines.forEach((m) => {
        const opt1 = document.createElement("option");
        opt1.value = m.machine_id;
        opt1.textContent = `${m.machine_id} — ${m.name}`;
        telSel.appendChild(opt1);

        const opt2 = document.createElement("option");
        opt2.value = m.machine_id;
        opt2.textContent = `${m.machine_id} — ${m.name}`;
        injSel.appendChild(opt2);
    });

    telSel.value = STATE.selectedTelemetryUnit;
    injSel.value = machines[machines.length - 1].machine_id;
}

async function refreshAll() {
    if (!STATE.health) {
        STATE.health = await apiJson("/api/health");
    }
    const fleet = await apiJson(`/api/fleet?step=${STATE.step}`);
    STATE.fleet = fleet;
    STATE.step = fleet.step;

    syncMachineSelects(fleet.machines);
    renderLedger(fleet);
    renderRiskChart(fleet.machines);
    renderFleetCards(fleet);
    renderPriorityQueue(fleet);
    renderWorkOrdersAndLog(fleet);
    await refreshTelemetry();
}

/* ---------------- 8. Wire Timeline, Scarcity & Fault Injection Controls ---------------- */
function initControls() {
    const slider = document.getElementById("step-slider");
    slider.addEventListener("input", () => {
        document.getElementById("slider-readout").textContent = `Hr ${slider.value}`;
    });
    slider.addEventListener("change", async () => {
        STATE.step = Number(slider.value);
        await refreshAll();
    });

    document.getElementById("btn-prev-hr").addEventListener("click", async () => {
        STATE.step = Math.max(0, STATE.step - 1);
        await refreshAll();
    });

    document.getElementById("btn-next-hr").addEventListener("click", async () => {
        STATE.step = Math.min(119, STATE.step + 1);
        await refreshAll();
    });

    document.querySelectorAll("[data-jump]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            STATE.step = Number(btn.dataset.jump);
            await refreshAll();
        });
    });

    document.getElementById("btn-reset").addEventListener("click", async () => {
        const res = await apiJson("/api/reset", { method: "POST" });
        STATE.step = 35;
        showToast(res.message || "Reset cleanly.", "success");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("telemetry-unit-select").addEventListener("change", async (e) => {
        STATE.selectedTelemetryUnit = e.target.value;
        await refreshTelemetry();
    });

    const calSlider = document.getElementById("cal-interval-slider");
    calSlider.addEventListener("input", () => {
        document.getElementById("cal-interval-readout").textContent = `${calSlider.value} hrs`;
    });
    calSlider.addEventListener("change", async () => {
        STATE.calendarInterval = Number(calSlider.value);
        await refreshComparison();
    });

    document.getElementById("btn-apply-constraints").addEventListener("click", async () => {
        const payload = {
            technicians_total: Number(document.getElementById("inp-techs").value),
            parts_inventory: {
                "Coolant Pump": Number(document.getElementById("inp-cp").value),
                "Hydraulic Valve": Number(document.getElementById("inp-hv").value),
                "Drive Bearing": Number(document.getElementById("inp-db").value),
            },
        };
        const res = await apiJson("/api/constraints", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        showToast(res.message || "Constraints updated.", "info");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-inject-fault").addEventListener("click", async () => {
        const payload = {
            machine_id: document.getElementById("inj-machine").value,
            start_step: STATE.step,
            fault_type: document.getElementById("inj-type").value,
        };
        const res = await apiJson("/api/inject-fault", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        showToast(res.message || "Fault injected.", res.ok ? "warning" : "info");
        await refreshAll();
        await refreshComparison();
    });
}

/* ---------------- 9. Strict On-Topic AI Assistant Drawer ---------------- */
function formatMarkdownSimple(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function appendAiMessage(text, role = "bot", isWarning = false) {
    const box = document.getElementById("ai-messages");
    const div = document.createElement("div");
    if (isWarning) {
        div.className = "msg warning";
        div.innerHTML = `<div class="msg-badge">OFF-TOPIC GUARDRAIL</div><div>${formatMarkdownSimple(text)}</div>`;
    } else {
        div.className = `msg ${role}`;
        div.innerHTML = formatMarkdownSimple(text);
    }
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function updateAiChips(suggestions = []) {
    if (!suggestions.length) return;
    const container = document.getElementById("ai-chips");
    container.innerHTML = "";
    suggestions.forEach((q) => {
        const btn = document.createElement("button");
        btn.className = "chip";
        btn.textContent = q;
        btn.addEventListener("click", () => sendAiQuestion(q));
        container.appendChild(btn);
    });
}

async function sendAiQuestion(question) {
    const trimmed = question.trim();
    if (!trimmed) return;
    appendAiMessage(trimmed, "user", false);

    try {
        const res = await apiJson("/api/assistant", {
            method: "POST",
            body: JSON.stringify({ question: trimmed }),
        });
        appendAiMessage(res.answer, "bot", Boolean(res.warning));
        if (res.suggested_questions) {
            updateAiChips(res.suggested_questions);
        }
    } catch (err) {
        appendAiMessage("Could not reach the Agro-Twin AI endpoint. Ensure Flask server is running.", "bot", true);
    }
}

function initAssistantDrawer() {
    const drawer = document.getElementById("ai-drawer");
    const fab = document.getElementById("ai-fab");
    const openTop = document.getElementById("btn-open-ai");
    const closeBtn = document.getElementById("btn-close-ai");
    const form = document.getElementById("ai-form");
    const input = document.getElementById("ai-input");

    function openDrawer() {
        drawer.classList.remove("closed");
        input.focus();
    }
    function closeDrawer() {
        drawer.classList.add("closed");
    }

    fab.addEventListener("click", openDrawer);
    openTop.addEventListener("click", openDrawer);
    closeBtn.addEventListener("click", closeDrawer);

    document.querySelectorAll(".btn-ask-seg").forEach((btn) => {
        btn.addEventListener("click", () => {
            openDrawer();
            sendAiQuestion(btn.dataset.prompt);
        });
    });

    document.querySelectorAll("#ai-chips .chip").forEach((chip) => {
        chip.addEventListener("click", () => sendAiQuestion(chip.dataset.q));
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const q = input.value;
        input.value = "";
        await sendAiQuestion(q);
    });

    // Welcome onboarding message explaining how to use the site & guardrail
    appendAiMessage(
        "Hello! I am the **Agro-Twin Website Guide**. I can explain how to use any segment of this website, check live machine health, or explain our AI & baseline results. Note: I strictly answer questions about this website only — off-topic questions are blocked.",
        "bot",
        false
    );
}

/* ---------------- Boot Application ---------------- */
window.addEventListener("DOMContentLoaded", async () => {
    initAmbientCanvas();
    initRevealAndSegments();
    initControls();
    initAssistantDrawer();
    await refreshAll();
    await refreshComparison();
});
