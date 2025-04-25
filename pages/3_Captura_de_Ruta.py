import streamlit as st
import pandas as pd
import os

st.title("# Captura de Nueva Ruta")

FILE = "rutas_guardadas.csv"

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Tipo", "Cliente", "Origen", "Destino", "Ingreso_Total", "Costo_Total"])

st.subheader("Formulario para agregar nueva ruta")

tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
cliente = st.text_input("Nombre del Cliente (opcional para VACIO)")
origen = st.text_input("Origen")
destino = st.text_input("Destino")
ingreso_total = st.number_input("Ingreso Total Estimado (MXN)", min_value=0.0)
costo_total = st.number_input("Costo Total Estimado (MXN)", min_value=0.0)

if st.button("Guardar Ruta"):
    nueva_ruta = pd.DataFrame([{
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "Ingreso_Total": ingreso_total,
        "Costo_Total": costo_total
    }])
    df = pd.concat([df, nueva_ruta], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Ruta guardada exitosamente.")
    st.experimental_rerun()
