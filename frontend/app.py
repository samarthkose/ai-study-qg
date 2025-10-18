import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

API_URL = "http://127.0.0.1:8000"

st.title("🧠 AI Study Question Generator")

# --- Step 1: Input Notes ---
st.header("Step 1: Paste your notes")
text_input = st.text_area("Paste your notes or lecture material here", height=200)

if st.button("Ingest Notes"):
    if not text_input.strip():
        st.warning("Please paste some text first.")
    else:
        resp = requests.post(f"{API_URL}/ingest", data={"text": text_input})
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.note_id = data["note_id"]
            st.session_state.paragraphs = [p.strip() for p in text_input.split("\n\n") if p.strip()]
            st.session_state.questions = []  # reset previous questions
            st.success(f"✅ Note ingested! Paragraphs: {data['paragraph_count']}")
        else:
            st.error("Failed to ingest notes.")

# --- Step 2: Generate Questions ---
st.header("Step 2: Generate Questions")
num_questions = st.slider("Questions per paragraph", 1, 5, 1)

if "note_id" in st.session_state:
    if st.button("Generate Questions"):
        note_id = st.session_state.note_id
        with st.spinner("Generating questions... please wait ⏳"):
            resp = requests.post(
                f"{API_URL}/generate",
                data={"note_id": note_id, "num_questions": num_questions}
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.questions = data.get("questions", [])
            st.success(f"Generated {len(st.session_state.questions)} questions!")
        else:
            st.error("Error generating questions.")

# --- Step 3: Display Questions with Reroll ---
if st.session_state.get("questions"):
    for i, q in enumerate(st.session_state.questions, start=1):
        st.markdown(f"### Question {i}")
        st.write(q["question"])
        st.write("**Choices:**")
        for c in q["choices"]:
            st.write(f"- {c}")
        st.info(f"**Answer:** {q['answer']}")

        # ✅ Display explanation
        if "explanation" in q and q["explanation"]:
            st.write(f"💡 Explanation: {q['explanation']}")

        # Reroll button
        if st.button(f"🔄 Reroll Question {i}"):
            paragraph_index = i - 1
            paragraph_text = st.session_state.paragraphs[paragraph_index % len(st.session_state.paragraphs)]
            reroll_resp = requests.post(
                f"{API_URL}/generate",
                data={"note_id": st.session_state.note_id, "num_questions": 1}
            )
            if reroll_resp.status_code == 200:
                new_q = reroll_resp.json()["questions"][0]
                st.session_state.questions[i-1] = new_q
                st.experimental_rerun()
            else:
                st.error("Error rerolling question.")

# --- Step 4: Download PDF with improved formatting and auto-wrapping ---
if st.session_state.get("questions"):
    if st.button("📥 Download Questions as PDF"):
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from io import BytesIO

        def draw_wrapped_text(pdf, text, x, y, max_width, font_name="Helvetica", font_size=10, leading=12):
            pdf.setFont(font_name, font_size)
            words = text.split()
            line = ""
            for word in words:
                # Check if adding this word exceeds max_width
                if pdf.stringWidth(line + " " + word, font_name, font_size) <= max_width:
                    line = line + " " + word if line else word
                else:
                    pdf.drawString(x, y, line)
                    y -= leading
                    line = word
            if line:
                pdf.drawString(x, y, line)
                y -= leading
            return y

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y = height - 50  # start near top
        max_width = width - 100  # 50 margin each side
        leading = 12

        for i, q in enumerate(st.session_state.questions, start=1):
            # --- Question ---
            y = draw_wrapped_text(pdf, f"Q{i}: {q['question']}", 50, y, max_width, font_name="Helvetica-Bold", font_size=12, leading=leading)

            # --- Choices ---
            for choice in q["choices"]:
                y = draw_wrapped_text(pdf, f"• {choice}", 70, y, max_width, font_name="Helvetica", font_size=11, leading=leading)

            # --- Answer ---
            y = draw_wrapped_text(pdf, f"Answer: {q['answer']}", 70, y, max_width, font_name="Helvetica-Oblique", font_size=10, leading=leading)

            # --- Explanation ---
            if q.get("explanation"):
                y = draw_wrapped_text(pdf, f"Explanation: {q['explanation']}", 70, y, max_width, font_name="Helvetica", font_size=10, leading=leading)

            # Extra spacing for readability
            y -= 10

            # Page break
            if y < 50:
                pdf.showPage()
                y = height - 50

        pdf.save()
        buffer.seek(0)
        st.download_button(
            label="Download PDF",
            data=buffer,
            file_name="quiz.pdf",
            mime="application/pdf"
        )
