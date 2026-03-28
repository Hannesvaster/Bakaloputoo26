const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const exampleButtons = document.querySelectorAll(".example-btn");

const API_URL = "http://127.0.0.1:8000/chat";

function autoResizeTextarea() {
  questionInput.style.height = "auto";
  questionInput.style.height = `${questionInput.scrollHeight}px`;
}

function createMessageRow(text, sender) {
  const row = document.createElement("div");
  row.classList.add("message-row", sender === "user" ? "user-row" : "bot-row");

  const avatar = document.createElement("div");
  avatar.classList.add("avatar", sender === "user" ? "user-avatar" : "bot-avatar");
  avatar.textContent = sender === "user" ? "You" : "AI";

  const message = document.createElement("div");
  message.classList.add("message", sender);
  message.textContent = text;

  if (sender === "user") {
    row.appendChild(message);
    row.appendChild(avatar);
  } else {
    row.appendChild(avatar);
    row.appendChild(message);
  }

  chatBox.appendChild(row);
  chatBox.scrollTop = chatBox.scrollHeight;

  return row;
}

async function sendQuestion(question) {
  createMessageRow(question, "user");
  const loadingRow = createMessageRow("Vastus koostatakse...", "bot");
  loadingRow.querySelector(".message").classList.add("loading");

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      throw new Error("Server tagastas vea.");
    }

    const data = await response.json();
    loadingRow.remove();

    createMessageRow(data.answer, "bot");
  } catch (error) {
    loadingRow.remove();
    createMessageRow("Midagi läks valesti. Kontrolli, kas backend töötab.", "bot");
    console.error(error);
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  autoResizeTextarea();
  await sendQuestion(question);
});

questionInput.addEventListener("input", autoResizeTextarea);

questionInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

exampleButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const question = button.textContent.trim();
    await sendQuestion(question);
  });
});

autoResizeTextarea();