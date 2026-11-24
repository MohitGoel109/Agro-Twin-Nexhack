/* Agro-Twin Interactive Flask Frontend: SVG X-Ray Blueprint, EN/हिंदी Voice, Weather Stress, Rupee ROI, SMS Cards & On-Topic AI Guide */

const STATUS_META = {
    HEALTHY: { label: "Healthy", labelHi: "स्वस्थ", cls: "" },
    SERVICED_READY: { label: "Serviced & ready", labelHi: "सर्विस पूर्ण", cls: "saved" },
    SERVICING: { label: "In service", labelHi: "सर्विस जारी", cls: "saved" },
    DATA_CHECK: { label: "Data hold", labelHi: "डेटा जांच", cls: "hold" },
    EARLY_WARNING: { label: "Early warning", labelHi: "प्रारंभिक चेतावनी", cls: "urgent" },
    CRITICAL_WARNING: { label: "Critical fault", labelHi: "गंभीर खराबी", cls: "urgent" },
    BROKEN_DOWN: { label: "Broken down", labelHi: "मशीन बंद", cls: "urgent" },
};

const SENSOR_LABELS = {
    CLEAN: "Clean feed",
    SENSOR_NOISE_FILTERED: "Spike filtered",
    MISSING_DATA_HOLD: "Missing telemetry",
};

const I18N = {
    en: {
        trackTag: "AI in Agriculture",
        navAll: "All Segments",
        navFleet: "01 · Fleet",
        navTel: "02 · X-Ray & Telemetry",
        navImpact: "03 · Rupee ROI",
        navOps: "04 · SMS & Ops",
        askGuide: "Ask AI Guide",
        eyebrow: "AI in Agriculture · Predictive Maintenance Digital Twin",
        heroTitle: "Catch farm machinery faults before harvest stalls.",
        heroSub:
            "Built for shared rural tractor and harvester fleets. Agro-Twin replays ordinary machine sensors, separates isolated sensor spikes and dropouts from genuine wear, and prioritizes scarce mechanics and spare parts with plain-English and Hindi explainability.",
        kpiHourLbl: "Harvest hour",
        kpiReadyLbl: "Fleet readiness",
        kpiPrevLbl: "Breakdowns prevented",
        kpiWoLbl: "Open work orders",
        kpiTechLbl: "Technicians free",
    },
    hi: {
        trackTag: "कृषि में एआई",
        navAll: "सभी भाग",
        navFleet: "01 · बेड़ा स्थिति",
        navTel: "02 · एक्स-रे और सेंसर",
        navImpact: "03 · रुपये (₹) बचत",
        navOps: "04 · SMS और कार्य",
        askGuide: "AI गाइड से पूछें",
        eyebrow: "कृषि में एआई · प्रेडिक्टिव मेंटेनेंस डिजिटल ट्विन",
        heroTitle: "कटाई रुकने से पहले कृषि मशीनों की खराबी पहचानें।",
        heroSub:
            "साझा ट्रैक्टर और हार्वेस्टर बेड़े के लिए निर्मित। Agro-Twin सेंसर डेटा से असली घिसाव और झूठे अलार्म में अंतर करता है और मैकेनिक व स्पेयर पार्ट्स को प्राथमिकता देता है।",
        kpiHourLbl: "कटाई घंटा",
        kpiReadyLbl: "बेड़ा उपलब्धता",
        kpiPrevLbl: "रोके गए ब्रेकडाउन",
        kpiWoLbl: "खुले वर्क ऑर्डर",
        kpiTechLbl: "उपलब्ध मैकेनिक",
    },
};

const STATE = {
    step: 35,
    calendarInterval: 72,
    selectedTelemetryUnit: "TR-101",
    weatherMode: "normal",
    lang: "en",
    fleet: null,
    health: null,
    bgMotionEnabled: true,
    ambientColors: {
        dot: "rgba(243, 239, 230, 0.035)",
        line: "rgba(243, 239, 230, 0.04)",
        accent: "rgba(229, 154, 50, 0.065)",
    },
};

const THEMES = new Set(["dark", "light", "harvest", "forest", "ocean"]);

function themeColor(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function statusColor(status) {
    const colorByStatus = {
        HEALTHY: "--chart-rpm",
        SERVICED_READY: "--chart-rpm",
        SERVICING: "--chart-oil",
        DATA_CHECK: "--chart-oil",
        EARLY_WARNING: "--chart-vibration",
        CRITICAL_WARNING: "--accent-brick",
        BROKEN_DOWN: "--accent-brick",
    };
    return themeColor(colorByStatus[status] || "--chart-muted");
}

function initThemeSelector() {
    const selector = document.getElementById("theme-select");
    if (!selector) return;

    let savedTheme = "dark";
    try {
        const storedTheme = localStorage.getItem("agro-twin-theme");
        if (THEMES.has(storedTheme)) savedTheme = storedTheme;
    } catch (error) {
        console.warn("Unable to read the saved theme preference.", error);
    }

    const applyTheme = (theme) => {
        const selectedTheme = THEMES.has(theme) ? theme : "dark";
        document.documentElement.dataset.theme = selectedTheme;
        selector.value = selectedTheme;
        STATE.ambientColors = {
            dot: themeColor("--ambient-dot"),
            line: themeColor("--ambient-line"),
            accent: themeColor("--ambient-accent"),
        };
    };

    applyTheme(savedTheme);
    selector.addEventListener("change", () => {
        const theme = selector.value;
        applyTheme(theme);
        try {
            localStorage.setItem("agro-twin-theme", theme);
        } catch (error) {
            console.warn("Unable to save the theme preference.", error);
        }

        if (STATE.fleet) {
            renderRiskChart(STATE.fleet.machines);
            refreshTelemetry();
            refreshComparison();
        }
    });
}

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

        ctx.fillStyle = STATE.ambientColors.dot;
        const gap = 46;
        for (let x = 24; x < width; x += gap) {
            for (let y = 24; y < height; y += gap) {
                ctx.fillRect(x, y, 1.2, 1.2);
            }
        }

        const lineCount = 6;
        for (let i = 0; i < lineCount; i++) {
            ctx.beginPath();
            const baseY = (height / (lineCount + 1)) * (i + 1);
            const isAmber = i === 2 || i === 4;
            ctx.strokeStyle = isAmber ? STATE.ambientColors.accent : STATE.ambientColors.line;
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

/* ---------------- 2. Bilingual EN / हिंदी Toggle & Browser Voice Readout ---------------- */
function applyLanguage() {
    const dict = I18N[STATE.lang] || I18N.en;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.dataset.i18n;
        if (dict[key]) el.textContent = dict[key];
    });
    const langBtn = document.getElementById("btn-lang");
    if (langBtn) {
        langBtn.textContent = STATE.lang === "en" ? "EN / हिंदी" : "हिंदी / EN";
    }
    if (STATE.fleet) {
        renderFleetCards(STATE.fleet);
    }
}

function speakPriorityAlert() {
    if (!("speechSynthesis" in window)) {
        showToast("Browser speech synthesis is not supported in this browser.", "warning");
        return;
    }
    window.speechSynthesis.cancel();
    const fleet = STATE.fleet;
    if (!fleet) return;

    const top = fleet.priority_queue && fleet.priority_queue.length ? fleet.priority_queue[0] : null;
    let speechText = "";
    if (STATE.lang === "hi") {
        speechText = top
            ? `चेतावनी। ${top.machine_id} में ${Math.round(top.fault_probability * 100)} प्रतिशत खराबी का जोखिम है। कृपया 4 घंटे की अग्रिम सर्विस बुक करें और ${top.part_needed} तैयार रखें।`
            : `घंटा ${fleet.step} पर सभी कृषि मशीनें सामान्य रूप से कार्य कर रही हैं।`;
    } else {
        speechText = top
            ? `Agro-Twin Alert. Unit ${top.machine_id}, ${top.name}, has ${Math.round(top.fault_probability * 100)} percent fault risk. Schedule a 4-hour preventive service using ${top.part_needed}.`
            : `Agro-Twin status at Hour ${fleet.step}. All six agricultural units are operating normally.`;
    }

    const utter = new SpeechSynthesisUtterance(speechText);
    utter.lang = STATE.lang === "hi" ? "hi-IN" : "en-IN";
    utter.rate = 0.98;
    window.speechSynthesis.speak(utter);
    showToast(STATE.lang === "hi" ? "हिंदी अलर्ट पढ़ा जा रहा है..." : "Speaking priority alert aloud...", "info");
}

/* ---------------- 3. Gentle Scroll Reveal & Segment Switcher ---------------- */
function initRevealAndSegments() {
    const sections = document.querySelectorAll(".reveal");
    if ("IntersectionObserver" in window) {
        const obs = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) entry.target.classList.add("visible");
                });
            },
            { threshold: 0.06 }
        );
        sections.forEach((s) => obs.observe(s));
    } else {
        sections.forEach((s) => s.classList.add("visible"));
    }

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

/* ---------------- 4. Toast Helper & Fetch Wrapper ---------------- */
let toastTimer = null;
function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    })[char]);
}

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

/* ---------------- 5. Render KPIs, Fleet Cards, Priority Queue & Work Orders ---------------- */
function unitHeadline(m, currentStep) {
    const st = m.status;
    if (st === "SERVICED_READY") {
        return STATE.lang === "hi"
            ? "4 घंटे की अग्रिम मरम्मत पूर्ण — 18 घंटे का ब्रेकडाउन रोका गया।"
            : "4-hour preventive repair completed early — 18-hour harvest breakdown prevented.";
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
    const wMode = fleet.weather_mode || STATE.weatherMode;
    STATE.weatherMode = wMode;
    document.getElementById("kpi-weather-note").textContent =
        wMode === "heatwave_45c" ? "Heatwave 45°C thermal stress" : "Normal 30°C field weather";

    document.getElementById("btn-weather-normal").classList.toggle("active-weather", wMode !== "heatwave_45c");
    document.getElementById("btn-weather-heat").classList.toggle("active-weather", wMode === "heatwave_45c");

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

    document.getElementById("inp-techs").value = fleet.resources.technicians_total;
    document.getElementById("inp-cp").value = fleet.resources.parts_inventory["Coolant Pump"] ?? 0;
    document.getElementById("inp-hv").value = fleet.resources.parts_inventory["Hydraulic Valve"] ?? 0;
    document.getElementById("inp-db").value = fleet.resources.parts_inventory["Drive Bearing"] ?? 0;
}

function renderRiskChart(machines) {
    const el = document.getElementById("chart-risk");
    if (!el) return;

    if (!window.Plotly) {
        el.innerHTML = `<div style="padding:16px;color:var(--text-secondary);font-size:13px;">Offline chart fallback: ${machines
            .map((m) => `${m.machine_id}: ${(m.fault_probability * 100).toFixed(0)}% (±${(m.uncertainty * 100).toFixed(0)}%)`)
            .join(" | ")}</div>`;
        return;
    }

    const x = machines.map((m) => m.machine_id);
    const y = machines.map((m) => Number((m.fault_probability * 100).toFixed(1)));
    const err = machines.map((m) => Number((m.uncertainty * 100).toFixed(1)));
    const colors = machines.map((m) => {
        if (m.status === "CRITICAL_WARNING" || m.status === "BROKEN_DOWN") return themeColor("--chart-temp");
        if (m.status === "EARLY_WARNING") return themeColor("--chart-vibration");
        if (m.status === "DATA_CHECK") return themeColor("--chart-oil");
        if (m.status === "SERVICED_READY" || m.status === "SERVICING") return themeColor("--chart-rpm");
        return themeColor("--chart-muted");
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
        error_y: { type: "data", array: err, visible: true, color: themeColor("--chart-text"), thickness: 1.6, width: 5 },
        text: y.map((v) => `${Math.round(v)}%`),
        textposition: "outside",
        textfont: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-title") },
        hovertext: hover,
        hoverinfo: "text",
    };

    const layout = {
        title: {
            text: "Fault risk by unit with ensemble + missing-data uncertainty bands",
            x: 0,
            font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") },
        },
        paper_bgcolor: themeColor("--chart-paper"),
        plot_bgcolor: themeColor("--chart-plot"),
        font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
        margin: { l: 48, r: 20, t: 48, b: 36 },
        height: 330,
        xaxis: { showgrid: false, linecolor: themeColor("--chart-axis") },
        yaxis: { title: "Risk (%)", range: [0, 118], gridcolor: themeColor("--chart-grid"), zerolinecolor: themeColor("--chart-axis") },
        shapes: [
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 70, y1: 70, line: { color: themeColor("--chart-temp"), width: 1.2, dash: "dot" } },
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 40, y1: 40, line: { color: themeColor("--chart-muted"), width: 1, dash: "dot" } },
        ],
    };

    Plotly.react(el, [trace], layout, { displayModeBar: false, responsive: true });
}

function renderFleetCards(fleet) {
    const grid = document.getElementById("fleet-cards-grid");
    grid.innerHTML = "";

    fleet.machines.forEach((m, idx) => {
        const meta = STATUS_META[m.status] || { label: m.status, labelHi: m.status, cls: "" };
        const color = statusColor(m.status);
        const machineId = escapeHtml(m.machine_id);
        const machineName = escapeHtml(m.name);
        const partNeeded = escapeHtml(m.part_needed);
        const badgeText = STATE.lang === "hi" ? meta.labelHi : meta.label;
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
            const schedLabel = STATE.lang === "hi" ? `4h सर्विस बुक करें (${m.part_needed})` : `Schedule 4h service (${m.part_needed})`;
            actionHtml = `
                <div class="unit-actions">
                    <button class="btn btn-amber" data-schedule="${machineId}">${escapeHtml(schedLabel)}</button>
                    ${!m.acknowledged ? `<button class="btn btn-subtle" data-ack="${machineId}">Acknowledge</button>` : ""}
                </div>
            `;
        } else if (m.status === "DATA_CHECK" && !m.acknowledged) {
            actionHtml = `
                <div class="unit-actions">
                    <button class="btn btn-subtle" data-ack="${machineId}">Log sensor check</button>
                </div>
            `;
        }

        card.innerHTML = `
            <div class="unit-top">
                <div>
                    <span class="unit-id">${machineId}</span>
                    <span class="unit-name">${machineName}</span>
                </div>
                <span class="status-tag" style="background:${color};">${badgeText}</span>
            </div>
            <div class="unit-summary">${unitHeadline(m, fleet.step)}</div>
            <div class="risk-meter">
                <div class="risk-meter-fill" style="width:${riskPct}%; background:${color};"></div>
            </div>
            <div class="unit-metrics">
                Risk ${riskPct}% (±${uncPct}%) &nbsp;|&nbsp; Confidence ${confPct}% &nbsp;|&nbsp; ${feedLabel}${ackTag}
            </div>
            <div class="unit-reasons">${m.reasons.map(escapeHtml).join(" · ")}</div>
            ${actionHtml}
            <div class="unit-actions unit-manage-actions">
                <button class="btn btn-outline-danger" data-delete-machine="${machineId}" ${fleet.machines.length <= 1 ? "disabled" : ""}>Remove unit</button>
                <span class="unit-part-note">${partNeeded}</span>
            </div>
        `;

        grid.appendChild(card);
    });

    grid.querySelectorAll("[data-schedule]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.schedule;
            const res = await apiJson("/api/schedule", {
                method: "POST",
                body: JSON.stringify({ machine_id: id, step: STATE.step }),
            });
            showToast(res.message || "Scheduled.", res.ok ? "success" : "warning");
            await refreshAll();
            await refreshRoi();
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

    grid.querySelectorAll("[data-delete-machine]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            await removeMachine(btn.dataset.deleteMachine);
        });
    });
}

function renderPriorityQueue(fleet) {
    const tbody = document.getElementById("priority-tbody");
    if (!fleet.priority_queue.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="color:var(--text-muted);">No units require urgent maintenance at Hour ${fleet.step}.</td></tr>`;
        return;
    }

    tbody.innerHTML = fleet.priority_queue
        .map((p) => {
            const meta = STATUS_META[p.status] || { label: p.status };
            return `
                <tr>
                    <td style="font-family:'IBM Plex Mono',monospace;">${escapeHtml(p.machine_id)}</td>
                    <td>${escapeHtml(p.name)}</td>
                    <td>${escapeHtml(meta.label)}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;color:var(--accent-amber);">${p.priority_score}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${Math.round(p.fault_probability * 100)}%</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${Math.round(p.confidence * 100)}%</td>
                    <td>${escapeHtml(p.part_needed)} (${p.part_in_stock})</td>
                    <td style="color:var(--text-secondary);">${escapeHtml(p.recommended_action)}</td>
                </tr>
            `;
        })
        .join("");
}

function renderWorkOrdersAndLog(fleet) {
    const woBody = document.getElementById("wo-tbody");
    if (!fleet.work_orders.length) {
        woBody.innerHTML = `<tr><td colspan="7" style="color:var(--text-muted);">No work orders yet. Schedule a 4-hour service on TR-101 in Segment 01 to generate an SMS Job Card.</td></tr>`;
    } else {
        woBody.innerHTML = fleet.work_orders
            .map(
                (w) => `
                <tr>
                    <td style="font-family:'IBM Plex Mono',monospace;">${w.wo_id}</td>
                    <td>${escapeHtml(w.machine_id)} — ${escapeHtml(w.machine_name)}</td>
                    <td>${escapeHtml(w.part_needed)}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;color:var(--accent-amber);">${escapeHtml(w.status)}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${
                        w.scheduled_start !== null ? `Hr ${w.scheduled_start}–${w.completion_step}` : "Deferred"
                    }</td>
                    <td style="color:var(--text-secondary);">${escapeHtml(w.reason || w.cancellation_reason || "")}</td>
                    <td>${w.status !== "CANCELLED" ? `<button class="btn btn-subtle" data-sms-unit="${escapeHtml(w.machine_id)}">View SMS Card</button>` : "—"}</td>
                </tr>
            `
            )
            .join("");

        woBody.querySelectorAll("[data-sms-unit]").forEach((btn) => {
            btn.addEventListener("click", () => openSmsJobCard(btn.dataset.smsUnit));
        });
    }

    const logBox = document.getElementById("event-log-list");
    if (!fleet.recent_events.length) {
        logBox.innerHTML = `<div class="audit-item">No operator actions recorded yet. Acknowledgements, dispatches, and scarcity edits appear here live.</div>`;
    } else {
        logBox.innerHTML = [...fleet.recent_events]
            .reverse()
            .map((e) => {
                const stepStr = e.step !== undefined && e.step !== null ? `[Hr ${escapeHtml(e.step)}] ` : "";
                const target = e.machine_id ? ` · ${escapeHtml(e.machine_id)}` : "";
                const wo = e.wo_id ? ` · ${escapeHtml(e.wo_id)}` : "";
                return `<div class="audit-item">${stepStr}<strong style="color:var(--text-primary);">${escapeHtml(e.event)}</strong>${target}${wo}</div>`;
            })
            .join("");
    }
}

async function openSmsJobCard(machineId) {
    const res = await apiJson(`/api/sms-card/${machineId}?step=${STATE.step}`);
    if (!res.ok) {
        showToast(res.message || "Could not load SMS card.", "warning");
        return;
    }
    const panel = document.getElementById("sms-card-panel");
    panel.classList.remove("hidden");
    document.getElementById("sms-card-title").textContent = `${res.wo_id} · ${res.machine_id} — ${res.part_needed}`;
    document.getElementById("sms-en-text").textContent = res.sms_en;
    document.getElementById("sms-hi-text").textContent = res.sms_hi;
    document.getElementById("sms-checklist").innerHTML = (res.checklist || [])
        .map((step) => `<li>${escapeHtml(step)}</li>`)
        .join("");
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* ---------------- 6. Interactive SVG X-Ray Blueprint & Telemetry ---------------- */
function updateXrayBlueprint(machine, focusPart = null) {
    const parts = ["Coolant Pump", "Sensor Harness", "Hydraulic Valve", "Drive Bearing"];
    const targetPart = focusPart || machine.part_needed;

    document.getElementById("xray-unit-title").textContent = `${machine.machine_id} — ${machine.name}`;
    document.getElementById("xray-focus-note").textContent = `Target subsystem: ${targetPart}`;

    parts.forEach((pName) => {
        const box = document.getElementById(`part-box-${pName}`);
        if (!box) return;
        const isTarget = pName === targetPart;
        if (isTarget) {
            if (machine.status === "CRITICAL_WARNING" || machine.status === "EARLY_WARNING" || machine.status === "BROKEN_DOWN") {
                box.setAttribute("fill", "var(--bg-elevated)");
                box.setAttribute("stroke", "var(--accent-amber)");
                box.setAttribute("stroke-width", "2.4");
            } else if (machine.status === "DATA_CHECK") {
                box.setAttribute("fill", "var(--bg-elevated)");
                box.setAttribute("stroke", "var(--chart-oil)");
                box.setAttribute("stroke-width", "2.2");
            } else if (machine.status === "SERVICED_READY" || machine.status === "SERVICING") {
                box.setAttribute("fill", "var(--bg-elevated)");
                box.setAttribute("stroke", "var(--chart-rpm)");
                box.setAttribute("stroke-width", "2.2");
            } else {
                box.setAttribute("fill", "var(--bg-elevated)");
                box.setAttribute("stroke", "var(--text-secondary)");
                box.setAttribute("stroke-width", "2");
            }
        } else {
            box.setAttribute("fill", "var(--bg-subtle)");
            box.setAttribute("stroke", "var(--border-hover)");
            box.setAttribute("stroke-width", "1.4");
        }
    });

    const partSensorNotes = {
        "Coolant Pump": "Monitors Engine Temp (baseline 82°C). Rising temp + falling oil pressure flags cooling loop degradation.",
        "Hydraulic Valve": "Monitors Oil Pressure (baseline 45 PSI). Pressure drop + vibration flags valve spool leakage.",
        "Drive Bearing": "Monitors Vibration (2.0 mm/s) & RPM Variance (15 RPM). Rising vibration flags bearing wear.",
        "Sensor Harness": "Monitors CAN telemetry integrity. Single-hour spikes and dropouts are held to avoid false dispatches.",
    };

    document.getElementById("xray-insp-body").innerHTML = `
        <div><strong>Selected subsystem:</strong> ${targetPart}</div>
        <div style="margin-top:4px;"><strong>Mapped unit part:</strong> ${machine.part_needed} (${machine.part_in_stock} in stock)</div>
        <div style="margin-top:6px;">${partSensorNotes[targetPart] || ""}</div>
    `;
}

async function refreshTelemetry() {
    const unitId = STATE.selectedTelemetryUnit;
    const detail = await apiJson(`/api/machines/${unitId}/history?up_to_step=${STATE.step}`);
    if (!detail.ok) return;

    const m = detail.machine;
    const meta = STATUS_META[m.status] || { label: m.status };

    updateXrayBlueprint(m);

    document.getElementById("telemetry-explain-box").innerHTML = `
        <div><strong>Unit:</strong> ${escapeHtml(m.machine_id)} — ${escapeHtml(m.name)}</div>
        <div><strong>State:</strong> ${escapeHtml(meta.label)} &nbsp;|&nbsp; <strong>Feed:</strong> ${escapeHtml(SENSOR_LABELS[m.sensor_status] || m.sensor_status)}</div>
        <div><strong>Fault Risk:</strong> ${(m.fault_probability * 100).toFixed(1)}% (±${(m.uncertainty * 100).toFixed(1)}% uncertainty) &nbsp;|&nbsp; <strong>Confidence:</strong> ${(m.confidence * 100).toFixed(0)}%</div>
        <div><strong>Findings:</strong><br>${m.reasons.map((r) => `• ${escapeHtml(r)}`).join("<br>")}</div>
    `;

    if (STATE.health && STATE.health.model_info) {
        const info = STATE.health.model_info;
        document.getElementById("model-rules-box").innerHTML = `
            <div><strong>Model:</strong> ${escapeHtml(info.model_type)}</div>
            <div><strong>Noise Filter:</strong> ${escapeHtml(info.noise_filter)}</div>
            <div><strong>Leak-Free Guarantee:</strong> ${escapeHtml(info.leak_free_guarantee)}</div>
            <div><strong>Uncertainty Method:</strong> ${escapeHtml(info.uncertainty_method)}</div>
        `;
    }

    const el = document.getElementById("chart-telemetry");
    if (!window.Plotly) {
        el.innerHTML = `<div style="padding:16px;color:var(--text-secondary);">Telemetry points loaded: ${detail.history.length} hours for ${unitId}.</div>`;
        return;
    }

    const hist = detail.history;
    const steps = hist.map((h) => h.step);
    const traces = [
        { x: steps, y: hist.map((h) => h.engine_temp), name: "Engine Temp (C)", mode: "lines+markers", line: { color: themeColor("--chart-temp"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x", yaxis: "y" },
        { x: steps, y: hist.map((h) => h.vibration), name: "Vibration (mm/s)", mode: "lines+markers", line: { color: themeColor("--chart-vibration"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x2", yaxis: "y2" },
        { x: steps, y: hist.map((h) => h.oil_pressure), name: "Oil Pressure (PSI)", mode: "lines+markers", line: { color: themeColor("--chart-oil"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x3", yaxis: "y3" },
        { x: steps, y: hist.map((h) => h.rpm_variance), name: "RPM Variance (RPM)", mode: "lines+markers", line: { color: themeColor("--chart-rpm"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x4", yaxis: "y4" },
    ];

    const layout = {
        title: {
            text: `Raw hourly telemetry — ${unitId} (gaps = missing readings, baseline dashed)`,
            x: 0,
            font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") },
        },
        grid: { rows: 2, columns: 2, pattern: "independent", roworder: "top to bottom" },
        paper_bgcolor: themeColor("--chart-paper"),
        plot_bgcolor: themeColor("--chart-plot"),
        font: { family: "IBM Plex Mono, monospace", size: 10, color: themeColor("--chart-text") },
        height: 430,
        showlegend: false,
        margin: { l: 48, r: 20, t: 54, b: 36 },
        yaxis: { title: "Temp (C)", gridcolor: themeColor("--chart-grid") },
        yaxis2: { title: "Vib (mm/s)", gridcolor: themeColor("--chart-grid") },
        yaxis3: { title: "Oil (PSI)", gridcolor: themeColor("--chart-grid") },
        yaxis4: { title: "RPM Var", gridcolor: themeColor("--chart-grid") },
        xaxis: { showgrid: false },
        xaxis2: { showgrid: false },
        xaxis3: { showgrid: false, title: "Harvest hour" },
        xaxis4: { showgrid: false, title: "Harvest hour" },
    };

    Plotly.react(el, traces, layout, { displayModeBar: false, responsive: true });
}

/* ---------------- 7. Fair Baseline Comparison & Rupee (₹) ROI ---------------- */
function formatInr(val) {
    return "₹" + Math.round(Number(val || 0)).toLocaleString("en-IN");
}

async function refreshRoi() {
    const loss = Number(document.getElementById("inp-hourly-loss").value || 2500);
    const partCost = Number(document.getElementById("inp-part-cost").value || 2200);
    const roi = await apiJson(
        `/api/roi?hourly_loss_inr=${loss}&preventive_part_cost_inr=${partCost}&calendar_interval=${STATE.calendarInterval}`
    );
    document.getElementById("roi-gross").textContent = formatInr(roi.gross_harvest_protected_inr);
    document.getElementById("roi-spend").textContent = formatInr(roi.preventive_spend_inr);
    document.getElementById("roi-net").textContent = formatInr(roi.net_savings_inr);
    document.getElementById("roi-mult").textContent = `${roi.roi_multiple}x ROI`;
}

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

    await refreshRoi();

    if (!window.Plotly) return;

    const steps = comp.hourly_series.map((p) => p.step);
    const availTraces = [
        {
            x: steps,
            y: comp.hourly_series.map((p) => p.calendar_availability_pct),
            name: "Calendar-only",
            mode: "lines",
            line: { color: themeColor("--chart-calendar"), width: 2, dash: "dash" },
        },
        {
            x: steps,
            y: comp.hourly_series.map((p) => p.ai_twin_availability_pct),
            name: "Agro-Twin AI",
            mode: "lines",
            line: { color: themeColor("--chart-temp"), width: 2.8 },
            fill: "tonexty",
            fillcolor: themeColor("--chart-accent-soft"),
        },
    ];

    Plotly.react(
        "chart-compare-avail",
        availTraces,
        {
            title: { text: "Hourly availability (120h harvest)", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
            paper_bgcolor: themeColor("--chart-paper"),
            plot_bgcolor: themeColor("--chart-plot"),
            font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
            height: 330,
            margin: { l: 48, r: 16, t: 50, b: 40 },
            xaxis: { title: "Harvest hour", showgrid: false },
            yaxis: { title: "Available (%)", range: [45, 105], gridcolor: themeColor("--chart-grid") },
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
            marker: { color: themeColor("--chart-calendar") },
            text: [`${cal.total_downtime_hours}h`, `${cal.unplanned_breakdowns}`, `${cal.avg_warning_lead_time_hours}h`],
            textposition: "outside",
        },
        {
            type: "bar",
            name: "Agro-Twin AI",
            x: barCats,
            y: [ai.total_downtime_hours, ai.unplanned_breakdowns, ai.avg_warning_lead_time_hours],
            marker: { color: themeColor("--chart-temp") },
            text: [`${ai.total_downtime_hours}h`, `${ai.unplanned_breakdowns}`, `${ai.avg_warning_lead_time_hours}h`],
            textposition: "outside",
        },
    ];

    Plotly.react(
        "chart-compare-bar",
        barTraces,
        {
            title: { text: "Measured outcome comparison", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
            barmode: "group",
            paper_bgcolor: themeColor("--chart-paper"),
            plot_bgcolor: themeColor("--chart-plot"),
            font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
            height: 330,
            margin: { l: 44, r: 16, t: 50, b: 40 },
            xaxis: { showgrid: false },
            yaxis: { gridcolor: themeColor("--chart-grid") },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" },
        },
        { displayModeBar: false, responsive: true }
    );
}

/* ---------------- 8. Dropdowns, Refresh & Controls ---------------- */
function syncMachineSelects(machines) {
    const telSel = document.getElementById("telemetry-unit-select");
    const injSel = document.getElementById("inj-machine");
    const managerSel = document.getElementById("fleet-manager-unit-select");
    const currentInjId = injSel.value;
    const currentManagerId = managerSel.value;
    const machineIds = new Set(machines.map((machine) => machine.machine_id));

    [telSel, injSel, managerSel].forEach((select) => {
        const selectedId = select === telSel
            ? STATE.selectedTelemetryUnit
            : select === injSel
                ? currentInjId
                : currentManagerId;
        select.replaceChildren();
        machines.forEach((machine) => {
            const option = document.createElement("option");
            option.value = machine.machine_id;
            option.textContent = `${machine.machine_id} — ${machine.name}`;
            select.appendChild(option);
        });
        if (machineIds.has(selectedId)) {
            select.value = selectedId;
        } else if (select === injSel) {
            select.value = machines[machines.length - 1].machine_id;
        } else if (machines.length) {
            select.value = machines[0].machine_id;
        }
    });

    STATE.selectedTelemetryUnit = telSel.value;
    syncFleetManagerMode();
    if (document.getElementById("fleet-manager-mode").value === "edit") {
        populateFleetManagerForm(managerSel.value);
    }
}

function populateFleetManagerForm(machineId) {
    const machine = STATE.fleet?.machines.find((item) => item.machine_id === machineId);
    if (!machine) return;
    document.getElementById("fleet-manager-id").value = machine.machine_id;
    document.getElementById("fleet-manager-name").value = machine.name;
    document.getElementById("fleet-manager-criticality").value = machine.criticality ?? 1.0;
    document.getElementById("fleet-manager-part").value = machine.part_needed;
    document.getElementById("fleet-manager-condition").value = machine.fault_mode || "healthy";
}

function syncFleetManagerMode() {
    const isEditing = document.getElementById("fleet-manager-mode").value === "edit";
    const machineField = document.getElementById("fleet-manager-unit-field");
    const idInput = document.getElementById("fleet-manager-id");
    const deleteButton = document.getElementById("btn-delete-machine");
    machineField.classList.toggle("hidden", !isEditing);
    idInput.readOnly = isEditing;
    deleteButton.disabled = !isEditing || !STATE.fleet || STATE.fleet.machines.length <= 1;
}

async function removeMachine(machineId) {
    if (!STATE.fleet || STATE.fleet.machines.length <= 1) {
        showToast("At least one machine must remain in the fleet.", "warning");
        return;
    }
    if (!window.confirm(`Delete ${machineId} from the fleet? Active work orders will be cancelled and reserved parts released.`)) {
        return;
    }
    const res = await apiJson(`/api/machines/${encodeURIComponent(machineId)}`, { method: "DELETE" });
    showToast(res.message || "Machine could not be removed.", res.ok ? "success" : "warning");
    if (res.ok) {
        await refreshAll();
        await refreshComparison();
        await refreshRoi();
    }
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

function initControls() {
    document.getElementById("btn-lang").addEventListener("click", () => {
        STATE.lang = STATE.lang === "en" ? "hi" : "en";
        applyLanguage();
    });

    document.getElementById("btn-speak").addEventListener("click", speakPriorityAlert);

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

    document.getElementById("btn-weather-normal").addEventListener("click", async () => {
        const res = await apiJson("/api/weather", {
            method: "POST",
            body: JSON.stringify({ weather_mode: "normal" }),
        });
        STATE.weatherMode = "normal";
        showToast(res.stress_note || "Switched to Normal 30°C weather.", "info");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-weather-heat").addEventListener("click", async () => {
        const res = await apiJson("/api/weather", {
            method: "POST",
            body: JSON.stringify({ weather_mode: "heatwave_45c" }),
        });
        STATE.weatherMode = "heatwave_45c";
        showToast(res.stress_note || "Switched to Heatwave 45°C thermal stress.", "warning");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-reset").addEventListener("click", async () => {
        const res = await apiJson("/api/reset", { method: "POST" });
        STATE.step = 35;
        STATE.weatherMode = "normal";
        document.getElementById("sms-card-panel").classList.add("hidden");
        showToast(res.message || "Reset cleanly.", "success");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("telemetry-unit-select").addEventListener("change", async (e) => {
        STATE.selectedTelemetryUnit = e.target.value;
        await refreshTelemetry();
    });

    const managerMode = document.getElementById("fleet-manager-mode");
    const managerUnit = document.getElementById("fleet-manager-unit-select");
    managerMode.addEventListener("change", () => {
        syncFleetManagerMode();
        if (managerMode.value === "edit") {
            populateFleetManagerForm(managerUnit.value);
        } else {
            document.getElementById("fleet-manager-id").value = "";
            document.getElementById("fleet-manager-name").value = "";
            document.getElementById("fleet-manager-criticality").value = "1.0";
            document.getElementById("fleet-manager-part").value = "Coolant Pump";
            document.getElementById("fleet-manager-condition").value = "healthy";
        }
    });
    managerUnit.addEventListener("change", () => populateFleetManagerForm(managerUnit.value));

    document.getElementById("btn-save-machine").addEventListener("click", async () => {
        const machineId = document.getElementById("fleet-manager-id").value.trim();
        const name = document.getElementById("fleet-manager-name").value.trim();
        const criticality = Number(document.getElementById("fleet-manager-criticality").value);
        if (!machineId || !name || !Number.isFinite(criticality) || criticality < 0.8 || criticality > 1.5) {
            showToast("Enter a Unit ID, name, and criticality between 0.8 and 1.5.", "warning");
            return;
        }

        const payload = {
            name,
            part_needed: document.getElementById("fleet-manager-part").value,
            criticality,
            fault_mode: document.getElementById("fleet-manager-condition").value,
        };
        const isEditing = managerMode.value === "edit";
        const res = await apiJson(
            isEditing ? `/api/machines/${encodeURIComponent(machineId)}` : "/api/machines",
            {
                method: isEditing ? "PUT" : "POST",
                body: JSON.stringify(isEditing ? payload : { ...payload, machine_id: machineId }),
            }
        );
        showToast(res.message || "Machine could not be saved.", res.ok ? "success" : "warning");
        if (res.ok) {
            managerMode.value = "edit";
            await refreshAll();
            if (!isEditing) {
                managerUnit.value = res.machine.id;
                populateFleetManagerForm(managerUnit.value);
                syncFleetManagerMode();
            }
            await refreshComparison();
            await refreshRoi();
        }
    });

    document.getElementById("btn-delete-machine").addEventListener("click", async () => {
        await removeMachine(managerUnit.value);
    });

    // Clickable SVG X-Ray Blueprint Subsystems
    document.querySelectorAll(".xray-part").forEach((node) => {
        node.addEventListener("click", () => {
            if (!STATE.fleet) return;
            const m = STATE.fleet.machines.find((item) => item.machine_id === STATE.selectedTelemetryUnit);
            if (m) {
                updateXrayBlueprint(m, node.dataset.part);
                document.getElementById("chart-telemetry").scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        });
    });

    const calSlider = document.getElementById("cal-interval-slider");
    calSlider.addEventListener("input", () => {
        document.getElementById("cal-interval-readout").textContent = `${calSlider.value} hrs`;
    });
    calSlider.addEventListener("change", async () => {
        STATE.calendarInterval = Number(calSlider.value);
        await refreshComparison();
    });

    document.getElementById("btn-calc-roi").addEventListener("click", refreshRoi);

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

    document.getElementById("btn-save-webhook").addEventListener("click", async () => {
        const url = document.getElementById("inp-webhook-url").value.trim();
        const res = await apiJson("/api/webhook", {
            method: "POST",
            body: JSON.stringify({ webhook_url: url }),
        });
        showToast(res.message || "Webhook saved.", "success");
    });

    document.getElementById("btn-close-sms").addEventListener("click", () => {
        document.getElementById("sms-card-panel").classList.add("hidden");
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
            body: JSON.stringify({ question: trimmed, lang: STATE.lang }),
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

    appendAiMessage(
        "Hello! I am the **Agro-Twin Website Guide**. Ask me how to use any segment, inspect the SVG X-Ray blueprint, test Heatwave 45°C mode, or check Rupee ROI & live fleet health. Note: I strictly answer questions about this website only — off-topic questions are blocked.",
        "bot",
        false
    );
}

/* ---------------- Boot Application ---------------- */
window.addEventListener("DOMContentLoaded", async () => {
    initThemeSelector();
    initAmbientCanvas();
    initRevealAndSegments();
    initControls();
    initAssistantDrawer();
    await refreshAll();
    await refreshComparison();
});
