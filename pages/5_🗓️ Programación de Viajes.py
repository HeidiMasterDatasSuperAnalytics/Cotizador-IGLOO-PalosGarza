import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

st.title("🗓️ Programación de Viajes")

def safe_number(x):
    return 0 if pd.isna(x) or x is None else x

def cargar_rutas():
    if not os.path.exists(RUTA_RUTAS):
        st.error("No se encontró rutas_guardadas.csv")
        st.stop()
    df = pd.read_csv(RUTA_RUTAS)
    df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]
    df["% Utilidad"] = (df["Utilidad"] / df["Ingreso Total"] * 100).round(2)
    df["Ruta"] = df["Origen"] + " → " + df["Destino"]
    return df

def guardar_programacion(df_nueva):
    if os.path.exists(RUTA_PROG):
        df_prog = pd.read_csv(RUTA_PROG)
        df_total = pd.concat([df_prog, df_nueva], ignore_index=True)
    else:
        df_total = df_nueva
    df_total.to_csv(RUTA_PROG, index=False)

# =====================================
# 1. REGISTRO DE TRÁFICO (PERSONA 1)
# =====================================
st.header("🚛 Registro de Tráfico - Persona 1")

rutas_df = cargar_rutas()
tipo = st.selectbox("Tipo de ruta (ida)", ["IMPO", "EXPO"])
rutas_tipo = rutas_df[rutas_df["Tipo"] == tipo].copy()

if rutas_tipo.empty:
    st.info("No hay rutas registradas de este tipo.")
    st.stop()

ruta_sel = st.selectbox("Selecciona una ruta (Origen → Destino)", rutas_tipo["Ruta"].unique())
rutas_filtradas = rutas_tipo[rutas_tipo["Ruta"] == ruta_sel].copy()
rutas_filtradas = rutas_filtradas.sort_values(by="% Utilidad", ascending=False)

st.markdown("### Selecciona Cliente (ordenado por % utilidad)")
cliente_idx = st.selectbox("Cliente", rutas_filtradas.index,
                           format_func=lambda x: f"{rutas_filtradas.loc[x, 'Cliente']} ({rutas_filtradas.loc[x, '% Utilidad']:.2f}%)")
ruta_ida = rutas_filtradas.loc[cliente_idx]

with st.form("registro_trafico"):
    st.subheader("📝 Datos del tráfico")
    fecha = st.date_input("Fecha de tráfico", value=datetime.today())
    trafico = st.text_input("Número de Tráfico")
    unidad = st.text_input("Unidad")
    operador = st.text_input("Operador")
    submit = st.form_submit_button("💾 Registrar Tráfico")

    if submit:
        datos = ruta_ida.copy()
        datos["Fecha"] = fecha
        datos["Número_Trafico"] = trafico
        datos["Unidad"] = unidad
        datos["Operador"] = operador
        datos["Tramo"] = "IDA"
        datos["ID_Programacion"] = f"{trafico}_{fecha}"
        guardar_programacion(pd.DataFrame([datos]))
        st.success("✅ Tráfico registrado exitosamente.")

# =====================================
# 2. COMPLETAR TRÁFICO (PERSONA 2)
# =====================================
st.markdown("---")
st.header("🔁 Completar Tráfico - Persona 2")

if not os.path.exists(RUTA_PROG):
    st.info("No hay programaciones registradas todavía.")
    st.stop()

prog_df = pd.read_csv(RUTA_PROG)

# Identificar ID de programaciones con solo un tramo
tramos_capturados = prog_df.groupby("ID_Programacion").size().reset_index(name="Tramos")
tramos_incompletos = tramos_capturados[tramos_capturados["Tramos"] == 1]

if tramos_incompletos.empty:
    st.info("No hay programaciones pendientes de completar.")
    st.stop()

id_sel = st.selectbox("Selecciona tráfico pendiente", tramos_incompletos["ID_Programacion"])
ida = prog_df[prog_df["ID_Programacion"] == id_sel].iloc[0]
destino_ida = ida["Destino"]
tipo_ida = ida["Tipo"]

st.markdown(f"**Destino final del tramo registrado:** `{destino_ida}`")

rutas_df = cargar_rutas()

# Determinar tipo de ruta de regreso
tipo_regreso = "EXPO" if tipo_ida == "IMPO" else "IMPO"
candidatas = rutas_df[(rutas_df["Tipo"] == tipo_regreso) & (rutas_df["Origen"] == destino_ida)].copy()
candidatas = candidatas.sort_values(by="% Utilidad", ascending=False)

vacias = rutas_df[(rutas_df["Tipo"] == "VACIO") & (rutas_df["Origen"] == destino_ida)].copy()

st.markdown("### 🚛 Ruta de regreso sugerida")
if not candidatas.empty:
    idx = st.selectbox("Cliente (ordenado por % utilidad)", candidatas.index,
        format_func=lambda x: f"{candidatas.loc[x, 'Cliente']} ({candidatas.loc[x, '% Utilidad']:.2f}%)")
    ruta_regreso = candidatas.loc[idx]
else:
    st.info("No hay ruta directa. Selecciona una ruta VACÍA")
    if vacias.empty:
        st.warning("No hay rutas vacías disponibles.")
        st.stop()
    idx = st.selectbox("Ruta VACÍA", vacias.index,
        format_func=lambda x: f"{vacias.loc[x, 'Origen']} → {vacias.loc[x, 'Destino']}")
    ruta_regreso = vacias.loc[idx]

if st.button("💾 Guardar ruta de regreso"):
    datos = ruta_regreso.copy()
    datos["Fecha"] = ida["Fecha"]
    datos["Número_Trafico"] = ida["Número_Trafico"]
    datos["Unidad"] = ida["Unidad"]
    datos["Operador"] = ida["Operador"]
    datos["Tramo"] = "VUELTA"
    datos["ID_Programacion"] = ida["ID_Programacion"]

    guardar_programacion(pd.DataFrame([datos]))
    st.success("✅ Vuelta registrada. Tráfico completado.")

# =====================================
# 3. SIMULACIÓN FINAL DE TRÁFICOS COMPLETOS
# =====================================
st.markdown("---")
st.subheader("📊 Simulación de Tráficos Completos")

if os.path.exists(RUTA_PROG):
    df = pd.read_csv(RUTA_PROG)
    df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]

    completos = df.groupby("ID_Programacion").size().reset_index(name="Tramos")
    ids_completos = completos[completos["Tramos"] == 2]["ID_Programacion"]
    df_completos = df[df["ID_Programacion"].isin(ids_completos)].copy()

    if not df_completos.empty:
        resumen = df_completos.groupby("ID_Programacion").agg({
            "Ingreso Total": "sum",
            "Costo_Total_Ruta": "sum",
            "Utilidad": "sum"
        }).reset_index()

        resumen["% Utilidad Bruta"] = (resumen["Utilidad"] / resumen["Ingreso Total"] * 100).round(2)
        resumen["Costos Indirectos"] = resumen["Ingreso Total"] * 0.35
        resumen["Utilidad Neta"] = resumen["Utilidad"] - resumen["Costos Indirectos"]
        resumen["% Utilidad Neta"] = (resumen["Utilidad Neta"] / resumen["Ingreso Total"] * 100).round(2)

        st.dataframe(resumen, use_container_width=True)
    else:
        st.info("Aún no hay programaciones completas.")
else:
    st.info("No hay viajes programados todavía.")
