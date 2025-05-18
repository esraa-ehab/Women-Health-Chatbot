from PyPDF2 import PdfReader

def load_pdf_chunks(file_path, chunk_size=500):
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""
    chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    return chunks

pdf_chunks = load_pdf_chunks("womens_health_book.pdf")


import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def get_embedding(text):
    model = "models/text-embedding-004"
    response = genai.embed_content(
        model=model,
        content=text,
        task_type="retrieval_document"
    )
    return response['embedding']

embedding_data = []
for chunk in pdf_chunks:
    vector = get_embedding(chunk)
    embedding_data.append({"text": chunk, "embedding": vector})


import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(anonymized_telemetry=False))
collection = client.create_collection(name="womens_health")

for idx, item in enumerate(embedding_data):
    collection.add(
        documents=[item["text"]],
        embeddings=[item["embedding"]],
        ids=[str(idx)]
    )


def handle_small_talk(prompt):
    small_talk_responses = {
        "hi": "Hello! How can I help you today?",
        "hello": "Hi there! How can I assist you?",
        "how are you": "I'm just a chatbot, but I'm here and ready to help!",
        "good morning": "Good morning! How can I assist you today?",
        "good evening": "Good evening! Feel free to ask me anything.",
        "thanks": "You're welcome!",
        "thank you": "You're welcome!",
        "bye": "Goodbye! Take care.",
    }

    prompt_clean = prompt.lower().strip()
    return small_talk_responses.get(prompt_clean)


def ask_question(question, top_k=3):
    small_talk = handle_small_talk(question)
    if small_talk:
        return small_talk

    results = collection.query(
        query_embeddings=[get_embedding(question)],
        n_results=top_k
    )
    context = "\n\n".join(results["documents"][0])

    prompt = f"""
    You are a helpful and friendly women's health assistant.
    Use the following information to answer health-related questions.
    If the user's message is a greeting or casual, respond appropriately.

    Context:
    {context}

    User: {question}
    """
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text