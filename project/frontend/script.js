const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const exampleButtons = document.querySelectorAll(".example-btn");

const API_URL = "/chat";

function autoResizeTextarea() {
  questionInput.style.height = "auto";
  questionInput.style.height = `${questionInput.scrollHeight}px`;
}

function createMessageRow(sender, text, sources = []) {
  const row = document.createElement("div");
  row.classList.add("message-row", sender === "user" ? "user-row" : "bot-row");

  const avatar = document.createElement("div");
  avatar.classList.add("avatar", sender === "user" ? "user-avatar" : "bot-avatar");
  avatar.textContent = sender === "user" ? "You" : "AI";

  const message = document.createElement("div");
  message.classList.add("message", sender);

  const textBlock = document.createElement("div");
  textBlock.classList.add("message-text");
  textBlock.textContent = text;
  message.appendChild(textBlock);

  if (sender === "bot" && sources.length > 0) {
    const sourcesBlock = document.createElement("div");
    sourcesBlock.classList.add("sources");
    sourcesBlock.innerHTML = "<strong>Kasutatud kontekst:</strong>";

    sources.forEach((source) => {
      const tag = document.createElement("span");
      tag.classList.add("source-tag");
      tag.textContent = source;
      sourcesBlock.appendChild(tag);
    });

    message.appendChild(sourcesBlock);
  }

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
  createMessageRow("user", question);
  const loadingRow = createMessageRow("bot", "Vastus koostatakse...");
  loadingRow.querySelector(".message-text").classList.add("loading");

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

    createMessageRow("bot", data.answer, data.retrieved_context || []);
  } catch (error) {
    loadingRow.remove();
    createMessageRow("bot", "Midagi läks valesti. Kontrolli, kas backend töötab.");
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