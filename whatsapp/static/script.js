// Connect to Socket.IO
var socket = io();

// Get elements
const messagesDiv = document.getElementById("messages");
const input = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typing");

// Current user
const username = document.getElementById("username").value;

// Typing event
let typing = false;
let timeout = undefined;

input.addEventListener("input", () => {
    if (!typing) {
        typing = true;
        socket.emit("typing", { user: username, status: true });
        timeout = setTimeout(stopTyping, 2000);
    } else {
        clearTimeout(timeout);
        timeout = setTimeout(stopTyping, 2000);
    }
});

function stopTyping() {
    typing = false;
    socket.emit("typing", { user: username, status: false });
}

// Send message
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const msg = input.value.trim();
    if (msg === "") return;

    // Show message locally
    addMessage(msg, "right");

    // Emit to server
    socket.emit("private_message", {
        to: chatUser, // chatUser defined in chat.html template
        msg: msg
    });

    input.value = "";
}

// Receive message
socket.on("message", (data) => {
    if (data.user !== username) {
        addMessage(data.msg, "left");
        notifyMessage(data.user, data.msg);
    }
});

// Typing indicator
socket.on("typing", (data) => {
    if (data.user !== username) {
        typingIndicator.innerText = data.status ? `${data.user} is typing...` : "";
    }
});

// Function to add message to chat
function addMessage(msg, side) {
    const div = document.createElement("div");
    div.classList.add(side === "left" ? "message-left" : "message-right");
    div.innerText = msg;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Notifications
function notifyMessage(from, msg) {
    if (Notification.permission === "granted") {
        new Notification(`New message from ${from}`, { body: msg });
    } else if (Notification.permission !== "denied") {
        Notification.requestPermission();
    }
}

// Image send
const imageInput = document.getElementById("imageInput");
imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const imageData = e.target.result;
        addImage(imageData, "right");
        socket.emit("image_message", { to: chatUser, image: imageData });
    };
    reader.readAsDataURL(file);
});

socket.on("image_message", (data) => {
    if (data.user !== username) addImage(data.image, "left");
});

function addImage(src, side) {
    const img = document.createElement("img");
    img.src = src;
    img.classList.add("chat-image");
    img.style.maxWidth = "200px";
    img.style.borderRadius = "15px";
    img.style.marginBottom = "10px";

    const div = document.createElement("div");
    div.classList.add(side === "left" ? "message-left" : "message-right");
    div.appendChild(img);
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// TODO: File send & voice message similar approach (use FileReader + emit to server)