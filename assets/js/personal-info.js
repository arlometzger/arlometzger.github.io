window.personalInfo = {
    name: "Arlo Metzger",
    designation: "Projects, Experience, and Interests",
    location: "Brooklyn, New York",
    phone: "(718) 316-0360",
    email: "arlometzger1@gmail.com",
    socialMedia: {
        facebook: "#",
        linkedin: "#",
        pinterest: "#",
        twitter: "#"
    }
};

function populatePersonalInfo() {
    const info = window.personalInfo;

    document.querySelectorAll("[data-personal-name]").forEach((element) => {
        element.textContent = info.name;
    });
    document.querySelectorAll("[data-personal-designation]").forEach((element) => {
        element.textContent = info.designation;
    });
    document.querySelectorAll("[data-personal-location]").forEach((element) => {
        element.textContent = info.location;
    });
    document.querySelectorAll("[data-personal-phone]").forEach((element) => {
        element.textContent = info.phone;
    });
    document.querySelectorAll("[data-personal-email]").forEach((element) => {
        element.textContent = info.email;
    });

    document.querySelectorAll("[data-personal-social]").forEach((link) => {
        const url = info.socialMedia[link.dataset.personalSocial];
        if (!url || url === "#") {
            link.closest("li").style.display = "none";
            return;
        }
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
    });

    document.querySelectorAll("[data-personal-phone-link]").forEach((link) => {
        link.href = `tel:${info.phone.replace(/[^\d+]/g, "")}`;
    });
}

populatePersonalInfo();
