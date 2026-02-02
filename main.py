from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Siniestralidad Vial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "backend OK"}

# ===============================
# DATA (SE CARGA UNA SOLA VEZ)
# ===============================
from data_store import DF_VIGENTE, ANIO_ACTUAL

print(f"📊 Registros vigentes cargados: {DF_VIGENTE.shape[0]}")
print(f"📅 Año más reciente: {ANIO_ACTUAL}")

# ===============================
# ROUTERS
# ===============================
from consultas_fijas import router as router_fijas
app.include_router(router_fijas, prefix="/consulta", tags=["Consultas Fijas"])

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
