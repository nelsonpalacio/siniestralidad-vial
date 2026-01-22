import polars as pl

csv_path = "backend/datos/MLrefinado.csv"
parquet_path = "backend/datos/MLrefinado.parquet"

print("📥 Leyendo CSV...")

# Columnas que sabemos que son identificadores (texto)
columnas_texto = [
    "NoticiaCriminal",
    "NumeroRadicadoInforme"
]

df = pl.read_csv(
    csv_path,
    infer_schema_length=20000,  # analizamos muchas filas
    schema_overrides={col: pl.Utf8 for col in columnas_texto}
)

print(f"✅ CSV cargado: {df.shape[0]} filas, {df.shape[1]} columnas")

print("💾 Guardando archivo Parquet...")
df.write_parquet(parquet_path)

print("🎉 Conversión finalizada con éxito")
