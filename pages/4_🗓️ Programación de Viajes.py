import streamlit as st
import pandas as pd
import os
from datetime import datetime

RUTA_RUTAS = "rutas_guardadas.csv"
RUTA_PROG = "viajes_programados.csv"

st.title("🛣️ Programación de Viajes Avanzada IMPO ➔ VACÍO ➔ EXPO")

def safe(x):
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
# COMPLETAR Y SIMULAR AVANZADO
# =====================================
if not os.path.exists(RUTA_PROG) or not os.path.exists(RUTA_RUTAS):
    st.error("❌ Faltan archivos necesarios para continuar.")
    st.stop()

df_prog = pd.read_csv(RUTA_PROG)
df_rutas = cargar_rutas()

incompletos = df_prog.groupby("ID_Programacion").size().reset_index(name="count")
incompletos = incompletos[incompletos["count"] == 1]["ID_Programacion"]

if not incompletos.empty:
    id_sel = st.selectbox("Selecciona un tráfico pendiente", incompletos)
    ida = df_prog[df_prog["ID_Programacion"] == id_sel].iloc[0]
    destino_ida = ida["Destino"]
    tipo_ida = ida["Tipo"]

    tipo_regreso = "EXPO" if tipo_ida == "IMPO" else "IMPO"
    directas = df_rutas[(df_rutas["Tipo"] == tipo_regreso) & (df_rutas["Origen"] == destino_ida)].copy()

    if not directas.empty:
        # Hay rutas directas
        directas = directas.sort_values(by="% Utilidad", ascending=False)
        idx = st.selectbox("Cliente sugerido (por utilidad)", directas.index,
            format_func=lambda x: f"{directas.loc[x, 'Cliente']} - {directas.loc[x, 'Ruta']} ({directas.loc[x, '% Utilidad']:.2f}%)")
        vuelta = directas.loc[idx]
        rutas_seleccionadas = [ida, vuelta]
    else:
        # Buscar combinación VACÍO + EXPO
        vacios = df_rutas[(df_rutas["Tipo"] == "VACIO") & (df_rutas["Origen"] == destino_ida)].copy()
        mejor_combo = None
        mejor_utilidad = -999999

        for _, vacio in vacios.iterrows():
            origen_expo = vacio["Destino"]
            expo = df_rutas[(df_rutas["Tipo"] == tipo_regreso) & (df_rutas["Origen"] == origen_expo)]
            if not expo.empty:
                expo = expo.sort_values(by="% Utilidad", ascending=False).iloc[0]
                ingreso_total = safe(ida["Ingreso Total"]) + safe(expo["Ingreso Total"])
                costo_total = safe(ida["Costo_Total_Ruta"]) + safe(vacio["Costo_Total_Ruta"]) + safe(expo["Costo_Total_Ruta"])
                utilidad = ingreso_total - costo_total
                if utilidad > mejor_utilidad:
                    mejor_utilidad = utilidad
                    mejor_combo = (vacio, expo)

        if mejor_combo:
            vacio, expo = mejor_combo
            rutas_seleccionadas = [ida, vacio, expo]
        else:
            st.warning("❌ No se encontraron combinaciones de regreso disponibles.")
            st.stop()

    # Mostrar resumen
    st.header("📊 Ingresos y Utilidades")
    ingreso = sum(safe(r["Ingreso Total"]) for r in rutas_seleccionadas)
    costo = sum(safe(r["Costo_Total_Ruta"]) for r in rutas_seleccionadas)
    utilidad = ingreso - costo
    indirectos = ingreso * 0.35
    utilidad_neta = utilidad - indirectos

    st.metric("Ingreso Total", f"${ingreso:,.2f}")
    st.metric("Costo Total", f"${costo:,.2f}")
    st.metric("Utilidad Bruta", f"${utilidad:,.2f} ({(utilidad/ingreso*100):.2f}%)")
    st.metric("Costos Indirectos (35%)", f"${indirectos:,.2f}")
    st.metric("Utilidad Neta", f"${utilidad_neta:,.2f} ({(utilidad_neta/ingreso*100):.2f}%)")

    if st.button("💾 Guardar y cerrar tráfico"):
        nuevos_registros = []
        for tramo in rutas_seleccionadas[1:]:  # Solo registrar vacio + expo
            datos = tramo.copy()
            datos["Fecha"] = ida["Fecha"]
            datos["Número_Trafico"] = ida["Número_Trafico"]
            datos["Unidad"] = ida["Unidad"]
            datos["Operador"] = ida["Operador"]
            datos["ID_Programacion"] = ida["ID_Programacion"]
            datos["Tramo"] = "VUELTA"
            nuevos_registros.append(datos)
        guardar_programacion(pd.DataFrame(nuevos_registros))
        st.success("✅ Tráfico cerrado exitosamente.")
else:
    st.info("No hay tráficos pendientes.")
