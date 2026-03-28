const chatBox = document.getElementById("chatBox");
const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const exampleButtons = document.querySelectorAll(".example-btn");

const API_URL = "http://127.0.0.1:8000/chat";

function addMessage(text, sender) {
  const message = document.createElement("div");
  message.classList.add("message", sender);
  message.textContent = text;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
  return message;
}

async function sendQuestion(question) {
  addMessage(question, "user");
  const loadingMessage = addMessage("Vastus koostatakse...", "bot");
  loadingMessage.classList.add("loading");

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
    loadingMessage.remove();

    let finalText = data.answer;

    if (data.retrieved_context && data.retrieved_context.length > 0) {
      finalText += `\n\n(Kasutatud kontekst: ${data.retrieved_context.join(", ")})`;
    }

    addMessage(finalText, "bot");
  } catch (error) {
    loadingMessage.remove();
    addMessage("Midagi läks valesti. Kontrolli, kas backend töötab.", "bot");
    console.error(error);
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) return;

  questionInput.value = "";
  await sendQuestion(question);
});

exampleButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const question = button.textContent.trim();
    await sendQuestion(question);
  });
});