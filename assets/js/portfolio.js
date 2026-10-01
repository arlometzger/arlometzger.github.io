const projectList = document.getElementById("portfolio");
const loadMoreButton = document.getElementById("load-more-btn");
const projectsPerPage = 6;
const categories = ["Woodworking", "Machining", "3D modelling", "Pottery", "Miscellaneous"];
const requestedCategory = new URLSearchParams(window.location.search).get("category");
const activeCategory = categories.includes(requestedCategory) ? requestedCategory : "";
let visibleProjectCount = projectsPerPage;

function createProjectCard(project) {
    const card = document.createElement("article");
    card.className = "portfolio-card";

    const imageContainer = document.createElement("div");
    imageContainer.className = "portfolio-card__feature-image";
    const projectLink = document.createElement("a");
    projectLink.href = project.url || "singlePortfolio.html";

    if (project.image) {
        const image = document.createElement("img");
        image.src = project.image;
        image.alt = project.title;
        projectLink.appendChild(image);
    } else {
        const placeholder = document.createElement("span");
        placeholder.className = "portfolio-card__placeholder";
        placeholder.textContent = "Add a project photo";
        projectLink.appendChild(placeholder);
    }

    imageContainer.appendChild(projectLink);
    card.appendChild(imageContainer);

    const category = document.createElement("p");
    category.className = "portfolio-card__meta";
    category.textContent = project.category;
    card.appendChild(category);

    const title = document.createElement("h2");
    title.className = "portfolio-card__title";
    const titleLink = document.createElement("a");
    titleLink.href = project.url || "singlePortfolio.html";
    titleLink.textContent = project.title;
    title.appendChild(titleLink);
    card.appendChild(title);

    return card;
}

function renderProjects() {
    const projects = Array.isArray(window.projects) ? window.projects : [];
    const filteredProjects = activeCategory
        ? projects.filter((project) => project.category === activeCategory)
        : projects;
    const visibleProjects = filteredProjects.slice(0, visibleProjectCount);

    projectList.replaceChildren();
    if (visibleProjects.length === 0) {
        const message = document.createElement("p");
        message.className = "portfolio-empty-state";
        message.textContent = activeCategory
            ? `No ${activeCategory} projects yet.`
            : "No projects yet. Add your work in assets/js/projects.js.";
        projectList.appendChild(message);
    } else {
        visibleProjects.forEach((project) => projectList.appendChild(createProjectCard(project)));
    }

    loadMoreButton.hidden = visibleProjects.length >= filteredProjects.length;
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
