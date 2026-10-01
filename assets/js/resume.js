function appendResumeEntry(container, entry, type) {
    const article = document.createElement("article");
    article.className = "resume-entry";

    const heading = document.createElement("h3");
    heading.textContent = type === "education" ? entry.institution : entry.title;
    article.appendChild(heading);

    const details = [type === "education" ? entry.credential : entry.organization, entry.dates, entry.location]
        .filter(Boolean);
    if (details.length > 0) {
        const metadata = document.createElement("p");
        metadata.className = "resume-entry__metadata";
        metadata.textContent = details.join(" · ");
        article.appendChild(metadata);
    }

    if (entry.description) {
        const description = document.createElement("p");
        description.className = "resume-entry__description";
        description.textContent = entry.description;
        article.appendChild(description);
    }

    container.appendChild(article);
}

function renderResumeSection(containerId, entries, type) {
    const container = document.getElementById(containerId);
    if (!Array.isArray(entries) || entries.length === 0) {
        const emptyState = document.createElement("p");
        emptyState.className = "resume-empty-state";
        emptyState.textContent = `Add ${type} details to assets/js/resume-data.js.`;
        container.appendChild(emptyState);
        return;
    }

    entries.forEach((entry) => appendResumeEntry(container, entry, type));
}

const resumeData = window.resumeData || {};
renderResumeSection("resume-education", resumeData.education, "education");
renderResumeSection("resume-experience", resumeData.experience, "experience");

const skillsList = document.getElementById("resume-skills");
if (Array.isArray(resumeData.skills) && resumeData.skills.length > 0) {
    resumeData.skills.forEach((skill) => {
        const item = document.createElement("li");
        item.textContent = skill;
        skillsList.appendChild(item);
    });
} else {
    const emptyState = document.createElement("li");
    emptyState.className = "resume-empty-state";
    emptyState.textContent = "Add skills to assets/js/resume-data.js.";
    skillsList.appendChild(emptyState);
}

const resumeDownload = document.querySelector(".resume-download");
if (resumeData.pdfUrl && resumeDownload) {
    resumeDownload.href = resumeData.pdfUrl;
    resumeDownload.target = "_blank";
    resumeDownload.rel = "noopener noreferrer";
    resumeDownload.hidden = false;
}
