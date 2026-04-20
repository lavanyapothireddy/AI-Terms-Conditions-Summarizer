from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load lighter model (better for deployment)
summarizer = pipeline("summarization", model="t5-small")

# Request schema
class TextRequest(BaseModel):
    text: str


# 🔹 Split long text into chunks
def split_text(text, max_words=400):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))
    return chunks


# 🔹 Risk Detection
def detect_risks(text):
    text = text.lower()
    risks = []

    if "third party" in text:
        risks.append("⚠️ Data may be shared with third parties")

    if "no liability" in text or "not responsible" in text:
        risks.append("⚠️ Company is not responsible for damages")

    if "terminate" in text:
        risks.append("⚠️ Your account can be terminated anytime")

    if "collect" in text and "data" in text:
        risks.append("⚠️ Your personal data may be collected")

    if "auto renew" in text or "auto-renew" in text:
        risks.append("⚠️ Subscription may auto-renew")

    if "location" in text or "track" in text:
        risks.append("⚠️ Your activity/location may be tracked")

    if "cookies" in text:
        risks.append("⚠️ Cookies are used to track behavior")

    if "arbitration" in text:
        risks.append("⚠️ You may lose right to go to court")

    if "binding" in text:
        risks.append("⚠️ Terms are legally binding")

    return risks


# 🔹 Risk Level
def get_risk_level(risks):
    score = len(risks)

    if score == 0:
        return "Low"
    elif score <= 3:
        return "Medium"
    else:
        return "High"


# 🔹 API Endpoint
@app.post("/summarize")
def summarize(req: TextRequest):
    if not req.text.strip():
        return {
            "summary": "❌ Please enter some text",
            "risks": [],
            "risk_level": "Low"
        }

    chunks = split_text(req.text)

    summaries = []
    for chunk in chunks:
        result = summarizer(
            chunk,
            max_length=80,
            min_length=25,
            do_sample=False
        )
        summaries.append(result[0]['summary_text'])

    final_summary = " ".join(summaries)

    # Convert to bullet points
    bullets = final_summary.split(". ")
    formatted = "\n".join([f"- {b.strip()}" for b in bullets if b.strip()])

    risks = detect_risks(req.text)
    risk_level = get_risk_level(risks)

    return {
        "summary": formatted,
        "risks": risks if risks else ["✅ No major risks detected"],
        "risk_level": risk_level
    }
