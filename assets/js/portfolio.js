const projectCards = Array.from(document.querySelectorAll("[data-project-card]"));
const loadMoreButton = document.getElementById("load-more-btn");
const emptyFilterMessage = document.getElementById("portfolio-filter-empty");
const projectsPerPage = 6;
const categories = ["Woodworking", "Machining", "3D modelling", "Pottery", "Miscellaneous"];
const requestedCategory = new URLSearchParams(window.location.search).get("category");
const activeCategory = categories.includes(requestedCategory) ? requestedCategory : "";
let visibleProjectCount = projectsPerPage;

function renderProjects() {
    let visibleCount = 0;
    let matchingCount = 0;

    projectCards.forEach((card) => {
        const matchesCategory = !activeCategory || card.dataset.category === activeCategory;
        const withinVisibleLimit = visibleCount < visibleProjectCount;
        card.hidden = !matchesCategory || !withinVisibleLimit;
        if (matchesCategory) {
            matchingCount += 1;
            visibleCount += 1;
        }
    });

    emptyFilterMessage.hidden = !activeCategory || matchingCount > 0;
    emptyFilterMessage.textContent = activeCategory ? `No ${activeCategory} projects yet.` : "";
    loadMoreButton.hidden = matchingCount <= visibleProjectCount;
}

document.querySelectorAll("#portfolio-tab .tab-item").forEach((link) => {
    const linkCategory = new URL(link.href).searchParams.get("category") || "";
    if (linkCategory === activeCategory) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
    }
});

loadMoreButton.addEventListener("click", () => {
    visibleProjectCount += projectsPerPage;
    renderProjects();
});

renderProjects();
