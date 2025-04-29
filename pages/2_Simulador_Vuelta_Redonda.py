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
    col1, col2 = st.columns(2)

    with col1:
        cliente_impo = st.selectbox("Cliente Importación", impo_rutas["Cliente"].dropna().unique())
        rutas_impo = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
        impo_sel = st.selectbox("Ruta Importación", rutas_impo.index.tolist(), format_func=lambda x: f"{rutas_impo.loc[x, 'Origen']} → {rutas_impo.loc[x, 'Destino']}")

    with col2:
        cliente_expo = st.selectbox("Cliente Exportación", expo_rutas["Cliente"].dropna().unique())
        rutas_expo = expo_rutas[expo_rutas["Cliente"] == cliente_expo]
        expo_sel = st.selectbox("Ruta Exportación", rutas_expo.index.tolist(), format_func=lambda x: f"{rutas_expo.loc[x, 'Origen']} → {rutas_expo.loc[x, 'Destino']}")

    usar_vacio = st.checkbox("¿Agregar ruta VACÍA?")
    if usar_vacio and not vacio_rutas.empty:
        vacio_sel = st.selectbox("Ruta VACÍA (opcional)", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
    else:
        vacio_sel = None

    if st.button("🚛 Simular Vuelta Redonda"):
        ruta_impo = rutas_impo.loc[impo_sel]
        ruta_expo = rutas_expo.loc[expo_sel]
        ruta_vacio = vacio_rutas.loc[vacio_sel] if vacio_sel is not None else None

        rutas_seleccionadas = [ruta_impo]
        if ruta_vacio is not None:
            rutas_seleccionadas.append(ruta_vacio)
        rutas_seleccionadas.append(ruta_expo)

        ingreso_total = sum(safe_number(r.get("Ingreso_Original", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        st.subheader("🧾 Detalle de Rutas")
        for ruta in rutas_seleccionadas:
            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Cliente']}**  
            - {ruta['Origen']} → {ruta['Destino']}  
            - Ingreso Flete: ${safe_number(ruta['Ingreso_Original']):,.2f}  
            - Costo Total Ruta: ${safe_number(ruta['Costo_Total_Ruta']):,.2f}
            """)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.markdown("---")
        st.subheader("📊 Resultado General")
        st.write(f"**Ingreso Total:** ${ingreso_total:,.2f}")
        st.write(f"**Costo Total:** ${costo_total_general:,.2f}")
        st.write(f"**Utilidad Bruta:** ${utilidad_bruta:,.2f}")
        st.write(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
        st.write(f"**Utilidad Neta:** ${utilidad_neta:,.2f}")
        st.write(f"**% Utilidad Neta:** {porcentaje_utilidad:.2f}%")

        st.markdown("---")
        st.subheader("📋 Resumen de Rutas")

        col1, col2, col3 = st.columns(3)

        def resumen_ruta(r):
            return [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Costo_Casetas')):,.2f}",
                f"Cruce: ${safe_number(r.get('Costo_Cruce')):,.2f}",
                f"Extras: ${safe_number(r.get('Costo_Extras')):,.2f}"
            ]

        with col1:
            st.markdown("**IMPO**")
            for line in resumen_ruta(ruta_impo):
                st.write(line)

        with col2:
            st.markdown("**VACÍO**")
            if ruta_vacio is not None:
                resumen_vacio = [
                    f"Sueldo: ${safe_number(ruta_vacio.get('Sueldo_Operador')):,.2f}",
                    f"Diesel Camión: ${safe_number(ruta_vacio.get('Costo_Diesel_Camion')):,.2f}",
                    f"Extras: ${safe_number(ruta_vacio.get('Costo_Extras')):,.2f}"
                ]
                for line in resumen_vacio:
                    st.write(line)
            else:
                st.write("No aplica")

        with col3:
            st.markdown("**EXPO**")
            for line in resumen_ruta(ruta_expo):
                st.write(line)
else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
