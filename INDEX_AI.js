async function sendMessage() {
  const input = document.getElementById("userInput").value;

  document.querySelector(".chat-body").innerHTML +=
    `<div class="message user">${input}</div>`;

  const response = await fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: input })
  });

  const data = await response.json();

  document.querySelector(".chat-body").innerHTML +=
    `<div class="message bot"><i class="fa-solid fa-computer"></i> ${data.reply}</div>`;

  document.getElementById("userInput").value = "";
}
