/* Farmer Check-up screens: machine -> owner form -> question groups -> result. Rule-based backend in /checkup package. */
(function () {
    "use strict";

    var T = {
        en: {
            back: "Back to dashboard", title: "Farmer Check-up",
            note: "Based on common mechanical rules of thumb, not a replacement for a mechanic. Service intervals are placeholders; follow the machine manual. Stays on this demo. No personal data needed.",
            prev: "Back", next: "Next", submit: "See my result", pickMachine: "Which machine are you checking?",
            ownerTitle: "About your machine", step: "Step", of: "of", optional: "Choose owned or rented; the fields adjust to your choice. Skip anything you do not know.",
            loadedEarlier: "We loaded your earlier answers. You can change them.",
            sensorRisk: "Sensor risk", symptomRisk: "Your answers", combined: "Combined risk",
            suspected: "Suspected parts", why: "What we found", ideal: "Placeholder service intervals vs current", none: "Nothing specific found",
            bulkUnavailable: "Synthetic model report is unavailable; the rule-based check-up still works.",
            bulkRiskUnavailable: "The model-based estimate is unavailable; the rule-based result above is unchanged.",
            action: "What to do", editAns: "Edit my answers", report: "Get my report", reportHi: "रिपोर्ट हिंदी में", pdf: "Download PDF (English)", wa: "Share on WhatsApp",
            reqService: "Request service", requested: "Service requested.", saved: "Saved.",
            needsRepair: "This machine needs repair", loading: "Loading...", failed: "Something went wrong. Please try again.",
            pickFirst: "Please choose a machine first.", idleNote: "Sensor status", checkAgain: "Check another machine",
            sensorWord: "sensor", newCheck: "Start again",
            urg: { OK: "OK", WATCH: "WATCH", SERVICE_SOON: "SERVICE SOON", STOP_NOW: "STOP NOW" },
            act: {
                OK: "Looks fine. Keep to your routine service schedule.",
                WATCH: "Keep an eye on it and have it checked within a week.",
                SERVICE_SOON: "Get it serviced within 2-3 days or before the next heavy use.",
                STOP_NOW: "Stop using the machine and call a mechanic today."
            },
            st: { OK: "OK", DUE_SOON: "Due soon", OVERDUE: "Overdue", CHECK: "Check", NO_DATA: "No data" }
        },
        hi: {
            back: "डैशबोर्ड पर वापस", title: "किसान चेक-अप",
            note: "यह आम यांत्रिक अनुभव के नियमों पर आधारित है, मैकेनिक का विकल्प नहीं है। सर्विस अंतराल नमूना हैं; मशीन का मैनुअल मानें। यह केवल इस डेमो में रहता है। कोई निजी जानकारी नहीं चाहिए।",
            prev: "पीछे", next: "आगे", submit: "मेरा नतीजा देखें", pickMachine: "आप कौन सी मशीन जांच रहे हैं?",
            ownerTitle: "आपकी मशीन के बारे में", step: "चरण", of: "/", optional: "अपनी या किराये की चुनें; फ़ील्ड उसी अनुसार बदलेंगे। जो पता न हो उसे छोड़ दें।",
            loadedEarlier: "आपके पिछले जवाब लोड हो गए हैं। आप उन्हें बदल सकते हैं।",
            sensorRisk: "सेंसर जोखिम", symptomRisk: "आपके जवाब", combined: "कुल जोखिम",
            suspected: "संभावित खराब पुर्जे", why: "हमें क्या मिला", ideal: "नमूना सर्विस अंतराल बनाम मौजूदा", none: "कुछ खास नहीं मिला",
            bulkUnavailable: "सिम्युलेटेड मॉडल रिपोर्ट उपलब्ध नहीं है; नियम-आधारित चेक-अप फिर भी काम करता है।",
            bulkRiskUnavailable: "मॉडल-आधारित अनुमान उपलब्ध नहीं है; ऊपर का नियम-आधारित नतीजा अपरिवर्तित है।",
            action: "क्या करें", editAns: "जवाब बदलें", report: "मेरी रिपोर्ट", reportHi: "रिपोर्ट हिंदी में", pdf: "PDF डाउनलोड (अंग्रेज़ी)", wa: "व्हाट्सऐप पर भेजें",
            reqService: "सर्विस का अनुरोध करें", requested: "सर्विस का अनुरोध हो गया।", saved: "सेव हो गया।",
            needsRepair: "इस मशीन की मरम्मत ज़रूरी है", loading: "लोड हो रहा है...", failed: "कुछ गड़बड़ हुई। दोबारा कोशिश करें।",
            pickFirst: "पहले मशीन चुनें।", idleNote: "सेंसर स्थिति", checkAgain: "दूसरी मशीन जांचें",
            sensorWord: "सेंसर", newCheck: "फिर से शुरू करें",
            urg: { OK: "ठीक", WATCH: "नज़र रखें", SERVICE_SOON: "जल्द सर्विस", STOP_NOW: "अभी रोकें" },
            act: {
                OK: "सब ठीक लगता है। नियमित सर्विस समय पर कराते रहें।",
                WATCH: "नज़र रखें और एक हफ्ते में जांच कराएं।",
                SERVICE_SOON: "2-3 दिन में या अगले भारी काम से पहले सर्विस कराएं।",
                STOP_NOW: "मशीन चलाना बंद करें और आज ही मैकेनिक को बुलाएं।"
            },
            st: { OK: "ठीक", DUE_SOON: "जल्द", OVERDUE: "देर", CHECK: "जांचें", NO_DATA: "डेटा नहीं" }
        }
    };
    var ICON = { sound: "🔊", smell: "👃", look: "👀", feel: "✋", trend: "⏱", owner: "📋" };
    var ICON_URG = { OK: "✅", WATCH: "👁", SERVICE_SOON: "⚠️", STOP_NOW: "⛔" };

    var S = { bulk: null, bulkRisk: null, bulkError: false, bulkRiskError: false, lang: "en", data: null, machines: [], machine: null, owner: {}, answers: {}, step: 0, steps: [], result: null, loaded: false };

    function el(tag, cls, text) {
        var e = document.createElement(tag);
        if (cls) e.className = cls;
        if (text !== undefined) e.textContent = text;
        return e;
    }
    function t(k) { return T[S.lang][k]; }
    function L(obj, key) { return (S.lang === "hi" && obj[key + "_hi"]) || obj[key + "_en"] || obj[key]; }
    function pick(en, hi) { return S.lang === "hi" ? hi : en; }

    function api(url, opts) {
        return fetch(url, opts).then(function (r) {
            return r.json().then(function (j) { j.__status = r.status; return j; });
        });
    }
    function store(key, val) { try { if (val === undefined) { return JSON.parse(localStorage.getItem(key)); } localStorage.setItem(key, JSON.stringify(val)); } catch (e) { return null; } return null; }

    function applyTheme() {
        try {
            var th = localStorage.getItem("agro-twin-theme");
            if (th) document.documentElement.dataset.theme = th;
        } catch (e) { /* ignore */ }
    }

    function showError(msg) {
        var p = document.getElementById("ck-error");
        p.textContent = msg || "";
        p.classList.toggle("hidden", !msg);
    }

    function buildSteps() {
        var groups = S.data.groups.map(function (g) { return { kind: "group", id: g.id, g: g }; });
        S.steps = [{ kind: "machine" }, { kind: "owner" }].concat(groups);
    }

    function setProgress() {
        var total = S.steps.length;
        var pct = Math.round((S.step / total) * 100);
        var bar = document.getElementById("ck-bar");
        bar.style.width = pct + "%";
        bar.parentNode.setAttribute("aria-valuenow", String(pct));
        document.getElementById("ck-step-label").textContent =
            S.step < total ? t("step") + " " + (S.step + 1) + " " + t("of") + " " + total : "";
    }

    function applyStaticText() {
        document.documentElement.lang = S.lang === "hi" ? "hi" : "en";
        var nodes = document.querySelectorAll("[data-t]");
        for (var i = 0; i < nodes.length; i++) nodes[i].textContent = t(nodes[i].getAttribute("data-t"));
        var next = document.getElementById("ck-next");
        if (S.steps.length && S.step === S.steps.length - 1) next.textContent = t("submit");
    }

    function saveDraft() {
        if (!S.machine) return;
        store("agro-checkup-" + S.machine, { owner: S.owner, answers: S.answers, step: S.step });
    }

    /* ---------- stage renderers ---------- */
    function render() {
        var keepY = window.pageYOffset || 0;
        renderInner();
        window.scrollTo(0, keepY);
    }
    function renderInner() {
        showError("");
        var stage = document.getElementById("ck-stage");
        stage.innerHTML = "";
        var nav = document.getElementById("ck-nav");
        nav.classList.remove("hidden");
        if (S.result) { renderResult(stage); nav.classList.add("hidden"); setProgress(); return; }
        var st = S.steps[S.step];
        document.getElementById("ck-prev").style.visibility = S.step === 0 ? "hidden" : "visible";
        if (st.kind === "machine") renderMachine(stage);
        else if (st.kind === "owner") renderOwner(stage);
        else renderGroup(stage, st);
        applyStaticText();
        setProgress();
    }

    function renderMachine(stage) {
        stage.appendChild(el("h2", "ck-h", t("pickMachine")));
        var list = el("div", "ck-machines");
        S.machines.forEach(function (m) {
            var b = el("button", "ck-machine" + (S.machine === m.machine_id ? " sel" : ""));
            b.type = "button";
            b.appendChild(el("strong", "", m.machine_id));
            b.appendChild(el("span", "", " " + m.name));
            if (m.checkup_urgency) b.appendChild(el("em", "ck-chip", t("urg")[m.checkup_urgency] || m.checkup_urgency));
            b.addEventListener("click", function () { chooseMachine(m.machine_id); });
            list.appendChild(b);
        });
        stage.appendChild(list);
        if (S.loaded) stage.appendChild(el("p", "ck-info", t("loadedEarlier")));
    }

    function chooseMachine(id) {
        S.machine = id; S.owner = {}; S.answers = {}; S.loaded = false;
        var draft = store("agro-checkup-" + id);
        api("/api/checkup/" + encodeURIComponent(id)).then(function (j) {
            if (j.ok) { S.owner = j.owner || {}; S.answers = j.answers || {}; S.loaded = true; }
            else if (draft) { S.owner = draft.owner || {}; S.answers = draft.answers || {}; S.loaded = true; }
            render();
        }).catch(function (error) {
            render();
            showError(t("failed"));
            console.warn("Could not load farmer check-up profile.", error);
        });
    }

    function renderOwner(stage) {
        stage.appendChild(el("h2", "ck-h", ICON.owner + " " + t("ownerTitle")));
        stage.appendChild(el("p", "ck-info", t("optional")));
        S.data.owner_fields.forEach(function (f) {
            if (f.show_when && Object.keys(f.show_when).some(function (key) {
                return S.owner[key] !== f.show_when[key];
            })) return;
            var wrap = el("div", "ck-field");
            var lab = el("label", "ck-label", pick(f.en, f.hi));
            var id = "of-" + f.id;
            lab.setAttribute("for", id);
            wrap.appendChild(lab);
            var cur = S.owner[f.id];
            if (f.type === "number" || f.type === "date") {
                var inp = el("input", "ck-input");
                inp.id = id; inp.type = f.type;
                if (f.type === "number") { inp.inputMode = "decimal"; inp.min = f.min; inp.max = f.max; }
                if (cur !== undefined) inp.value = cur;
                inp.addEventListener("input", function () {
                    if (inp.value === "") delete S.owner[f.id]; else S.owner[f.id] = inp.value;
                    saveDraft();
                });
                wrap.appendChild(inp);
            } else if (f.type === "select") {
                var group = el("div", "ck-opts");
                f.options.forEach(function (o) {
                    group.appendChild(optBtn(pick(o[1], o[2]), cur === o[0], function (btn) {
                        if (S.owner[f.id] === o[0]) delete S.owner[f.id]; else S.owner[f.id] = o[0];
                        S.data.owner_fields.forEach(function (conditional) {
                            if (conditional.show_when &&
                                Object.prototype.hasOwnProperty.call(conditional.show_when, f.id) &&
                                conditional.show_when[f.id] !== S.owner[f.id]) {
                                delete S.owner[conditional.id];
                            }
                        });
                        saveDraft(); render();
                    }));
                });
                wrap.appendChild(group);
            } else if (f.type === "multi") {
                var g2 = el("div", "ck-opts");
                var arr = Array.isArray(cur) ? cur : [];
                f.options.forEach(function (o) {
                    g2.appendChild(optBtn(pick(o[1], o[2]), arr.indexOf(o[0]) >= 0, function () {
                        var a = (S.owner[f.id] || []).slice();
                        var i = a.indexOf(o[0]);
                        if (i >= 0) a.splice(i, 1); else a.push(o[0]);
                        if (a.length) S.owner[f.id] = a; else delete S.owner[f.id];
                        saveDraft(); render();
                    }));
                });
                wrap.appendChild(g2);
            }
            stage.appendChild(wrap);
        });
    }

    function optBtn(text, selected, onClick) {
        var b = el("button", "ck-opt" + (selected ? " sel" : ""), text);
        b.type = "button";
        b.setAttribute("aria-pressed", selected ? "true" : "false");
        b.addEventListener("click", onClick);
        return b;
    }

    function renderGroup(stage, st) {
        stage.appendChild(el("h2", "ck-h", (ICON[st.id] || "") + " " + pick(st.g.en, st.g.hi)));
        S.data.questions.filter(function (q) { return q.group === st.id; }).forEach(function (q) {
            var box = el("div", "ck-q");
            box.appendChild(el("p", "ck-qtext", pick(q.text_en, q.text_hi)));
            var opts = el("div", "ck-opts");
            var cur = S.answers[q.id] || [];
            q.options.forEach(function (o) {
                var sel = cur.indexOf(o.id) >= 0;
                opts.appendChild(optBtn(pick(o.en, o.hi), sel, function () {
                    var a = (S.answers[q.id] || []).slice();
                    var i = a.indexOf(o.id);
                    if (i >= 0) { a.splice(i, 1); }
                    else if (q.type === "single" || o.id === "unsure" || o.id === "none" || o.id === "smoke_none") { a = [o.id]; }
                    else { a = a.filter(function (x) { return x !== "unsure" && x !== "none"; }); a.push(o.id); }
                    if (a.length) S.answers[q.id] = a; else delete S.answers[q.id];
                    saveDraft(); render();
                }));
            });
            box.appendChild(opts);
            stage.appendChild(box);
        });
    }

    /* ---------- result ---------- */
    function pctText(x) { return Math.round((x || 0) * 100) + "%"; }

    function renderResult(stage) {
        var r = S.result;
        var u = r.urgency;
        var banner = el("div", "ck-verdict ck-u-" + u);
        banner.appendChild(el("span", "ck-v-icon", ICON_URG[u] || ""));
        var txt = el("div", "");
        txt.appendChild(el("strong", "ck-v-label", t("urg")[u] || u));
        if (u === "SERVICE_SOON" || u === "STOP_NOW") txt.appendChild(el("div", "ck-v-sub", t("needsRepair")));
        banner.appendChild(txt);
        stage.appendChild(banner);

        stage.appendChild(el("h2", "ck-h", t("action")));
        stage.appendChild(el("p", "ck-action", t("act")[u] || ""));

        var risks = el("div", "ck-risks");
        [["sensorRisk", r.sensor_risk], ["symptomRisk", r.symptom_risk], ["combined", r.combined_risk]].forEach(function (p) {
            var c = el("div", "ck-risk");
            c.appendChild(el("div", "ck-risk-n", pctText(p[1])));
            c.appendChild(el("div", "ck-risk-l", t(p[0])));
            risks.appendChild(c);
        });
        stage.appendChild(risks);

        stage.appendChild(el("h2", "ck-h", t("suspected")));
        var sus = el("div", "ck-opts");
        var names = S.data.systems;
        if (!r.suspected_systems.length) sus.appendChild(el("span", "ck-info", t("none")));
        r.suspected_systems.forEach(function (s) {
            var n = names[s] ? pick(names[s].en, names[s].hi) : s;
            sus.appendChild(el("span", "ck-tag", n));
        });
        stage.appendChild(sus);

        stage.appendChild(el("h2", "ck-h", t("why")));
        var ul = el("ul", "ck-reasons");
        r.reasons.slice(0, 5).forEach(function (x) { ul.appendChild(el("li", "", pick(x.en, x.hi))); });
        if (!r.reasons.length) ul.appendChild(el("li", "", t("none")));
        stage.appendChild(ul);

        stage.appendChild(el("h2", "ck-h", t("ideal")));
        var tbl = el("div", "ck-ideal");
        r.ideal_vs_current.forEach(function (row) {
            var line = el("div", "ck-row ck-s-" + row.status);
            line.appendChild(el("span", "ck-dot", ""));
            line.appendChild(el("span", "ck-row-text", pick(row.line_en, row.line_hi)));
            line.appendChild(el("span", "ck-row-badge", t("st")[row.status] || row.status));
            tbl.appendChild(line);
        });
        stage.appendChild(tbl);

        var btns = el("div", "ck-actions");
        var b1 = el("a", "btn btn-amber ck-big", t("report"));
        b1.href = "/api/checkup/" + encodeURIComponent(S.machine) + "/report?lang=en"; b1.target = "_blank"; b1.rel = "noopener";
        var b2 = el("a", "btn btn-subtle ck-big", t("reportHi"));
        b2.href = "/api/checkup/" + encodeURIComponent(S.machine) + "/report?lang=hi"; b2.target = "_blank"; b2.rel = "noopener";
        btns.appendChild(b1); btns.appendChild(b2);
        var bp = el("a", "btn btn-subtle ck-big", t("pdf"));
        bp.href = "/api/checkup/" + encodeURIComponent(S.machine) + "/report?lang=en&format=pdf"; bp.setAttribute("download", "");
        btns.appendChild(bp);
        var bw = el("button", "btn btn-subtle ck-big", t("wa"));
        bw.type = "button";
        bw.addEventListener("click", function () {
            api("/api/checkup/" + encodeURIComponent(S.machine) + "/report?lang=" + S.lang + "&format=json").then(function (rep) {
                if (rep && rep.mechanic_message) window.open("https://wa.me/?text=" + encodeURIComponent(rep.mechanic_message), "_blank", "noopener");
            }).catch(function () { showError(t("failed")); });
        });
        btns.appendChild(bw);
        if (u === "SERVICE_SOON" || u === "STOP_NOW") {
            var b3 = el("button", "btn btn-outline-danger ck-big", t("reqService"));
            b3.type = "button";
            b3.addEventListener("click", function () {
                api("/api/schedule", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ machine_id: S.machine }) })
                    .then(function (j) { b3.disabled = true; b3.textContent = j && j.ok ? t("requested") : (j && j.message) || t("failed"); })
                    .catch(function () { showError(t("failed")); });
            });
            btns.appendChild(b3);
        }
        var b4 = el("button", "btn btn-ghost ck-big", t("editAns"));
        b4.type = "button";
        b4.addEventListener("click", function () { S.result = null; S.step = 1; render(); });
        btns.appendChild(b4);
        var b5 = el("button", "btn btn-ghost ck-big", t("checkAgain"));
        b5.type = "button";
        b5.addEventListener("click", function () { S.result = null; S.machine = null; S.step = 0; loadMachines().then(render); });
        btns.appendChild(b5);
        stage.appendChild(btns);
        renderBulk(stage);
        stage.appendChild(el("p", "ck-note", t("note")));
    }

    function renderBulk(stage) {
        var box = el("div", "ck-bulk");
        if (S.bulk && S.bulk.report) {
            var r = S.bulk.report;
            box.appendChild(el("h2", "ck-h", pick("Trained on simulated machines", "सिम्युलेटेड मशीनों पर प्रशिक्षित")));
            box.appendChild(el("p", "ck-tag", pick("Trained on ", "प्रशिक्षण: ") + r.n_train_machines + pick(" simulated machines · Synthetic data", " सिम्युलेटेड मशीनें · कृत्रिम डेटा")));
            box.appendChild(el("p", "ck-info", pick("Held-out test: ", "अलग टेस्ट: ") + r.n_test_machines + pick(" machines never seen in training. Accuracy ", " मशीनें। सटीकता ") +
                Math.round(r.accuracy * 100) + "% (" + pick("fixed-interval rule: ", "तय अंतराल नियम: ") + Math.round(r.baseline_fixed_interval.accuracy * 100) + "%). " +
                pick("Hours-to-failure error: ", "खराबी तक घंटों की त्रुटि: ") + r.hours_to_failure_mae.all_test_machines + " h. " +
                pick("This shows the method works on our simulation, not that it is accurate on real tractors.", "यह हमारे सिमुलेशन पर तरीका काम करता दिखाता है, असली ट्रैक्टरों पर सटीकता नहीं।")));
        }
        if (S.bulkError) box.appendChild(el("p", "ck-info", t("bulkUnavailable")));
        if (S.bulk && S.bulk.benchmark) {
            var bm = S.bulk.benchmark, a = bm.any_failure, bl = bm.baseline_tool_wear_over_200_min;
            box.appendChild(el("p", "ck-tag", pick("Public benchmark: different machine type", "सार्वजनिक बेंचमार्क: अलग प्रकार की मशीन")));
            box.appendChild(el("p", "ck-info", pick("On the public UCI AI4I dataset (", "सार्वजनिक UCI AI4I डेटा पर (") + bm.rows + pick(" milling-machine records, itself synthetic) the same method scored F1 ", " मिलिंग मशीन रिकॉर्ड, खुद कृत्रिम) वही तरीका F1 ") + a.f1 +
                " (" + pick("simple rule: ", "सरल नियम: ") + bl.f1 + "). " +
                pick("This shows the method works on a public benchmark, not that it works on tractors.", "यह दिखाता है कि तरीका सार्वजनिक बेंचमार्क पर काम करता है, ट्रैक्टरों पर नहीं।")));
        }
        if (S.bulkRisk) {
            var b = S.bulkRisk;
            var top = b.top_system && S.data.systems[b.top_system] ? pick(S.data.systems[b.top_system].en, S.data.systems[b.top_system].hi) : "-";
            box.appendChild(el("p", "ck-info", pick("Learned model (simulated data): chance of a fault ", "सीखा मॉडल (सिम्युलेटेड डेटा): खराबी की संभावना ") + Math.round(b.p_any_fault * 100) + "%, " +
                pick("most likely part: ", "सबसे संभावित हिस्सा: ") + top + ", " + pick("estimated time to failure: ", "खराबी तक अनुमानित समय: ") + b.hours_to_failure_range[0] + "-" + b.hours_to_failure_range[1] + " h."));
        }
        if (S.bulkRiskError) box.appendChild(el("p", "ck-info", t("bulkRiskUnavailable")));
        stage.appendChild(box);
    }

    function submit() {
        var next = document.getElementById("ck-next");
        next.disabled = true;
        api("/api/checkup/" + encodeURIComponent(S.machine) + "/submit", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ owner: S.owner, answers: S.answers })
        }).then(function (j) {
            next.disabled = false;
            if (!j.ok) { showError((j.errors && j.errors.join("; ")) || j.error || t("failed")); return; }
            S.result = j.result; S.bulkRisk = null; S.bulkRiskError = false;
            api("/api/checkup/" + encodeURIComponent(S.machine) + "/bulk-risk").then(function (b) {
                if (b.ok) S.bulkRisk = b;
                else { S.bulkRiskError = true; console.warn("Bulk risk estimate unavailable:", b.error || b.__status); }
                render();
            }).catch(function (error) {
                S.bulkRiskError = true;
                console.warn("Bulk risk request failed.", error);
                render();
            });
            render(); window.scrollTo(0, 0);
        }).catch(function () { next.disabled = false; showError(t("failed")); });
    }

    function loadMachines() {
        return api("/api/checkup/machines").then(function (j) { S.machines = j.machines || []; });
    }

    function init() {
        applyTheme();
        document.getElementById("ck-lang").addEventListener("click", function () {
            S.lang = S.lang === "en" ? "hi" : "en"; store("agro-checkup-lang", S.lang); render();
        });
        document.getElementById("ck-prev").addEventListener("click", function () { if (S.step > 0) { S.step--; render(); } });
        document.getElementById("ck-next").addEventListener("click", function () {
            if (S.steps[S.step].kind === "machine" && !S.machine) { showError(t("pickFirst")); return; }
            if (S.step === S.steps.length - 1) { submit(); return; }
            S.step++; saveDraft(); render(); window.scrollTo(0, 0);
        });
        var savedLang = store("agro-checkup-lang"); if (savedLang === "hi") S.lang = "hi";
        api("/api/checkup/bulk-report").then(function (b) {
            if (b.ok) S.bulk = b;
            else { S.bulkError = true; console.warn("Bulk model report unavailable:", b.error || b.__status); }
            if (S.result) render();
        }).catch(function (error) {
            S.bulkError = true;
            console.warn("Bulk model report request failed.", error);
            if (S.result) render();
        });
        Promise.all([api("/api/checkup/questions"), loadMachines()]).then(function (res) {
            S.data = res[0]; buildSteps(); render();
        }).catch(function () { showError(t("failed")); });
    }
    init();
})();
