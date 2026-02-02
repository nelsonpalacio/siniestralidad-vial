# =========================================================
# INTÉRPRETE SEMÁNTICO UNIVERSAL
# =========================================================

import re
from .diccionario_semantico import (
    normalizar,
    INTENCIONES,
    ESTADO_VICTIMA,
    SEXO,
    TIPO_VEHICULO,
    CLASE_ACCIDENTE,
    ZONA,
    DEPARTAMENTOS
)

# ---------------------------------------------------------
# BUSCADOR GENÉRICO
# ---------------------------------------------------------

def buscar_en_diccionario(texto, diccionario):
    for valor_csv, palabras in diccionario.items():
        for p in palabras:
            if p in texto:
                return valor_csv
    return None


# ---------------------------------------------------------
# VALIDACIÓN SEMÁNTICA (PASO 4)
# ---------------------------------------------------------

def validar_plan(plan: dict):
    """
    Evita responder consultas ambiguas o incorrectas
    """

    if not plan.get("operacion"):
        return False, "No se pudo identificar la intención de la consulta"

    filtros = plan.get("filtros", {})

    if plan["operacion"] == "COUNT":
        if "AnoHecho" not in filtros:
            return False, "Debe especificar el año de la consulta"
        if "EstadoVictima" not in filtros:
            return False, "Debe indicar si son fallecidos o lesionados"

    return True, None


# ---------------------------------------------------------
# INTÉRPRETE PRINCIPAL
# ---------------------------------------------------------

def interpretar_pregunta(pregunta: str) -> dict:
    texto = normalizar(pregunta)

    plan = {
        "operacion": "COUNT",
        "filtros": {}
    }

    # -------------------------
    # INTENCIÓN
    # -------------------------
    for operacion, palabras in INTENCIONES.items():
        if any(p in texto for p in palabras):
            plan["operacion"] = operacion
            break

    # -------------------------
    # AÑO
    # -------------------------
    anio = re.search(r"\b(20\d{2})\b", texto)
    if anio:
        plan["filtros"]["AnoHecho"] = int(anio.group(1))

    # -------------------------
    # DEPARTAMENTO
    # -------------------------
    depto = buscar_en_diccionario(texto, DEPARTAMENTOS)
    if depto:
        plan["filtros"]["Departamento"] = depto

    # -------------------------
    # ESTADO VÍCTIMA
    # -------------------------
    estado = buscar_en_diccionario(texto, ESTADO_VICTIMA)
    if estado:
        plan["filtros"]["EstadoVictima"] = estado

    # -------------------------
    # SEXO
    # -------------------------
    sexo = buscar_en_diccionario(texto, SEXO)
    if sexo:
        plan["filtros"]["Sexo"] = sexo

    # -------------------------
    # TIPO VEHÍCULO
    # -------------------------
    vehiculo = buscar_en_diccionario(texto, TIPO_VEHICULO)
    if vehiculo:
        plan["filtros"]["TipoVehiculo"] = vehiculo

    # -------------------------
    # CLASE ACCIDENTE
    # -------------------------
    clase = buscar_en_diccionario(texto, CLASE_ACCIDENTE)
    if clase:
        plan["filtros"]["ClaseAccidente"] = clase

    # -------------------------
    # ZONA
    # -------------------------
    zona = buscar_en_diccionario(texto, ZONA)
    if zona:
        plan["filtros"]["Zona"] = zona

    # -------------------------
    # VALIDAR (PASO 4)
    # -------------------------
    valido, error = validar_plan(plan)
    if not valido:
        return {
            "ok": False,
            "error": error,
            "plan_parcial": plan
        }

    return {
        "ok": True,
        "plan": plan
    }
