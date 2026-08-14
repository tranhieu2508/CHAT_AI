import pyodbc
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};SERVER=DESKTOP-CSMBB68;DATABASE=chatdb;Trusted_Connection=yes;'
    )

def query_database(question):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM qa WHERE question LIKE ?", ('%' + question + '%',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Xin lỗi, chưa có dữ liệu phù hợp."

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = query_database(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
