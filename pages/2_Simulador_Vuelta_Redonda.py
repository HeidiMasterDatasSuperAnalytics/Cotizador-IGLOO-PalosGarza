import streamlit as st
import pandas as pd
import os

# Archivo de rutas
RUTA_RUTAS = "rutas_guardadas.csv"

st.title("🔁 Simulador de Vuelta Redonda")

# Función para manejo seguro de números
def safe_number(x):
    return 0 if (x is None or (isinstance(x, float) and pd.isna(x))) else x

# Cargar datos de rutas
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
        rutas_seleccionadas = []
        rutas_seleccionadas.append(rutas_impo.loc[[impo_sel]].squeeze())
        if vacio_sel is not None:
            rutas_seleccionadas.append(vacio_rutas.loc[[vacio_sel]].squeeze())
        rutas_seleccionadas.append(rutas_expo.loc[[expo_sel]].squeeze())

        # Inicializar acumuladores
        km_total = ingreso_total = diesel_camion_total = diesel_termo_total = sueldo_total = bono_total = casetas_total = extras_total = cruce_total = costo_total_general = 0

        st.subheader("🧾 Detalle de Rutas")
        for ruta in rutas_seleccionadas:
            ingreso_original = safe_number(ruta.get("Ingreso_Original", 0))
            costo_total_ruta = safe_number(ruta.get("Costo_Total_Ruta", 0))

            ingreso_total += ingreso_original
            costo_total_general += costo_total_ruta
            km_total += safe_number(ruta.get("KM", 0))
            diesel_camion_total += safe_number(ruta.get("Costo_Diesel_Camion", 0))
            diesel_termo_total += safe_number(ruta.get("Costo_Diesel_Termo", 0))
            sueldo_total += safe_number(ruta.get("Sueldo_Operador", 0))
            bono_total += safe_number(ruta.get("Bono", 0))
            casetas_total += safe_number(ruta.get("Costo_Casetas", 0))
            extras_total += safe_number(ruta.get("Costo_Extras", 0))
            cruce_total += safe_number(ruta.get("Costo_Cruce", 0))

            st.markdown(f"""
            **{ruta['Tipo']} — {ruta['Cliente']}**  
            - {ruta['Origen']} → {ruta['Destino']}  
            - Ingreso Flete: ${ingreso_original:,.2f}  
            - Costo Total Ruta: ${costo_total_ruta:,.2f}
            """)

        utilidad_bruta = ingreso_total - costo_total_general
        estimado_costos_indirectos = ingreso_total * 0.35
        utilidad_neta = utilidad_bruta - estimado_costos_indirectos
        porcentaje_utilidad_neta = (utilidad_neta / ingreso_total * 100) if ingreso_total > 0 else 0

        st.markdown("---")
        st.subheader("📊 Resultado General")

        st.write(f"**Ingreso Total Vuelta Redonda:** ${ingreso_total:,.2f}")
        st.write(f"**Costo Total Vuelta Redonda:** ${costo_total_general:,.2f}")
        st.write(f"**Utilidad Bruta:** ${utilidad_bruta:,.2f}")
        st.write(f"**Costo Indirecto Estimado (35%):** ${estimado_costos_indirectos:,.2f}")
        st.write(f"**Utilidad Neta Estimada:** ${utilidad_neta:,.2f}")
        st.write(f"**% Utilidad Neta:** {porcentaje_utilidad_neta:.2f}%")

        st.markdown("---")
        st.subheader("📋 Resumen de Gastos")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Total Kilómetros Recorridos:** {km_total:,.2f} km")
            st.write(f"**Total Diesel Camión:** ${diesel_camion_total:,.2f}")
            st.write(f"**Total Diesel Termo:** ${diesel_termo_total:,.2f}")
            st.write(f"**Total Sueldo Operador:** ${sueldo_total:,.2f}")

        with col2:
            st.write(f"**Total Bono ISR/IMSS:** ${bono_total:,.2f}")
            st.write(f"**Total Casetas:** ${casetas_total:,.2f}")
            st.write(f"**Total Extras:** ${extras_total:,.2f}")
            st.write(f"**Total Costo Cruce:** ${cruce_total:,.2f}")
else:
    st.warning("⚠️ No hay rutas guardadas todavía.")
