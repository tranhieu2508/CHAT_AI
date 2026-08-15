## Cách chạy dự án
1. Cài Python (>=3.9).
2. Cài SQL Server + ODBC Driver.
3. Mở SQL Server Management Studio, chạy file `chatdb_setup.sql` để tạo database `chatdb`.
4. Chỉnh lại connection string trong `INDEX_AI.py` nếu cần.
5. Cài thư viện cần thiết:
   ```bash
   pip install flask flask-cors pyodbc sentence-transformers faiss-cpu numpy

