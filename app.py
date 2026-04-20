from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str


def summarize_text(text):
    sentences = text.split(".")
    return sentences[:5]


def detect_risks(text):
    t = text.lower()
    risks = []

    if "third party" in t:
        risks.append("Data may be shared with third parties")
    if "terminate" in t:
        risks.append("Account can be terminated anytime")
    if "collect" in t and "data" in t:
        risks.append("Personal data may be collected")
    if "auto renew" in t:
        risks.append("Subscription may auto-renew")
    if "cookies" in t:
        risks.append("Cookies track your activity")

    return risks


def get_level(risks):
    if len(risks) == 0:
        return "Low"
    elif len(risks) <= 3:
        return "Medium"
    else:
        return "High"


@app.get("/")
def home():
    return {"message": "API running"}


@app.post("/summarize")
def summarize(req: TextRequest):
    try:
        if not req.text.strip():
            return {"summary": "No input", "risks": [], "risk_level": "Low"}

        points = summarize_text(req.text)
        summary = "\n".join(f"- {p.strip()}" for p in points if p.strip())

        risks = detect_risks(req.text)

        return {
            "summary": summary,
            "risks": risks if risks else ["No major risks"],
            "risk_level": get_level(risks)
        }

    except Exception as e:
        return {"error": str(e)}
