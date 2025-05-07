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

    st.subheader("📌 Selección de Rutas")
    
    tipo_principal = st.selectbox("Selecciona tipo principal", ["IMPO", "EXPO"])

    ruta_sugerida = None  # Inicializar

    if tipo_principal == "IMPO":
        cliente_impo = st.selectbox("Cliente Importación", impo_rutas["Cliente"].dropna().unique())
        rutas_impo = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
        impo_sel = st.selectbox("Ruta IMPO", rutas_impo.index.tolist(), format_func=lambda x: f"{rutas_impo.loc[x, 'Origen']} → {rutas_impo.loc[x, 'Destino']}")
        ruta_principal = rutas_impo.loc[impo_sel]

        # 🔍 Sugerencia automática de EXPO conectada
        destino_ref = ruta_principal["Destino"]
        candidatos = expo_rutas[expo_rutas["Origen"] == destino_ref].copy()
        candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
        candidatos = candidatos.sort_values(by="Utilidad", ascending=False)

        usar_expo = st.checkbox("¿Agregar ruta EXPO?")
        if usar_expo and not candidatos.empty:
            ruta_sugerida_sel = st.selectbox(
                "Ruta EXPO sugerida (ordenada por utilidad)",
                candidatos.index.tolist(),
                format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})"
            )
            ruta_expo = candidatos.loc[ruta_sugerida_sel]
        else:
            ruta_expo = None

        usar_vacio = st.checkbox("¿Agregar ruta VACÍA?")
        if usar_vacio and not vacio_rutas.empty:
            vacio_sel = st.selectbox("Ruta VACÍA", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
            ruta_vacio = vacio_rutas.loc[vacio_sel]
        else:
            ruta_vacio = None

    else:  # tipo_principal == "EXPO"
        cliente_expo = st.selectbox("Cliente Exportación", expo_rutas["Cliente"].dropna().unique())
        rutas_expo = expo_rutas[expo_rutas["Cliente"] == cliente_expo]
        expo_sel = st.selectbox("Ruta EXPO", rutas_expo.index.tolist(), format_func=lambda x: f"{rutas_expo.loc[x, 'Origen']} → {rutas_expo.loc[x, 'Destino']}")
        ruta_principal = rutas_expo.loc[expo_sel]

        # 🔍 Sugerencia automática de IMPO conectada
        destino_ref = ruta_principal["Destino"]
        candidatos = impo_rutas[impo_rutas["Origen"] == destino_ref].copy()
        candidatos["Utilidad"] = candidatos["Ingreso Total"] - candidatos["Costo_Total_Ruta"]
        candidatos = candidatos.sort_values(by="Utilidad", ascending=False)

        usar_impo = st.checkbox("¿Agregar ruta IMPO?")
        if usar_impo and not candidatos.empty:
            ruta_sugerida_sel = st.selectbox(
                "Ruta IMPO sugerida (ordenada por utilidad)",
                candidatos.index.tolist(),
                format_func=lambda x: f"{candidatos.loc[x, 'Origen']} → {candidatos.loc[x, 'Destino']} (${candidatos.loc[x, 'Utilidad']:.2f})"
            )
            ruta_impo = candidatos.loc[ruta_sugerida_sel]
        else:
            ruta_impo = None

        usar_vacio = st.checkbox("¿Agregar ruta VACÍA?")
        if usar_vacio and not vacio_rutas.empty:
            vacio_sel = st.selectbox("Ruta VACÍA", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
            ruta_vacio = vacio_rutas.loc[vacio_sel]
        else:
            ruta_vacio = None

    if st.button("🚛 Simular Vuelta Redonda"):
        rutas_seleccionadas = [ruta_principal]
        if tipo_principal == "IMPO" and 'ruta_expo' in locals() and ruta_expo is not None:
            rutas_seleccionadas.append(ruta_expo)
        elif tipo_principal == "EXPO" and 'ruta_impo' in locals() and ruta_impo is not None:
            rutas_seleccionadas.append(ruta_impo)

        if 'ruta_vacio' in locals() and ruta_vacio is not None:
            rutas_seleccionadas.append(ruta_vacio)

        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.subheader("📊 Resultado General")
        st.markdown(f"**Ingreso Total:** ${ingreso_total:,.2f}")
        st.markdown(f"**Costo Total:** ${costo_total_general:,.2f}")
        st.markdown(f"**Utilidad Bruta:** ${utilidad_bruta:,.2f} ({porcentaje_utilidad_bruta:.2f}%)")
        st.markdown(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
        st.markdown(f"**Utilidad Neta:** ${utilidad_neta:,.2f} ({porcentaje_utilidad_neta:.2f}%)")

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")

