# =========================================================
# EJECUTOR DE PLANES SEMÁNTICOS
# =========================================================

def ejecutar_plan(df, plan: dict) -> dict:
    df_filtrado = df.copy()

    # -------------------------
    # APLICAR FILTROS
    # -------------------------
    for columna, valor in plan.get("filtros", {}).items():
        if columna not in df_filtrado.columns:
            continue

        # 🔹 SOPORTE PARA RANGOS (ej: Año)
        if isinstance(valor, dict) and "desde" in valor and "hasta" in valor:
            df_filtrado = df_filtrado[
                (df_filtrado[columna] >= valor["desde"]) &
                (df_filtrado[columna] <= valor["hasta"])
            ]
            continue

        # 🔹 FILTRO NORMAL (igualdad)
        df_filtrado = df_filtrado[
            df_filtrado[columna].astype(str).str.upper()
            == str(valor).upper()
        ]

    # -------------------------
    # OPERACIONES
    # -------------------------
    if plan["operacion"] == "COUNT":
        total = int(df_filtrado.shape[0])
        return {
            "valor": total,
            "filas_filtradas": total
        }

    return {
        "valor": None,
        "mensaje": "Operación no soportada"
    }
