# 5_🗓️ Programación de Viajes.py
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
    submit = st.form_submit_button("📅 Registrar Tráfico")

    if submit:
        fecha_str = fecha.strftime("%Y-%m-%d")
        datos = ruta_ida.copy()
        datos["Fecha"] = fecha_str
        datos["Número_Trafico"] = trafico
        datos["Unidad"] = unidad
        datos["Operador"] = operador
        datos["Tramo"] = "IDA"
        datos["ID_Programacion"] = f"{trafico}_{fecha_str}"
        guardar_programacion(pd.DataFrame([datos]))
        st.success("✅ Tráfico registrado exitosamente.")

# =====================================
# 2. COMPLETAR TRÁFICO + SIMULACIÓN
# =====================================
st.markdown("---")
st.header("🔁 Completar y Simular Tráfico - Persona 2")

if not os.path.exists(RUTA_PROG):
    st.info("No hay programaciones registradas todavía.")
    st.stop()

prog_df = pd.read_csv(RUTA_PROG)
if "ID_Programacion" not in prog_df.columns:
    st.warning("El archivo no contiene la columna 'ID_Programacion'.")
    st.stop()

tramos_capturados = prog_df.groupby("ID_Programacion").size().reset_index(name="Tramos")
tramos_incompletos = tramos_capturados[tramos_capturados["Tramos"] == 1]

if tramos_incompletos.empty:
    st.info("No hay tráficos pendientes por completar.")
else:
    id_sel = st.selectbox("Selecciona un tráfico pendiente", tramos_incompletos["ID_Programacion"])
    ida = prog_df[prog_df["ID_Programacion"] == id_sel].iloc[0]
    destino_ida = ida["Destino"]
    tipo_ida = ida["Tipo"]

    st.markdown(f"**Destino final del tramo registrado:** `{destino_ida}`")

    rutas_df = cargar_rutas()
    tipo_regreso = "EXPO" if tipo_ida == "IMPO" else "IMPO"
    candidatas = rutas_df[(rutas_df["Tipo"] == tipo_regreso) & (rutas_df["Origen"] == destino_ida)].copy()
    candidatas = candidatas.sort_values(by="% Utilidad", ascending=False)
    vacias = rutas_df[(rutas_df["Tipo"] == "VACIO") & (rutas_df["Origen"] == destino_ida)].copy()

    st.markdown("### 🚛 Opciones de Regreso")
    ruta_vuelta = None
    if not candidatas.empty:
        idx = st.selectbox("Cliente sugerido (ordenado por % utilidad)", candidatas.index,
            format_func=lambda x: f"{candidatas.loc[x, 'Cliente']} ({candidatas.loc[x, '% Utilidad']:.2f}%)")
        ruta_vuelta = candidatas.loc[idx]
    elif not vacias.empty:
        st.info("No hay ruta directa. Selecciona una ruta VACÍA")
        idx = st.selectbox("Ruta VACÍA", vacias.index,
            format_func=lambda x: f"{vacias.loc[x, 'Origen']} → {vacias.loc[x, 'Destino']}")
        ruta_vuelta = vacias.loc[idx]
    else:
        st.warning("No hay rutas de regreso disponibles.")

    if ruta_vuelta is not None:
        st.markdown("### 📊 Simulación del Viaje Completo")
        ingreso_total = safe_number(ida["Ingreso Total"]) + safe_number(ruta_vuelta["Ingreso Total"])
        costo_total = safe_number(ida["Costo_Total_Ruta"]) + safe_number(ruta_vuelta["Costo_Total_Ruta"])
        utilidad = ingreso_total - costo_total
        utilidad_neta = utilidad - (ingreso_total * 0.35)
        pct_bruta = (utilidad / ingreso_total * 100) if ingreso_total > 0 else 0
        pct_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.metric("Ingreso Total", f"${ingreso_total:,.2f}")
        st.metric("Costo Total", f"${costo_total:,.2f}")
        st.metric("Utilidad Bruta", f"${utilidad:,.2f} ({pct_bruta:.2f}%)")
        st.metric("Utilidad Neta", f"${utilidad_neta:,.2f} ({pct_neta:.2f}%)")

        if st.button("📅 Concluir Tráfico con esta Vuelta"):
            datos = ruta_vuelta.copy()
            datos["Fecha"] = ida["Fecha"]
            datos["Número_Trafico"] = ida["Número_Trafico"]
            datos["Unidad"] = ida["Unidad"]
            datos["Operador"] = ida["Operador"]
            datos["Tramo"] = "VUELTA"
            datos["ID_Programacion"] = ida["ID_Programacion"]
            guardar_programacion(pd.DataFrame([datos]))
            st.success("✅ Tráfico concluido exitosamente.")

# =====================================
# 3. TRÁFICOS COMPLETOS
# =====================================
st.markdown("---")
st.subheader("📊 Tráficos Concluidos")

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
        st.info("Aún no hay tráficos completos.")

# =====================================
# 4. TODOS LOS TRAMOS REGISTRADOS
# =====================================
st.markdown("---")
st.subheader("📄 Todos los Tramos Registrados")

if os.path.exists(RUTA_PROG):
    df = pd.read_csv(RUTA_PROG)
    df["Utilidad"] = df["Ingreso Total"] - df["Costo_Total_Ruta"]

    columnas = [
        "Fecha", "Tramo", "Número_Trafico", "Unidad", "Operador", "Tipo",
        "Cliente", "Origen", "Destino",
        "Ingreso Total", "Costo_Total_Ruta", "Utilidad", "ID_Programacion"
    ]

    st.dataframe(df[columnas], use_container_width=True)
    st.markdown(f"**Total de tramos registrados:** {len(df)}")
else:
    st.info("No hay tráficos registrados todavía.")
