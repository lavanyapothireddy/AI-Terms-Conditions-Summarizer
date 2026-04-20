from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline

app = FastAPI()

# CORS (allow all)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Lazy load model (important for Render)
summarizer = None

def get_model():
    global summarizer
    if summarizer is None:
        summarizer = pipeline(
            "summarization",
            model="t5-small",
            device=-1
        )
    return summarizer


# Request schema
class TextRequest(BaseModel):
    text: str


# 🔹 Split long text
def split_text(text, max_words=400):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


# 🔹 Risk detection
def detect_risks(text):
    text = text.lower()
    risks = []

    if "third party" in text:
        risks.append("⚠️ Data may be shared with third parties")
    if "terminate" in text:
        risks.append("⚠️ Account can be terminated anytime")
    if "collect" in text and "data" in text:
        risks.append("⚠️ Personal data may be collected")
    if "auto renew" in text or "auto-renew" in text:
        risks.append("⚠️ Subscription may auto-renew")
    if "cookies" in text:
        risks.append("⚠️ Cookies are used to track activity")
    if "arbitration" in text:
        risks.append("⚠️ You may lose right to go to court")

    return risks


# 🔹 Risk level
def get_risk_level(risks):
    if len(risks) == 0:
        return "Low"
    elif len(risks) <= 3:
        return "Medium"
    else:
        return "High"


# Home route
@app.get("/")
def home():
    return {"message": "API is running 🚀"}


# 🔹 Main API
@app.post("/summarize")
def summarize(req: TextRequest):
    if not req.text.strip():
        return {
            "summary": "❌ Please enter some text",
            "risks": [],
            "risk_level": "Low"
        }

    model = get_model()

    chunks = split_text(req.text)
    summaries = []

    for chunk in chunks:
        result = model(
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

    return {
        "summary": formatted,
        "risks": risks if risks else ["✅ No major risks detected"],
        "risk_level": get_risk_level(risks)
    }
