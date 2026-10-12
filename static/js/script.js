// =========================
// SEARCH POPUP
// =========================

function openSearch() {
    const searchBox = document.getElementById("search-box");

    if (searchBox) {
        searchBox.style.display = "flex";
    }
}

function closeSearch() {
    const searchBox = document.getElementById("search-box");

    if (searchBox) {
        searchBox.style.display = "none";
    }
}


// =========================
// CLOSE SEARCH ON BACKGROUND CLICK
// =========================

document.addEventListener("click", function (event) {

    const searchBox = document.getElementById("search-box");

    if (
        searchBox &&
        event.target === searchBox
    ) {
        closeSearch();
    }

});


// =========================
// AI CHATBOT
// =========================

function openChatbot() {

    const chatbotBox = document.getElementById("chatbot-box");

    if (chatbotBox) {
        chatbotBox.style.display = "flex";
    }
}


// =========================
// ESC KEY
// =========================

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {
        closeSearch();
    }

});