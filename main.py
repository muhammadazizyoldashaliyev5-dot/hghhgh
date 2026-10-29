import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

app = FastAPI(title="SMC / ICT Gemini AI Chart Analyzer")
client = genai.Client(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
Sen SMC va ICT bo'yicha grafik tahlil qiluvchi yordamchisan.
O'zbek tilida aniq va tushunarli javob ber.

Quyidagilarni tekshir:
1. Market Structure: HH, HL, LH, LL.
2. BOS va CHoCH.
3. Liquidity va Liquidity Sweep.
4. Support va Resistance.
5. Fair Value Gap (FVG).
6. Order Block.
7. Bullish va Bearish ssenariylari.
8. Entry, Stop Loss va Take Profit faqat narxlar grafikda aniq
   o'qilsa yoki foydalanuvchi tomonidan berilgan bo'lsa.

Rasmda ko'rinmagan narxlarni o'ylab topma.
Noaniqlik va ssenariy bekor bo'ladigan shartlarni ayt.
Bu ta'limiy tahlil; moliyaviy natija kafolatlanmaydi.
"""

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "provider": "Google Gemini",
        "api_key_configured": bool(API_KEY),
        "model": MODEL,
    }

@app.post("/api/analyze")
async def analyze_chart(file: UploadFile = File(...)):
    if not client:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY .env faylida sozlanmagan. .env faylini tekshiring."
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="PNG, JPG yoki WEBP formatidagi grafik rasmini yuklang."
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Yuklangan rasm bo'sh.")

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Rasm hajmi 10 MB dan oshmasligi kerak."
        )

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=file.content_type,
        )
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                SYSTEM_PROMPT
                + "\n\nYuklangan grafikni SMC/ICT bo'yicha tahlil qil. "
                + "Trend, liquidity sweep, BOS/CHoCH, FVG, order block, "
                + "ehtimoliy yo'nalish va grafikda narxlar aniq ko'rinsa "
                + "entry, Stop Loss va Take Profit haqida yoz.",
                image_part,
            ],
        )
        analysis = getattr(response, "text", None)
        if not analysis:
            raise HTTPException(
                status_code=502,
                detail="Gemini bo'sh javob qaytardi. Boshqa rasm bilan urinib ko'ring."
            )
        return {"success": True, "analysis": analysis}

    except HTTPException:
        raise
    except Exception as exc:
        # Do not expose the API key; SDK errors normally do not contain it.
        message = str(exc)
        raise HTTPException(
            status_code=502,
            detail=f"Gemini AI tahlil xatosi: {message}",
        )

STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def homepage():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "static/index.html topilmadi."}
