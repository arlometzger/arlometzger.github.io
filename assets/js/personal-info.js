window.personalInfo = {
    name: "Arlo Metzger",
    designation: "Woodworking, machining & more",
    phone: "(718) 316-0360",
    email: "arlometzger1@gmail.com",
    socialMedia: {
        linkedin: "",
        instagram: ""
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
    document.querySelectorAll("[data-personal-social]").forEach((link) => {
        const url = info.socialMedia[link.dataset.personalSocial];
        if (!url || url === "#") {
            link.closest("li").hidden = true;
            return;
        }
        link.href = url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
    });

    document.querySelectorAll("[data-personal-phone-link]").forEach((link) => {
        link.href = `tel:${info.phone.replace(/[^\d+]/g, "")}`;
    });
    document.querySelectorAll("[data-personal-email-link]").forEach((link) => {
        link.href = `mailto:${info.email}`;
    });
}

populatePersonalInfo();
