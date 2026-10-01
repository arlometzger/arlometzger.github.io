const toggleIcon = document.getElementById('mode-changer');

toggleIcon.onclick = () => {
    const localStorageMode = localStorage.getItem('mode');
    const isDarkMode = localStorageMode === 'dark';

    localStorage.setItem('mode', isDarkMode ? 'light' : 'dark');
    document.body.classList.toggle("dark-theme");

    const moonSvg = document.getElementById('moon-svg');
    const sunSvg = document.getElementById('sun-svg');
    const modeChanger = document.getElementById('mode-changer');

    if (document.body.classList.contains("dark-theme")) {
        moonSvg.style.display = "none";
        sunSvg.style.display = "block";
        modeChanger.style.background = "#434343";
    } else {
        sunSvg.style.display = "none";
        moonSvg.style.display = "block";
        modeChanger.style.background = "#EDEDED";
    }
};

// Initialize theme on page load
if (localStorage.getItem('mode') === 'dark') {
    document.body.classList.add("dark-theme");
}
