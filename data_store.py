import pandas as pd
from pathlib import Path
import unicodedata

# ===============================
# UTILIDAD
# ===============================
def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return texto
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto


# ===============================
# RUTAS
# ===============================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
CSV_PATH = DATA_DIR / "MLrefinado.csv"

print("📂 Cargando CSV desde:", CSV_PATH)

# ===============================
# CARGA CSV (UNA SOLA VEZ)
# ===============================
df = pd.read_csv(CSV_PATH, low_memory=False)

# ===============================
# NORMALIZACIONES
# ===============================
df["FechaHecho"] = pd.to_datetime(df["FechaHecho"], errors="coerce")
df["FechaVersion"] = pd.to_datetime(df["FechaVersion"], errors="coerce")

for col in ["Departamento", "Municipio", "Zona", "EstadoVictima"]:
    if col in df.columns:
        df[col] = df[col].apply(normalizar)

# ===============================
# VARIABLES GLOBALES
# ===============================
FECHA_MAX = df["FechaVersion"].max()
ULTIMO_MES_VERSION = FECHA_MAX.month
ANIO_ACTUAL = int(df["AnoHecho"].max())

# ===============================
# DATAFRAME VIGENTE
# ===============================
#DF_VIGENTE = df[
 #   (df["EsVersionFinal"] == 0) &
  #  (df["MesVersion"] == ULTIMO_MES_VERSION)
#]
DF_VIGENTE = df.copy()


print("✅ DataFrame vigente cargado")
print("📊 Filas:", DF_VIGENTE.shape[0])
print("📅 Año actual:", ANIO_ACTUAL)
