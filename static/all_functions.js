// static/js/somethingJS.js
function welcome() {
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    document.getElementById("chat-text-box").focus();

    updateChat();
}


