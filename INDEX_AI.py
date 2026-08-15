import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

app = Flask(__name__)
CORS(app)

# Load model tạo embedding
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Kết nối SQL và load dữ liệu QA
def load_data():
    conn = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=DESKTOP-CSMBB68;DATABASE=chatdb;Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM qa")
    data = cursor.fetchall()
    conn.close()
    questions = [row[0] for row in data]
    answers = [row[1] for row in data]
    return questions, answers

questions, answers = load_data()

if not questions:
    print("⚠️ Không có dữ liệu trong bảng qa!")
    embeddings = np.empty((0, 384), dtype='float32')
else:
    # Tạo vector cho toàn bộ câu hỏi
    embeddings = model.encode(questions)
    embeddings = np.array(embeddings).astype('float32')

index = faiss.IndexFlatL2(embeddings.shape[1])
if embeddings.shape[0] > 0:
    index.add(embeddings)

def query_database(question):
    if embeddings.shape[0] == 0:
        return "Xin lỗi, chưa có dữ liệu trong hệ thống."
    query_vec = model.encode([question])
    query_vec = np.array(query_vec).astype('float32')
    D, I = index.search(query_vec, k=1)
    return answers[I[0][0]]

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = query_database(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

