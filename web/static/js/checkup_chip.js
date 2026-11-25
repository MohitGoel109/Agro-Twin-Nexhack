/* Adds a "Farmer reported" chip to fleet cards on the main dashboard. Self-contained: does not touch app.js. */
(function () {
    "use strict";
    var grid = null, busy = false, data = {}, extra = {};
    var LABEL = { OK: "OK", WATCH: "WATCH", SERVICE_SOON: "SERVICE SOON", STOP_NOW: "STOP NOW" };

    function decorate() {
        if (!grid) return;
        var cards = grid.querySelectorAll(".unit-card");
        for (var i = 0; i < cards.length; i++) {
            var c = cards[i];
            if (c.querySelector(".ck-fleet-chip")) continue;
            var idEl = c.querySelector(".unit-id");
            var u = idEl && data[idEl.textContent.trim()];
            if (!u) continue;
            var a = document.createElement("a");
            a.className = "ck-fleet-chip u-" + u;
            a.href = "/checkup";
            var x = extra[idEl.textContent.trim()] || {};
            var w = x.worst_system_status ? " \u00B7 Worst: " + x.worst_system_status.replace("_", " ") : "";
            a.textContent = "Farmer reported: " + (LABEL[u] || u) + (x.owner_form_filled ? " \u00B7 Owner form filled" : "") + w + " \u00B7 Report ready";
            var summary = c.querySelector(".unit-summary");
            if (summary && summary.parentNode) summary.parentNode.insertBefore(a, summary.nextSibling);
        }
    }

    function refresh() {
        fetch("/api/checkup/machines").then(function (r) {
            if (!r.ok) throw new Error("Machine check-up list request failed: " + r.status);
            return r.json();
        }).then(function (j) {
            data = {}; extra = {};
            (j.machines || []).forEach(function (m) {
                if (m.checkup_urgency) { data[m.machine_id] = m.checkup_urgency; extra[m.machine_id] = m; }
            });
            decorate();
        }).catch(function (error) { console.warn("Could not refresh farmer check-up chips.", error); });
    }

    function start() {
        grid = document.getElementById("fleet-cards-grid");
        if (!grid) return;
        new MutationObserver(function () {
            if (busy) return;
            busy = true;
            decorate();
            busy = false;
        }).observe(grid, { childList: true });
        refresh();
        setInterval(refresh, 15000);
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
