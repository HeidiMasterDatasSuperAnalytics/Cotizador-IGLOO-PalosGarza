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
    df = pd.DataFrame(columns=["Tipo", "Cliente", "Origen", "Destino", "KM", "Horas_Termo", "Ingreso_Total", "Costo_Diesel", "Costo_Total"])

datos = load_datos_generales()

st.subheader("Formulario para agregar nueva ruta")

tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])
cliente = st.text_input("Nombre del Cliente (opcional para VACIO)")
origen = st.text_input("Origen")
destino = st.text_input("Destino")
km = st.number_input("Kilómetros recorridos", min_value=0.0)
horas_termo = st.number_input("Horas de uso del Termo", min_value=0.0)
ingreso_total = st.number_input("Ingreso Total Estimado (MXN)", min_value=0.0)

# Cálculo de diesel
rendimiento = float(datos.get("Rendimiento Camion", 2.5))
diesel = float(datos.get("Costo Diesel", 24))
costo_diesel = (km / rendimiento) * diesel if rendimiento > 0 else 0

st.write(f"**Costo Diesel Estimado:** ${costo_diesel:,.2f}")

if st.button("Guardar Ruta"):
    nueva_ruta = pd.DataFrame([{
        "Tipo": tipo,
        "Cliente": cliente,
        "Origen": origen,
        "Destino": destino,
        "KM": km,
        "Horas_Termo": horas_termo,
        "Ingreso_Total": ingreso_total,
        "Costo_Diesel": costo_diesel,
        "Costo_Total": costo_diesel  # Sueldo operador se calculará en el simulador
    }])
    df = pd.concat([df, nueva_ruta], ignore_index=True)
    df.to_csv(FILE, index=False)
    st.success("Ruta guardada exitosamente.")
    st.experimental_rerun()
