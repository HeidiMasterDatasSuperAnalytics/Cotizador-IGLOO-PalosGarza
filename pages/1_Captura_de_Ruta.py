import streamlit as st
import pandas as pd
import os

# LOGO
from PIL import Image

logo = Image.open("Igloo Original.png")
col1, col2 = st.columns([1, 5])

with col1:
    st.image(logo, width=100)

with col2:
    st.title("Captura de Ruta")

# Rutas de archivos
RUTA_RUTAS = "rutas_guardadas.csv"

# Cargar rutas existentes
if os.path.exists(RUTA_RUTAS):
    df_rutas = pd.read_csv(RUTA_RUTAS)
else:
    df_rutas = pd.DataFrame()

# Formulario de Captura
with st.form("Captura de Ruta"):

    fecha = st.date_input("Fecha de captura")

    tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
    cliente = st.text_input("Nombre del Cliente")
    origen = st.text_input("Origen")
    destino = st.text_input("Destino")
    km = st.number_input("Kilómetros recorridos", min_value=0.0)

    moneda_ingreso = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"])
    ingreso_flete = st.number_input(f"Ingreso Flete en {moneda_ingreso}", min_value=0.0)

    moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"])
    ingreso_cruce = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0)

    casetas = st.number_input("Costo de Casetas", min_value=0.0)

    horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0)
    lavado_termo = st.number_input("Lavado de Termo", min_value=0.0)
    movimiento_local = st.number_input("Movimiento Local", min_value=0.0)
    puntualidad = st.number_input("Puntualidad", min_value=0.0)
    pension = st.number_input("Pensión", min_value=0.0)
    estancia = st.number_input("Estancia", min_value=0.0)
    fianza_termo = st.number_input("Fianza Termo Rentado/Externo", min_value=0.0)
    renta_termo = st.number_input("Renta de Termo", min_value=0.0)

    submitted = st.form_submit_button("Guardar Ruta")

    if submitted:
        nueva_ruta = {
            "Fecha": fecha,
            "Tipo": tipo,
            "Cliente": cliente,
            "Origen": origen,
            "Destino": destino,
            "KM": km,
            "Moneda": moneda_ingreso,
            "Ingreso_Original": ingreso_flete,
            "Moneda_Cruce": moneda_cruce,
            "Cruce_Original": ingreso_cruce,
            "Casetas": casetas,
            "Horas_Termo": horas_termo,
            "Lavado_Termo": lavado_termo,
            "Movimiento_Local": movimiento_local,
            "Puntualidad": puntualidad,
            "Pension": pension,
            "Estancia": estancia,
            "Fianza_Termo": fianza_termo,
            "Renta_Termo": renta_termo
        }

        df_rutas = pd.concat([df_rutas, pd.DataFrame([nueva_ruta])], ignore_index=True)
        df_rutas.to_csv(RUTA_RUTAS, index=False)
        st.success("✅ La ruta se guardó exitosamente.")
        st.experimental_rerun()


