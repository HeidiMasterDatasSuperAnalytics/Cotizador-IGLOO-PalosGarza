import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

st.title("🗓️ Programación de Viajes")

def safe_number(x):
    return 0 if pd.isna(x) or x is None else x

# =====================================
# FUNCIONES AUXILIARES
# =====================================
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
# 1. CAPTURA NUEVO TRÁFICO (PERSONA 1)
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
        datos["Estado"] = "INCOMPLETO"
        datos["ID_Programacion"] = f"{trafico}_{fecha}"
        guardar_programacion(pd.DataFrame([datos]))
        st.success("✅ Tráfico registrado exitosamente.")

# =====================================
# 2. COMPLETAR VUELTA (PERSONA 2)
# =====================================
st.markdown("---")
st.header("🔁 Completar Tráfico - Persona 2")

if not os.path.exists(RUTA_PROG):
    st.info("No hay programaciones registradas todavía.")
    st.stop()

prog_df = pd.read_csv(RUTA_PROG)
prog_incompleto = prog_df[prog_df["Estado"] == "INCOMPLETO"]

if prog_incompleto.empty:
    st.info("No hay tráficos pendientes de completar.")
    st.stop()

id_sel = st.selectbox("Selecciona un tráfico pendiente", prog_incompleto["ID_Programacion"].unique())
trafico_base = prog_incompleto[prog_incompleto["ID_Programacion"] == id_sel].iloc[0]

tipo_ida = trafico_base["Tipo"]
destino_ida = trafico_base["Destino"]

st.markdown(f"**Destino final del tráfico de ida:** `{destino_ida}`")

# Buscar rutas sugeridas de regreso
rutas_df = cargar_rutas()
if tipo_ida == "IMPO":
    tipo_regreso = "EXPO"
elif tipo_ida == "EXPO":
    tipo_regreso = "IMPO"
else:
    tipo_regreso = None

rutas_vuelta = rutas_df[(rutas_df["Tipo"] == tipo_regreso) & (rutas_df["Origen"] == destino_ida)].copy()
vacias = rutas_df[(rutas_df["Tipo"] == "VACIO") & (rutas_df["Origen"] == destino_ida)].copy()

if rutas_vuelta.empty and vacias.empty:
    st.warning("⚠️ No se encontraron rutas de regreso desde ese destino.")
    st.stop()

# Mostrar sugerencias
st.markdown("### 🚛 Ruta de Regreso")
if not rutas_vuelta.empty:
    rutas_vuelta = rutas_vuelta.sort_values(by="% Utilidad", ascending=False)
    idx_regreso = st.selectbox("Cliente sugerido (ordenado por % utilidad)", rutas_vuelta.index,
        format_func=lambda x: f"{rutas_vuelta.loc[x, 'Cliente']} ({rutas_vuelta.loc[x, '% Utilidad']:.2f}%)")
    ruta_vuelta = rutas_vuelta.loc[idx_regreso]
else:
    st.info("No hay rutas directas. Selecciona una ruta VACÍA")
    idx_vacio = st.selectbox("Ruta VACÍA disponible", vacias.index,
        format_func=lambda x: f"{vacias.loc[x, 'Origen']} → {vacias.loc[x, 'Destino']}")
    ruta_vuelta = vacias.loc[idx_vacio]

if st.button("💾 Guardar regreso y completar tráfico"):
    datos = ruta_vuelta.copy()
    datos["Fecha"] = trafico_base["Fecha"]
    datos["Número_Trafico"] = trafico_base["Número_Trafico"]
    datos["Unidad"] = trafico_base["Unidad"]
    datos["Operador"] = trafico_base["Operador"]
    datos["Tramo"] = "VUELTA"
    datos["Estado"] = "COMPLETO"
    datos["ID_Programacion"] = trafico_base["ID_Programacion"]

    guardar_programacion(pd.DataFrame([datos]))

    # Actualizar estado de ida
    prog_df.loc[prog_df["ID_Programacion"] == id_sel, "Estado"] = "COMPLETO"
    prog_df.to_csv(RUTA_PROG, index=False)
    st.success("✅ Vuelta registrada. Programación completada.")

# =====================================
# 3. TABLA COMPLETA
# =====================================
st.markdown("---")
st.subheader("📋 Programaciones Guardadas")

if os.path.exists(RUTA_PROG):
    df = pd.read_csv(RUTA_PROG)
    df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]
    mostrar = df[[
        "Fecha", "Tramo", "Estado", "Número_Trafico", "Unidad", "Operador", "Tipo", "Cliente",
        "Origen", "Destino", "Ingreso Total", "Costo_Total_Ruta", "Utilidad"
    ]]
    st.dataframe(mostrar, use_container_width=True)
