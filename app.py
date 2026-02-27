import streamlit as st
import fitz  # PyMuPDF
import time
from ai_functions import summarize_notes, generate_flashcards, client

# --- Page Config ---
st.set_page_config(page_title="AI Study Buddy", layout="wide")

# --- Custom Styling (FIXED) ---
st.markdown("""
<style>

/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
}

/* Main content box */
.block-container {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 15px;
}

/* Fix all text colors */
h1, h2, h3, p, label, div {
    color: #2c3e50 !important;
}

/* Title styling */
.title {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
    color: #2c3e50;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #36D1DC, #5B86E5);
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 16px;
}
/* Change upload button color */
div.stFileUploader button {
    background-color: #4CAF50;
    color: white;
    border-radius: 8px;
}

/* Cards */
.card {
    background: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    margin-top: 10px;
}

/* Fix text area */
textarea {
    background-color: white !important;
    color: black !important;
}
/* Fix cursor color */
textarea, input {
    caret-color: black !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4facfe, #00f2fe);
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<div class='title'></div>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;font-size: 70px;'>🤖 AI Study Buddy 📚 </h4>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'> ✨ Learn Smart | Revise Fast | Score Better ✨</h4>", unsafe_allow_html=True)
st.markdown("---")

# --- PDF Extraction ---
def extract_text_from_pdf(uploaded_file):
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- Sidebar Input ---
notes_text = ""

with st.sidebar:
    st.header("📥 Input Material")

    input_method = st.radio("Choose Method:", ["Paste Text", "Upload File"])

    if input_method == "Paste Text":
        notes_text = st.text_area("✍️ Paste your notes:", height=250)

    else:
        uploaded_file = st.file_uploader("📄 Upload PDF or TXT", type=["pdf", "txt"])

        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                notes_text = extract_text_from_pdf(uploaded_file)
                if notes_text:
                    st.success("PDF loaded ✅")

            elif uploaded_file.type == "text/plain":
                notes_text = uploaded_file.read().decode("utf-8")
                st.success("Text file loaded ✅")

    # --- Timer ---
    st.markdown("---")
    st.subheader("⏱️ Study Timer")

    minutes = st.slider("Set minutes", 1, 60, 25)

    if st.button("Start Timer"):
        timer_placeholder = st.empty()

        for i in range(minutes * 60, 0, -1):
            mins, secs = divmod(i, 60)
            timer_placeholder.write(f"⏳ {mins:02d}:{secs:02d}")
            time.sleep(1)

        st.success("🎉 Time's up! Take a break ☕")

# --- MAIN UI ---
if not notes_text:
    st.info("👈 Add your notes from sidebar to start studying!")
    st.markdown("""
    ### 🤖 Features of this App:
    - 📝 Generate summaries  
    - 🗂 Create flashcards  
    - 🎯 Practice quizzes  
    - 🧠 Extract key concepts  
    - 📊 Track your study progress  
    """)

else:
    st.header("📊 Study Tools")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Summary 🤖",
        "🗂 Flashcards 📚",
        "🎯 Quiz 🎮",
        "🧠 Concepts 💡"
    ])

    # --- SUMMARY ---
    with tab1:
        st.subheader("Summary & Study Plan")

        if st.button("Generate Summary"):
            with st.spinner("🤖 Generating summary..."):
                try:
                    result = summarize_notes(notes_text)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button("⬇ Download Summary", result)
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- FLASHCARDS ---
    with tab2:
        st.subheader("Flashcards")

        count = st.slider("Number of cards", 5, 20, 10)

        if st.button("Generate Flashcards"):
            with st.spinner("🤖 Creating flashcards..."):
                try:
                    flashcards = generate_flashcards(notes_text, count=count)

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(flashcards)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.download_button("⬇ Download Flashcards", flashcards)
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- QUIZ ---
    with tab3:
        st.subheader("Practice Quiz")

        if st.button("Generate Quiz"):
            with st.spinner("🤖 Generating quiz..."):
                try:
                    prompt = f"""
Create 5 multiple choice questions from the text.

Format:
Q1.
A)
B)
C)
D)
Answer:

Text:
{notes_text}
"""

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {e}")

    # --- CONCEPTS ---
    with tab4:
        st.subheader("Key Concepts")

        if st.button("Extract Concepts"):
            with st.spinner("🤖 Analyzing..."):
                try:
                    prompt = f"Extract key concepts from this:\n{notes_text}"

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error: {e}")

    # --- BOOKMARK ---
    st.markdown("---")
    st.subheader("📌 Bookmark Important Notes")

    bookmark = st.text_area("Write key points:")

    if st.button("Save Bookmark"):
        st.session_state["bookmark"] = bookmark
        st.success("Saved! ✅")

    if "bookmark" in st.session_state:
        st.info(st.session_state["bookmark"])

    # --- PROGRESS ---
    st.markdown("---")
    st.subheader("📊 Study Progress")

    progress = st.slider("Completion %", 0, 100, 20)
    st.progress(progress)

    if progress == 100:
        st.balloons()
        st.success("🎉 Excellent! You completed your study!")