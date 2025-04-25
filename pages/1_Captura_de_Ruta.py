import streamlit as st
import pandas as pd
import os
from datetime import date

st.title("# Captura de Ruta")

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_DATOS = "datos_generales.csv"

def cargar_datos_generales():
    if os.path.exists(RUTA_DATOS):
        return pd.read_csv(RUTA_DATOS).set_index("Parametro").to_dict()["Valor"]
    return {}

datos_generales = cargar_datos_generales()

tipo_cambio_usd = float(datos_generales.get("Tipo de cambio USD", 17.5))
tipo_cambio_mxn = float(datos_generales.get("Tipo de cambio MXN", 1.0))

st.subheader("📝 Nueva Ruta")

fecha = st.date_input("Fecha", value=date.today())
tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
cliente = st.text_input("Nombre del Cliente")
origen = st.text_input("Origen")
destino = st.text_input("Destino")
km = st.number_input("Kilómetros recorridos", min_value=0.0)

moneda = st.selectbox("Moneda Ingreso Flete", ["MXN", "USD"])
ingreso_original = st.number_input(f"Ingreso Flete en {moneda}", min_value=0.0)
tipo_cambio = tipo_cambio_usd if moneda == "USD" else tipo_cambio_mxn
ingreso_total = ingreso_original * tipo_cambio

moneda_cruce = st.selectbox("Moneda de Ingreso de Cruce", ["MXN", "USD"])
cruce_original = st.number_input(f"Ingreso de Cruce en {moneda_cruce}", min_value=0.0)
tipo_cambio_cruce = tipo_cambio_usd if moneda_cruce == "USD" else tipo_cambio_mxn
cruce_total = cruce_original * tipo_cambio_cruce

casetas = st.number_input("Costo de Casetas", min_value=0.0)
horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0)
lavado = st.number_input("Lavado Termo", min_value=0.0)
mov_local = st.number_input("Movimiento Local", min_value=0.0)
puntualidad = st.number_input("Puntualidad", min_value=0.0)
pension = st.number_input("Pensión", min_value=0.0)
estancia = st.number_input("Estancia", min_value=0.0)
fianza = st.number_input("Fianza termo Rentado/Externo", min_value=0.0)
renta = st.number_input("Renta de Termo", min_value=0.0)

if st.button("Guardar Ruta"):
    nueva_ruta = pd.DataFrame([{ 
        "Fecha": fecha,
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "KM": km,
        "Horas_Termo": horas_termo,
        "Casetas": casetas,
        "Lavado_Termo": lavado,
        "Movimiento_Local": mov_local,
        "Puntualidad": puntualidad,
        "Pension": pension,
        "Estancia": estancia,
        "Fianza_Termo": fianza,
        "Renta_Termo": renta,
        "Moneda": moneda,
        "Ingreso_Original": ingreso_original,
        "Ingreso_Total": ingreso_total,
        "Moneda_Cruce": moneda_cruce,
        "Cruce_Original": cruce_original,
        "Cruce_Total": cruce_total,
    }])

    if os.path.exists(RUTA_RUTAS):
        rutas_existentes = pd.read_csv(RUTA_RUTAS)
        rutas_actualizadas = pd.concat([rutas_existentes, nueva_ruta], ignore_index=True)
    else:
        rutas_actualizadas = nueva_ruta

    rutas_actualizadas.to_csv(RUTA_RUTAS, index=False)
    st.success("✅ Ruta guardada correctamente.")
    st.experimental_rerun()
