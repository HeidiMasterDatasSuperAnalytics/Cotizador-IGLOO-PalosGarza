import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

st.title("🗓️ Programación de Viajes")

# Cargar rutas
if os.path.exists(RUTA_RUTAS):
    rutas_df = pd.read_csv(RUTA_RUTAS)
else:
    st.warning("No se encontró el archivo rutas_guardadas.csv")
    st.stop()

# Separar por tipo
impo = rutas_df[rutas_df["Tipo"] == "IMPO"]
expo = rutas_df[rutas_df["Tipo"] == "EXPO"]
vacio = rutas_df[rutas_df["Tipo"] == "VACIO"]

tipo = st.selectbox("Tipo de Ruta", ["IMPO", "EXPO", "VACIO"])

if tipo == "IMPO":
    candidatas = impo.copy()
elif tipo == "EXPO":
    candidatas = expo.copy()
else:
    candidatas = vacio.copy()

if candidatas.empty:
    st.warning(f"No hay rutas guardadas para tipo {tipo}")
    st.stop()

# Selección de ruta
candidatas["Ruta"] = candidatas["Origen"] + " → " + candidatas["Destino"]
rutas_opciones = candidatas["Ruta"].unique().tolist()
ruta_sel = st.selectbox("Selecciona la Ruta (Origen → Destino)", rutas_opciones)

filtro_ruta = candidatas[candidatas["Ruta"] == ruta_sel].copy()
filtro_ruta["Utilidad"] = filtro_ruta["Ingreso Total"] - filtro_ruta["Costo_Total_Ruta"]
filtro_ruta["% Utilidad"] = (filtro_ruta["Utilidad"] / filtro_ruta["Ingreso Total"] * 100).round(2)
filtro_ruta = filtro_ruta.sort_values(by="% Utilidad", ascending=False)

# Cliente ordenado por utilidad
st.markdown("### Selecciona Cliente")
cliente_idx = st.selectbox(
    "Cliente", filtro_ruta.index,
    format_func=lambda x: f"{filtro_ruta.loc[x, 'Cliente']} ({filtro_ruta.loc[x, '% Utilidad']:.2f}%)"
)
ruta_final = filtro_ruta.loc[cliente_idx]

st.markdown("---")
st.markdown("### 🚛 Datos del Viaje")
with st.form("programar_viaje"):
    fecha = st.date_input("Fecha de Viaje", value=datetime.today())
    trafico = st.text_input("Número de Tráfico")
    unidad = st.text_input("Unidad")
    operador = st.text_input("Nombre del Operador")

    guardar = st.form_submit_button("💾 Guardar Programación")

    if guardar:
        nuevo_viaje = ruta_final.copy()
        nuevo_viaje["Fecha Viaje"] = fecha
        nuevo_viaje["Número_Trafico"] = trafico
        nuevo_viaje["Unidad"] = unidad
        nuevo_viaje["Operador"] = operador
        nuevo_viaje["Ruta_Referencia"] = cliente_idx

        # Guardar en CSV
        if os.path.exists(RUTA_PROG):
            df_prog = pd.read_csv(RUTA_PROG)
        else:
            df_prog = pd.DataFrame()

        df_prog = pd.concat([df_prog, pd.DataFrame([nuevo_viaje])], ignore_index=True)
        df_prog.to_csv(RUTA_PROG, index=False)

        st.success("✅ Viaje programado exitosamente.")

st.markdown("---")
st.markdown("## 📋 Programación Registrada")

if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    columnas = ["Fecha Viaje", "Número_Trafico", "Unidad", "Operador", "Tipo", "Cliente", "Origen", "Destino", "Ingreso Total", "Costo_Total_Ruta", "Ingreso_Original", "Utilidad"]
    df_prog["Utilidad"] = df_prog["Ingreso Total"] - df_prog["Costo_Total_Ruta"]
    st.dataframe(df_prog[columnas], use_container_width=True)
    st.markdown(f"**Total viajes programados:** {len(df_prog)}")
else:
    st.info("Aún no se han programado viajes.")
