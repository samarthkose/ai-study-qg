from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException, Form

from .db import SessionLocal, init_db
from .models import Note, Question
from .embed import embed_texts
from .vectorstore import FaissStore
from .qg import generate_from_paragraph  # ✅ real OpenRouter integration

# ------------------- Setup -------------------
load_dotenv()  # Reads the .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()
init_db()
vs = FaissStore(dim=384)

# ------------------- Endpoints -------------------

@app.post("/ingest")
async def ingest_text(text: str = Form(...)):
    """
    Save the note, split into paragraphs, embed them, and store in vectorstore.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    db = SessionLocal()
    note = Note(text=text)
    db.add(note)
    db.commit()
    db.refresh(note)

    # Embed paragraphs and add to vectorstore
    embeds = embed_texts(paragraphs)
    vs.add(embeds)

    db.close()
    return {"note_id": note.id, "paragraph_count": len(paragraphs)}


@app.post("/generate")
async def generate(note_id: int = Form(...), num_questions: int = Form(1)):
    """
    Generate MCQs from a note using OpenRouter.
    """
    db = SessionLocal()
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(404, "note not found")

    paragraphs = [p.strip() for p in note.text.split("\n\n") if p.strip()]
    created = []
    results = []

    for p in paragraphs:
        mcqs = generate_from_paragraph(p, num_questions=num_questions)
        for mcq in mcqs:
            q = Question(
                source_note_id=note.id,
                qtype="mcq",
                prompt=mcq["question"],
                answer=mcq["answer"],
                choices=mcq.get("choices", []),
                explanation=mcq.get("explanation", "")
            )
            db.add(q)
            db.commit()
            db.refresh(q)
            created.append(q.id)
            results.append(mcq)

    db.close()
    return {"created_questions": created, "questions": results}
