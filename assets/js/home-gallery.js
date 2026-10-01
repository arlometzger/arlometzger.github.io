function renderHomeGalleries() {
    const projects = Array.isArray(window.projects) ? window.projects : [];

    document.querySelectorAll("[data-project-gallery]").forEach((gallery) => {
        const category = gallery.dataset.projectGallery;
        const categoryProjects = projects
            .filter((project) => project.category === category)
            .slice(0, 3);

        gallery.replaceChildren();
        for (let index = 0; index < 3; index += 1) {
            const project = categoryProjects[index];
            if (!project || !project.image) {
                const placeholder = document.createElement("div");
                placeholder.className = "craft-gallery__placeholder";
                placeholder.setAttribute("role", "img");
                placeholder.setAttribute("aria-label", `Add a ${category} project photo`);

                const icon = document.createElement("i");
                icon.className = "fa-regular fa-image";
                icon.setAttribute("aria-hidden", "true");

                const label = document.createElement("span");
                label.textContent = "Add a project photo";

                placeholder.append(icon, label);
                gallery.appendChild(placeholder);
                continue;
            }

            const link = document.createElement("a");
            link.className = "craft-gallery__item";
            link.href = project.url || `portfolio.html?category=${encodeURIComponent(category)}`;
            link.setAttribute("aria-label", `View ${project.title}`);

            const image = document.createElement("img");
            image.src = project.image;
            image.alt = project.title;
            image.loading = "lazy";
            link.appendChild(image);
            gallery.appendChild(link);
        }
    });
}

renderHomeGalleries();
