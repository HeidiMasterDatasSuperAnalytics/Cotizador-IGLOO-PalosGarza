import streamlit as st
import pandas as pd
import os
import pdfkit
import streamlit.components.v1 as components

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("📄 Consulta Individual de Ruta")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    st.subheader("🔍 Selecciona la Ruta")
    index_sel = st.selectbox("Ruta", df.index.tolist(), format_func=lambda x: f"{df.loc[x, 'Tipo']} - {df.loc[x, 'Origen']} → {df.loc[x, 'Destino']}")

    ruta = df.loc[index_sel]

    # --- Cálculos
    ingreso_total = safe_number(ruta.get("Ingreso Total"))
    costo_total = safe_number(ruta.get("Costo_Total_Ruta"))
    utilidad_bruta = ingreso_total - costo_total
    costos_indirectos = ingreso_total * 0.35
    utilidad_neta = utilidad_bruta - costos_indirectos
    porcentaje_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
    porcentaje_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

    # --- Mostrar ingresos y utilidades
    st.markdown("## 💰 Ingresos y Utilidades")
    def color_text(valor, positivo=True, porcentaje=False):
        color = "green" if (valor >= 0 if positivo else valor >= 50 if porcentaje else valor >= 15) else "red"
        return f"<span style='color:{color}; font-weight:bold'>{valor:,.2f}{'%' if porcentaje else ''}</span>"

    st.markdown(f"- **Ingreso Total:** {color_text(ingreso_total)}")
    st.markdown(f"- **Costo Total Ruta:** {color_text(costo_total, positivo=False)}")
    st.markdown(f"- **Utilidad Bruta:** {color_text(utilidad_bruta)}")
    st.markdown(f"- **% Utilidad Bruta:** {color_text(porcentaje_bruta, porcentaje=True)}")
    st.markdown(f"- **Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
    st.markdown(f"- **Utilidad Neta:** {color_text(utilidad_neta)}")
    st.markdown(f"- **% Utilidad Neta:** {color_text(porcentaje_neta, porcentaje=True)}", unsafe_allow_html=True)

    # --- Mostrar en dos columnas
    st.markdown("## 📊 Detalle y Costos de la Ruta")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📌 Detalles")
        st.write(f"**Fecha:** {ruta.get('Fecha')}")
        st.write(f"**Tipo de Ruta:** {ruta.get('Tipo')}")
        st.write(f"**Cliente:** {ruta.get('Cliente')}")
        st.write(f"**Origen:** {ruta.get('Origen')}")
        st.write(f"**Destino:** {ruta.get('Destino')}")
        st.write(f"**Kilómetros:** {safe_number(ruta.get('KM'))}")
        st.write(f"**Horas Termo:** {safe_number(ruta.get('Horas_Termo'))}")

    with col2:
        st.markdown("### 💵 Costos")
        st.write(f"**Diesel Camión:** ${safe_number(ruta.get('Costo_Diesel_Camion')):,.2f}")
        st.write(f"**Diesel Termo:** ${safe_number(ruta.get('Costo_Diesel_Termo')):,.2f}")
        st.write(f"**Sueldo Operador:** ${safe_number(ruta.get('Sueldo_Operador')):,.2f}")
        st.write(f"**Bono:** ${safe_number(ruta.get('Bono')):,.2f}")
        st.write(f"**Casetas:** ${safe_number(ruta.get('Casetas')):,.2f}")
        st.write(f"**Costo Cruce:** ${safe_number(ruta.get('Costo Cruce Convertido')):,.2f}")
        st.write("**Extras:**")
        st.write(f"- Lavado Termo: ${safe_number(ruta.get('Lavado_Termo')):,.2f}")
        st.write(f"- Movimiento Local: ${safe_number(ruta.get('Movimiento_Local')):,.2f}")
        st.write(f"- Puntualidad: ${safe_number(ruta.get('Puntualidad')):,.2f}")
        st.write(f"- Pensión: ${safe_number(ruta.get('Pension')):,.2f}")
        st.write(f"- Estancia: ${safe_number(ruta.get('Estancia')):,.2f}")
        st.write(f"- Fianza Termo: ${safe_number(ruta.get('Fianza_Termo')):,.2f}")
        st.write(f"- Renta Termo: ${safe_number(ruta.get('Renta_Termo')):,.2f}")

    # --- Exportar a PDF
    st.markdown("---")
    if st.button("📄 Exportar a PDF"):
        html_content = f"""
        <h2>Consulta Individual de Ruta</h2>
        <p><b>Fecha:</b> {ruta.get('Fecha')}</p>
        <p><b>Ruta:</b> {ruta.get('Origen')} → {ruta.get('Destino')}</p>
        <p><b>Tipo:</b> {ruta.get('Tipo')} | <b>Cliente:</b> {ruta.get('Cliente')}</p>
        <h3>Ingresos y Utilidades</h3>
        <ul>
        <li>Ingreso Total: ${ingreso_total:,.2f}</li>
        <li>Costo Total: ${costo_total:,.2f}</li>
        <li>Utilidad Bruta: ${utilidad_bruta:,.2f} ({porcentaje_bruta:.2f}%)</li>
        <li>Costos Indirectos: ${costos_indirectos:,.2f}</li>
        <li>Utilidad Neta: ${utilidad_neta:,.2f} ({porcentaje_neta:.2f}%)</li>
        </ul>
        """

        pdfkit.from_string(html_content, "consulta_ruta.pdf")
        with open("consulta_ruta.pdf", "rb") as f:
            st.download_button("📥 Descargar PDF", f, file_name="consulta_ruta.pdf")

else:
    st.warning("⚠️ No hay rutas registradas para consultar.")

