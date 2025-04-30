import streamlit as st
import pandas as pd
import os

RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔍 Consulta Individual de Ruta")

def safe_number(x):
    return 0 if pd.isna(x) else x

if os.path.exists(RUTA_RUTAS):
    df = pd.read_csv(RUTA_RUTAS)

    st.subheader("📌 Selecciona una Ruta")
    index_sel = st.selectbox(
        "Selecciona índice",
        df.index.tolist(),
        format_func=lambda x: f"{df.loc[x, 'Tipo']} - {df.loc[x, 'Cliente']} - {df.loc[x, 'Origen']} → {df.loc[x, 'Destino']}"
    )

    ruta = df.loc[index_sel]
        st.markdown("---")
    st.subheader("📊 Ingresos y Utilidades")

    st.write(f"**Ingreso Total:** ${ingreso_total:,.2f}")
    st.write(f"**Costo Total:** ${costo_total:,.2f}")
    st.markdown(colored_bold("Utilidad Bruta", f"${utilidad_bruta:,.2f}", utilidad_bruta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Bruta", f"{porcentaje_bruta:.2f}%", porcentaje_bruta >= 50), unsafe_allow_html=True)
    st.write(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
    st.markdown(colored_bold("Utilidad Neta", f"${utilidad_neta:,.2f}", utilidad_neta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Neta", f"{porcentaje_neta:.2f}%", porcentaje_neta >= 15), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 Detalles y Costos de la Ruta")

    detalles = [
        f"Fecha: {ruta['Fecha']}",
        f"Tipo: {ruta['Tipo']}",
        f"Cliente: {ruta['Cliente']}",
        f"Origen → Destino: {ruta['Origen']} → {ruta['Destino']}",
        f"KM: {safe_number(ruta['KM']):,.2f}",
        f"Moneda Flete: {ruta['Moneda']}",
        f"Ingreso Flete Original: ${safe_number(ruta['Ingreso_Original']):,.2f}",
        f"Tipo de cambio: {safe_number(ruta['Tipo de cambio']):,.2f}",
        f"Ingreso Flete Convertido: ${safe_number(ruta['Ingreso Flete']):,.2f}",
        f"Moneda Cruce: {ruta['Moneda_Cruce']}",
        f"Ingreso Cruce Original: ${safe_number(ruta['Cruce_Original']):,.2f}",
        f"Tipo cambio Cruce: {safe_number(ruta['Tipo cambio Cruce']):,.2f}",
        f"Ingreso Cruce Convertido: ${safe_number(ruta['Ingreso Cruce']):,.2f}",
        f"Moneda Costo Cruce: {ruta['Moneda Costo Cruce']}",
        f"Costo Cruce Original: ${safe_number(ruta['Costo Cruce']):,.2f}",
        f"Costo Cruce Convertido: ${safe_number(ruta['Costo Cruce Convertido']):,.2f}",
        f"Diesel Camión: ${safe_number(ruta['Costo_Diesel_Camion']):,.2f}",
        f"Diesel Termo: ${safe_number(ruta['Costo_Diesel_Termo']):,.2f}",
        f"Sueldo Operador: ${safe_number(ruta['Sueldo_Operador']):,.2f}",
        f"Bono: ${safe_number(ruta['Bono']):,.2f}",
        f"Casetas: ${safe_number(ruta['Casetas']):,.2f}",
        "**Extras:**",
        f"- Lavado Termo: ${safe_number(ruta['Lavado_Termo']):,.2f}",
        f"- Movimiento Local: ${safe_number(ruta['Movimiento_Local']):,.2f}",
        f"- Puntualidad: ${safe_number(ruta['Puntualidad']):,.2f}",
        f"- Pensión: ${safe_number(ruta['Pension']):,.2f}",
        f"- Estancia: ${safe_number(ruta['Estancia']):,.2f}",
        f"- Fianza Termo: ${safe_number(ruta['Fianza_Termo']):,.2f}",
        f"- Renta Termo: ${safe_number(ruta['Renta_Termo']):,.2f}",
    ]

    for line in detalles:
        st.write(line)

    # Cálculos de ingresos y utilidades
    ingreso_total = safe_number(ruta["Ingreso Total"])
    costo_total = safe_number(ruta["Costo_Total_Ruta"])
    utilidad_bruta = ingreso_total - costo_total
    costos_indirectos = ingreso_total * 0.35
    utilidad_neta = utilidad_bruta - costos_indirectos
    porcentaje_bruta = (utilidad_bruta / ingreso_total * 100) if ingreso_total > 0 else 0
    porcentaje_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

    def colored_bold(label, value, condition, threshold=0):
        color = "green" if condition else "red"
        return f"<strong>{label}:</strong> <span style='color:{color}; font-weight:bold'>{value}</span>"

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
