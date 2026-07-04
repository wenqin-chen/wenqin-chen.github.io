/* Theme toggle — respects saved choice, then system preference. */
(function () {
  var root = document.documentElement;
  var btn = document.getElementById("theme-toggle");
  function systemDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function isDark() {
    var t = root.getAttribute("data-theme");
    return t ? t === "dark" : systemDark();
  }
  function paint() {
    if (!btn) return;
    btn.textContent = isDark() ? "☀" : "☾"; // sun / moon
    btn.setAttribute("aria-label", isDark() ? "Switch to light mode" : "Switch to dark mode");
  }
  paint();
  if (btn) {
    btn.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      paint();
    });
  }
})();
