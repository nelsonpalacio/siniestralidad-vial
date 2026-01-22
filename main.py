from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

app = FastAPI()  # Define app primero

# CORS: permite que frontend acceda a backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # para desarrollo, permitir todo
    allow_methods=["*"],
    allow_headers=["*"],
)




# Montar carpeta frontend como estática
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")

# Ruta para servir el index.html en la raíz
@app.get("/")
def serve_index():
    return FileResponse(frontend_path / "index.html")

print("🚀 Iniciando backend...")

# ===============================
# RUTAS BASE
# ===============================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
CSV_PATH = DATA_DIR / "MLrefinado.csv"

print("📂 Buscando CSV en:", CSV_PATH)

# ===============================
# CARGA DE DATOS
# ===============================
try:
    df = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"📊 Datos cargados en memoria: {df.shape[0]} filas, {df.shape[1]} columnas")
except FileNotFoundError:
    print("❌ ERROR: No se encontró el archivo MLrefinado.csv en /datos")
    raise

# ===============================
# CARGA FESTIVOS
# ===============================
FESTIVOS_PATH = DATA_DIR / "festivos_colombia.csv"

try:
    df_festivos = pd.read_csv(FESTIVOS_PATH, sep=";")
    df_festivos["Fecha"] = pd.to_datetime(
        df_festivos["Fecha"],
        dayfirst=True,
        errors="coerce"
    )
    print(f"📅 Festivos cargados: {df_festivos.shape[0]}")
except FileNotFoundError:
    print("❌ ERROR: No se encontró festivos_colombia.csv en /datos")
    raise

# ===============================
# NORMALIZACIÓN FECHAS
# ===============================
df["FechaHecho"] = pd.to_datetime(df["FechaHecho"], errors="coerce")
print("📆 FechaHecho convertida a datetime")

# ===============================
# NORMALIZACIÓN DE DATOS
# ===============================
df["FechaVersion"] = pd.to_datetime(df["FechaVersion"], errors="coerce")

COLUMNAS_TXT = ["Departamento", "Municipio", "EstadoVictima", "Zona"]
for col in COLUMNAS_TXT:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.upper()
        )

# ===============================
# VARIABLES DERIVADAS GLOBALES
# ===============================
FECHA_MAX = df["FechaVersion"].max()
ULTIMO_MES_VERSION = FECHA_MAX.month
ANIO_ACTUAL = int(df["AnoHecho"].max())

DF_VIGENTE = df[
    (df["EsVersionFinal"] == 0) &
    (df["MesVersion"] == ULTIMO_MES_VERSION)
]

print("✅ Datos normalizados y versión vigente calculada")

# ===============================
# ENDPOINT RAÍZ
# ===============================
@app.get("/")
def root():
    return {
        "mensaje": "API de Siniestralidad Vial activa",
        "filas": int(df.shape[0]),
        "columnas": int(df.shape[1]),
        "anio_actual": ANIO_ACTUAL
    }
# =====================
# Q01 – TOTAL ÚLTIMOS 3 AÑOS
# =====================
@app.get("/consulta/Q01")
def q01_total_ultimos_3_anios():

    anios = (
        DF_VIGENTE["AnoHecho"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
    )[-3:]

    resultado = {}
    for anio in anios:
        total = DF_VIGENTE[DF_VIGENTE["AnoHecho"] == anio].shape[0]
        resultado[str(anio)] = int(total)

    return resultado

# =====================
# Q02 – ESTADO ÚLTIMO AÑO
# =====================
@app.get("/consulta/Q02")
def q02_estado_ultimo_anio():
    total = DF_VIGENTE[DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL].shape[0]

    return {
        "anio": ANIO_ACTUAL,
        "total_victimas": int(total)
    }

# =====================
# Q03 – COMPARACIÓN AÑOS
# =====================
@app.get("/consulta/Q03")
def q03_comparacion_anios():

    anios = sorted(DF_VIGENTE["AnoHecho"].dropna().unique())
    anio_anterior = int(anios[-2])
    anio_actual = int(anios[-1])

    def contar(anio, estado):
        return int(DF_VIGENTE[
            (DF_VIGENTE["AnoHecho"] == anio) &
            (DF_VIGENTE["EstadoVictima"] == estado)
        ].shape[0])

    return {
        "anio_anterior": anio_anterior,
        "anio_actual": anio_actual,
        "muertos_anterior": contar(anio_anterior, "MUERTOS"),
        "lesionados_anterior": contar(anio_anterior, "LESIONADOS"),
        "muertos_actual": contar(anio_actual, "MUERTOS"),
        "lesionados_actual": contar(anio_actual, "LESIONADOS")
    }
# =====================
# Q04 – MUERTOS VS LESIONADOS (ÚLTIMO AÑO)
# =====================
@app.get("/consulta/Q04")
def q04_muertos_vs_lesionados():

    df_anio = DF_VIGENTE[DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL]

    total_siniestros = df_anio.shape[0]
    muertos = df_anio[df_anio["EstadoVictima"] == "MUERTOS"].shape[0]
    lesionados = df_anio[df_anio["EstadoVictima"] == "LESIONADOS"].shape[0]

    return {
        "anio": ANIO_ACTUAL,
        "total_siniestros": int(total_siniestros),
        "muertos": int(muertos),
        "lesionados": int(lesionados)
    }

# =====================
# Q05 – ANTIOQUIA ÚLTIMO AÑO
# =====================
@app.get("/consulta/Q05")
def q05_antioquia():

    df_ant = DF_VIGENTE[
        (DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL) &
        (DF_VIGENTE["Departamento"] == "ANTIOQUIA")
    ]

    total_siniestros = df_ant.shape[0]

    muertos = df_ant[df_ant["EstadoVictima"] == "MUERTOS"].shape[0]
    lesionados = df_ant[df_ant["EstadoVictima"] == "LESIONADOS"].shape[0]

    return {
        "departamento": "ANTIOQUIA",
        "anio": ANIO_ACTUAL,
        "total_siniestros": int(total_siniestros),
        "muertos": int(muertos),
        "lesionados": int(lesionados)
    }


# =====================
# Q06 – DEPTO CON MÁS SINIESTROS
# =====================
@app.get("/consulta/Q06")
def q06_departamento_mas():

    df_anio = DF_VIGENTE[DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL]

    conteo = (
        df_anio
        .groupby("Departamento")
        .size()
        .sort_values(ascending=False)
    )

    depto = conteo.index[0]

    df_depto = df_anio[df_anio["Departamento"] == depto]

    total_siniestros = df_depto.shape[0]
    muertos = df_depto[df_depto["EstadoVictima"] == "MUERTOS"].shape[0]
    lesionados = df_depto[df_depto["EstadoVictima"] == "LESIONADOS"].shape[0]

    return {
        "anio": ANIO_ACTUAL,
        "departamento": depto,
        "total_siniestros": int(total_siniestros),
        "muertos": int(muertos),
        "lesionados": int(lesionados)
    }


# =====================
# Q07 – MEDELLÍN ÚLTIMO AÑO
# =====================
@app.get("/consulta/Q07")
def q07_medellin():

    total = DF_VIGENTE[
        (DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL) &
        (DF_VIGENTE["Municipio"] == "MEDELLIN") &
        (DF_VIGENTE["EstadoVictima"] == "MUERTOS")
    ].shape[0]

    return {
        "municipio": "MEDELLÍN",
        "anio": ANIO_ACTUAL,
        "victimas_fatales": int(total)
    }

# =====================
# Q08 – TOP 10 MUNICIPIOS
# =====================
@app.get("/consulta/Q08")
def q08_top_municipios():

    top = (
        DF_VIGENTE[
            (DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL) &
            (DF_VIGENTE["EstadoVictima"] == "MUERTOS")
        ]
        .groupby("Municipio")
        .size()
        .sort_values(ascending=False)
        .head(10)
    )

    return {
        "anio": ANIO_ACTUAL,
        "data": top.astype(int).to_dict()
    }

# =====================
# Q09 – URBANO VS RURAL
# =====================
@app.get("/consulta/Q09")
def q09_urbano_rural():

    conteo = (
        DF_VIGENTE[DF_VIGENTE["AnoHecho"] == ANIO_ACTUAL]
        .groupby("Zona")
        .size()
    )

    return {
        "anio": ANIO_ACTUAL,
        "URBANA": int(conteo.get("URBANA", 0)),
        "RURAL": int(conteo.get("RURAL", 0))
    }
# =====================
# Q10 – MES CON MÁS VÍCTIMAS (2025)
# =====================
@app.get("/consulta/Q10")
def q10_mes_mas_victimas_2025():
    anio = 2025

    conteo = (
        df[df["AnoHecho"] == anio]
        .groupby("MesHecho")
        .size()
        .sort_values(ascending=False)
    )

    mes = int(conteo.index[0])
    total = int(conteo.iloc[0])

    return {
        "anio": anio,
        "mes_mayor_victimas": mes,
        "total_victimas": total
    }

# =====================
# Q11 – MES CON MENOS VÍCTIMAS (2025)
# =====================
@app.get("/consulta/Q11")
def q11_mes_menos_victimas_2025():
    anio = 2025

    conteo = (
        df[df["AnoHecho"] == anio]
        .groupby("MesHecho")
        .size()
        .sort_values()
    )

    mes = int(conteo.index[0])
    total = int(conteo.iloc[0])

    return {
        "anio": anio,
        "mes_menor_victimas": mes,
        "total_victimas": total
    }


# =====================
# Q12 – RANGO HORARIO CON MÁS HECHOS
# =====================
@app.get("/consulta/Q12")
def q12_rangos_horarios_2025():
    anio = 2025

    conteo = (
        df[df["AnoHecho"] == anio]
        .groupby("Rango3horas")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "anio": anio,
        "rangos_horarios": conteo.astype(int).to_dict()
    }

# =====================
# Q13 – DÍA DEL MES CON MÁS MUERTES
# =====================
@app.get("/consulta/Q13")
def q13_dia_semana_mas_fatal():
    # 1️⃣ Último año disponible
    anio = int(df["AnoHecho"].max())

    # 2️⃣ Filtrar hechos fatales
    df_filtrado = df[
        (df["AnoHecho"] == anio) &
        (df["EstadoVictima"] == "MUERTOS")
    ]

    # 3️⃣ Agrupar por día de la semana
    conteo = (
        df_filtrado
        .groupby("DiaOcurrencia")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "anio": anio,
        "dia_semana_con_mas_hechos_fatales": conteo.index[0],
        "hechos_fatales": int(conteo.iloc[0]),
        "detalle_completo": conteo.astype(int).to_dict()
    }




# =====================
# Q14 – FESTIVOS VS DÍAS NORMALES
# =====================
@app.get("/consulta/Q14")
def q14_festivos_vs_normales():

    # Último año disponible
    ultimo_anio = int(df["AnoHecho"].max())

    # Filtrar último año
    df_anio = df[df["AnoHecho"] == ultimo_anio].copy()

    # Normalizar fechas
    df_anio["Fecha"] = pd.to_datetime(
        df_anio["FechaHecho"],
        errors="coerce"
    ).dt.date

    # Festivos como set
    festivos_set = set(df_festivos["Fecha"].dt.date)

    # Clasificar día
    df_anio["TipoDia"] = df_anio["Fecha"].apply(
        lambda f: "Festivo" if f in festivos_set else "Día normal"
    )

    # Conteo
    conteo = (
        df_anio
        .groupby("TipoDia")
        .size()
        .reset_index(name="total_siniestros")
    )

    return {
        "anio": ultimo_anio,
        "resultado": conteo.to_dict(orient="records")
    }

# =====================
# Q15 – USUARIO VIAL CON MÁS VÍCTIMAS
# =====================
@app.get("/consulta/Q15")
def q15_actor_vial_mas_victimas():

    conteo = (
        DF_VIGENTE
        .groupby("ActorVial")
        .size()
        .sort_values(ascending=False)
    )

    actor = conteo.index[0]
    total = int(conteo.iloc[0])

    return {
        "actor_vial": actor,
        "total_victimas": total,
        "detalle": conteo.astype(int).to_dict()
    }



# =====================
# Q16 – MOTOCICLETAS FALLECIDOS EN 2025
# =====================
@app.get("/consulta/Q16")
def q16_motocicletas_fallecidos_2025():

    anio = 2025

    total = df[
        (df["AnoHecho"] == anio) &
        (df["TipoVehiculo"].str.upper() == "MOTOCICLETA") &
        (df["EstadoVictima"] == "MUERTOS")
    ].shape[0]

    return {
        "anio": anio,
        "tipo_vehiculo": "Motocicleta",
        "estado_victima": "Muertos",
        "fallecidos": int(total)
    }




# =====================
# Q17 – PEATONES FALLECIDOS EN 2024
# =====================
@app.get("/consulta/Q17")
def q17_peatones_fallecidos_2024():

    anio = 2024

    total = df[
        (df["AnoHecho"] == anio) &
        (df["EstadoVictima"] == "MUERTOS") &
        (df["ActorVial"].str.upper().str.contains("PEAT", na=False))
    ].shape[0]

    return {
        "anio": anio,
        "actor_vial": "PEATÓN",
        "fallecidos": int(total)
    }


# =====================
# Q18 – TIPO DE VEHÍCULO MÁS INVOLUCRADO (ÚLTIMOS 3 AÑOS)
# =====================
@app.get("/consulta/Q18")
def q18_tipo_vehiculo_mas_fatal_ultimos_3_anios():

    # Últimos 3 años disponibles
    anios = (
        DF_VIGENTE["AnoHecho"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
    )[-3:]

    df_3_anios = DF_VIGENTE[
        (DF_VIGENTE["AnoHecho"].isin(anios)) &
        (DF_VIGENTE["EstadoVictima"] == "MUERTOS")
    ]

    conteo = (
        df_3_anios
        .groupby("TipoVehiculo")
        .size()
        .sort_values(ascending=False)
    )

    vehiculo = conteo.index[0]
    total = int(conteo.iloc[0])

    return {
        "anios_analizados": anios.tolist(),
        "tipo_vehiculo_mas_involucrado": vehiculo,
        "total_hechos_fatales": total,
        "detalle": conteo.astype(int).to_dict()
    }
# =====================
# Q19 – RANGO DE EDAD MÁS AFECTADO (FATALES)
# =====================
@app.get("/consulta/Q19")
def q19_rango_edad_mas_afectado():
    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby("RangoEdad")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "rango_edad_mas_afectado": conteo.index[0],
        "total_fallecidos": int(conteo.iloc[0]),
        "detalle_completo": conteo.astype(int).to_dict()
    }

# =====================
# Q20 – FALLECIDOS POR RANGO DE EDAD Y SEXO
# =====================
@app.get("/consulta/Q20")
def q20_rango_edad_y_sexo():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby(["RangoEdad", "Sexo"])
        .size()
        .reset_index(name="Fallecidos")
        .sort_values("Fallecidos", ascending=False)
    )

    return {
        "distribucion": conteo.to_dict(orient="records")
    }

# =====================
# Q21 – CLASE DE ACCIDENTE MÁS FRECUENTE (FATALES)
# =====================
@app.get("/consulta/Q21")
def q21_clase_accidente_mas_frecuente():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby("ClaseAccidente")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "clase_accidente_mas_frecuente": conteo.index[0],
        "total_fallecidos": int(conteo.iloc[0]),
        "detalle_completo": conteo.astype(int).to_dict()
    }

# =====================
# Q22 – OBJETO DE COLISIÓN MÁS COMÚN
# =====================
@app.get("/consulta/Q22")
def q22_objeto_colision_mas_comun():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby("ObjetoColision")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "objeto_colision_mas_comun": conteo.index[0],
        "total_fallecidos": int(conteo.iloc[0]),
        "detalle_completo": conteo.astype(int).to_dict()
    }

# =====================
# Q23 – HIPÓTESIS ASOCIADAS A HECHOS FATALES
# =====================
@app.get("/consulta/Q23")
def q23_hipotesis_fatales():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby("Hipotesis")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "hipotesis_mas_frecuentes": conteo.astype(int).to_dict()
    }

# =====================
# Q24 – CAUSAS DE MUERTE MÁS FRECUENTES
# =====================
@app.get("/consulta/Q24")
def q24_causas_muerte_frecuentes():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    conteo = (
        df_filtrado
        .groupby("CausaMuerte")
        .size()
        .sort_values(ascending=False)
    )

    return {
        "causas_muerte_mas_frecuentes": conteo.astype(int).to_dict()
    }

# =====================
# Q25 – VARIACIÓN VÍCTIMAS FATALES ANTIOQUIA (2024 vs 2025)
# =====================
@app.get("/consulta/Q25")
def q25_variacion_antioquia_2024_2025():

    df_ant = df[
        (df["Departamento"] == "ANTIOQUIA") &
        (df["EstadoVictima"] == "MUERTOS") &
        (df["AnoHecho"].isin([2024, 2025]))
    ]

    conteo = df_ant.groupby("AnoHecho").size()

    v_2024 = int(conteo.get(2024, 0))
    v_2025 = int(conteo.get(2025, 0))

    return {
        "departamento": "ANTIOQUIA",
        "victimas_2024": v_2024,
        "victimas_2025": v_2025,
        "variacion": "AUMENTARON" if v_2025 > v_2024 else "DISMINUYERON" if v_2025 < v_2024 else "SE MANTUVIERON"
    }

# =====================
# Q26 – VARIACIÓN VÍCTIMAS FATALES COLOMBIA (AÑO ANTERIOR VS ÚLTIMO)
# =====================
@app.get("/consulta/Q26")
def q26_variacion_colombia():

    anios = sorted(df["AnoHecho"].dropna().unique())
    anio_anterior = int(anios[-2])
    anio_actual = int(anios[-1])

    df_filtrado = df[
        (df["EstadoVictima"] == "MUERTOS") &
        (df["AnoHecho"].isin([anio_anterior, anio_actual]))
    ]

    conteo = df_filtrado.groupby("AnoHecho").size()

    v_ant = int(conteo.get(anio_anterior, 0))
    v_act = int(conteo.get(anio_actual, 0))

    return {
        "anio_anterior": anio_anterior,
        "anio_actual": anio_actual,
        "victimas_anio_anterior": v_ant,
        "victimas_anio_actual": v_act,
        "variacion": "AUMENTARON" if v_act > v_ant else "DISMINUYERON" if v_act < v_ant else "SE MANTUVIERON"
    }

# =====================
# Q27 – VARIACIÓN VÍCTIMAS FATALES USUARIOS DE MOTO
# =====================
@app.get("/consulta/Q27")
def q27_variacion_motociclistas():

    anios = sorted(df["AnoHecho"].dropna().unique())
    anio_1 = int(anios[-2])
    anio_2 = int(anios[-1])

    df_moto = df[
        (df["EstadoVictima"] == "MUERTOS") &
        (df["ActorVial"] == "MOTOCICLISTA") &
        (df["AnoHecho"].isin([anio_1, anio_2]))
    ]

    conteo = df_moto.groupby("AnoHecho").size()

    v1 = int(conteo.get(anio_1, 0))
    v2 = int(conteo.get(anio_2, 0))

    return {
        "usuario_vial": "MOTOCICLISTA",
        "anio_1": anio_1,
        "anio_2": anio_2,
        "victimas_anio_1": v1,
        "victimas_anio_2": v2,
        "variacion": "AUMENTARON" if v2 > v1 else "DISMINUYERON" if v2 < v1 else "SE MANTUVIERON"
    }

# =====================
# Q28 – DEPARTAMENTOS QUE AUMENTARON O REDUJERON VÍCTIMAS
# =====================
@app.get("/consulta/Q28")
def q28_departamentos_variacion():

    anios = sorted(df["AnoHecho"].dropna().unique())
    anio_ant = int(anios[-2])
    anio_act = int(anios[-1])

    df_filtrado = df[
        (df["EstadoVictima"] == "MUERTOS") &
        (df["AnoHecho"].isin([anio_ant, anio_act]))
    ]

    tabla = (
        df_filtrado
        .groupby(["Departamento", "AnoHecho"])
        .size()
        .unstack(fill_value=0)
    )

    aumentaron = (tabla[anio_act] > tabla[anio_ant]).sum()
    disminuyeron = (tabla[anio_act] < tabla[anio_ant]).sum()

    return {
        "anio_anterior": anio_ant,
        "anio_actual": anio_act,
        "departamentos_que_aumentaron": int(aumentaron),
        "departamentos_que_disminuyeron": int(disminuyeron)
    }

# =====================
# Q29 – JÓVENES VS ADULTOS MAYORES (FATALES)
# =====================
@app.get("/consulta/Q29")
def q29_jovenes_vs_adultos_mayores():

    df_filtrado = df[df["EstadoVictima"] == "MUERTOS"]

    jovenes = df_filtrado[df_filtrado["RangoEdad"].isin(["15-19", "20-24", "25-29"])].shape[0]
    adultos_mayores = df_filtrado[df_filtrado["RangoEdad"].isin(["60-64", "65-69", "70+", "60+"])].shape[0]

    return {
        "jovenes_15_29": int(jovenes),
        "adultos_mayores_60_mas": int(adultos_mayores),
        "grupo_mas_afectado": "JÓVENES" if jovenes > adultos_mayores else "ADULTOS MAYORES" if adultos_mayores > jovenes else "IGUAL"
    }

