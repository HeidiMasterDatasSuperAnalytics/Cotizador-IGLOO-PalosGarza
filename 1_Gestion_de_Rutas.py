import streamlit as st
import pandas as pd
import os

st.title("# Gestión de Rutas Guardadas")

FILE = "rutas_guardadas.csv"

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    st.warning("No hay rutas guardadas todavía.")
    df = pd.DataFrame()

if not df.empty:
    st.dataframe(df)

    to_delete = st.multiselect("Selecciona las rutas que deseas eliminar (por índice):", df.index.tolist())
    if st.button("Eliminar rutas seleccionadas") and to_delete:
        df.drop(index=to_delete, inplace=True)
        df.to_csv(FILE, index=False)
        st.success("Rutas eliminadas correctamente.")
        st.experimental_rerun()

    st.write("Puedes editar los datos directamente en Excel y volver a subirlos si lo deseas.")
    st.download_button("Descargar rutas en Excel", df.to_csv(index=False), file_name="rutas_guardadas.csv")
