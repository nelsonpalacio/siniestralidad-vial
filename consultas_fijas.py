from fastapi import APIRouter
from data_store import DF_VIGENTE

import pandas as pd

router = APIRouter()

# =====================
# UTILIDADES
# =====================
def ultimo_anio(df):
    return int(df["AnoHecho"].dropna().astype(int).max())


def anios_ordenados(df):
    return sorted(df["AnoHecho"].dropna().astype(int).unique())


# =====================
# Q01 – TOTAL ÚLTIMOS 3 AÑOS
# =====================
@router.get("/Q01")
def q01():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    anios = anios_ordenados(df)[-3:]
    d = df[df["AnoHecho"].isin(anios)]

    pivot = (
        d.groupby(["AnoHecho", "EstadoVictima"])["NumeroRadicadoInforme"]
         .nunique()
         .unstack(fill_value=0)
    )

    respuesta = {}
    for a in anios:
        respuesta[str(a)] = {
            "Lesionados": int(pivot.loc[a].get("lesionados", 0)),
            "Muertos": int(pivot.loc[a].get("muertos", 0)),
            "Total": int(pivot.loc[a].sum())
        }

    return respuesta




# =====================
# Q02 – ESTADO ÚLTIMO AÑO
# =====================
@router.get("/Q02")
def q02():
    a = ultimo_anio(DF_VIGENTE)

    # FILTRO BASE: último año + versión vigente
    d = DF_VIGENTE[
        (DF_VIGENTE["AnoHecho"] == a) &
        (DF_VIGENTE["VersionFinalActual"] == 1)
    ]

    # Normalizar EstadoVictima
    d["EstadoVictima"] = d["EstadoVictima"].str.strip().str.lower()

    return {
        "anio": a,
        "total": int(d.shape[0]),
        "muertos": int(d[d["EstadoVictima"] == "muertos"].shape[0]),
        "lesionados": int(d[d["EstadoVictima"] == "lesionados"].shape[0]),
    }

# =====================
# Q03 – COMPARACIÓN DOS AÑOS
# =====================
@router.get("/Q03")
def q03():
    df = DF_VIGENTE[DF_VIGENTE["EsVersionFinal"] == 0].copy()

    ultima_fecha = pd.to_datetime(df["FechaVersion"], errors="coerce").max()
    mes_version = int(ultima_fecha.month)
    anio_actual = int(ultima_fecha.year)
    anio_anterior = anio_actual - 1

    df_actual = df[(df["AnoHecho"] == anio_actual) & (df["MesVersion"] == mes_version)]
    df_anterior = df[(df["AnoHecho"] == anio_anterior) & (df["MesVersion"] == mes_version)]

    df_actual["EstadoVictima"] = df_actual["EstadoVictima"].str.strip().str.lower()
    df_anterior["EstadoVictima"] = df_anterior["EstadoVictima"].str.strip().str.lower()

    def contar(d, estado):
        return int(d[d["EstadoVictima"] == estado]["NumeroRadicadoInforme"].count())

    return {
        "anio_anterior": anio_anterior,
        "anio_actual": anio_actual,
        "mes_version": mes_version,
        "muertos_anterior": contar(df_anterior, "muertos"),
        "lesionados_anterior": contar(df_anterior, "lesionados"),
        "muertos_actual": contar(df_actual, "muertos"),
        "lesionados_actual": contar(df_actual, "lesionados"),
    }




# =====================
# Q04 – RESUMEN NACIONAL
# =====================
@router.get("/Q04")
def q04():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    anio_actual = int(df["AnoHecho"].max())
    d = df[df["AnoHecho"] == anio_actual]

    # Totales
    total = int(d["NumeroRadicadoInforme"].count())
    muertos = int(d[d["EstadoVictima"].str.strip().str.lower() == "muertos"]["NumeroRadicadoInforme"].count())
    lesionados = int(d[d["EstadoVictima"].str.strip().str.lower() == "lesionados"]["NumeroRadicadoInforme"].count())

    # Detalle por ActorVial
    detalle = (
        d.groupby(["EstadoVictima", "ActorVial"])["NumeroRadicadoInforme"]
        .count()
        .unstack(fill_value=0)
        .to_dict()
    )

    return {
        "anio": anio_actual,
        "total_siniestros": total,
        "muertos": muertos,
        "lesionados": lesionados,
        "detalle_actor_vial": detalle
    }


# =====================
# Q05 – ANTIOQUIA
# =====================
@router.get("/Q05")
def q05():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    d = df[
        (df["AnoHecho"] == anio_actual) &
        (df["Departamento"] == "antioquia")
    ]

    total = int(d["NumeroRadicadoInforme"].count())
    muertos = int(d[d["EstadoVictima"].str.strip().str.lower() == "muertos"]["NumeroRadicadoInforme"].count())
    lesionados = int(d[d["EstadoVictima"].str.strip().str.lower() == "lesionados"]["NumeroRadicadoInforme"].count())

    return {
        "anio": anio_actual,
        "departamento": "ANTIOQUIA",
        "total": total,
        "muertos": muertos,
        "lesionados": lesionados,
    }



# =====================
# Q06 – DEPTO CON MÁS VÍCTIMAS
# =====================
@router.get("/Q06")
def q06():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    top5 = (
        df[df["AnoHecho"] == anio_actual]
        .groupby("Departamento")["NumeroRadicadoInforme"]
        .count()
        .sort_values(ascending=False)
        .head(5)
    )

    return {
        "anio": anio_actual,
        "top5": top5.astype(int).to_dict()
    }



# =====================
# Q07 – MUERTOS MEDELLÍN
# =====================
@router.get("/Q07")
def q07():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    t = df[
        (df["AnoHecho"] == anio_actual) &
        (df["Municipio"] == "medellin") &
        (df["EstadoVictima"].str.strip().str.lower() == "muertos")
    ]["NumeroRadicadoInforme"].count()

    return {
        "anio": anio_actual,
        "municipio": "MEDELLIN",
        "muertos": int(t)
    }



# =====================
# Q08 – TOP 10 MUNICIPIOS
# =====================
@router.get("/Q08")
def q08():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    top = (
        df[
            (df["AnoHecho"] == anio_actual) &
            (df["EstadoVictima"].str.strip().str.lower() == "muertos")
        ]
        .groupby("Municipio")["NumeroRadicadoInforme"]
        .count()
        .sort_values(ascending=False)
        .head(10)
    )

    return {
        "anio": anio_actual,
        "data": top.astype(int).to_dict()
    }



# =====================
# Q09 – URBANO VS RURAL
# =====================
@router.get("/Q09")
def q09():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    g = (
        df[df["AnoHecho"] == anio_actual]
        .groupby("Zona")["NumeroRadicadoInforme"]
        .count()
    )

    return {
        "anio": anio_actual,
        "URBANA": int(g.get("urbana", 0)),
        "RURAL": int(g.get("rural", 0)),
    }



# =====================
# Q10 – MES CON MÁS SINIESTROS
# =====================
@router.get("/Q10")
def q10():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    anio_actual = int(df["AnoHecho"].max())
    d = df[df["AnoHecho"] == anio_actual].copy()

    # Normalizar EstadoVictima
    d["EstadoVictima"] = d["EstadoVictima"].str.strip().str.lower()

    # Total por mes (sin distinguir muertos/lesionados)
    total_mes = (
        d.groupby("MesHecho")["NumeroRadicadoInforme"]
        .count()
        .sort_index()
    )

    # Muertos por mes
    muertos_mes = (
        d[d["EstadoVictima"] == "muertos"]
        .groupby("MesHecho")["NumeroRadicadoInforme"]
        .count()
        .reindex(range(1, 13), fill_value=0)
    )

    # Lesionados por mes
    lesionados_mes = (
        d[d["EstadoVictima"] == "lesionados"]
        .groupby("MesHecho")["NumeroRadicadoInforme"]
        .count()
        .reindex(range(1, 13), fill_value=0)
    )

    # Armar salida en el formato deseado
    resultado = {}
    for mes in range(1, 13):
        resultado[mes] = {
            "total": int(total_mes.get(mes, 0)),
            "muertos": int(muertos_mes.get(mes, 0)),
            "lesionados": int(lesionados_mes.get(mes, 0))
        }

    return {
        "anio": anio_actual,
        "meses": resultado
    }





# =====================
# Q11 – MES CON MENOS SINIESTROS
# =====================
@router.get("/Q11")
def q11():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    d = df[df["AnoHecho"] == anio_actual]

    conteo = d.groupby("MesHecho")["NumeroRadicadoInforme"].count()

    top3 = conteo.nsmallest(3).sort_values().astype(int)

    return {
        "anio": anio_actual,
        "top3_meses_menos": top3.to_dict()
    }



# =====================
# Q12 – HORA CON MÁS SINIESTROS
# =====================
@router.get("/Q12")
def q12():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    d = df[df["AnoHecho"] == anio_actual]

    conteo = d.groupby("Rango3horas")["NumeroRadicadoInforme"].count().sort_index()

    return {
        "anio": anio_actual,
        "rangos": conteo.astype(int).to_dict()
    }



# =====================
# Q13 – DÍA CON MÁS SINIESTROS
# =====================
@router.get("/Q13")
def q13():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    anio_actual = int(df["AnoHecho"].max())

    d = df[df["AnoHecho"] == anio_actual].copy()
    d["EstadoVictima"] = d["EstadoVictima"].str.strip().str.lower()

    conteo = (
        d.groupby(["DiaOcurrencia", "EstadoVictima"])["NumeroRadicadoInforme"]
        .count()
        .unstack(fill_value=0)
    )

    # asegurar columnas
    for col in ["muertos", "lesionados"]:
        if col not in conteo.columns:
            conteo[col] = 0

    conteo["total"] = conteo["muertos"] + conteo["lesionados"]

    return {
        "anio": anio_actual,
        "dias": conteo[["total", "muertos", "lesionados"]]
                .astype(int)
                .to_dict(orient="index")
    }



# =====================
# FESTIVOS 2025-2026 (puedes extender)
# =====================
FESTIVOS = {
    2025: [
        '2025-01-01', '2025-03-03', '2025-04-17', '2025-04-18',
        '2025-05-01', '2025-05-26', '2025-06-16', '2025-06-23',
        '2025-07-20', '2025-08-07', '2025-08-18', '2025-10-13',
        '2025-11-03', '2025-11-10', '2025-12-08', '2025-12-25'
    ],
    2026: [
        '2026-01-01', '2026-03-16', '2026-03-26', '2026-03-27',
        '2026-05-01', '2026-05-18', '2026-06-08', '2026-06-15',
        '2026-07-20', '2026-08-07', '2026-08-17', '2026-10-12',
        '2026-11-02', '2026-11-09', '2026-12-08', '2026-12-25'
    ]
}

def es_festivo(fecha):
    """Recibe datetime.date o datetime.datetime"""
    f_str = fecha.strftime("%Y-%m-%d")
    ano = fecha.year
    return f_str in FESTIVOS.get(ano, [])

def es_fin_de_semana(fecha):
    return fecha.weekday() >= 5  # 5=sábado,6=domingo

def es_festivo_o_findes(fecha):
    return es_festivo(fecha) or es_fin_de_semana(fecha)

# =====================
# Q14 – FESTIVOS VS NO FESTIVOS
# =====================
@router.get("/Q14")
def q14():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a].copy()

    d["FechaHecho"] = pd.to_datetime(d["FechaHecho"], errors="coerce")

    festivos_count = d["FechaHecho"].apply(lambda x: es_festivo_o_findes(x)).sum()
    total = len(d)

    return {
        "anio": a,
        "FESTIVO_O_FINDES": int(festivos_count),
        "DIA_HABIL": int(total - festivos_count)
    }
# =====================
# Q15 – ACTOR VIAL MÁS AFECTADO
# =====================
@router.get("/Q15")
def q15():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a]

    top5 = (
        d.groupby("ActorVial")["NumeroRadicadoInforme"]
        .count()
        .sort_values(ascending=False)
        .head(5)
        .astype(int)
        .to_dict()
    )

    return {
        "anio": a,
        "top5": top5
    }



# =====================
# Q16 – Cantidad de moticiclistas muertos en el ultimo año
# =====================
@router.get("/Q16")
def q16():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a].copy()

    d["EstadoVictima"] = d["EstadoVictima"].astype(str).str.strip().str.upper()
    d["TipoVehiculo"] = d["TipoVehiculo"].astype(str).str.strip().str.upper()

    t = d[
        (d["TipoVehiculo"] == "MOTOCICLETA") &
        (d["EstadoVictima"] == "MUERTOS")
    ].shape[0]

    return {"anio": a, "muertes_motocicletas": int(t)}



# =====================
# Q17 – peatones muertos 2024
# =====================
@router.get("/Q17")
def q17():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    d = df.copy()
    d["EstadoVictima"] = d["EstadoVictima"].astype(str).str.strip().str.upper()
    d["ActorVial"] = d["ActorVial"].astype(str).str.strip().str.upper()

    t = d[
        (d["AnoHecho"] == 2024) &
        (d["ActorVial"] == "PEATÓN") &
        (d["EstadoVictima"] == "MUERTOS")
    ].shape[0]

    return {"anio": 2024, "muertes_peatones": int(t)}


# =====================
# Q18 – Cvehiculos mas muertos 3 años
# =====================
@router.get("/Q18")
def q18():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    años = sorted(df["AnoHecho"].dropna().astype(int).unique())[-3:]
    años = [int(a) for a in años]

    resultado = {}

    for a in años:
        d = df[df["AnoHecho"] == a].copy()

        d["EstadoVictima"] = d["EstadoVictima"].astype(str).str.strip().str.upper()
        d["TipoVehiculo"] = d["TipoVehiculo"].astype(str).str.strip().str.upper()

        muertos = d[d["EstadoVictima"] == "MUERTOS"]

        top5 = (
            muertos.groupby("TipoVehiculo")["NumeroRadicadoInforme"]
            .count()
            .sort_values(ascending=False)
            .head(5)
            .astype(int)
            .to_dict()
        )

        total = int(muertos.shape[0])

        resultado[str(a)] = {
            "total_muertes": total,
            "top5": top5
        }

    return {"anios": años, "data": resultado}

    # =====================
# Q19 – Muertos ultim año
# =====================
@router.get("/Q19")
def q19():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    a = ultimo_anio(df)

    d = df[df["AnoHecho"] == a].copy()
    d["Sexo"] = d["Sexo"].astype(str).str.strip().str.upper()
    d["EstadoVictima"] = d["EstadoVictima"].astype(str).str.strip().str.lower()

    muertos = d[d["EstadoVictima"].str.contains("muert")]

    g = muertos.groupby("Sexo")["NumeroRadicadoInforme"].count().astype(int)

    return {"anio": a, "data": g.to_dict()}




# =====================
# Q20 – TOP RANGOS EDAD
# =====================
@router.get("/Q20")
def q20():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()
    a = ultimo_anio(df)

    d = df[df["AnoHecho"] == a].copy()

    g = (
        d.groupby("RangoEdad")["NumeroRadicadoInforme"]
        .count()
        .sort_values(ascending=False)
        .head(3)
        .astype(int)
        .to_dict()
    )

    return {"anio": a, "data": g}

# =====================
# Q21 – EDAD + SEXO
# =====================
@router.get("/Q21")
def q21():
    # Filtrar versiones finales
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    # Último año con datos
    a = ultimo_anio(df)

    # Filtrar por año
    d = df[df["AnoHecho"] == a].copy()

    # Normalizar EstadoVictima
    d["EstadoVictima"] = d["EstadoVictima"].astype(str).str.strip().str.lower()

    # Solo muertos
    muertos = d[d["EstadoVictima"] == "muertos"]

    # Top 3 por ClaseAccidente
    top3 = (
        muertos.groupby("ClaseAccidente")["NumeroRadicadoInforme"]
        .count()
        .sort_values(ascending=False)
        .head(3)
    )

    return {
        "anio": a,
        "top3": [
            {"clase": str(idx), "muertos": int(val)}
            for idx, val in top3.items()
        ]
    }

# =====================
# Q22 – Objeto de colision
# =====================
@router.get("/Q22")
def q22():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    # Normalizar EstadoVictima
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()

    # FILTRAR SOLO LOS CASOS CON MUERTOS
    df = df[df["EstadoVictima"] == "muertos"]

    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a]

    top3 = (
        d.groupby("ClaseAccidente")["NumeroRadicadoInforme"]
         .count()
         .sort_values(ascending=False)
         .head(3)
    )

    return {
        "anio": a,
        "top3": [
            {"clase_accidente": str(idx), "cantidad": int(val)}
            for idx, val in top3.items()
        ]
    }


# =====================
# Q23 – OBJETO COLISIÓN
# =====================
@router.get("/Q23")
def q23():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a].copy()

    top1 = (
        d.groupby("ObjetoColision")["NumeroRadicadoInforme"]
         .count()
         .sort_values(ascending=False)
         .head(1)
    )

    if top1.empty:
        return {"anio": a, "objeto_colision": None, "cantidad": 0}

    idx = top1.index[0]
    val = int(top1.iloc[0])

    return {
        "anio": a,
        "objeto_colision": str(idx),
        "cantidad": val
    }


# =====================
# Q24 – HIPÓTESIS MÁS COMÚN
# =====================
@router.get("/Q24")
def q24():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    # Normalizar EstadoVictima
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()

    # Filtrar solo muertos
    df = df[df["EstadoVictima"] == "muertos"]

    # Último año con datos
    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a].copy()

    top5 = (
        d.groupby("Hipotesis")["NumeroRadicadoInforme"]
         .count()
         .sort_values(ascending=False)
         .head(5)
    )

    return {
        "anio": a,
        "top5": [
            {"hipotesis": str(idx), "cantidad": int(val)}
            for idx, val in top5.items()
        ]
    }

# =====================
# Q25 – CAUSA MUERTE
# =====================
@router.get("/Q25")
def q25():
    df = DF_VIGENTE[DF_VIGENTE["VersionFinalActual"] == 1].copy()

    # Normalizar EstadoVictima
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()

    # Filtrar solo muertos
    df = df[df["EstadoVictima"] == "muertos"]

    # Último año con datos
    a = ultimo_anio(df)
    d = df[df["AnoHecho"] == a].copy()

    top5 = (
        d.groupby("CausaMuerte")["NumeroRadicadoInforme"]
         .count()
         .sort_values(ascending=False)
         .head(5)
    )

    return {
        "anio": a,
        "top5": [
            {"causa_muerte": str(idx), "cantidad": int(val)}
            for idx, val in top5.items()
        ]
    }

# =====================
# Q26 – VARIACIÓN ANTIOQUIA
# =====================
@router.get("/Q26")
def q26():
    df = DF_VIGENTE[DF_VIGENTE["EsVersionFinal"] == 0].copy()

    # obtener último mes disponible
    ultima_fecha = pd.to_datetime(df["FechaVersion"], errors="coerce").max()
    mes_actual = int(ultima_fecha.month)
    anio_actual = int(ultima_fecha.year)
    anio_anterior = anio_actual - 1

    # normalizar columnas
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()
    df["Departamento"] = df["Departamento"].astype(str).str.strip().str.lower()

    # filtrar Antioquia + muertos + mes y año
    df_actual = df[
        (df["Departamento"] == "antioquia") &
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_actual) &
        (df["MesVersion"] == mes_actual)
    ]

    df_anterior = df[
        (df["Departamento"] == "antioquia") &
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_anterior) &
        (df["MesVersion"] == mes_actual)
    ]

    muertes_actual = int(df_actual["NumeroRadicadoInforme"].count())
    muertes_anterior = int(df_anterior["NumeroRadicadoInforme"].count())

    variacion = muertes_actual - muertes_anterior
    tendencia = "aumentaron" if variacion > 0 else "disminuyeron" if variacion < 0 else "se mantuvieron"

    return {
        "departamento": "ANTIOQUIA",
        "anio_actual": anio_actual,
        "anio_anterior": anio_anterior,
        "mes": mes_actual,
        "muertes_anterior": muertes_anterior,
        "muertes_actual": muertes_actual,
        "variacion": variacion,
        "tendencia": tendencia
    }


# =====================
# Q27 – VARIACIÓN NACIONAL
# =====================
@router.get("/Q27")
def q27():
    df = DF_VIGENTE[DF_VIGENTE["EsVersionFinal"] == 0].copy()

    # Última fecha disponible
    ultima_fecha = pd.to_datetime(df["FechaVersion"], errors="coerce").max()
    mes_actual = int(ultima_fecha.month)
    anio_actual = int(ultima_fecha.year)
    anio_anterior = anio_actual - 1

    # Normalizar EstadoVictima
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()

    # Filtrar solo muertos y el mes correspondiente
    df_actual = df[
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_actual) &
        (df["MesVersion"] == mes_actual)
    ]

    df_anterior = df[
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_anterior) &
        (df["MesVersion"] == mes_actual)
    ]

    muertes_actual = int(df_actual["NumeroRadicadoInforme"].count())
    muertes_anterior = int(df_anterior["NumeroRadicadoInforme"].count())

    variacion = muertes_actual - muertes_anterior
    tendencia = "aumentaron" if variacion > 0 else "disminuyeron" if variacion < 0 else "se mantuvieron"

    return {
        "anio_actual": anio_actual,
        "anio_anterior": anio_anterior,
        "mes": mes_actual,
        "muertes_anterior": muertes_anterior,
        "muertes_actual": muertes_actual,
        "variacion": variacion,
        "tendencia": tendencia
    }


# =====================
# Q28 – MUERTES MOTOCICLISTAS
# =====================
@router.get("/Q28")
def q28():
    df = DF_VIGENTE[DF_VIGENTE["EsVersionFinal"] == 0].copy()

    # Última fecha disponible
    ultima_fecha = pd.to_datetime(df["FechaVersion"], errors="coerce").max()
    mes_actual = int(ultima_fecha.month)
    anio_actual = int(ultima_fecha.year)
    anio_anterior = anio_actual - 1

    # Normalizar columnas
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()
    df["TipoVehiculo"] = df["TipoVehiculo"].astype(str).str.strip().str.lower()

    # Filtrar solo motos y muertos
    df_actual = df[
        (df["EstadoVictima"] == "muertos") &
        (df["TipoVehiculo"] == "motocicleta") &
        (df["AnoHecho"] == anio_actual) &
        (df["MesVersion"] == mes_actual)
    ]

    df_anterior = df[
        (df["EstadoVictima"] == "muertos") &
        (df["TipoVehiculo"] == "motocicleta") &
        (df["AnoHecho"] == anio_anterior) &
        (df["MesVersion"] == mes_actual)
    ]

    muertes_actual = int(df_actual["NumeroRadicadoInforme"].count())
    muertes_anterior = int(df_anterior["NumeroRadicadoInforme"].count())

    variacion = muertes_actual - muertes_anterior
    tendencia = "aumentaron" if variacion > 0 else "disminuyeron" if variacion < 0 else "se mantuvieron"

    return {
        "anio_actual": anio_actual,
        "anio_anterior": anio_anterior,
        "mes": mes_actual,
        "muertes_anterior": muertes_anterior,
        "muertes_actual": muertes_actual,
        "variacion": variacion,
        "tendencia": tendencia
    }


# =====================
# Q29 – VARIACIÓN DEPARTAMENTOS
# =====================
@router.get("/Q29")
def q29():
    df = DF_VIGENTE[DF_VIGENTE["EsVersionFinal"] == 0].copy()

    # Última fecha disponible
    ultima_fecha = pd.to_datetime(df["FechaVersion"], errors="coerce").max()
    mes_actual = int(ultima_fecha.month)
    anio_actual = int(ultima_fecha.year)
    anio_anterior = anio_actual - 1

    # Normalizar columnas
    df["EstadoVictima"] = df["EstadoVictima"].astype(str).str.strip().str.lower()
    df["Departamento"] = df["Departamento"].astype(str).str.strip().str.lower()

    # Filtrar solo muertos y mes actual
    df_actual = df[
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_actual) &
        (df["MesVersion"] == mes_actual)
    ]

    df_anterior = df[
        (df["EstadoVictima"] == "muertos") &
        (df["AnoHecho"] == anio_anterior) &
        (df["MesVersion"] == mes_actual)
    ]

    # Contar muertes por departamento
    muertes_actual = df_actual.groupby("Departamento")["NumeroRadicadoInforme"].count()
    muertes_anterior = df_anterior.groupby("Departamento")["NumeroRadicadoInforme"].count()

    # Unir los dos años
    comparacion = pd.concat([muertes_anterior, muertes_actual], axis=1, keys=["anterior", "actual"]).fillna(0)
    comparacion["variacion"] = comparacion["actual"] - comparacion["anterior"]

    # Clasificar departamentos
    aumentaron = comparacion[comparacion["variacion"] > 0]
    disminuyeron = comparacion[comparacion["variacion"] < 0]
    se_mantuvieron = comparacion[comparacion["variacion"] == 0]

    # Convertir a listas
    def to_list(df):
        return [
            {
                "departamento": str(idx),
                "muertes_anterior": int(row["anterior"]),
                "muertes_actual": int(row["actual"]),
                "variacion": int(row["variacion"])
            }
            for idx, row in df.iterrows()
        ]

    return {
        "anio_actual": anio_actual,
        "anio_anterior": anio_anterior,
        "mes": mes_actual,
        "aumentaron": to_list(aumentaron),
        "disminuyeron": to_list(disminuyeron),
        "se_mantuvieron": to_list(se_mantuvieron),
        "totales": {
            "departamentos_aumentaron": int(aumentaron.shape[0]),
            "departamentos_disminuyeron": int(disminuyeron.shape[0]),
            "departamentos_se_mantuvieron": int(se_mantuvieron.shape[0])
        }
    }
