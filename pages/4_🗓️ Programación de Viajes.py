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
# 2. VER, EDITAR, ELIMINAR
# =====================================
if os.path.exists(RUTA_PROG):
    df_prog = pd.read_csv(RUTA_PROG)
    st.markdown("---")
    st.subheader("📋 Programaciones Registradas")

    if "ID_Programacion" in df_prog.columns:
        st.dataframe(df_prog, use_container_width=True)

        ids = df_prog["ID_Programacion"].dropna().unique()
        id_edit = st.selectbox("Selecciona un tráfico para editar o eliminar", ids)
        df_filtrado = df_prog[df_prog["ID_Programacion"] == id_edit].reset_index()
        st.write("**Vista previa del tráfico seleccionado:**")
        st.dataframe(df_filtrado)

        if st.button("🗑️ Eliminar tráfico completo"):
            df_prog = df_prog[df_prog["ID_Programacion"] != id_edit]
            df_prog.to_csv(RUTA_PROG, index=False)
            st.success("✅ Tráfico eliminado exitosamente.")
            st.experimental_rerun()

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

# =====================================
# 3. COMPLETAR Y SIMULAR TRÁFICO
# =====================================
st.markdown("---")
st.title("🔁 Completar y Simular Tráfico Detallado")

def safe(x): return 0 if pd.isna(x) or x is None else x

def calcular_utilidad(ida, vuelta):
    ingreso = safe(ida["Ingreso Total"]) + safe(vuelta["Ingreso Total"])
    costo = safe(ida["Costo_Total_Ruta"]) + safe(vuelta["Costo_Total_Ruta"])
    utilidad = ingreso - costo
    indirectos = ingreso * 0.35
    utilidad_neta = utilidad - indirectos
    return ingreso, costo, utilidad, indirectos, utilidad_neta

def cargar_resumen(ruta, titulo):
    resumen = {
        "KM": ruta.get("KM", "No aplica"),
        "Diesel Camión": f"${safe(ruta.get("Costo Diesel Camion", 0)):,.2f}",
        "Diesel Termo": f"${safe(ruta.get("Costo Diesel Termo", 0)):,.2f}",
        "Sueldo": f"${safe(ruta.get("Sueldo Operador", 0)):,.2f}",
        "Casetas": f"${safe(ruta.get("Casetas", 0)):,.2f}",
        "Costo Cruce Convertido": f"${safe(ruta.get("Costo Cruce Convertido", 0)):,.2f}",
        "Extras": {
            "Lavado Termo": safe(ruta.get("Lavado Termo", 0)),
            "Movimiento Local": safe(ruta.get("Movimiento Local", 0)),
            "Puntualidad": safe(ruta.get("Puntualidad", 0)),
            "Pensión": safe(ruta.get("Pension", 0)),
            "Estancia": safe(ruta.get("Estancia", 0)),
            "Fianza Termo": safe(ruta.get("Fianza Termo", 0)),
            "Renta Termo": safe(ruta.get("Renta Termo", 0))
        }
    }
    return resumen

def mostrar_resumen(nombre, resumen):
    st.markdown(f"#### {nombre}")
    for k, v in resumen.items():
        if k == "Extras":
            st.markdown("**Extras detallados:**")
            for extra, val in v.items():
                st.markdown(f"- {extra}: ${val:,.2f}")
        else:
            st.markdown(f"- {k}: {v}")

if not os.path.exists(RUTA_PROG) or not os.path.exists(RUTA_RUTAS):
    st.error("❌ Faltan archivos necesarios para continuar.")
    st.stop()

df_prog = pd.read_csv(RUTA_PROG)
df_rutas = pd.read_csv(RUTA_RUTAS)

incompletos = df_prog.groupby("ID_Programacion").size().reset_index(name="count")
incompletos = incompletos[incompletos["count"] == 1]["ID_Programacion"]

if not incompletos.empty:
    id_sel = st.selectbox("Selecciona un tráfico pendiente", incompletos)
    ida = df_prog[df_prog["ID_Programacion"] == id_sel].iloc[0]
    destino_ida = ida["Destino"]
    tipo_ida = ida["Tipo"]

    tipo_regreso = "EXPO" if tipo_ida == "IMPO" else "IMPO"
    directas = df_rutas[(df_rutas["Tipo"] == tipo_regreso) & (df_rutas["Origen"] == destino_ida)].copy()
    directas["Ruta"] = directas["Origen"] + " → " + directas["Destino"]
    directas = directas.sort_values(by="% Utilidad", ascending=False)

    if not directas.empty:
        idx = st.selectbox("Cliente sugerido (por utilidad)", directas.index,
            format_func=lambda x: f"{directas.loc[x, 'Cliente']} - {directas.loc[x, 'Ruta']} ({directas.loc[x, '% Utilidad']:.2f}%)")
        vuelta = directas.loc[idx]

        ingreso, costo, utilidad, indirectos, utilidad_neta = calcular_utilidad(ida, vuelta)

        st.header("📊 Ingresos y Utilidades")
        st.markdown(f"- **Ingreso Total:** ${ingreso:,.2f}")
        st.markdown(f"- **Costo Total:** ${costo:,.2f}")
        st.markdown(f"- **Utilidad Bruta:** ${utilidad:,.2f}")
        st.markdown(f"- **% Utilidad Bruta:** {utilidad / ingreso * 100:.2f}%")
        st.markdown(f"- **Costos Indirectos (35%):** ${indirectos:,.2f}")
        st.markdown(f"- **Utilidad Neta:** ${utilidad_neta:,.2f}")
        st.markdown(f"- **% Utilidad Neta:** {utilidad_neta / ingreso * 100:.2f}%")

        st.header("📋 Resumen de Rutas")
        mostrar_resumen("IDA", cargar_resumen(ida, "IDA"))
        mostrar_resumen("VUELTA", cargar_resumen(vuelta, "VUELTA"))
    else:
        st.warning("No se encontraron rutas de regreso desde ese destino.")
else:
    st.info("No hay tráficos pendientes.")
