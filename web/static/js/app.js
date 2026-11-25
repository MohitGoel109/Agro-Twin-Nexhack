/* Agro-Twin Normalized Easy-First Interactive UI (Illiterate-Friendly Voice, Visual Traffic Lights, 5 Themes, Full Engineer Mode Toggle & Fleet CRUD) */

const STATUS_META = {
    HEALTHY: { label: "Safe to Drive", labelHi: "ठीक है (सुरक्षित)", cls: "healthy", bars: 5, barColor: "--accent-sage" },
    SERVICED_READY: { label: "Fixed & Ready", labelHi: "मरम्मत पूर्ण", cls: "saved", bars: 5, barColor: "--accent-sage" },
    SERVICING: { label: "Being Fixed", labelHi: "मरम्मत चल रही है", cls: "saved", bars: 4, barColor: "--accent-slate" },
    DATA_CHECK: { label: "Signal Check", labelHi: "सिग्नल जांच", cls: "hold", bars: 3, barColor: "--accent-slate" },
    EARLY_WARNING: { label: "Check Soon", labelHi: "जल्द जांचें", cls: "warn", bars: 2, barColor: "--accent-amber" },
    CRITICAL_WARNING: { label: "Fix Now!", labelHi: "अभी ठीक करें!", cls: "urgent", bars: 1, barColor: "--accent-brick" },
    BROKEN_DOWN: { label: "Stopped!", labelHi: "मशीन बंद है!", cls: "urgent", bars: 0, barColor: "--accent-brick" },
};

const SENSOR_LABELS = {
    CLEAN: "Clean signal",
    SENSOR_NOISE_FILTERED: "False bump ignored",
    MISSING_DATA_HOLD: "Signal lost (waiting)",
};

const I18N = {
    en: {
        trackTag: "Farm Helper",
        navHome: "Home",
        card1Title: "Your Farm Machines",
        card1Desc: "See red/green cards & book a 4-hour repair",
        card2Title: "Machine Picture (X-Ray)",
        card2Desc: "Tap any glowing part to hear what is wrong",
        card3Title: "Money Saved (₹)",
        card3Desc: "See how many Rupees early repair protects",
        card4Title: "Repairs, SMS & Add Machines",
        card4Desc: "Open mechanic SMS cards & manage fleet",
        navFleet: "1. Machines",
        navTel: "2. Machine Picture",
        navImpact: "3. Money Saved (₹)",
        navOps: "4. Repairs & Tools",
        btnListen: "Listen",
        askGuide: "Ask Helper",
        modeEasy: "View: Easy",
        modeFull: "View: Full",
        heroTitle: "Check Your Tractors & Fix Problems Early.",
        heroSub: "Green means safe to work. Red means repair needed. Tap any speaker button to listen in English or Hindi.",
        heroListenTitle: "Tap to Listen",
        heroListenSub: "Hear which machine needs help",
        step1Title: "Red = Problem",
        step1Sub: "Green = Safe to drive",
        step2Title: "Tap Speaker",
        step2Sub: "Listen to what is wrong",
        step3Title: "Tap Orange Button",
        step3Sub: "Book 4-hour mechanic",
        kpiReadyLbl: "Machines Ready",
        kpiPrevLbl: "Breakdowns Stopped",
        kpiWoLbl: "Repairs Booked",
        kpiTechLbl: "Free Mechanics",
        kpiHourLbl: "Harvest Time",
        lblTime: "Time",
        jump35: "Alert (Hr 35)",
        jump48: "After Repair (Hr 48)",
        btnNormalW: "30°C Normal",
        btnHeatW: "45°C Very Hot",
        btnReset: "Start Over",
        seg1Kicker: "Step 1 · Your Farm Machines",
        seg1Title: "Which machines are safe, and which need repair?",
        seg1Sub: "Red card = fix now. Green card = safe to drive. Blue card = sensor check only (do not stop work).",
        legRed: "Fix Now",
        legGreen: "Safe",
        legBlue: "Checking",
        showTechFleet: "Show technical risk graph & priority table (For Engineers / Judges)",
        seg2Kicker: "Step 2 · Machine Picture",
        seg2Title: "See exactly which part needs repair",
        seg2Sub: "Pick a tractor below. The glowing orange part shows where the problem is. Tap any part on the picture to hear what it does.",
        lblPickUnit: "Choose machine",
        xrayKicker: "TAP ANY PART TO LISTEN",
        xrayPartTitle: "Selected Part Info",
        showTechTel: "Show raw 4-sensor graphs & AI explainability proof (For Engineers / Judges)",
        seg3Kicker: "Step 3 · Money Saved",
        seg3Title: "How much harvest money (₹) does early repair save?",
        seg3Sub: "Fixing small problems early saves big breakdowns during harvest time.",
        roiKicker: "HARVEST MONEY CALCULATOR (₹)",
        roiTitle: "Net Money Protected for Your Farm",
        lblLossHr: "Loss per stopped hour (₹)",
        lblPartCost: "Spare part price (₹)",
        btnCalc: "Calculate ₹",
        roiNetLbl: "Total Money Saved",
        roiGrossLbl: "Crop Work Protected",
        roiSpendLbl: "Small Part Cost",
        roiMultLbl: "Value Returned",
        cmpAvailLbl: "Machines Working",
        cmpSavedLbl: "Hours Saved",
        cmpBreakLbl: "Sudden Breakdowns",
        cmpLeadLbl: "Early Warning Time",
        showTechCmp: "Show Calendar vs. AI comparison charts (For Engineers / Judges)",
        seg4Kicker: "Step 4 · Booked Repairs & Mechanic SMS",
        seg4Title: "Repair List & Phone SMS for Mechanics",
        seg4Sub: "Every booked repair creates a short English and Hindi SMS card that works even without internet.",
        woTitle: "Booked Repairs",
        showTechOps: "Manage mechanics, spare parts, add/delete machines & webhooks (Manager / Judge Tools)",
        fabHelper: "Voice & AI Helper",
        aiTitle: "Agro-Twin Helper",
        aiSub: "Speak or tap a question · Website-only guide",
    },
    hi: {
        trackTag: "किसान सहायक",
        navHome: "मुख्य पेज",
        card1Title: "आपकी मशीनें",
        card1Desc: "लाल/हरे कार्ड देखें और 4 घंटे की मरम्मत बुक करें",
        card2Title: "मशीन का चित्र (X-Ray)",
        card2Desc: "चमकते पुर्जे पर टैप करके आवाज़ में सुनें",
        card3Title: "पैसे की बचत (₹)",
        card3Desc: "देखें समय पर मरम्मत से कितने रुपये बचते हैं",
        card4Title: "मरम्मत, SMS और मशीन जोड़ें",
        card4Desc: "मैकेनिक SMS कार्ड देखें और मशीनें जोड़ें/हटाएं",
        navFleet: "1. मशीनें",
        navTel: "2. मशीन का चित्र",
        navImpact: "3. पैसे की बचत (₹)",
        navOps: "4. मरम्मत और SMS",
        btnListen: "सुनें",
        askGuide: "मदद पूछें",
        modeEasy: "दृश्य: आसान",
        modeFull: "दृश्य: पूरा",
        heroTitle: "अपने ट्रैक्टर जांचें और खराबी पहले ठीक करें।",
        heroSub: "हरा मतलब मशीन ठीक है। लाल मतलब मरम्मत जरूरी है। सुनने के लिए किसी भी स्पीकर बटन को दबाएं।",
        heroListenTitle: "सुनने के लिए दबाएं",
        heroListenSub: "जानें किस मशीन में खराबी है",
        step1Title: "लाल = खराबी",
        step1Sub: "हरा = चलाने के लिए ठीक",
        step2Title: "स्पीकर दबाएं",
        step2Sub: "आवाज़ में खराबी सुनें",
        step3Title: "नारंगी बटन दबाएं",
        step3Sub: "4 घंटे की मरम्मत बुक करें",
        kpiReadyLbl: "तैयार मशीनें",
        kpiPrevLbl: "बचाए गए ब्रेकडाउन",
        kpiWoLbl: "बुक मरम्मत",
        kpiTechLbl: "खाली मैकेनिक",
        kpiHourLbl: "कटाई समय",
        lblTime: "समय",
        jump35: "चेतावनी (Hr 35)",
        jump48: "मरम्मत के बाद (Hr 48)",
        btnNormalW: "30°C सामान्य",
        btnHeatW: "45°C तेज गर्मी",
        btnReset: "फिर से शुरू",
        seg1Kicker: "कदम 1 · आपकी मशीनें",
        seg1Title: "कौन सी मशीन ठीक है और किसे मरम्मत चाहिए?",
        seg1Sub: "लाल कार्ड = अभी ठीक करें। हरा कार्ड = सुरक्षित। नीला कार्ड = केवल सिग्नल जांच।",
        legRed: "अभी ठीक करें",
        legGreen: "सुरक्षित",
        legBlue: "जांच",
        showTechFleet: "तकनीकी जोखिम ग्राफ और तालिका देखें (इंजीनियर / जज के लिए)",
        seg2Kicker: "कदम 2 · मशीन का चित्र",
        seg2Title: "चित्र में देखें कौन सा पुर्जा खराब है",
        seg2Sub: "नीचे मशीन चुनें। चमकता नारंगी हिस्सा खराबी दिखाता है। सुनने के लिए किसी भी पुर्जे पर टैप करें।",
        lblPickUnit: "मशीन चुनें",
        xrayKicker: "सुनने के लिए पुर्जे पर टैप करें",
        xrayPartTitle: "चुने गए पुर्जे की जानकारी",
        showTechTel: "4-सेंसर ग्राफ और AI विवरण देखें (इंजीनियर / जज के लिए)",
        seg3Kicker: "कदम 3 · पैसे की बचत",
        seg3Title: "समय पर मरम्मत से कितने रुपये (₹) बचते हैं?",
        seg3Sub: "छोटी खराबी पहले ठीक करने से कटाई का बड़ा नुकसान बचता है।",
        roiKicker: "बचत कैलकुलेटर (₹)",
        roiTitle: "खेती के पैसे की कुल बचत",
        lblLossHr: "1 घंटे रुकने का नुकसान (₹)",
        lblPartCost: "पुर्जे की कीमत (₹)",
        btnCalc: "जोड़ें ₹",
        roiNetLbl: "कुल बचत",
        roiGrossLbl: "फसल काम की सुरक्षा",
        roiSpendLbl: "छोटे पुर्जे का खर्च",
        roiMultLbl: "फायदा",
        cmpAvailLbl: "चालू मशीनें",
        cmpSavedLbl: "बचाए गए घंटे",
        cmpBreakLbl: "अचानक खराबी",
        cmpLeadLbl: "अग्रिम चेतावनी",
        showTechCmp: "तुलना ग्राफ देखें (इंजीनियर / जज के लिए)",
        seg4Kicker: "कदम 4 · मरम्मत सूची और SMS",
        seg4Title: "बुक की गई मरम्मत और मैकेनिक SMS",
        seg4Sub: "बिना इंटरनेट के भी मैकेनिक को हिंदी और अंग्रेज़ी SMS कार्ड भेजा जा सकता है।",
        woTitle: "बुक की गई मरम्मत",
        showTechOps: "मैकेनिक, पुर्जे, नई मशीन जोड़ना/हटाना और वेबहुक (मैनेजर / जज टूल)",
        fabHelper: "बोलकर पूछें (AI)",
        aiTitle: "Agro-Twin सहायक",
        aiSub: "बोलें या बटन दबाएं · केवल वेबसाइट गाइड",
    },
};

const THEMES = new Set(["dark", "light", "harvest", "forest", "ocean"]);

const URL_PARAMS = new URLSearchParams(window.location.search);

function readPref(key, fallback) {
    try {
        const v = localStorage.getItem(key);
        return v !== null ? v : fallback;
    } catch (e) {
        return fallback;
    }
}

function writePref(key, val) {
    try {
        localStorage.setItem(key, String(val));
    } catch (e) {}
}

const STATE = {
    activePage: document.body?.dataset?.page || "home",
    step: null, // Syncs live from Flask server so moving between pages keeps your current hour!
    calendarInterval: 72,
    selectedTelemetryUnit: URL_PARAMS.get("unit") || "TR-101",
    pendingSmsUnit: URL_PARAMS.get("sms") || null,
    weatherMode: "normal",
    lang: readPref("agro-twin-lang", "en"),
    theme: "dark",
    simpleMode: readPref("agro-twin-simple-mode", "true") !== "false",
    autoSpeakAi: true,
    fleet: null,
    health: null,
    bgMotionEnabled: true,
    lastSms: null,
    lastXrayPart: "Coolant Pump",
};

function themeColor(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function statusColor(status) {
    const colorByStatus = {
        HEALTHY: "--accent-sage",
        SERVICED_READY: "--accent-sage",
        SERVICING: "--accent-slate",
        DATA_CHECK: "--accent-slate",
        EARLY_WARNING: "--accent-amber",
        CRITICAL_WARNING: "--accent-brick",
        BROKEN_DOWN: "--accent-brick",
    };
    return themeColor(colorByStatus[status] || "--chart-muted") || "#5b9a6f";
}

function escapeHtml(text) {
    return String(text ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

/* ---------------- 1. Theme Selector (All 5 Themes Preserved) ---------------- */
function initThemeSelector() {
    const selector = document.getElementById("theme-select");
    if (!selector) return;

    let savedTheme = "dark";
    try {
        const storedTheme = localStorage.getItem("agro-twin-theme");
        if (THEMES.has(storedTheme)) savedTheme = storedTheme;
    } catch (error) {
        console.warn("Unable to read saved theme.", error);
    }

    const applyTheme = (theme) => {
        const selectedTheme = THEMES.has(theme) ? theme : "dark";
        if (selectedTheme === "dark") {
            delete document.documentElement.dataset.theme;
        } else {
            document.documentElement.dataset.theme = selectedTheme;
        }
        selector.value = selectedTheme;
        STATE.theme = selectedTheme;
        try {
            localStorage.setItem("agro-twin-theme", selectedTheme);
        } catch (error) {
            console.warn("Unable to save theme.", error);
        }
        if (STATE.fleet) {
            renderRiskChart(STATE.fleet.machines);
            renderFleetCards(STATE.fleet);
            refreshTelemetry();
            refreshComparison();
        }
    };

    applyTheme(savedTheme);
    selector.addEventListener("change", (e) => applyTheme(e.target.value));
}

/* ---------------- 2. Easy Farmer View vs Full Engineer View ---------------- */
function applyViewMode() {
    document.body.classList.toggle("simple-mode", STATE.simpleMode);
    const btn = document.getElementById("btn-view-mode");
    const dict = I18N[STATE.lang] || I18N.en;
    if (btn) {
        btn.innerHTML = `<span>${STATE.simpleMode ? dict.modeEasy : dict.modeFull}</span>`;
    }
    // In Full View, auto-open all technical drawers; in Easy View, collapse them for calm clarity
    ["drawer-fleet-tech", "drawer-telemetry-tech", "drawer-compare-tech", "drawer-ops-tech"].forEach((id) => {
        const d = document.getElementById(id);
        if (d) d.open = !STATE.simpleMode;
    });

    if (!STATE.simpleMode && window.Plotly) {
        setTimeout(() => {
            ["chart-risk", "chart-telemetry", "chart-compare-avail", "chart-compare-bar"].forEach((cid) => {
                const node = document.getElementById(cid);
                if (node && node.data) Plotly.Plots.resize(node);
            });
        }, 120);
    }
}

/* ---------------- 3. Calm Topographic Field Contour Background ---------------- */
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
        const dotColor = themeColor("--ambient-dot") || "rgba(243, 239, 230, 0.035)";
        const lineColor = themeColor("--ambient-line") || "rgba(243, 239, 230, 0.04)";
        const accentColor = themeColor("--ambient-accent") || "rgba(229, 154, 50, 0.065)";

        ctx.fillStyle = dotColor;
        const gap = 52;
        for (let x = 26; x < width; x += gap) {
            for (let y = 26; y < height; y += gap) {
                ctx.fillRect(x, y, 1.2, 1.2);
            }
        }

        const lineCount = 5;
        for (let i = 0; i < lineCount; i++) {
            ctx.beginPath();
            const baseY = (height / (lineCount + 1)) * (i + 1);
            ctx.strokeStyle = i === 2 ? accentColor : lineColor;
            ctx.lineWidth = 1;
            for (let x = 0; x <= width; x += 32) {
                const wave =
                    Math.sin(x * 0.0024 + t * 0.35 + i * 1.1) * 18 +
                    Math.cos(x * 0.0012 - t * 0.2 + i * 0.7) * 10;
                const y = baseY + wave;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        if (STATE.bgMotionEnabled) t += 0.006;
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

/* ---------------- 4. Voice Readout Helper (English + Hindi) ---------------- */
function speakText(text, forceLang = null) {
    if (!("speechSynthesis" in window)) {
        showToast("Voice readout is not available in this browser.", "warning");
        return;
    }
    window.speechSynthesis.cancel();
    const clean = String(text || "").replace(/\*\*/g, "").replace(/`/g, "");
    const utter = new SpeechSynthesisUtterance(clean);
    const useLang = forceLang || STATE.lang;
    utter.lang = useLang === "hi" ? "hi-IN" : "en-IN";
    utter.rate = 0.95;
    window.speechSynthesis.speak(utter);
}

function speakPriorityAlert() {
    const fleet = STATE.fleet;
    if (!fleet) return;
    const top = fleet.priority_queue && fleet.priority_queue.length ? fleet.priority_queue[0] : null;
    if (STATE.lang === "hi") {
        const msg = top
            ? `ध्यान दें। मशीन ${top.machine_id}, ${top.name} में खराबी आ रही है। इसका ${top.part_needed} खराब हो रहा है। कृपया नारंगी बटन दबाकर 4 घंटे की मरम्मत बुक करें।`
            : `सब ठीक है। अभी आपकी सभी ${fleet.machines_total} मशीनें सुरक्षित चल रही हैं।`;
        speakText(msg, "hi");
        showToast("आवाज़ में स्थिति बताई जा रही है...", "info");
    } else {
        const msg = top
            ? `Attention. Machine ${top.machine_id}, ${top.name}, needs repair soon. Its ${top.part_needed} has a problem. Tap the orange button to book a 4-hour mechanic.`
            : `All good. All ${fleet.machines_total} farm machines are safe to drive right now.`;
        speakText(msg, "en");
        showToast("Reading farm status aloud...", "info");
    }
}

function speakMachineCard(m) {
    if (STATE.lang === "hi") {
        let msg = `मशीन ${m.machine_id}, ${m.name}। `;
        if (m.status === "CRITICAL_WARNING" || m.status === "EARLY_WARNING") {
            msg += `खतरा है। इसका ${m.part_needed} खराब हो रहा है। कृपया अभी नारंगी बटन दबाकर 4 घंटे की मरम्मत बुक करें।`;
        } else if (m.status === "SERVICED_READY") {
            msg += `यह मशीन ठीक हो गई है और काम के लिए तैयार है।`;
        } else if (m.status === "SERVICING") {
            msg += `अभी मैकेनिक इसकी मरम्मत कर रहे हैं।`;
        } else if (m.status === "DATA_CHECK") {
            msg += `मशीन ठीक है, केवल सेंसर सिग्नल की जांच हो रही है। काम न रोकें।`;
        } else {
            msg += `यह मशीन पूरी तरह सुरक्षित है और खेत में चल सकती है।`;
        }
        speakText(msg, "hi");
    } else {
        let msg = `Machine ${m.machine_id}, ${m.name}. `;
        if (m.status === "CRITICAL_WARNING" || m.status === "EARLY_WARNING") {
            msg += `Repair needed now. Problem in ${m.part_needed}. Tap the orange button to book a 4-hour repair and stop a big breakdown.`;
        } else if (m.status === "SERVICED_READY") {
            msg += `Repaired and ready for harvest. Breakdown was prevented.`;
        } else if (m.status === "SERVICING") {
            msg += `Mechanic is repairing this machine right now.`;
        } else if (m.status === "DATA_CHECK") {
            msg += `Sensor signal check only. Do not waste a mechanic yet.`;
        } else {
            msg += `Healthy and safe to drive.`;
        }
        speakText(msg, "en");
    }
}

function applyLanguage() {
    const dict = I18N[STATE.lang] || I18N.en;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.dataset.i18n;
        if (dict[key]) el.textContent = dict[key];
    });
    const langBtn = document.getElementById("btn-lang");
    if (langBtn) langBtn.textContent = STATE.lang === "en" ? "EN / हिंदी" : "हिंदी / EN";
    applyViewMode();
    if (STATE.fleet) {
        renderFleetCards(STATE.fleet);
    }
}

/* ---------------- 5. Machine SVG Silhouettes & Simple Plain-Language Summaries ---------------- */
function machineIconSvg(machineId) {
    const upper = String(machineId || "").toUpperCase();
    if (upper.startsWith("HV")) {
        // Combine Harvester SVG
        return `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="10" y="14" width="22" height="14" rx="2"/><path d="M32 22h8l3 6H32"/><circle cx="17" cy="34" r="6"/><circle cx="34" cy="35" r="4.5"/><path d="M12 14l4-6h10l3 6"/></svg>`;
    }
    if (upper.startsWith("SD")) {
        // Seed Drill SVG
        return `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M10 14h28l-4 12H14z"/><line x1="16" y1="26" x2="16" y2="36"/><line x1="24" y1="26" x2="24" y2="36"/><line x1="32" y1="26" x2="32" y2="36"/><circle cx="11" cy="34" r="4"/><circle cx="37" cy="34" r="4"/></svg>`;
    }
    // Tractor SVG (default)
    return `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 28V18h14l4-8h10v18"/><circle cx="33" cy="32" r="7.5"/><circle cx="14" cy="34" r="5"/><line x1="15" y1="18" x2="15" y2="11"/></svg>`;
}

function statusIconSvg(status) {
    if (status === "CRITICAL_WARNING" || status === "BROKEN_DOWN") {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
    }
    if (status === "EARLY_WARNING") {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
    }
    if (status === "DATA_CHECK") {
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>`;
    }
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>`;
}

function unitHeadline(m, currentStep) {
    const hi = STATE.lang === "hi";
    const st = m.status;
    if (st === "SERVICED_READY") {
        return hi
            ? "4 घंटे की मरम्मत पूरी हो गई। बड़ी खराबी रुक गई!"
            : "4-hour repair finished! Big 18-hour breakdown stopped.";
    }
    if (st === "SERVICING") {
        return hi
            ? "मैकेनिक अभी इस मशीन की मरम्मत कर रहे हैं।"
            : "Mechanic is fixing this machine right now.";
    }
    if (st === "BROKEN_DOWN") {
        return hi
            ? "मशीन खेत में रुक गई है। 18 घंटे लगेंगे।"
            : "Machine broke down in the field (18 hours stopped).";
    }
    if (m.sensor_status === "SENSOR_NOISE_FILTERED") {
        return hi
            ? "सिर्फ झटका था — मशीन ठीक है, मैकेनिक की जरूरत नहीं।"
            : "Just a bumpy field spike — machine is safe, no mechanic needed.";
    }
    if (m.sensor_status === "MISSING_DATA_HOLD") {
        return hi
            ? "सेंसर सिग्नल रुका हुआ है — सिग्नल आने का इंतज़ार है।"
            : "Sensor signal paused — waiting for clean signal before calling mechanic.";
    }
    if (st === "CRITICAL_WARNING" || st === "EARLY_WARNING") {
        const hrsLeft = m.actual_breakdown_step && m.actual_breakdown_step > currentStep
            ? m.actual_breakdown_step - currentStep
            : null;
        if (hi) {
            const timePart = hrsLeft ? `लगभग ${hrsLeft} घंटे में बंद हो सकती है। ` : "";
            return `${timePart}${m.part_needed} बदलना जरूरी है।`;
        }
        const timePart = hrsLeft ? `May stop in ~${hrsLeft} hrs. ` : "";
        return `${timePart}Check & replace ${m.part_needed} now.`;
    }
    return hi
        ? "सब कुछ ठीक है। खेत में चलाने के लिए तैयार।"
        : "Everything looks good. Ready to work in the field.";
}

/* ---------------- 6. Scroll Reveal & Segment Switcher ---------------- */
function initRevealAndSegments() {
    // Wire Step 2 speaker button on Home page
    document.getElementById("guide-step-2")?.addEventListener("click", speakPriorityAlert);
}

/* ---------------- 7. Toast & Fetch ---------------- */
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

/* ---------------- 8. Render Ledger, Fleet Cards, Risk Chart & Priority Queue ---------------- */
function renderLedger(fleet) {
    document.getElementById("kpi-hour").textContent = `Hr ${fleet.step}`;
    const wMode = fleet.weather_mode || STATE.weatherMode;
    STATE.weatherMode = wMode;
    document.getElementById("kpi-weather-note").textContent =
        wMode === "heatwave_45c" ? "45°C Very Hot weather" : "30°C Normal weather";

    document.getElementById("btn-weather-normal").classList.toggle("active-weather", wMode !== "heatwave_45c");
    document.getElementById("btn-weather-heat").classList.toggle("active-weather", wMode === "heatwave_45c");

    document.getElementById("kpi-readiness").textContent = `${fleet.fleet_readiness_pct}%`;
    document.getElementById("kpi-active").textContent = `${fleet.machines_available} of ${fleet.machines_total} working`;
    document.getElementById("kpi-prevented").textContent = `${fleet.breakdowns_prevented}`;
    document.getElementById("kpi-downtime").textContent = `${fleet.total_downtime_hours} hrs stopped`;
    document.getElementById("kpi-workorders").textContent = `${fleet.open_work_orders_count}`;
    document.getElementById("kpi-flagged").textContent = `${fleet.priority_queue.length} need(s) repair`;
    document.getElementById("kpi-techs").textContent = `${fleet.resources.technicians_available} / ${fleet.resources.technicians_total}`;
    document.getElementById("kpi-techs-busy").textContent = `${fleet.resources.technicians_busy} busy right now`;

    document.getElementById("step-slider").value = fleet.step;
    document.getElementById("slider-readout").textContent = `Hr ${fleet.step}`;

    document.getElementById("inp-techs").value = fleet.resources.technicians_total;
    document.getElementById("inp-cp").value = fleet.resources.parts_inventory["Coolant Pump"] ?? 0;
    document.getElementById("inp-hv").value = fleet.resources.parts_inventory["Hydraulic Valve"] ?? 0;
    document.getElementById("inp-db").value = fleet.resources.parts_inventory["Drive Bearing"] ?? 0;
}

function renderRiskChart(machines) {
    const el = document.getElementById("chart-risk");
    if (!el || !window.Plotly) return;

    const x = machines.map((m) => m.machine_id);
    const y = machines.map((m) => Number((m.fault_probability * 100).toFixed(1)));
    const err = machines.map((m) => Number((m.uncertainty * 100).toFixed(1)));
    const colors = machines.map((m) => statusColor(m.status));

    const trace = {
        type: "bar",
        x,
        y,
        width: 0.48,
        marker: { color: colors },
        error_y: { type: "data", array: err, visible: true, color: themeColor("--chart-title"), thickness: 1.6, width: 5 },
        text: y.map((v) => `${Math.round(v)}%`),
        textposition: "outside",
        textfont: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-title") },
    };

    const layout = {
        title: { text: "Fault Risk & Uncertainty Bands", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
        paper_bgcolor: themeColor("--chart-paper"),
        plot_bgcolor: themeColor("--chart-plot"),
        font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
        margin: { l: 48, r: 20, t: 46, b: 36 },
        height: 310,
        xaxis: { showgrid: false, linecolor: themeColor("--chart-axis") },
        yaxis: { title: "Risk (%)", range: [0, 118], gridcolor: themeColor("--chart-grid") },
        shapes: [
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 70, y1: 70, line: { color: themeColor("--accent-brick"), width: 1.2, dash: "dot" } },
            { type: "line", x0: -0.5, x1: x.length - 0.5, y0: 40, y1: 40, line: { color: themeColor("--accent-amber"), width: 1, dash: "dot" } },
        ],
    };

    Plotly.react(el, [trace], layout, { displayModeBar: false, responsive: true });
}

function renderFleetCards(fleet) {
    const grid = document.getElementById("fleet-cards-grid");
    grid.innerHTML = "";
    const hi = STATE.lang === "hi";
    const canDelete = fleet.machines.length > 1;

    // Sort urgent machines to the very top so non-readers see problems first!
    const orderRank = (st) => {
        if (st === "BROKEN_DOWN") return 0;
        if (st === "CRITICAL_WARNING") return 1;
        if (st === "EARLY_WARNING") return 2;
        if (st === "SERVICING") return 3;
        if (st === "DATA_CHECK") return 4;
        if (st === "SERVICED_READY") return 5;
        return 6;
    };
    const sorted = [...fleet.machines].sort((a, b) => orderRank(a.status) - orderRank(b.status));

    sorted.forEach((m, idx) => {
        const meta = STATUS_META[m.status] || { label: m.status, labelHi: m.status, cls: "", bars: 5, barColor: "--accent-sage" };
        const badgeText = hi ? meta.labelHi : meta.label;
        const badgeColor = statusColor(m.status);
        const barFill = themeColor(meta.barColor) || badgeColor;
        const riskPct = Math.round(m.fault_probability * 100);
        const uncPct = Math.round(m.uncertainty * 100);
        const confPct = Math.round(m.confidence * 100);

        const barsHtml = [1, 2, 3, 4, 5]
            .map((n) => `<span class="hbar b${n}" style="${n <= meta.bars ? `background:${barFill};` : ""}"></span>`)
            .join("");

        const healthText =
            meta.bars >= 5
                ? (hi ? "स्वास्थ्य: बहुत अच्छा" : "Health: Full")
                : meta.bars >= 3
                ? (hi ? "स्वास्थ्य: ठीक (सिग्नल जांच)" : "Health: OK (Checking)")
                : (hi ? "स्वास्थ्य: कम — मरम्मत जरूरी!" : "Health: Low — Fix Now!");

        const card = document.createElement("div");
        card.className = `unit-card ${meta.cls}`;
        card.style.animationDelay = `${idx * 35}ms`;

        const listenLbl = hi ? "सुनें" : "Listen";
        const bookBtnHtml =
            m.status === "CRITICAL_WARNING" || m.status === "EARLY_WARNING"
                ? `<button class="btn btn-amber btn-lg" data-schedule="${escapeHtml(m.machine_id)}">
                       <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
                       <span>${hi ? `4 घंटे की मरम्मत बुक करें` : `Book 4h Repair`}</span>
                   </button>`
                : "";

        const smsLinkHtml =
            m.status === "SERVICING" || m.status === "SERVICED_READY"
                ? `<a class="btn btn-amber" href="/repairs?sms=${encodeURIComponent(m.machine_id)}">${hi ? "SMS कार्ड देखें" : "Open SMS Card"}</a>`
                : "";

        const ackBtnHtml =
            (m.status === "CRITICAL_WARNING" || m.status === "EARLY_WARNING" || m.status === "DATA_CHECK") && !m.acknowledged
                ? `<button class="btn btn-subtle engineer-only" data-ack="${escapeHtml(m.machine_id)}">Acknowledge</button>`
                : "";

        const delBtnHtml = `<button class="btn btn-outline-danger engineer-only" data-remove="${escapeHtml(m.machine_id)}" ${canDelete ? "" : "disabled"}>Remove</button>`;

        card.innerHTML = `
            <div class="unit-header-row">
                <div class="unit-identity">
                    <div class="machine-avatar" aria-hidden="true">${machineIconSvg(m.machine_id)}</div>
                    <div>
                        <span class="unit-id">${escapeHtml(m.machine_id)}</span>
                        <span class="unit-name">${escapeHtml(m.name)}</span>
                    </div>
                </div>
                <span class="status-pill-big" style="background:${badgeColor};">
                    ${statusIconSvg(m.status)}
                    <span>${escapeHtml(badgeText)}</span>
                </span>
            </div>

            <div class="health-meter-row">
                <span class="health-label">${escapeHtml(healthText)}</span>
                <div class="health-bars" aria-label="Health bars">${barsHtml}</div>
            </div>

            <div class="simple-finding">${escapeHtml(unitHeadline(m, fleet.step))}</div>

            <div class="part-strip">
                <strong>${hi ? "पुर्जा:" : "Part:"}</strong> ${escapeHtml(m.part_needed)}
                &nbsp;·&nbsp;
                <span>${m.part_in_stock > 0 ? (hi ? `${m.part_in_stock} उपलब्ध` : `${m.part_in_stock} in stock`) : (hi ? "स्टॉक खत्म" : "Out of stock")}</span>
            </div>

            <div class="unit-metrics-tech engineer-only">
                Risk ${riskPct}% (±${uncPct}%) &nbsp;|&nbsp; Confidence ${confPct}% &nbsp;|&nbsp; ${escapeHtml(SENSOR_LABELS[m.sensor_status] || m.sensor_status)}<br>
                ${escapeHtml(m.reasons.join(" · "))}
            </div>

            <div class="unit-actions">
                <button class="btn btn-voice" data-speak-unit="${escapeHtml(m.machine_id)}" type="button">
                    <svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                    <span>${listenLbl}</span>
                </button>
                ${bookBtnHtml}
                ${smsLinkHtml}
                <a class="btn btn-subtle" href="/picture?unit=${encodeURIComponent(m.machine_id)}">
                    <span>${hi ? "चित्र देखें" : "See Picture"}</span>
                </a>
                ${ackBtnHtml}
                ${delBtnHtml}
            </div>
        `;

        grid.appendChild(card);
    });

    grid.querySelectorAll("[data-speak-unit]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const m = fleet.machines.find((item) => item.machine_id === btn.dataset.speakUnit);
            if (m) speakMachineCard(m);
        });
    });

    grid.querySelectorAll("[data-inspect-unit]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            STATE.selectedTelemetryUnit = btn.dataset.inspectUnit;
            const sel = document.getElementById("telemetry-unit-select");
            if (sel) sel.value = STATE.selectedTelemetryUnit;
            await refreshTelemetry();
            const seg = document.getElementById("seg-telemetry");
            if (seg) {
                seg.classList.remove("hidden-seg");
                seg.classList.add("visible");
                seg.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    grid.querySelectorAll("[data-schedule]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.schedule;
            const res = await apiJson("/api/schedule", {
                method: "POST",
                body: JSON.stringify({ machine_id: id, step: STATE.step }),
            });
            showToast(res.message || "Repair booked!", res.ok ? "success" : "warning");
            if (res.ok) {
                speakText(
                    STATE.lang === "hi"
                        ? `${id} के लिए 4 घंटे की मरम्मत बुक हो गई है।`
                        : `4-hour repair booked for ${id}.`,
                    STATE.lang
                );
            }
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

    grid.querySelectorAll("[data-remove]").forEach((btn) => {
        btn.addEventListener("click", () => removeMachine(btn.dataset.remove));
    });
}

function renderPriorityQueue(fleet) {
    const tbody = document.getElementById("priority-tbody");
    if (!fleet.priority_queue.length) {
        tbody.innerHTML = `<tr><td colspan="8" style="color:var(--text-muted);">All machines are fine at Hour ${fleet.step}.</td></tr>`;
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
                    <td>${escapeHtml(p.recommended_action)}</td>
                </tr>
            `;
        })
        .join("");
}

function renderWorkOrdersAndLog(fleet) {
    const woBody = document.getElementById("wo-tbody");
    if (!fleet.work_orders.length) {
        woBody.innerHTML = `<tr><td colspan="7" style="color:var(--text-muted);">No repairs booked yet. Tap the orange "Book 4h Repair" button on any red machine above.</td></tr>`;
    } else {
        woBody.innerHTML = fleet.work_orders
            .map(
                (w) => `
                <tr>
                    <td style="font-family:'IBM Plex Mono',monospace;">${escapeHtml(w.wo_id)}</td>
                    <td>${escapeHtml(w.machine_id)} — ${escapeHtml(w.machine_name)}</td>
                    <td>${escapeHtml(w.part_needed)}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;color:var(--accent-amber);">${escapeHtml(w.status)}</td>
                    <td style="font-family:'IBM Plex Mono',monospace;">${
                        w.scheduled_start !== null ? `Hr ${w.scheduled_start}–${w.completion_step}` : "Waiting"
                    }</td>
                    <td>${escapeHtml(w.reason)}</td>
                    <td><button class="btn btn-amber btn-sm" data-sms-unit="${escapeHtml(w.machine_id)}">SMS Card</button></td>
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
        logBox.innerHTML = `<div class="audit-item">No actions logged yet.</div>`;
    } else {
        logBox.innerHTML = [...fleet.recent_events]
            .reverse()
            .map((e) => {
                const stepStr = e.step !== undefined ? `[Hr ${e.step}] ` : "";
                const target = e.machine_id ? ` · ${escapeHtml(e.machine_id)}` : "";
                const wo = e.wo_id ? ` · ${escapeHtml(e.wo_id)}` : "";
                return `<div class="audit-item">${stepStr}<strong style="color:var(--text-primary);">${escapeHtml(e.event)}</strong>${target}${wo}</div>`;
            })
            .join("");
    }
}

async function openSmsJobCard(machineId) {
    const res = await apiJson(`/api/sms-card/${encodeURIComponent(machineId)}?step=${STATE.step}`);
    if (!res.ok) {
        showToast(res.message || "Could not load SMS card.", "warning");
        return;
    }
    STATE.lastSms = res;
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

/* ---------------- 9. Interactive SVG X-Ray Picture + Voice Explain ---------------- */
const PART_NOTES = {
    "Coolant Pump": {
        en: "Keeps the engine cool. When this wears out, the tractor engine gets too hot.",
        hi: "इंजन को ठंडा रखता है। इसके खराब होने पर ट्रैक्टर का इंजन ज़्यादा गरम हो जाता है।",
    },
    "Hydraulic Valve": {
        en: "Controls oil pressure for lifting tools. A leak makes lifting weak or slow.",
        hi: "ऑयल प्रेशर को नियंत्रित करता है। इसके लीक होने पर हल या लिफ्ट कमज़ोर हो जाती है।",
    },
    "Drive Bearing": {
        en: "Keeps wheels and shaft turning smoothly. Wear causes loud shaking and vibration.",
        hi: "पहिये और शाफ्ट को सही घुमाता है। इसके घिसने पर तेज़ कंपन और आवाज़ आती है।",
    },
    "Sensor Harness": {
        en: "Carries wire signals from the tractor. Loose wires cause signal gaps, not engine damage.",
        hi: "मशीन से सिग्नल लाता है। तार ढीला होने पर केवल सिग्नल रुकता है, इंजन खराब नहीं होता।",
    },
};

function updateXrayBlueprint(machine, focusPart = null, shouldSpeak = false) {
    const parts = ["Coolant Pump", "Sensor Harness", "Hydraulic Valve", "Drive Bearing"];
    const targetPart = focusPart || machine.part_needed;
    STATE.lastXrayPart = targetPart;

    document.getElementById("xray-unit-title").textContent = `${machine.machine_id} — ${machine.name}`;
    document.getElementById("xray-focus-note").textContent =
        STATE.lang === "hi" ? `जांच पुर्जा: ${targetPart}` : `Part to check: ${targetPart}`;

    parts.forEach((pName) => {
        const box = document.getElementById(`part-box-${pName}`);
        if (!box) return;
        const isTarget = pName === targetPart;
        if (isTarget) {
            if (machine.status === "CRITICAL_WARNING" || machine.status === "EARLY_WARNING" || machine.status === "BROKEN_DOWN") {
                box.setAttribute("fill", "rgba(217, 83, 79, 0.28)");
                box.setAttribute("stroke", themeColor("--accent-amber") || "#e59a32");
                box.setAttribute("stroke-width", "3");
            } else if (machine.status === "DATA_CHECK") {
                box.setAttribute("fill", "rgba(110, 136, 152, 0.28)");
                box.setAttribute("stroke", themeColor("--accent-slate") || "#6e8898");
                box.setAttribute("stroke-width", "2.6");
            } else if (machine.status === "SERVICED_READY" || machine.status === "SERVICING") {
                box.setAttribute("fill", "rgba(91, 154, 111, 0.26)");
                box.setAttribute("stroke", themeColor("--accent-sage") || "#5b9a6f");
                box.setAttribute("stroke-width", "2.6");
            } else {
                box.setAttribute("fill", "rgba(91, 154, 111, 0.2)");
                box.setAttribute("stroke", themeColor("--accent-sage") || "#5b9a6f");
                box.setAttribute("stroke-width", "2.4");
            }
        } else {
            box.setAttribute("fill", "#1d1c18");
            box.setAttribute("stroke", "#444139");
            box.setAttribute("stroke-width", "1.4");
        }
    });

    const noteObj = PART_NOTES[targetPart] || { en: "", hi: "" };
    const noteText = STATE.lang === "hi" ? noteObj.hi : noteObj.en;
    const stockTxt = machine.part_in_stock > 0 ? `${machine.part_in_stock} in stock` : "Out of stock";

    document.getElementById("xray-insp-body").innerHTML = `
        <div><strong>${escapeHtml(targetPart)}</strong></div>
        <div style="margin-top:6px;">${escapeHtml(noteText)}</div>
        <div style="margin-top:10px;"><strong>Machine part:</strong> ${escapeHtml(machine.part_needed)} (${escapeHtml(stockTxt)})</div>
    `;

    if (shouldSpeak) {
        speakText(`${targetPart}. ${noteText}`, STATE.lang);
    }
}

async function refreshTelemetry() {
    const unitId = STATE.selectedTelemetryUnit;
    const detail = await apiJson(`/api/machines/${encodeURIComponent(unitId)}/history?up_to_step=${STATE.step}`);
    if (!detail.ok) return;

    const m = detail.machine;
    const meta = STATUS_META[m.status] || { label: m.status };

    updateXrayBlueprint(m);

    document.getElementById("telemetry-explain-box").innerHTML = `
        <div><strong>Unit:</strong> ${escapeHtml(m.machine_id)} — ${escapeHtml(m.name)}</div>
        <div><strong>State:</strong> ${escapeHtml(meta.label)} &nbsp;|&nbsp; <strong>Feed:</strong> ${escapeHtml(SENSOR_LABELS[m.sensor_status] || m.sensor_status)}</div>
        <div><strong>Risk:</strong> ${(m.fault_probability * 100).toFixed(1)}% (±${(m.uncertainty * 100).toFixed(1)}%) &nbsp;|&nbsp; <strong>Confidence:</strong> ${(m.confidence * 100).toFixed(0)}%</div>
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
    if (!el || !window.Plotly) return;

    const hist = detail.history;
    const steps = hist.map((h) => h.step);
    const traces = [
        { x: steps, y: hist.map((h) => h.engine_temp), name: "Engine Temp (C)", mode: "lines+markers", line: { color: themeColor("--chart-temp"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x", yaxis: "y" },
        { x: steps, y: hist.map((h) => h.vibration), name: "Vibration (mm/s)", mode: "lines+markers", line: { color: themeColor("--chart-vibration"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x2", yaxis: "y2" },
        { x: steps, y: hist.map((h) => h.oil_pressure), name: "Oil Pressure (PSI)", mode: "lines+markers", line: { color: themeColor("--chart-oil"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x3", yaxis: "y3" },
        { x: steps, y: hist.map((h) => h.rpm_variance), name: "RPM Variance", mode: "lines+markers", line: { color: themeColor("--chart-rpm"), width: 2 }, marker: { size: 3.5 }, connectgaps: false, xaxis: "x4", yaxis: "y4" },
    ];

    const layout = {
        title: { text: `Hourly Sensor Readings — ${unitId}`, x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
        grid: { rows: 2, columns: 2, pattern: "independent", roworder: "top to bottom" },
        paper_bgcolor: themeColor("--chart-paper"),
        plot_bgcolor: themeColor("--chart-plot"),
        font: { family: "IBM Plex Mono, monospace", size: 10, color: themeColor("--chart-text") },
        height: 410,
        showlegend: false,
        margin: { l: 48, r: 20, t: 50, b: 36 },
        yaxis: { title: "Temp (C)", gridcolor: themeColor("--chart-grid") },
        yaxis2: { title: "Shake (mm/s)", gridcolor: themeColor("--chart-grid") },
        yaxis3: { title: "Oil (PSI)", gridcolor: themeColor("--chart-grid") },
        yaxis4: { title: "RPM Var", gridcolor: themeColor("--chart-grid") },
        xaxis: { showgrid: false },
        xaxis2: { showgrid: false },
        xaxis3: { showgrid: false, title: "Hour" },
        xaxis4: { showgrid: false, title: "Hour" },
    };

    Plotly.react(el, traces, layout, { displayModeBar: false, responsive: true });
}

/* ---------------- 10. Money Saved (₹) & Baseline Comparison ---------------- */
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
    document.getElementById("cmp-avail-gain").textContent = `+${imp.availability_gain_pct}% better than fixed schedule`;
    document.getElementById("cmp-saved").textContent = `${imp.downtime_hours_saved} hrs`;
    document.getElementById("cmp-downtime-split").textContent = `${ai.total_downtime_hours}h vs ${cal.total_downtime_hours}h old way`;
    document.getElementById("cmp-breakdowns").textContent = `${ai.unplanned_breakdowns}`;
    document.getElementById("cmp-breakdowns-note").textContent = `${imp.breakdowns_avoided} breakdowns prevented`;
    document.getElementById("cmp-lead").textContent = `${ai.avg_warning_lead_time_hours} hrs`;
    document.getElementById("cmp-holds").textContent = `${ai.noisy_or_missing_alerts_held} false alarms stopped`;

    await refreshRoi();

    if (!window.Plotly) return;
    const steps = comp.hourly_series.map((p) => p.step);

    Plotly.react(
        "chart-compare-avail",
        [
            { x: steps, y: comp.hourly_series.map((p) => p.calendar_availability_pct), name: "Old Fixed Schedule", mode: "lines", line: { color: themeColor("--chart-calendar"), width: 2, dash: "dash" } },
            { x: steps, y: comp.hourly_series.map((p) => p.ai_twin_availability_pct), name: "Agro-Twin AI", mode: "lines", line: { color: themeColor("--accent-amber"), width: 2.8 }, fill: "tonexty", fillcolor: themeColor("--chart-accent-soft") },
        ],
        {
            title: { text: "Machines Working Over 120 Hours", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
            paper_bgcolor: themeColor("--chart-paper"),
            plot_bgcolor: themeColor("--chart-plot"),
            font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
            height: 310,
            margin: { l: 48, r: 16, t: 48, b: 38 },
            xaxis: { title: "Hour", showgrid: false },
            yaxis: { title: "Working (%)", range: [45, 105], gridcolor: themeColor("--chart-grid") },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" },
        },
        { displayModeBar: false, responsive: true }
    );

    const barCats = ["Hours Stopped", "Breakdowns", "Early Warning (hrs)"];
    Plotly.react(
        "chart-compare-bar",
        [
            { type: "bar", name: "Old Fixed Schedule", x: barCats, y: [cal.total_downtime_hours, cal.unplanned_breakdowns, cal.avg_warning_lead_time_hours], marker: { color: themeColor("--chart-muted") }, text: [`${cal.total_downtime_hours}h`, `${cal.unplanned_breakdowns}`, `${cal.avg_warning_lead_time_hours}h`], textposition: "outside" },
            { type: "bar", name: "Agro-Twin AI", x: barCats, y: [ai.total_downtime_hours, ai.unplanned_breakdowns, ai.avg_warning_lead_time_hours], marker: { color: themeColor("--accent-amber") }, text: [`${ai.total_downtime_hours}h`, `${ai.unplanned_breakdowns}`, `${ai.avg_warning_lead_time_hours}h`], textposition: "outside" },
        ],
        {
            title: { text: "Old Way vs Agro-Twin", x: 0, font: { family: "IBM Plex Sans, sans-serif", size: 14, color: themeColor("--chart-title") } },
            barmode: "group",
            paper_bgcolor: themeColor("--chart-paper"),
            plot_bgcolor: themeColor("--chart-plot"),
            font: { family: "IBM Plex Mono, monospace", size: 11, color: themeColor("--chart-text") },
            height: 310,
            margin: { l: 44, r: 16, t: 48, b: 38 },
            xaxis: { showgrid: false },
            yaxis: { gridcolor: themeColor("--chart-grid") },
            legend: { orientation: "h", y: 1.12, x: 1, xanchor: "right" },
        },
        { displayModeBar: false, responsive: true }
    );
}

/* ---------------- 11. Fleet CRUD Sync & Controls ---------------- */
function syncMachineSelects(machines) {
    const telSel = document.getElementById("telemetry-unit-select");
    const injSel = document.getElementById("inj-machine");
    const managerSel = document.getElementById("fleet-manager-unit-select");
    const ids = new Set(machines.map((m) => m.machine_id));

    const prevTel = ids.has(STATE.selectedTelemetryUnit) ? STATE.selectedTelemetryUnit : machines[0].machine_id;
    const prevInj = ids.has(injSel.value) ? injSel.value : machines[machines.length - 1].machine_id;
    const prevMgr = ids.has(managerSel.value) ? managerSel.value : machines[0].machine_id;

    [telSel, injSel, managerSel].forEach((sel) => {
        sel.innerHTML = "";
        machines.forEach((m) => {
            const opt = document.createElement("option");
            opt.value = m.machine_id;
            opt.textContent = `${m.machine_id} — ${m.name}`;
            sel.appendChild(opt);
        });
    });

    telSel.value = prevTel;
    injSel.value = prevInj;
    managerSel.value = prevMgr;
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
        showToast("At least one machine must remain.", "warning");
        return;
    }
    if (!window.confirm(`Delete ${machineId} from your fleet?`)) return;
    const res = await apiJson(`/api/machines/${encodeURIComponent(machineId)}`, { method: "DELETE" });
    showToast(res.message || "Machine removed.", res.ok ? "success" : "warning");
    if (res.ok) {
        await refreshAll();
        await refreshComparison();
    }
}

async function refreshAll(explicitStep = null) {
    if (!STATE.health) STATE.health = await apiJson("/api/health");
    const stepQuery = explicitStep !== null ? `?step=${explicitStep}` : (STATE.step !== null ? `?step=${STATE.step}` : "");
    const fleet = await apiJson(`/api/fleet${stepQuery}`);
    STATE.fleet = fleet;
    STATE.step = fleet.step;

    syncMachineSelects(fleet.machines);
    renderLedger(fleet);
    renderRiskChart(fleet.machines);
    renderFleetCards(fleet);
    renderPriorityQueue(fleet);
    renderWorkOrdersAndLog(fleet);
    await refreshTelemetry();

    // If opened via /repairs?sms=TR-101, open that SMS Job Card automatically!
    if (STATE.activePage === "repairs" && STATE.pendingSmsUnit) {
        const target = STATE.pendingSmsUnit;
        STATE.pendingSmsUnit = null;
        await openSmsJobCard(target);
    }
}

function initControls() {
    document.getElementById("btn-lang").addEventListener("click", () => {
        STATE.lang = STATE.lang === "en" ? "hi" : "en";
        writePref("agro-twin-lang", STATE.lang);
        applyLanguage();
    });

    document.getElementById("btn-view-mode").addEventListener("click", () => {
        STATE.simpleMode = !STATE.simpleMode;
        writePref("agro-twin-simple-mode", STATE.simpleMode);
        applyViewMode();
    });

    document.getElementById("btn-speak").addEventListener("click", speakPriorityAlert);
    document.getElementById("btn-hero-listen").addEventListener("click", speakPriorityAlert);

    document.getElementById("btn-speak-part").addEventListener("click", () => {
        const m = STATE.fleet?.machines.find((item) => item.machine_id === STATE.selectedTelemetryUnit);
        if (m) updateXrayBlueprint(m, STATE.lastXrayPart || m.part_needed, true);
    });

    document.getElementById("btn-speak-sms").addEventListener("click", () => {
        if (!STATE.lastSms) return;
        speakText(STATE.lang === "hi" ? STATE.lastSms.sms_hi : STATE.lastSms.sms_en, STATE.lang);
    });

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
        const res = await apiJson("/api/weather", { method: "POST", body: JSON.stringify({ weather_mode: "normal" }) });
        STATE.weatherMode = "normal";
        showToast(res.stress_note || "Switched to 30°C Normal weather.", "info");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-weather-heat").addEventListener("click", async () => {
        const res = await apiJson("/api/weather", { method: "POST", body: JSON.stringify({ weather_mode: "heatwave_45c" }) });
        STATE.weatherMode = "heatwave_45c";
        showToast(res.stress_note || "45°C Very Hot heatwave active!", "warning");
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

    // Clickable SVG X-Ray Parts -> Highlight AND speak aloud!
    document.querySelectorAll(".xray-part").forEach((node) => {
        node.addEventListener("click", () => {
            if (!STATE.fleet) return;
            const m = STATE.fleet.machines.find((item) => item.machine_id === STATE.selectedTelemetryUnit);
            if (m) updateXrayBlueprint(m, node.dataset.part, true);
        });
    });

    // Resize Plotly charts cleanly whenever a technical drawer is opened
    document.querySelectorAll(".tech-drawer").forEach((drawer) => {
        drawer.addEventListener("toggle", () => {
            if (drawer.open && window.Plotly) {
                setTimeout(() => {
                    drawer.querySelectorAll(".plot-box").forEach((node) => {
                        if (node && node.data) Plotly.Plots.resize(node);
                    });
                }, 80);
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
        const res = await apiJson("/api/constraints", { method: "POST", body: JSON.stringify(payload) });
        showToast(res.message || "Stock limits updated.", "info");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-inject-fault").addEventListener("click", async () => {
        const payload = {
            machine_id: document.getElementById("inj-machine").value,
            start_step: STATE.step,
            fault_type: document.getElementById("inj-type").value,
        };
        const res = await apiJson("/api/inject-fault", { method: "POST", body: JSON.stringify(payload) });
        showToast(res.message || "Fault injected.", res.ok ? "warning" : "info");
        await refreshAll();
        await refreshComparison();
    });

    document.getElementById("btn-save-webhook").addEventListener("click", async () => {
        const url = document.getElementById("inp-webhook-url").value.trim();
        const res = await apiJson("/api/webhook", { method: "POST", body: JSON.stringify({ webhook_url: url }) });
        showToast(res.message || "Webhook saved.", "success");
    });

    document.getElementById("btn-close-sms").addEventListener("click", () => {
        document.getElementById("sms-card-panel").classList.add("hidden");
    });

    // Fleet Manager CRUD Controls
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
            showToast("Enter a Machine ID, Name, and Importance between 0.8 and 1.5.", "warning");
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
            { method: isEditing ? "PUT" : "POST", body: JSON.stringify(isEditing ? payload : { ...payload, machine_id: machineId }) }
        );
        showToast(res.message || "Could not save machine.", res.ok ? "success" : "warning");
        if (res.ok) {
            managerMode.value = "edit";
            await refreshAll();
            if (!isEditing && res.machine) {
                managerUnit.value = res.machine.id;
                populateFleetManagerForm(managerUnit.value);
                syncFleetManagerMode();
            }
            await refreshComparison();
        }
    });

    document.getElementById("btn-delete-machine").addEventListener("click", () => removeMachine(managerUnit.value));
}

/* ---------------- 12. Voice-First On-Topic AI Helper Drawer ---------------- */
function formatMarkdownSimple(text) {
    return escapeHtml(text)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function appendAiMessage(text, role = "bot", isWarning = false) {
    const box = document.getElementById("ai-messages");
    const div = document.createElement("div");
    if (isWarning) {
        div.className = "msg warning";
        div.innerHTML = `<div class="msg-badge">WEBSITE-ONLY GUARDRAIL</div><div>${formatMarkdownSimple(text)}</div>`;
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
        if (STATE.autoSpeakAi) {
            speakText(res.answer, STATE.lang);
        }
        if (res.suggested_questions) updateAiChips(res.suggested_questions);
    } catch (err) {
        appendAiMessage("Could not connect to Agro-Twin Helper. Make sure the server is running.", "bot", true);
    }
}

function initAssistantDrawer() {
    const drawer = document.getElementById("ai-drawer");
    const fab = document.getElementById("ai-fab");
    const openTop = document.getElementById("btn-open-ai");
    const closeBtn = document.getElementById("btn-close-ai");
    const form = document.getElementById("ai-form");
    const input = document.getElementById("ai-input");
    const autoBtn = document.getElementById("btn-ai-autospeak");
    const micBtn = document.getElementById("btn-ai-mic");

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

    autoBtn.addEventListener("click", () => {
        STATE.autoSpeakAi = !STATE.autoSpeakAi;
        autoBtn.textContent = STATE.autoSpeakAi ? "Voice: On" : "Voice: Off";
        autoBtn.classList.toggle("active-weather", STATE.autoSpeakAi);
        if (!STATE.autoSpeakAi && "speechSynthesis" in window) window.speechSynthesis.cancel();
    });

    // Browser Voice Microphone Input (Zero API Keys — works in Chrome/Edge!)
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec && micBtn) {
        const rec = new SpeechRec();
        rec.interimResults = false;
        rec.maxAlternatives = 1;

        micBtn.addEventListener("click", () => {
            rec.lang = STATE.lang === "hi" ? "hi-IN" : "en-IN";
            try {
                micBtn.classList.add("listening");
                showToast(STATE.lang === "hi" ? "अब बोलें..." : "Listening... speak your question.", "info");
                rec.start();
            } catch (e) {
                micBtn.classList.remove("listening");
            }
        });

        rec.onresult = (event) => {
            micBtn.classList.remove("listening");
            const spoken = event.results[0][0].transcript;
            input.value = spoken;
            sendAiQuestion(spoken);
            input.value = "";
        };

        rec.onerror = () => {
            micBtn.classList.remove("listening");
            showToast("Could not hear voice clearly. Please tap a button or try again.", "warning");
        };

        rec.onend = () => micBtn.classList.remove("listening");
    } else if (micBtn) {
        micBtn.addEventListener("click", () => {
            showToast("Voice mic works best in Chrome or Edge. Tap any quick question button below!", "info");
        });
    }

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
        "Hello! Tap the **microphone button** to speak, or tap any quick button below. I can guide you through the website, tell you which tractor needs repair, or read answers aloud. I only answer questions about this Agro-Twin website.",
        "bot",
        false
    );
}

/* ---------------- Boot ---------------- */
window.addEventListener("DOMContentLoaded", async () => {
    STATE.activePage = document.body?.dataset?.page || "home";
    initThemeSelector();
    applyLanguage();
    initAmbientCanvas();
    initRevealAndSegments();
    initControls();
    initAssistantDrawer();
    await refreshAll();
    await refreshComparison();
});
