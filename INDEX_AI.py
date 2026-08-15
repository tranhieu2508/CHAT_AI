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
VECTOR_DIM = 384

# Khởi tạo FAISS Index và mảng lưu thông tin
index = faiss.IndexFlatL2(VECTOR_DIM)
questions = []
answers = []

def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};SERVER=DESKTOP-CSMBB68;DATABASE=chatdb;Trusted_Connection=yes;'
    )

# Nạp dữ liệu từ KnowledgeBase
def load_data():
    global index, questions, answers
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT question_variants, answer FROM KnowledgeBase WHERE status='ACTIVE'")
        data = cursor.fetchall()
        conn.close()

        questions, answers = [], []
        for row in data:
            variants = row[0].split('|')
            for q in variants:
                questions.append(q.strip())
                answers.append(row[1])

        index.reset()
        if questions:
            texts_to_embed = [f"Hỏi: {q} - Trả lời: {a}" for q, a in zip(questions, answers)]
            embeddings = model.encode(texts_to_embed)
            embeddings = np.array(embeddings).astype('float32')
            index.add(embeddings)
            print(f"✅ Đã nạp {len(questions)} biến thể câu hỏi vào FAISS Index!")
        else:
            print("⚠️ KnowledgeBase trống.")
    except Exception as e:
        print(f"❌ Lỗi kết nối SQL Server: {e}")

# Nạp dữ liệu lần đầu
load_data()

def query_database(user_question):
    if index.ntotal == 0:
        return "Xin lỗi, hiện tại chưa có dữ liệu trong hệ thống."

    query_vec = model.encode([user_question])
    query_vec = np.array(query_vec).astype('float32')
    D, I = index.search(query_vec, k=1)

    distance = D[0][0]
    best_match_idx = I[0][0]
    MAX_DISTANCE_THRESHOLD = 20.0

    if best_match_idx != -1 and distance < MAX_DISTANCE_THRESHOLD:
        return answers[best_match_idx]
    else:
        # Ghi nhận câu hỏi chưa có vào Tickets
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Tickets (user_id, question) VALUES (?, ?)", ("unknown", user_question))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Lỗi ghi vào Tickets: {e}")
        return "Xin lỗi, quy định này chưa có trong hệ thống. Thắc mắc của bạn đã được ghi nhận!"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Vui lòng nhập câu hỏi!"}), 400

    reply = query_database(user_message)
    return jsonify({"reply": reply})

@app.route("/reload", methods=["GET"])
def reload_db():
    load_data()
    return jsonify({"status": "success", "message": f"Đã nạp lại {index.ntotal} câu hỏi vào FAISS!"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
