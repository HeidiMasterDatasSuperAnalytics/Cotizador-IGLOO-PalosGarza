import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

st.title("🗓️ Programación de Viajes")

# Cargar rutas
if not os.path.exists(RUTA_RUTAS):
    st.warning("No se encontró el archivo rutas_guardadas.csv")
    st.stop()

rutas_df = pd.read_csv(RUTA_RUTAS)
impo = rutas_df[rutas_df["Tipo"] == "IMPO"]
expo = rutas_df[rutas_df["Tipo"] == "EXPO"]
vacio = rutas_df[rutas_df["Tipo"] == "VACIO"]

# Paso 1: Ruta principal
tipo = st.selectbox("Tipo de Ruta Principal", ["IMPO", "EXPO"])

if tipo == "IMPO":
    candidatas = impo.copy()
else:
    candidatas = expo.copy()

if candidatas.empty:
    st.warning(f"No hay rutas guardadas para tipo {tipo}")
    st.stop()

candidatas["Ruta"] = candidatas["Origen"] + " → " + candidatas["Destino"]
opciones_ruta = candidatas["Ruta"].unique().tolist()
ruta_sel = st.selectbox("Selecciona Ruta", opciones_ruta)

filtro = candidatas[candidatas["Ruta"] == ruta_sel].copy()
filtro["Utilidad"] = filtro["Ingreso Total"] - filtro["Costo_Total_Ruta"]
filtro["% Utilidad"] = (filtro["Utilidad"] / filtro["Ingreso Total"] * 100).round(2)
filtro = filtro.sort_values(by="% Utilidad", ascending=False)

st.markdown("### Cliente para la Ruta Principal")
cliente_idx = st.selectbox(
    "Cliente", filtro.index,
    format_func=lambda x: f"{filtro.loc[x, 'Cliente']} ({filtro.loc[x, '% Utilidad']:.2f}%)"
)
ruta_principal = filtro.loc[cliente_idx]
destino_ref = ruta_principal["Destino"]

# Paso 2: Sugerencias VACÍAS y Secundarias
st.markdown("---")
ruta_vacio = None
ruta_secundaria = None

if tipo == "IMPO":
    st.subheader("📌 Sugerencia: Ruta VACÍA desde IMPO")
    vacias = vacio[vacio["Origen"] == destino_ref].copy()
    if not vacias.empty:
        vacio_idx = st.selectbox("Ruta VACÍA sugerida", vacias.index,
            format_func=lambda x: f"{vacias.loc[x, 'Origen']} → {vacias.loc[x, 'Destino']}")
        ruta_vacio = vacias.loc[vacio_idx]

    st.subheader("📌 Sugerencia: Ruta EXPO")
    origen_expo = ruta_vacio["Destino"] if ruta_vacio is not None else destino_ref
    sugeridas = expo[expo["Origen"] == origen_expo].copy()
    if not sugeridas.empty:
        sugeridas["Utilidad"] = sugeridas["Ingreso Total"] - sugeridas["Costo_Total_Ruta"]
        sugeridas["% Utilidad"] = (sugeridas["Utilidad"] / sugeridas["Ingreso Total"] * 100).round(2)
        sugeridas = sugeridas.sort_values(by="% Utilidad", ascending=False)
        expo_idx = st.selectbox("Ruta EXPO sugerida", sugeridas.index,
            format_func=lambda x: f"{sugeridas.loc[x, 'Cliente']} ({sugeridas.loc[x, '% Utilidad']:.2f}%)")
        ruta_secundaria = sugeridas.loc[expo_idx]

elif tipo == "EXPO":
    st.subheader("📌 Sugerencia: Ruta VACÍA desde EXPO")
    vacias = vacio[vacio["Origen"] == destino_ref].copy()
    if not vacias.empty:
        vacio_idx = st.selectbox("Ruta VACÍA sugerida", vacias.index,
            format_func=lambda x: f"{vacias.loc[x, 'Origen']} → {vacias.loc[x, 'Destino']}")
        ruta_vacio = vacias.loc[vacio_idx]

    st.subheader("📌 Sugerencia: Ruta IMPO")
    origen_impo = ruta_vacio["Destino"] if ruta_vacio is not None else destino_ref
    sugeridas = impo[impo["Origen"] == origen_impo].copy()
    if not sugeridas.empty:
        sugeridas["Utilidad"] = sugeridas["Ingreso Total"] - sugeridas["Costo_Total_Ruta"]
        sugeridas["% Utilidad"] = (sugeridas["Utilidad"] / sugeridas["Ingreso Total"] * 100).round(2)
        sugeridas = sugeridas.sort_values(by="% Utilidad", ascending=False)
        impo_idx = st.selectbox("Ruta IMPO sugerida", sugeridas.index,
            format_func=lambda x: f"{sugeridas.loc[x, 'Cliente']} ({sugeridas.loc[x, '% Utilidad']:.2f}%)")
        ruta_secundaria = sugeridas.loc[impo_idx]

# Paso 3: Datos del Viaje
st.markdown("---")
st.subheader("🚛 Datos Generales del Viaje")
with st.form("form_viaje"):
    fecha = st.date_input("Fecha de Viaje", value=datetime.today())
    trafico = st.text_input("Número de Tráfico")
    unidad = st.text_input("Unidad")
    operador = st.text_input("Nombre del Operador")

    submit = st.form_submit_button("💾 Guardar Programación")

    if submit:
        viajes = []

        def agregar_ruta(ruta, tramo):
            r = ruta.copy()
            r["Fecha Viaje"] = fecha
            r["Número_Trafico"] = trafico
            r["Unidad"] = unidad
            r["Operador"] = operador
            r["Tramo"] = tramo
            return r

        viajes.append(agregar_ruta(ruta_principal, "PRINCIPAL"))
        if ruta_vacio is not None:
            viajes.append(agregar_ruta(ruta_vacio, "VACIO"))
        if ruta_secundaria is not None:
            viajes.append(agregar_ruta(ruta_secundaria, "SECUNDARIA"))

        df_viajes = pd.DataFrame(viajes)

        if os.path.exists(RUTA_PROG):
            prog_existente = pd.read_csv(RUTA_PROG)
            df_viajes = pd.concat([prog_existente, df_viajes], ignore_index=True)

        df_viajes.to_csv(RUTA_PROG, index=False)
        st.success("✅ Programación guardada con todos los tramos.")

# Paso 4: Mostrar programación
st.markdown("---")
st.subheader("📋 Programación Guardada")
if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    df_prog["Utilidad"] = df_prog["Ingreso Total"] - df_prog["Costo_Total_Ruta"]
    mostrar = df_prog[[
        "Fecha Viaje", "Tramo", "Número_Trafico", "Unidad", "Operador",
        "Tipo", "Cliente", "Origen", "Destino", "Ingreso Total", "Costo_Total_Ruta", "Utilidad"
    ]]
    st.dataframe(mostrar, use_container_width=True)
else:
    st.info("No hay viajes programados todavía.")
