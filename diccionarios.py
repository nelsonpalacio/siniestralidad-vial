# =========================================================
# DICCIONARIO SEMÁNTICO – PROYECTO ONSV
# =========================================================

import unicodedata

# ---------------------------------------------------------
# NORMALIZACIÓN
# ---------------------------------------------------------

def normalizar(texto: str) -> str:
    texto = texto.lower()
    texto = ''.join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


# ---------------------------------------------------------
# INTENCIONES
# ---------------------------------------------------------

INTENCIONES = {
    "COUNT": [
        "cuantos", "cuantas", "cantidad", "numero",
        "total", "cuántos", "cuántas"
    ],
    "PERCENT": [
        "porcentaje", "proporcion", "proporción", "ratio"
    ]
}


# ---------------------------------------------------------
# CONCEPTOS DE MUERTE / VÍCTIMAS
# ---------------------------------------------------------

CONCEPTOS_MUERTE = [
    "muertes", "muerte", "fallecidos", "fallecidas",
    "fallecio", "fallecieron", "victimas", "casos",
    "fatal", "fatales"
]


# ---------------------------------------------------------
# ACTOR / ESTADO DE LA VÍCTIMA  → EstadoVictima
# ---------------------------------------------------------

ESTADO_VICTIMA = {
    "MOTOCICLISTA": [
        "motociclista", "motociclistas",
        "moto", "motocicleta", "motorizado"
    ],
    "PEATON": [
        "peaton", "peatones", "atropellado",
        "transeunte", "persona a pie"
    ],
    "CONDUCTOR": [
        "conductor", "conductores",
        "automovilista", "chofer"
    ],
    "PASAJERO": [
        "pasajero", "pasajeros", "acompanante"
    ]
}


# ---------------------------------------------------------
# SEXO → Sexo
# ---------------------------------------------------------

SEXO = {
    "M": ["hombre", "masculino", "varon"],
    "F": ["mujer", "femenino"]
}


# ---------------------------------------------------------
# TIPO DE VEHÍCULO → TipoVehiculo
# ---------------------------------------------------------

TIPO_VEHICULO = {
    "MOTOCICLETA": ["moto", "motocicleta"],
    "AUTOMOVIL": ["automovil", "auto", "carro"],
    "BUS": ["bus", "buseta"],
    "CAMION": ["camion", "camioneta"],
    "BICICLETA": ["bicicleta", "bici"]
}


# ---------------------------------------------------------
# CLASE DE ACCIDENTE → ClaseAccidente
# ---------------------------------------------------------

CLASE_ACCIDENTE = {
    "CHOQUE": ["choque", "colision"],
    "ATROPELLO": ["atropello", "atropellamiento"],
    "VOLCAMIENTO": ["volcamiento", "volcado"],
    "CAIDA": ["caida", "caida del vehiculo"]
}


# ---------------------------------------------------------
# ZONA → Zona
# ---------------------------------------------------------

ZONA = {
    "URBANA": ["urbana", "ciudad"],
    "RURAL": ["rural", "campo"]
}


# ---------------------------------------------------------
# DEPARTAMENTOS → Departamento (CSV REAL)
# ---------------------------------------------------------

DEPARTAMENTOS = {
    "AMAZONAS": ["amazonas"],
    "ANTIOQUIA": ["antioquia"],
    "ARAUCA": ["arauca"],
    "ATLANTICO": ["atlantico"],
    "BOLIVAR": ["bolivar"],
    "BOYACA": ["boyaca"],
    "CALDAS": ["caldas"],
    "CAQUETA": ["caqueta"],
    "CASANARE": ["casanare"],
    "CAUCA": ["cauca"],
    "CESAR": ["cesar"],
    "CHOCO": ["choco"],
    "CORDOBA": ["cordoba"],
    "CUNDINAMARCA": ["cundinamarca"],
    "GUAINIA": ["guainia"],
    "GUAVIARE": ["guaviare"],
    "HUILA": ["huila"],
    "LA GUAJIRA": ["guajira", "la guajira"],
    "MAGDALENA": ["magdalena"],
    "META": ["meta"],
    "NARIÑO": ["narino"],
    "NORTE DE SANTANDER": ["norte de santander"],
    "PUTUMAYO": ["putumayo"],
    "QUINDIO": ["quindio"],
    "RISARALDA": ["risaralda"],
    "SAN ANDRES": ["san andres"],
    "SANTANDER": ["santander"],
    "SUCRE": ["sucre"],
    "TOLIMA": ["tolima"],
    "VALLE DEL CAUCA": ["valle", "valle del cauca"],
    "VAUPES": ["vaupes"],
    "VICHADA": ["vichada"],
    "BOGOTÁ": ["bogota", "bogotá"]
}
