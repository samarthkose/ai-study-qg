from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    source = Column(String, default="paste")
    text = Column(Text)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    source_note_id = Column(Integer, ForeignKey("notes.id"))
    qtype = Column(String)  # mcq, short, cloze
    prompt = Column(Text)
    answer = Column(Text)
    choices = Column(JSON, nullable=True)
    explanation = Column(Text, default="")  # <-- Added this line
    tags = Column(JSON, nullable=True)
    difficulty = Column(String, default="medium")
    embedding_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    ease = Column(Float, default=2.5)
    interval = Column(Integer, default=0)
    repetition = Column(Integer, default=0)
    due = Column(DateTime, nullable=True)
    last_score = Column(Integer, default=0)
