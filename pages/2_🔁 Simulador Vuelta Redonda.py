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

        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)

        st.subheader("🧾 Detalle de Rutas")
        for ruta in rutas_seleccionadas:
            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Cliente']}**  
            - {ruta['Origen']} → {ruta['Destino']}  
            - Ingreso Total: ${safe_number(ruta['Ingreso Total']):,.2f}  
            - Costo Total Ruta: ${safe_number(ruta['Costo_Total_Ruta']):,.2f}
            """)

        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        porcentaje_utilidad_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.markdown("---")
        st.subheader("📊 Resultado General")

        st.markdown(f"<strong>Ingreso Total:</strong> <span style='font-weight:bold'>${ingreso_total:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"<strong>Costo Total:</strong> <span style='font-weight:bold'>${costo_total_general:,.2f}</span>", unsafe_allow_html=True)

        color_utilidad_bruta = "green" if utilidad_bruta >= 0 else "red"
        st.markdown(f"<strong>Utilidad Bruta:</strong> <span style='color:{color_utilidad_bruta}; font-weight:bold'>${utilidad_bruta:,.2f}</span>", unsafe_allow_html=True)

        color_porcentaje_bruta = "green" if porcentaje_utilidad_bruta >= 50 else "red"
        st.markdown(f"<strong>% Utilidad Bruta:</strong> <span style='color:{color_porcentaje_bruta}; font-weight:bold'>{porcentaje_utilidad_bruta:.2f}%</span>", unsafe_allow_html=True)

        st.markdown(f"<strong>Costos Indirectos (35%):</strong> <span style='font-weight:bold'>${costos_indirectos:,.2f}</span>", unsafe_allow_html=True)

        color_utilidad_neta = "green" if utilidad_neta >= 0 else "red"
        st.markdown(f"<strong>Utilidad Neta:</strong> <span style='color:{color_utilidad_neta}; font-weight:bold'>${utilidad_neta:,.2f}</span>", unsafe_allow_html=True)

        color_porcentaje_neta = "green" if porcentaje_utilidad_neta >= 15 else "red"
        st.markdown(f"<strong>% Utilidad Neta:</strong> <span style='color:{color_porcentaje_neta}; font-weight:bold'>{porcentaje_utilidad_neta:.2f}%</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📋 Resumen de Rutas")

        col1, col2, col3 = st.columns(3)

        def resumen_ruta(r):
            return [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Casetas')):,.2f}",
                f"Costo Cruce Convertido: ${safe_number(r.get('Costo Cruce Convertido')):,.2f}",
                "**Extras detallados:**",
                f"Lavado Termo: ${safe_number(r.get('Lavado_Termo')):,.2f}",
                f"Movimiento Local: ${safe_number(r.get('Movimiento_Local')):,.2f}",
                f"Puntualidad: ${safe_number(r.get('Puntualidad')):,.2f}",
                f"Pensión: ${safe_number(r.get('Pension')):,.2f}",
                f"Estancia: ${safe_number(r.get('Estancia')):,.2f}",
                f"Fianza Termo: ${safe_number(r.get('Fianza_Termo')):,.2f}",
                f"Renta Termo: ${safe_number(r.get('Renta_Termo')):,.2f}"
            ]

        with col1:
            st.markdown("**IMPO**")
            for line in resumen_ruta(ruta_impo):
                st.write(line)

        with col2:
            st.markdown("**VACÍO**")
            if ruta_vacio is not None:
                for line in resumen_ruta(ruta_vacio):
                    st.write(line)
            else:
                st.write("No aplica")

        with col3:
            st.markdown("**EXPO**")
            for line in resumen_ruta(ruta_expo):
                st.write(line)

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
