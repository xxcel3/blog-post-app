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


document.addEventListener("DOMContentLoaded", function() {
    //like buttons
    const likeButtons = document.querySelectorAll(".like-button");
    likeButtons.forEach(function(button) {
        button.addEventListener("click", function() {
            const postID = button.dataset.postID;
            recordLike(postID);
        });
    });

    //dislike buttons
    const dislikeButtons = document.querySelectorAll(".dislike-button");
    dislikeButtons.forEach(function(button) {
        button.addEventListener("click", function() {
            const postID = button.dataset.postID;
            recordDislike(postID);
        });
    });
});


function recordLike(postID) {
    fetch('/record-like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
        },
        body: JSON.stringify({ postId: postID })
    })
}


function recordDislike(postID) {
    fetch('/record-dislike', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json'
        },
        body: JSON.stringify({ postId: postID })
    })
}


// https://medium.com/swlh/javascript-how-to-create-a-like-button-3716c33b1879



