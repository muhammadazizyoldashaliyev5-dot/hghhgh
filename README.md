# SMC / ICT Gemini AI Chart Analyzer

## Windows PowerShell orqali ishga tushirish

1. ZIP faylni oching va PowerShell'da ushbu papkaga kiring.
2. Virtual muhit yarating va faollashtiring:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Kutubxonalarni o'rnating:

```powershell
python -m pip install -r requirements.txt
```

4. `.env.example` faylini `.env` nomi bilan nusxalang:

```powershell
Copy-Item .env.example .env
notepad .env
```

5. `.env` ichida `GEMINI_API_KEY` qiymatini Google AI Studio kalitingiz bilan almashtiring. Kalitni hech kimga yubormang.

6. Serverni ishga tushiring:

```powershell
python -m uvicorn main:app --reload
```

7. Brauzerda `http://127.0.0.1:8000` ni oching. API tekshiruvi: `http://127.0.0.1:8000/api/health`.

Frontend `static/index.html` ichida. U `/api/analyze` manziliga rasmni yuboradi; backend Gemini orqali tahlil qilib, javobni sahifaga qaytaradi.

Agar `GEMINI_MODEL` hisobingizda mavjud bo'lmasa, Google AI Studio/API model ro'yxatida mavjud model nomini qo'ying. Bepul foydalanish limitlari o'zgarishi mumkin.
