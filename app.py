from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer
from pathlib import Path
import torch
import re
import os

app = FastAPI(
    title="Text Summarizer App",
    description="Text Summarizer using T5",
    version="1.0"
)

app.mount("/static", StaticFiles(directory="."), name="static")

# MODEL_PATH = Path(__file__).parent / ".saved_summary_model_model"

# model = T5ForConditionalGeneration.from_pretrained(str(MODEL_PATH), local_files_only=True)
# tokenizer = T5Tokenizer.from_pretrained(str(MODEL_PATH), local_files_only=True)


# MODEL_NAME = "ankitkumaer123/text-summarizer"

# model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

# tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
model = None
tokenizer = None

if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

print("Using Device:", device)

def load_model():
    global model, tokenizer

    if model is None:
        model = T5ForConditionalGeneration.from_pretrained(
            "ankitkumaer123/text-summarizer"
        )

        tokenizer = T5Tokenizer.from_pretrained(
            "ankitkumaer123/text-summarizer"
        )

        model.to(device)
        model.eval()
class DialogueInput(BaseModel):
    dialogue: str

def clean_data(text: str) -> str:
    text = re.sub(r"\r\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    return text.strip()

def summarize_dialogue(dialogue: str) -> str:
    load_model()
    dialogue = clean_data(dialogue)
    dialogue = "summarize: " + dialogue

    inputs = tokenizer(
        dialogue,
        padding="max_length",
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            num_beams=4,
            max_length=150,
            min_length=30,
            repetition_penalty=2.5,
            length_penalty=1.0,
            early_stopping=True,
            no_repeat_ngram_size=3
        )

    summary = tokenizer.decode(
        output[0],
        skip_special_tokens=True,
        clean_up_tokenization_spaces=True
    )

    return summary

@app.post("/summarize/")
async def summarize(data: DialogueInput):
    try:
        
        summary = summarize_dialogue(data.dialogue)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def home():
    if not os.path.exists("index.html"):
        raise HTTPException(status_code=404, detail="index.html not found")
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()