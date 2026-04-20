document.getElementById("scanBtn").addEventListener("click", scan);

async function scan() {
  const summary = document.getElementById("summary");
  const risks = document.getElementById("risks");
  const level = document.getElementById("level");

  summary.innerText = "Extracting page content...";
  risks.innerText = "";
  level.innerText = "";

  try {
    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.scripting.executeScript(
      {
        target: { tabId: tab.id },
        func: () => document.body.innerText.slice(0, 5000),
      },
      async (results) => {
        if (chrome.runtime.lastError) {
          summary.innerText = "Error: " + chrome.runtime.lastError.message;
          return;
        }

        if (!results || !results[0]) {
          summary.innerText = "No content found";
          return;
        }

        const text = results[0].result;

        summary.innerText = "Analyzing...";

        try {
          const response = await fetch(
            "https://ai-terms-conditions-summarizer.onrender.com/summarize",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ text: text })
            }
          );

          if (!response.ok) {
            summary.innerText = "Server error";
            return;
          }

          const data = await response.json();

          summary.innerText = data.summary;
          risks.innerText = data.risks.join("\n");
          level.innerText = data.risk_level;

        } catch (err) {
          summary.innerText = "API connection failed";
        }
      }
    );

  } catch (err) {
    summary.innerText = "Extension error";
  }
}
