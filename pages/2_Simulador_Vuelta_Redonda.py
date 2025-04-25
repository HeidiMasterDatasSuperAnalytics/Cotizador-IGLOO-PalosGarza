import streamlit as st
import pandas as pd
import os

st.title("# Simulador de Vuelta Redonda")

FILE = "rutas_guardadas.csv"

def calcular_utilidad(impo, expo, datos_generales):
    ingreso_total = impo["Ingreso_Total"] + expo["Ingreso_Total"]
    costo_total = impo["Costo_Total"] + expo["Costo_Total"]
    utilidad = ingreso_total - costo_total
    porcentaje_utilidad = (utilidad / ingreso_total) * 100 if ingreso_total > 0 else 0
    return utilidad, porcentaje_utilidad

if os.path.exists(FILE):
    df = pd.read_csv(FILE)

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]

    st.subheader("Selecciona rutas para simular")

    impo_sel = st.selectbox("Ruta de Importación", impo_rutas.index.tolist(), format_func=lambda x: f"{impo_rutas.loc[x, 'Origen']} → {impo_rutas.loc[x, 'Destino']}")
    expo_sel = st.selectbox("Ruta de Exportación", expo_rutas.index.tolist(), format_func=lambda x: f"{expo_rutas.loc[x, 'Origen']} → {expo_rutas.loc[x, 'Destino']}")

    if st.button("Simular Vuelta Redonda"):
        impo = impo_rutas.loc[impo_sel]
        expo = expo_rutas.loc[expo_sel]

        datos_generales = {
            "Rendimiento Camion": 2.5,
            "Costo Diesel": 24,
        }

        utilidad, porcentaje_utilidad = calcular_utilidad(impo, expo, datos_generales)

        st.success(f"Utilidad estimada: ${utilidad:,.2f}")
        st.info(f"Rentabilidad sobre ingresos: {porcentaje_utilidad:.2f}%")

else:
    st.warning("No hay rutas guardadas todavía para simular.")
