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

    # =====================
    # 📊 Ingresos y Utilidades
    # =====================
    st.markdown("---")
    st.subheader("📊 Ingresos y Utilidades")

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

    st.write(f"**Ingreso Total:** ${ingreso_total:,.2f}")
    st.write(f"**Costo Total:** ${costo_total:,.2f}")
    st.markdown(colored_bold("Utilidad Bruta", f"${utilidad_bruta:,.2f}", utilidad_bruta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Bruta", f"{porcentaje_bruta:.2f}%", porcentaje_bruta >= 50), unsafe_allow_html=True)
    st.write(f"**Costos Indirectos (35%):** ${costos_indirectos:,.2f}")
    st.markdown(colored_bold("Utilidad Neta", f"${utilidad_neta:,.2f}", utilidad_neta >= 0), unsafe_allow_html=True)
    st.markdown(colored_bold("% Utilidad Neta", f"{porcentaje_neta:.2f}%", porcentaje_neta >= 15), unsafe_allow_html=True)

    # =====================
    # 📋 Detalles y Costos
    # =====================
    st.markdown("---")
    st.subheader("📋 Detalles y Costos de la Ruta")

    ChatGPT dijo:
¡Claro! Para hacerlo más visual y ordenado, he actualizado el bloque de "📋 Detalles y Costos de la Ruta" para que se muestre en dos columnas paralelas (lado izquierdo y derecho), separando lógica y estéticamente los datos generales y los costos detallados.

✅ Versión con dos columnas para Detalles y Costos
python
Copiar
Editar
# =====================
# 📋 Detalles y Costos (2 columnas)
# =====================
st.markdown("---")
st.subheader("📋 Detalles y Costos de la Ruta")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🔎 Detalles Generales**")
    st.write(f"Fecha: {ruta['Fecha']}")
    st.write(f"Tipo: {ruta['Tipo']}")
    st.write(f"Cliente: {ruta['Cliente']}")
    st.write(f"Origen → Destino: {ruta['Origen']} → {ruta['Destino']}")
    st.write(f"KM: {safe_number(ruta['KM']):,.2f}")
    st.write(f"Moneda Flete: {ruta['Moneda']}")
    st.write(f"Ingreso Flete Original: ${safe_number(ruta['Ingreso_Original']):,.2f}")
    st.write(f"Tipo de cambio: {safe_number(ruta['Tipo de cambio']):,.2f}")
    st.write(f"Ingreso Flete Convertido: ${safe_number(ruta['Ingreso Flete']):,.2f}")
    st.write(f"Moneda Cruce: {ruta['Moneda_Cruce']}")
    st.write(f"Ingreso Cruce Original: ${safe_number(ruta['Cruce_Original']):,.2f}")
    st.write(f"Tipo cambio Cruce: {safe_number(ruta['Tipo cambio Cruce']):,.2f}")
    st.write(f"Ingreso Cruce Convertido: ${safe_number(ruta['Ingreso Cruce']):,.2f}")
    st.write(f"Moneda Costo Cruce: {ruta['Moneda Costo Cruce']}")
    st.write(f"Costo Cruce Original: ${safe_number(ruta['Costo Cruce']):,.2f}")
    st.write(f"Costo Cruce Convertido: ${safe_number(ruta['Costo Cruce Convertido']):,.2f}")

with col2:
    st.markdown("**🧾 Costos y Extras**")
    st.write(f"Diesel Camión: ${safe_number(ruta['Costo_Diesel_Camion']):,.2f}")
    st.write(f"Diesel Termo: ${safe_number(ruta['Costo_Diesel_Termo']):,.2f}")
    st.write(f"Sueldo Operador: ${safe_number(ruta['Sueldo_Operador']):,.2f}")
    st.write(f"Bono: ${safe_number(ruta['Bono']):,.2f}")
    st.write(f"Casetas: ${safe_number(ruta['Casetas']):,.2f}")
    st.write("**Extras Detallados:**")
    st.write(f"- Lavado Termo: ${safe_number(ruta['Lavado_Termo']):,.2f}")
    st.write(f"- Movimiento Local: ${safe_number(ruta['Movimiento_Local']):,.2f}")
    st.write(f"- Puntualidad: ${safe_number(ruta['Puntualidad']):,.2f}")
    st.write(f"- Pensión: ${safe_number(ruta['Pension']):,.2f}")
    st.write(f"- Estancia: ${safe_number(ruta['Estancia']):,.2f}")
    st.write(f"- Fianza Termo: ${safe_number(ruta['Fianza_Termo']):,.2f}")
    st.write(f"- Renta Termo: ${safe_number(ruta['Renta_Termo']):,.2f}")
    for line in detalles:
        st.write(line)

else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
