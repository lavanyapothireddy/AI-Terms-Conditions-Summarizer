from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Request schema
class TextRequest(BaseModel):
    text: str

# Risk Detection Function
def detect_risks(text):
    risks = []
    text = text.lower()

    if "third party" in text:
        risks.append("⚠️ Data may be shared with third parties")

    if "no liability" in text or "not responsible" in text:
        risks.append("⚠️ Company is not responsible for damages")

    if "terminate" in text:
        risks.append("⚠️ Your account can be terminated anytime")

    if "collect" in text and "data" in text:
        risks.append("⚠️ Your personal data may be collected")

    return risks

# Risk Level Function
def get_risk_level(risks):
    score = len(risks)

    if score == 0:
        return "Low"
    elif score <= 2:
        return "Medium"
    else:
        return "High"

# API Endpoint
@app.post("/summarize")
def summarize(req: TextRequest):
    result = summarizer(
        req.text,
        max_length=100,
        min_length=30,
        do_sample=False
    )

    summary = result[0]['summary_text']

    # Convert to bullet points
    bullets = summary.split(". ")
    formatted = "\n".join([f"- {point.strip()}" for point in bullets if point])

    risks = detect_risks(req.text)
    risk_level = get_risk_level(risks)

    return {
        "summary": formatted,
        "risks": risks if risks else ["✅ No major risks detected"],
        "risk_level": risk_level
    }
    summarizer = None

@app.on_event("startup")
def load_model():
    global summarizer
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
