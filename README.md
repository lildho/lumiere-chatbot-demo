# Lumière Clinic — AI Agent Chatbot


---

## Struktur Proyek

```
beauty_clinic_agent/
├── backend/
│   ├── main.py              ← Kode backend utama (FastAPI)
│   ├── requirements.txt     ← Daftar library Python
│   └── .env.example         ← Template konfigurasi
├── frontend/
│   └── index.html           ← Widget chatbot + halaman demo
└── SYSTEM_PROMPT.md         ← Instruksi inti AI Agent
```

---

## 🚀 Cara Menjalankan Backend

### 1. Siapkan Python Environment
```bash
# Pastikan Python 3.10+ terinstall
python --version

# Buat virtual environment (sangat disarankan)
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi API Key
```bash
# Salin file konfigurasi
cp .env.example .env

# Edit file .env dan isi API Key OpenAI Anda
# OPENAI_API_KEY=sk-proj-xxxxx
```

### 3. Jalankan Server
```bash
uvicorn main:app --reload --port 8000
```

Server berjalan di: http://localhost:8000
Dokumentasi API otomatis: http://localhost:8000/docs

---

## 🌐 Cara Memasang Widget di Website

### Opsi A: Standalone (untuk testing)
Cukup buka file `frontend/index.html` di browser.

### Opsi B: Embed ke website yang sudah ada
Salin kode berikut sebelum tag `</body>` di halaman website Anda:

```html
<!-- 1. Paste CSS di dalam <head> -->
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">

<!-- 2. Paste seluruh <style>...</style> dari index.html ke <head> website Anda -->
<!-- 3. Paste elemen #chat-trigger dan #chat-window ke <body> website Anda -->
<!-- 4. Paste blok <script>...</script> sebelum </body> -->
<!-- 5. Ubah CONFIG.BACKEND_URL di JS menjadi URL server production Anda -->
```

---

## 🔌 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/` | Health check |
| POST | `/chat` | Kirim pesan, terima respons AI |
| GET | `/appointments` | Lihat semua booking (admin) |
| GET | `/appointments/{id}` | Detail satu booking |
| DELETE | `/conversations/{session_id}` | Reset sesi chat |

### Contoh Request `/chat`:
```json
POST http://localhost:8000/chat
Content-Type: application/json

{
  "session_id": "sess_1234567890_abc123",
  "message": "Halo, saya ingin tanya soal facial"
}
```

### Contoh Response:
```json
{
  "success": true,
  "session_id": "sess_1234567890_abc123",
  "response": "Halo Kak! Tentu, Lumière Clinic menyediakan..."
}
```

---

## ☁️ Deploy ke Production

### Rekomendasi Stack:
- **Backend**: Railway.app atau Render.com (gratis untuk mulai)
- **Frontend**: Netlify atau Vercel (gratis, cukup drag & drop folder frontend)
- **Database**: Supabase (PostgreSQL, gratis) — untuk gantikan in-memory storage

### Langkah Deploy Backend ke Railway:
1. Buat akun di railway.app
2. New Project → Deploy from GitHub
3. Set Environment Variable: `OPENAI_API_KEY`
4. Railway akan otomatis detect FastAPI dan deploy
5. Salin URL yang diberikan Railway (contoh: `https://lumiere-api.up.railway.app`)
6. Update `CONFIG.BACKEND_URL` di `index.html` dengan URL tersebut

---

## ⚠️ Catatan Penting untuk Production

1. **Tambahkan autentikasi** pada endpoint `/appointments` agar tidak bisa diakses publik
2. **Ganti in-memory storage** (`appointments_db`) dengan database nyata (PostgreSQL + SQLAlchemy)
3. **Batasi CORS** — ganti `allow_origins=["*"]` dengan domain website Anda
4. **Rate limiting** — tambahkan `slowapi` untuk mencegah spam
5. **Enkripsi session** — pertimbangkan Redis untuk session management yang lebih aman

---

## 📞 Dukungan

Untuk pertanyaan teknis, hubungi tim pengembang Anda atau lihat:
- Dokumentasi OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- Dokumentasi FastAPI: https://fastapi.tiangolo.com
