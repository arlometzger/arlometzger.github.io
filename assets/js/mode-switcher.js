const toggleIcon = document.querySelector(".mode-changer");
const moonSvg = document.getElementById("moon-svg");
const sunSvg = document.getElementById("sun-svg");

function updateModeIcon() {
    const isDarkMode = document.body.classList.contains("dark-theme");
    if (moonSvg) moonSvg.style.display = isDarkMode ? "none" : "block";
    if (sunSvg) sunSvg.style.display = isDarkMode ? "block" : "none";
    if (toggleIcon) toggleIcon.style.background = isDarkMode ? "#434343" : "#EDEDED";
}

if (localStorage.getItem("mode") === "dark") {
    document.body.classList.add("dark-theme");
}
updateModeIcon();

if (toggleIcon) {
    toggleIcon.addEventListener("click", () => {
        const isDarkMode = document.body.classList.toggle("dark-theme");
        localStorage.setItem("mode", isDarkMode ? "dark" : "light");
        updateModeIcon();
    });
}
