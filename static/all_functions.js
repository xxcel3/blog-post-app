// static/js/somethingJS.js

function welcome() { //might need modification in future, is this even needed?
    document.addEventListener("keypress", function (event) {
        if (event.code === "Enter") {
            sendChat();
        }
    });

    document.getElementById("chat-text-box").focus();

    current_post_listen();

    setInterval(current_post_listen, 5000);
}

//we need available_posts_listen() can be done later

//we need  current_post_listen() which will send get request
//to get the current messages to display both can be done with ajax
function current_post_listen() { //based on updateChat() from hw
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            clearChat();
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }
    request.open("GET", "/id/chat-message"); //id will be for each topic but for now will hard code as /id/*
    request.send();
}
function addMessageToChat(messageJSON) {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += chatMessageHTML(messageJSON);
    chatMessages.scrollIntoView(false);
    chatMessages.scrollTop = chatMessages.scrollHeight - chatMessages.clientHeight;
}
function chatMessageHTML(messageJSON) {
    const username = messageJSON.username;
    const message = messageJSON.message;
    const messageId = messageJSON.id; //not used for now
    let messageHTML = "<br><span id='message_" + messageId + "'><b>" + username + "</b>: " + message + "</span>";
    return messageHTML;
}
function clearChat() {
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML = "";
}

//we need send_chat() which sends the post request like hw only with ajax
function sendChat() {
    const chatTextBox = document.getElementById("chat-text-box");
    const message = chatTextBox.value;
    chatTextBox.value = "";

    // Using AJAX
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) { //checking request.readyState
            console.log(this.response);
        }
    }

    const messageJSON = {
        "message": message
    };

    request.open("POST", "/id/chat-message");
    request.setRequestHeader("Content-Type", "application/json")
    request.send(JSON.stringify(messageJSON));
    
    chatTextBox.focus();
}


//we need post_navigate() when a post is clicked

//create newPost() which will send a GET /frontpage/newPost request
function newPost() {
    window.location.href = "/frontpage/newPost";
}
function submitNewPost() {
    window.location.href = "/frontpage/newPost";
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



