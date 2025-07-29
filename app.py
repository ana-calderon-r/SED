import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

st.set_page_config(layout="wide")

# ======= Encabezado con Logo =======
logo_path = "data/logo_pluz.png"  # asegúrate de que la ruta sea correcta
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(logo_path, width=100)
with col_title:
    st.markdown("""
        <h1 style='margin-bottom: 0;'>Estimador de Corriente</h1>
        <p style='margin-top: 0; color: gray;'>Visualización y estimación de Sistemas Eléctricos de Distribución</p>
    """, unsafe_allow_html=True)

# ======= Menú =======
menu = st.selectbox("Selecciona una opción", ["Diagramas", "Datos", "Calculadora"])



# ================== CARGA DE ARCHIVOS ==================
DATA_DIR = "data"
archivos_sed = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
sed_opciones = {archivo.replace(".xlsx", "").replace("_", " "): archivo for archivo in archivos_sed}
sed_seleccionada = st.selectbox("Selecciona la SED:", list(sed_opciones.keys()))
archivo_cargado = os.path.join(DATA_DIR, sed_opciones[sed_seleccionada])

df = pd.read_excel(archivo_cargado)
df['Starttime'] = pd.to_datetime(df['Starttime'])
df['Fecha'] = df['Starttime'].dt.date
df['HoraMinuto'] = df['Starttime'].dt.strftime('%H:%M')
df['I_Total'] = (df['I1Avg'] + df['I2Avg'] + df['I3Avg'])
df['I_Promedio'] = df['I_Total'] / 3
df['V_Total'] = (df['U1Avg'] + df['U2Avg'] + df['U3Avg']) / 3

def normalizar_dia(grupo):
    max_corriente = grupo['I_Total'].max()
    grupo['I_Norm'] = grupo['I_Total'] / max_corriente
    return grupo

df_norm = df.groupby('Fecha', group_keys=False).apply(normalizar_dia)

curva_promedio = df_norm.groupby('HoraMinuto')['I_Norm'].mean().reset_index()
curva_I_prom = df.groupby('HoraMinuto')['I_Total'].mean().reset_index()
curva_V_prom = df.groupby('HoraMinuto')['V_Total'].mean().reset_index()

# ================== GRÁFICAS ==================

# Curva normalizada principal
st.subheader("Curva normalizada")
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(curva_promedio['HoraMinuto'], curva_promedio['I_Norm'], label='Corriente Normalizada')
ax1.set_title('Factores normalizados')
ax1.set_xlabel('Hora')
ax1.set_ylabel('Corriente Normalizada')
ax1.grid(True)

# Espaciado en el eje X
import numpy as np
xticks = curva_promedio['HoraMinuto'].iloc[::3]  # Mostrar cada hora
ax1.set_xticks(np.arange(len(curva_promedio))[::3])
ax1.set_xticklabels(xticks, rotation=45)

plt.xticks(rotation=90)
st.pyplot(fig1)

# Corriente promedio por hora y Voltaje promedio por hora juntos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Corriente promedio por hora")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.plot(curva_I_prom['HoraMinuto'], curva_I_prom['I_Total']/3, color='orange')
    ax2.set_title('Corriente Promedio')
    ax2.set_xlabel('Hora')
    ax2.set_ylabel('Corriente (A)')
    ax2.grid(True)

    import numpy as np
    xticks_I = curva_I_prom['HoraMinuto'].iloc[::6]  # cada hora
    ax2.set_xticks(np.arange(len(curva_I_prom))[::6])
    ax2.set_xticklabels(xticks_I, rotation=45)

    plt.tight_layout()
    st.pyplot(fig2)

with col2:
    st.subheader("Voltaje promedio por hora")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.plot(curva_V_prom['HoraMinuto'], curva_V_prom['V_Total'], color='green')
    ax3.set_title('Voltaje Promedio')
    ax3.set_xlabel('Hora')
    ax3.set_ylabel('Voltaje (V)')
    ax3.grid(True)

    xticks_V = curva_V_prom['HoraMinuto'].iloc[::6]  # cada hora
    ax3.set_xticks(np.arange(len(curva_V_prom))[::6])
    ax3.set_xticklabels(xticks_V, rotation=45)

    plt.tight_layout()
    st.pyplot(fig3)
# ================== CÁLCULOS EXTRA ==================
corriente_max_promedio = df['I_Promedio'].max()

curva_I_prom['I_Promedio'] = curva_I_prom['I_Total'] / 3
I_promedio_max = curva_I_prom['I_Promedio'].max()
umbral_pico = 0.9 * I_promedio_max
horas_pico = curva_I_prom[curva_I_prom['I_Promedio'] >= umbral_pico]['HoraMinuto'].tolist()

st.subheader("Corriente máxima promedio trifásica alcanzada")
st.write(f"{corriente_max_promedio:.2f} A")

if horas_pico:
    st.info("⏰ Rango de horas pico (corriente promedio ≥ 90% del valor máximo):")
    st.write(", ".join(horas_pico))
else:
    st.warning("No se encontraron horas pico con corriente promedio ≥ 90% del valor máximo.")

# ================== ESTIMACIÓN ==================
st.subheader("Estimación de corriente")

hora_medida = st.text_input("Hora de medición (formato HH:MM)", value="10:20")
corriente_medida = st.number_input("Corriente medida en esa hora (A)", value=100.0)
hora_objetivo = st.text_input("Hora a estimar la corriente (formato HH:MM)", value="19:00")

try:
    R_medida = curva_promedio[curva_promedio['HoraMinuto'] == hora_medida]['I_Norm'].values[0]
    R_objetivo = curva_promedio[curva_promedio['HoraMinuto'] == hora_objetivo]['I_Norm'].values[0]

    I_pico = corriente_medida / R_medida
    I_estimado = I_pico * R_objetivo

    st.success(f"🔍 La corriente estimada a las {hora_objetivo} es de **{I_estimado:.2f} A**")

except IndexError:
    st.error("❌ Una de las horas ingresadas no se encuentra en los datos.")


    st.success(f"I pico estimado: {I_pico:.2f} A")
    st.success(f"I estimada a las {hora_objetivo}: {I_estimado:.2f} A")
except IndexError:
    st.error("Verifica que las horas ingresadas existan en los datos.")
