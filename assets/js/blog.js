const blogCards = Array.from(document.querySelectorAll("[data-blog-card]"));
const loadMoreButton = document.getElementById("load-more-btn");
const postsPerPage = 6;
let visiblePostCount = postsPerPage;

function renderPosts() {
    blogCards.forEach((card, index) => {
        card.hidden = index >= visiblePostCount;
    });

    loadMoreButton.hidden = blogCards.length <= visiblePostCount;
}

loadMoreButton.addEventListener("click", () => {
    visiblePostCount += postsPerPage;
    renderPosts();
});

renderPosts();
