const dialogueInput = document.getElementById("dialougue-input");
const summaryText   = document.getElementById("summary-text");

document.getElementById("dialougue-input").addEventListener("input", () => {
  const txt   = dialogueInput.value.trim();
  const words = txt ? txt.split(/\s+/).length : 0;
  const chars = dialogueInput.value.length;
  const secs  = Math.ceil(words / 3);

  document.getElementById("word-count").textContent = words;
  document.getElementById("char-count").textContent = chars;
  document.getElementById("read-time").textContent  = secs >= 60 ? Math.round(secs / 60) + "m" : secs + "s";
});

async function handleSubmit() {
  const dialogue     = dialogueInput.value.trim();
  const submitButton = document.querySelector(".btn-primary");

  if (!dialogue) {
    summaryText.innerText = "Please enter some text before submitting.";
    return;
  }

  if (dialogue.split(/\s+/).length < 10) {
    summaryText.innerText = "Text is too short. Please enter at least 10 words.";
    return;
  }

  summaryText.innerText        = "Summarizing your text, please wait...";
  submitButton.disabled        = true;
  submitButton.textContent     = "Processing...";

  try {
    const response = await fetch("/summarize/", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ dialogue })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} — ${response.statusText}`);
    }

    const data = await response.json();
    summaryText.innerText = data.summary || "No summary was returned from the server.";

  } catch (err) {
    console.error("Summarization failed:", err);
    summaryText.innerText = `Something went wrong: ${err.message}`;

  } finally {
    submitButton.disabled    = false;
    submitButton.textContent = "✨ Summarize";
  }
}

function clearAll() {
  dialogueInput.value       = "";
  summaryText.innerText     = "Your summary will appear here after you click Summarize...";
  document.getElementById("word-count").textContent = "0";
  document.getElementById("char-count").textContent = "0";
  document.getElementById("read-time").textContent  = "0s";
}

function copyText() {
  const text = summaryText.innerText;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(".copy-btn");
    btn.textContent = "✅ Copied!";
    setTimeout(() => btn.textContent = "📋 Copy", 2000);
  });
}