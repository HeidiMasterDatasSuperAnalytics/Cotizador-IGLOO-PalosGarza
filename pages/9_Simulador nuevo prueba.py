import streamlit as st
import pandas as pd
import os
import pdfkit

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔁 Simulador de Vuelta Redonda")

def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

def generar_html_detalle(rutas, ingreso_total, costo_total_general, utilidad_bruta, pct_bruta, costos_indirectos, utilidad_neta, pct_neta):
    html = "<h2>📄 Detalle de Rutas</h2>"
    for r in rutas:
        html += f"""
        <p><strong>{r['Tipo']} — {r['Cliente']}</strong><br>
        {r['Origen']} → {r['Destino']}<br>
        Ingreso Original: ${safe_number(r['Ingreso_Original']):,.2f} {r.get('Moneda_Ingreso', '')} @ TC {safe_number(r.get('Tipo_Cambio_Ingreso')):,.2f}<br>
        Ingreso Total: ${safe_number(r['Ingreso Total']):,.2f}<br>
        Costo Total Ruta: ${safe_number(r['Costo_Total_Ruta']):,.2f}</p>
        """

    html += f"""
    <hr><h2>📊 Resultado General</h2>
    <p><strong>Ingreso Total:</strong> ${ingreso_total:,.2f}<br>
    <strong>Costo Total:</strong> ${costo_total_general:,.2f}<br>
    <strong>Utilidad Bruta:</strong> ${utilidad_bruta:,.2f} ({pct_bruta:.2f}%)<br>
    <strong>Costos Indirectos (35%):</strong> ${costos_indirectos:,.2f}<br>
    <strong>Utilidad Neta:</strong> ${utilidad_neta:,.2f} ({pct_neta:.2f}%)</p>
    <hr><h2>📋 Resumen de Rutas</h2>
    """
    for tipo in ["IMPO", "VACIO", "EXPO"]:
        r = next((x for x in rutas if x["Tipo"] == tipo), None)
        if r is not None:
            html += f"<h3>{tipo}</h3><ul>"
            for item in [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Casetas')):,.2f}",
                f"Costo Cruce Convertido: ${safe_number(r.get('Costo Cruce Convertido')):,.2f}",
                f"Ingreso Original: ${safe_number(r.get('Ingreso_Original')):,.2f}",
                f"Moneda: {r.get('Moneda_Ingreso', 'N/A')}",
                f"Tipo de cambio: {safe_number(r.get('Tipo_Cambio_Ingreso')):,.2f}",
                "Extras detallados:",
                f" - Lavado Termo: ${safe_number(r.get('Lavado_Termo')):,.2f}",
                f" - Movimiento Local: ${safe_number(r.get('Movimiento_Local')):,.2f}",
                f" - Puntualidad: ${safe_number(r.get('Puntualidad')):,.2f}",
                f" - Pensión: ${safe_number(r.get('Pension')):,.2f}",
                f" - Estancia: ${safe_number(r.get('Estancia')):,.2f}",
                f" - Fianza Termo: ${safe_number(r.get('Fianza_Termo')):,.2f}",
                f" - Renta Termo: ${safe_number(r.get('Renta_Termo')):,.2f}"
            ]:
                html += f"<li>{item}</li>"
            html += "</ul>"
        else:
            html += f"<h3>{tipo}</h3><p>No aplica</p>"
    return html

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    impo_rutas = df[df["Tipo"] == "IMPO"]
    expo_rutas = df[df["Tipo"] == "EXPO"]
    vacio_rutas = df[df["Tipo"] == "VACIO"]

    col1, col2 = st.columns(2)
    with col1:
        cliente_impo = st.selectbox("Cliente Importación", impo_rutas["Cliente"].dropna().unique())
        rutas_impo = impo_rutas[impo_rutas["Cliente"] == cliente_impo]
        impo_sel = st.selectbox("Ruta Importación", rutas_impo.index.tolist(), format_func=lambda x: f"{rutas_impo.loc[x, 'Origen']} → {rutas_impo.loc[x, 'Destino']}")
        ruta_impo = rutas_impo.loc[impo_sel]

    with col2:
        cliente_expo = st.selectbox("Cliente Exportación", expo_rutas["Cliente"].dropna().unique())
        rutas_expo = expo_rutas[expo_rutas["Cliente"] == cliente_expo]
        expo_sel = st.selectbox("Ruta Exportación", rutas_expo.index.tolist(), format_func=lambda x: f"{rutas_expo.loc[x, 'Origen']} → {rutas_expo.loc[x, 'Destino']}")
        ruta_expo = rutas_expo.loc[expo_sel]

    usar_vacio = st.checkbox("¿Agregar ruta VACÍA?")
    if usar_vacio and not vacio_rutas.empty:
        vacio_sel = st.selectbox("Ruta VACÍA (opcional)", vacio_rutas.index.tolist(), format_func=lambda x: f"{vacio_rutas.loc[x, 'Origen']} → {vacio_rutas.loc[x, 'Destino']}")
        ruta_vacio = vacio_rutas.loc[vacio_sel]
    else:
        ruta_vacio = None

    if st.button("🚛 Simular Vuelta Redonda"):
        rutas_seleccionadas = [ruta_impo]
        if ruta_vacio is not None:
            rutas_seleccionadas.append(ruta_vacio)
        rutas_seleccionadas.append(ruta_expo)

        ingreso_total = sum(safe_number(r.get("Ingreso Total", 0)) for r in rutas_seleccionadas)
        costo_total_general = sum(safe_number(r.get("Costo_Total_Ruta", 0)) for r in rutas_seleccionadas)
        utilidad_bruta = ingreso_total - costo_total_general
        costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - costos_indirectos
        pct_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
        pct_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        # 📄 Detalle de Rutas
        st.markdown("## 📄 Detalle de Rutas")
        for r in rutas_seleccionadas:
            st.markdown(f"""
**{r['Tipo']} — {r.get('Cliente', 'nan')}**  
- {r['Origen']} → {r['Destino']}  
- Ingreso Original: ${safe_number(r.get('Ingreso_Original')):,.2f} {r.get('Moneda_Ingreso')}  
- Tipo de cambio: {safe_number(r.get('Tipo_Cambio_Ingreso')):,.2f}  
- Ingreso Total: ${safe_number(r.get('Ingreso Total')):,.2f}  
- Costo Total Ruta: ${safe_number(r.get('Costo_Total_Ruta')):,.2f}
""")

        # 📊 Resultado General
        st.markdown("---")
        st.markdown("## 📊 Resultado General")
        st.markdown(f"**Ingreso Total:** ${ingreso_total:,.2f}")
        st.markdown(f"**Costo Total:** ${costo_total_general:,.2f}")
        st.markdown(f"**Utilidad Bruta:** ${utilidad_bruta:,.2f} ({pct_bruta:.2f}%)")
        st.markdown(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
        st.markdown(f"**Utilidad Neta:** ${utilidad_neta:,.2f} ({pct_neta:.2f}%)")

        # 📋 Resumen de Rutas
        st.markdown("---")
        st.markdown("## 📋 Resumen de Rutas")
        tipos = ["IMPO", "VACIO", "EXPO"]
        cols = st.columns(3)

        def resumen_ruta(r):
            return [
                f"KM: {safe_number(r.get('KM')):,.2f}",
                f"Diesel Camión: ${safe_number(r.get('Costo_Diesel_Camion')):,.2f}",
                f"Diesel Termo: ${safe_number(r.get('Costo_Diesel_Termo')):,.2f}",
                f"Sueldo: ${safe_number(r.get('Sueldo_Operador')):,.2f}",
                f"Casetas: ${safe_number(r.get('Casetas')):,.2f}",
                f"Costo Cruce Convertido: ${safe_number(r.get('Costo Cruce Convertido')):,.2f}",
                f"Ingreso Original: ${safe_number(r.get('Ingreso_Original')):,.2f}",
                f"Moneda: {r.get('Moneda_Ingreso', 'N/A')}",
                f"Tipo de cambio: {safe_number(r.get('Tipo_Cambio_Ingreso')):,.2f}",
                "**Extras detallados:**",
                f"Lavado Termo: ${safe_number(r.get('Lavado_Termo')):,.2f}",
                f"Movimiento Local: ${safe_number(r.get('Movimiento_Local')):,.2f}",
                f"Puntualidad: ${safe_number(r.get('Puntualidad')):,.2f}",
                f"Pensión: ${safe_number(r.get('Pension')):,.2f}",
                f"Estancia: ${safe_number(r.get('Estancia')):,.2f}",
                f"Fianza Termo: ${safe_number(r.get('Fianza_Termo')):,.2f}",
                f"Renta Termo: ${safe_number(r.get('Renta_Termo')):,.2f}"
            ]

        for i, tipo in enumerate(tipos):
            with cols[i]:
                st.markdown(f"**{tipo}**")
                ruta = next((r for r in rutas_seleccionadas if r["Tipo"] == tipo), None)
                if ruta is not None:
                    for line in resumen_ruta(ruta):
                        st.write(line)
                else:
                    st.write("No aplica")

        # Exportar a PDF
        st.markdown("---")
        st.markdown("## 📤 Exportar a PDF")
        if st.button("Descargar resultado en PDF"):
            html = generar_html_detalle(rutas_seleccionadas, ingreso_total, costo_total_general,
                                        utilidad_bruta, pct_bruta, costos_indirectos, utilidad_neta, pct_neta)
            ruta_pdf = "simulacion_rutas.pdf"
            try:
                pdfkit.from_string(html, ruta_pdf)
                with open(ruta_pdf, "rb") as f:
                    st.download_button("📄 Descargar PDF", f, file_name=ruta_pdf)
            except Exception as e:
                st.error(f"Error al generar PDF: {e}")

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
