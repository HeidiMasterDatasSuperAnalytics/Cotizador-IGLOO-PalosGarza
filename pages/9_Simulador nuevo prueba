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

    if tipo_principal == "IMPO":
        cliente_impo = st.selectbox("Cliente Importación", impo_rutas["Cliente"].dropna().unique())
        rutas_impo = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
        impo_sel = st.selectbox("Ruta IMPO", rutas_impo.index.tolist(), format_func=lambda x: f"{rutas_impo.loc[x, 'Origen']} → {rutas_impo.loc[x, 'Destino']}")
        ruta_principal = rutas_impo.loc[impo_sel]

        usar_expo = st.checkbox("¿Agregar ruta EXPO?")
        if usar_expo and not expo_rutas.empty:
            cliente_expo = st.selectbox("Cliente Exportación", expo_rutas["Cliente"].dropna().unique())
            rutas_expo = expo_rutas[expo_rutas["Cliente"] == cliente_expo]
            expo_sel = st.selectbox("Ruta EXPO", rutas_expo.index.tolist(), format_func=lambda x: f"{rutas_expo.loc[x, 'Origen']} → {rutas_expo.loc[x, 'Destino']}")
            ruta_expo = rutas_expo.loc[expo_sel]
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

        usar_impo = st.checkbox("¿Agregar ruta IMPO?")
        if usar_impo and not impo_rutas.empty:
            cliente_impo = st.selectbox("Cliente Importación", impo_rutas["Cliente"].dropna().unique())
            rutas_impo = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
            impo_sel = st.selectbox("Ruta IMPO", rutas_impo.index.tolist(), format_func=lambda x: f"{rutas_impo.loc[x, 'Origen']} → {rutas_impo.loc[x, 'Destino']}")
            ruta_impo = rutas_impo.loc[impo_sel]
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
        if tipo_principal == "IMPO":
            if ruta_expo is not None:
                rutas_seleccionadas.append(ruta_expo)
        else:
            if ruta_impo is not None:
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
