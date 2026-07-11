/* GymPro front-end helpers: sidebar toggle, toasts, loading spinner */
(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        // --- Mobile sidebar toggle ------------------------------------
        const toggle = document.getElementById("sidebarToggle");
        const sidebar = document.getElementById("sidebar");
        const backdrop = document.getElementById("sidebarBackdrop");

        if (toggle && sidebar) {
            toggle.addEventListener("click", function () {
                sidebar.classList.toggle("open");
                if (backdrop) backdrop.classList.toggle("show");
            });
        }
        if (backdrop && sidebar) {
            backdrop.addEventListener("click", function () {
                sidebar.classList.remove("open");
                backdrop.classList.remove("show");
            });
        }

        // --- Auto-dismiss Bootstrap alerts ----------------------------
        document.querySelectorAll(".alert-dismissible").forEach(function (alert) {
            setTimeout(function () {
                if (window.bootstrap) {
                    const inst = bootstrap.Alert.getOrCreateInstance(alert);
                    inst.close();
                }
            }, 5000);
        });

        // --- Loading spinner on form submit / nav ---------------------
        const overlay = document.getElementById("loading-overlay");
        if (overlay) {
            document.querySelectorAll("form").forEach(function (form) {
                form.addEventListener("submit", function () {
                    overlay.classList.add("active");
                });
            });
        }

        // --- Confirm delete buttons -----------------------------------
        document.querySelectorAll("[data-confirm]").forEach(function (el) {
            el.addEventListener("click", function (e) {
                if (!window.confirm(el.getAttribute("data-confirm"))) {
                    e.preventDefault();
                }
            });
        });
    });
})();
