# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# ===============================
# APP
# ===============================
app = FastAPI(title="API Siniestralidad Vial")

# ===============================
# MIDDLEWARE CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Iniciando backend...")

# ===============================
# FRONTEND
# ===============================
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


# ===============================
# DATA (SE CARGA UNA SOLA VEZ)
# ===============================
# Este import ejecuta la carga del CSV una sola vez
from data_store import DF_VIGENTE, ANIO_ACTUAL

print(f"📊 Registros vigentes cargados: {DF_VIGENTE.shape[0]}")
print(f"📅 Año más reciente: {ANIO_ACTUAL}")


# ===============================
# ROUTERS
# ===============================
from consultas_fijas import router as router_fijas
#from consultas_natural import router as router_natural

app.include_router(router_fijas, prefix="/consulta", tags=["Consultas Fijas"])
#app.include_router(router_natural, prefix="/consulta", tags=["Consulta Natural"])


# ===============================
# HEALTHCHECK
# ===============================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "filas_vigentes": int(DF_VIGENTE.shape[0]),
        "anio_actual": ANIO_ACTUAL
    }
