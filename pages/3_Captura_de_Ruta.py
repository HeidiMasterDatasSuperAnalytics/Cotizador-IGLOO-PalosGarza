import streamlit as st
import pandas as pd
import os

st.title("# Captura de Nueva Ruta")

FILE = "rutas_guardadas.csv"
DATOS = "datos_generales.csv"

def load_datos_generales():
    if os.path.exists(DATOS):
        return pd.read_csv(DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Tipo", "Cliente", "Origen", "Destino", "KM", "Ingreso_Total", "Costo_Total"])

datos = load_datos_generales()

st.subheader("Formulario para agregar nueva ruta")

tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
cliente = st.text_input("Nombre del Cliente (opcional para VACIO)")
origen = st.text_input("Origen")
destino = st.text_input("Destino")
km = st.number_input("Kilómetros recorridos", min_value=0.0)
ingreso_total = st.number_input("Ingreso Total Estimado (MXN)", min_value=0.0)

# Cálculo de costos
rendimiento = float(datos.get("Rend
