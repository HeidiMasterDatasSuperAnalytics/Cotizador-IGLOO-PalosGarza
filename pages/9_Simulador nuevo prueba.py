import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔁 Simulador de Vuelta Redonda")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]
    vacio_rutas = df[df["Tipo"] == "VACIO"]

    st.subheader("📌 Paso 1: Selección de ruta principal")
    tipo_principal = st.selectbox("¿Qué tipo de ruta deseas seleccionar primero?", ["IMPO", "EXPO"])

    ruta_principal = None
    ruta_vacio = None
    ruta_secundaria = None
    rutas_seleccionadas = []

    if tipo_principal == "IMPO":
        cliente = st.selectbox("Cliente IMPO", impo_rutas["Cliente"].dropna().unique())
        rutas = impo_rutas[impo_rutas["Cliente"] == cliente]
        idx = st.selectbox("Ruta IMPO", rutas.index.tolist(), format_func=lambda x: f"{rutas.loc[x, 'Origen']} → {rutas.loc[x, 'Destino']}")
        ruta_principal = rutas.loc[idx]
        rutas_seleccionadas.append(ruta_principal)

        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        destino_impo = ruta_principal["Destino"]
        vacio_candidatos = vacio_rutas[vacio_rutas["Origen"] == destino_impo]
        if not vacio_candidatos.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_impo + ")", vacio_candidatos.index.tolist(),
                                     format_func=lambda x: f"{vacio_candidatos.loc[x, 'Origen']} → {vacio_candidatos.loc[x, 'Destino']}")
            ruta_vacio = vacio_candidatos.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta EXPO sugerida (opcional)")
        if ruta_vacio is not None:
            destino_vacio = ruta_vacio["Destino"]
            candidatos = expo_rutas[expo_rutas["Origen"] == destino_vacio].copy()
        else:
            candidatos = expo_rutas[expo_rutas["Origen"] == destino_impo].copy()

        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos = candidatos.sort_values(by="Utilidad", ascending=False)
            expo_idx = st.selectbox("Ruta EXPO sugerida", candidatos.index.tolist(),
                                    format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})")
            ruta_secundaria = candidatos.loc[expo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    else:  # tipo_principal == "EXPO"
        cliente = st.selectbox("Cliente EXPO", expo_rutas["Cliente"].dropna().unique())
        rutas = expo_rutas[expo_rutas["Cliente"] == cliente]
        idx = st.selectbox("Ruta EXPO", rutas.index.tolist(), format_func=lambda x: f"{rutas.loc[x, 'Origen']} → {rutas.loc[x, 'Destino']}")
        ruta_principal = rutas.loc[idx]
        rutas_seleccionadas.append(ruta_principal)

        st.markdown("---")
        st.subheader("📌 Paso 2: Ruta VACÍA sugerida (opcional)")
        destino_expo = ruta_principal["Destino"]
        vacio_candidatos = vacio_rutas[vacio_rutas["Origen"] == destino_expo]
        if not vacio_candidatos.empty:
            vacio_idx = st.selectbox("Ruta VACÍA (Origen = " + destino_expo + ")", vacio_candidatos.index.tolist(),
                                     format_func=lambda x: f"{vacio_candidatos.loc[x, 'Origen']} → {vacio_candidatos.loc[x, 'Destino']}")
            ruta_vacio = vacio_candidatos.loc[vacio_idx]
            rutas_seleccionadas.append(ruta_vacio)

        st.markdown("---")
        st.subheader("📌 Paso 3: Ruta IMPO sugerida (opcional)")
        if ruta_vacio is not None:
            destino_vacio = ruta_vacio["Destino"]
            candidatos = impo_rutas[impo_rutas["Origen"] == destino_vacio].copy()
        else:
            candidatos = impo_rutas[impo_rutas["Origen"] == destino_expo].copy()

        if not candidatos.empty:
            candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
            candidatos = candidatos.sort_values(by="Utilidad", ascending=False)
            impo_idx = st.selectbox("Ruta IMPO sugerida", candidatos.index.tolist(),
                                    format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})")
            ruta_secundaria = candidatos.loc[impo_idx]
            rutas_seleccionadas.append(ruta_secundaria)

    if st.button("🚛 Simular Vuelta Redonda"):
        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.markdown("---")
        st.subheader("📊 Resultado General")
        st.markdown(f"**Ingreso Total:** ${ingreso_total:,.2f}")
        st.markdown(f"**Costo Total:** ${costo_total_general:,.2f}")
        st.markdown(f"**Utilidad Bruta:** ${utilidad_bruta:,.2f} ({porcentaje_utilidad_bruta:.2f}%)")
        st.markdown(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
        st.markdown(f"**Utilidad Neta:** ${utilidad_neta:,.2f} ({porcentaje_utilidad_neta:.2f}%)")

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
