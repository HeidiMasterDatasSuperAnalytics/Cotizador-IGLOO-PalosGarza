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
        if not trafico or not unidad or not operador:
            st.error("❌ Todos los campos son obligatorios para registrar un tráfico.")
        else:
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
# 5. GESTIÓN DE PROGRAMACIONES
# =====================================
st.markdown("---")
st.subheader("🛠️ Gestión de Tráficos Programados")

if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)

    if "ID_Programacion" not in df_prog.columns:
        st.warning("⚠️ Algunos registros no tienen ID_Programacion y no se pueden mostrar aquí.")
    else:
        ids = df_prog["ID_Programacion"].dropna().unique()
        if len(ids) == 0:
            st.info("No hay programaciones válidas para editar o eliminar.")
        else:
            id_edit = st.selectbox("Selecciona un tráfico para editar o eliminar", ids)

            df_filtrado = df_prog[df_prog["ID_Programacion"] == id_edit].reset_index()
            st.write("**Vista previa del tráfico seleccionado:**")
            st.dataframe(df_filtrado)

            # Botón de eliminar
            if st.button("🗑️ Eliminar tráfico completo"):
                df_prog = df_prog[df_prog["ID_Programacion"] != id_edit]
                df_prog.to_csv(RUTA_PROG, index=False)
                st.success("✅ Tráfico eliminado exitosamente.")
                st.experimental_rerun()

            # Opción de editar unidad y operador del tramo IDA
            tramo_ida = df_filtrado[df_filtrado["Tramo"] == "IDA"].iloc[0]
            with st.form("editar_trafico"):
                nueva_unidad = st.text_input("Editar Unidad", value=tramo_ida["Unidad"])
                nuevo_operador = st.text_input("Editar Operador", value=tramo_ida["Operador"])
                editar_btn = st.form_submit_button("💾 Guardar cambios")

                if editar_btn:
                    df_prog.loc[(df_prog["ID_Programacion"] == id_edit) & (df_prog["Tramo"] == "IDA"), "Unidad"] = nueva_unidad
                    df_prog.loc[(df_prog["ID_Programacion"] == id_edit) & (df_prog["Tramo"] == "IDA"), "Operador"] = nuevo_operador
                    df_prog.to_csv(RUTA_PROG, index=False)
                    st.success("✅ Cambios guardados exitosamente.")
else:
    st.info("No hay programaciones registradas todavía.")
