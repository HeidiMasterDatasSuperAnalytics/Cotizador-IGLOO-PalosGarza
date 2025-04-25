# pages/1_Gestion_de_Rutas.py

import streamlit as st
import pandas as pd
import os

st.title("# Gestión de Rutas Guardadas")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)
    datos_generales = cargar_datos_generales()

    # Obtener tipo de cambio y diesel
    tipo_cambio_usd = float(datos_generales.get("Tipo de cambio USD", 17.5))
    tipo_cambio_mxn = float(datos_generales.get("Tipo de cambio MXN", 1.0))
    precio_diesel = float(datos_generales.get("Costo Diesel", 24))

    # Agregar columna: Tipo de cambio aplicado
    df["Tipo_Cambio"] = df["Moneda"].apply(lambda x: tipo_cambio_usd if x == "USD" else tipo_cambio_mxn)

    # Insertar columnas visuales
    df.insert(df.columns.get_loc("Costo_Diesel"), "Precio_Diesel", precio_diesel)
    moneda_col = df.pop("Moneda")
    df.insert(df.columns.get_loc("Destino") + 1, "Moneda", moneda_col)
    tipo_cambio_col = df.pop("Tipo_Cambio")
    df.insert(df.columns.get_loc("Moneda") + 1, "Tipo_Cambio", tipo_cambio_col)

    # Mostrar tabla
    st.dataframe(df, use_container_width=True)

    st.subheader("Selecciona las rutas que deseas eliminar (por índice):")
    indices = st.multiselect("Índices a eliminar", df.index.tolist())

    if st.button("Eliminar rutas seleccionadas") and indices:
        df.drop(index=indices, inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ Rutas eliminadas correctamente.")
        st.rerun()

    # Botón para descargar copia de seguridad
    st.subheader("📥 Descargar copia de seguridad de datos")
    st.download_button("Descargar rutas_guardadas.csv", df.to_csv(index=False), file_name="rutas_guardadas.csv")

    if os.path.exists(RUTA_DATOS):
        datos_df = pd.read_csv(RUTA_DATOS)
        st.download_button("Descargar datos_generales.csv", datos_df.to_csv(index=False), file_name="datos_generales.csv")

else:
    st.warning("No hay rutas guardadas aún.")
