import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta a la carpeta con tus archivos
DATA_DIR = "data"

# Lista de archivos disponibles
archivos_sed = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
sed_opciones = {archivo.replace(".xlsx", "").replace("_", " "): archivo for archivo in archivos_sed}

# Selección de la SED
sed_seleccionada = st.selectbox("Selecciona la SED:", list(sed_opciones.keys()))
archivo_cargado = os.path.join(DATA_DIR, sed_opciones[sed_seleccionada])

# Cargar y procesar el archivo
df = pd.read_excel(archivo_cargado)
df['Starttime'] = pd.to_datetime(df['Starttime'])
df['Fecha'] = df['Starttime'].dt.date
df['HoraMinuto'] = df['Starttime'].dt.strftime('%H:%M')
df['I_Total'] = (df['I1Avg'] + df['I2Avg'] + df['I3Avg'])
df['I_Promedio'] = (df['I1Avg'] + df['I2Avg'] + df['I3Avg']) / 3
df['V_Total'] = (df['U1Avg'] + df['U2Avg'] + df['U3Avg']) / 3  # Voltaje promedio



# Normalización por día
def normalizar_dia(grupo):
    max_corriente = grupo['I_Total'].max()
    grupo['I_Norm'] = grupo['I_Total'] / max_corriente
    return grupo

df_norm = df.groupby('Fecha', group_keys=False).apply(normalizar_dia)

# Curvas promedio
curva_promedio = df_norm.groupby('HoraMinuto')['I_Norm'].mean().reset_index()
curva_I_prom = df.groupby('HoraMinuto')['I_Total'].mean().reset_index()
curva_V_prom = df.groupby('HoraMinuto')['V_Total'].mean().reset_index()

# ================== GRÁFICAS ==================
st.subheader("Curva promedio normalizada")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(curva_promedio['HoraMinuto'], curva_promedio['I_Norm'], label='Corriente Normalizada')
ax.set_title('Curva promedio normalizada')
ax.set_xlabel('Hora')
ax.set_ylabel('Corriente normalizada')
ax.grid(True)
plt.xticks(rotation=90)
st.pyplot(fig)

st.subheader("Corriente promedio por hora")
fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.plot(curva_I_prom['HoraMinuto'], curva_I_prom['I_Promedio'], color='orange', label='Corriente Promedio')
ax2.set_title('Corriente promedio diaria')
ax2.set_xlabel('Hora')
ax2.set_ylabel('Corriente (A)')
ax2.grid(True)
plt.xticks(rotation=90)
st.pyplot(fig2)

st.subheader("Voltaje promedio por hora")
fig3, ax3 = plt.subplots(figsize=(12, 5))
ax3.plot(curva_V_prom['HoraMinuto'], curva_V_prom['V_Total'], color='green', label='Voltaje Promedio')
ax3.set_title('Voltaje promedio diario')
ax3.set_xlabel('Hora')
ax3.set_ylabel('Voltaje (V)')
ax3.grid(True)
plt.xticks(rotation=90)
st.pyplot(fig3)

# ================== CÁLCULOS EXTRA ==================
corriente_max_promedio = df['I_Promedio'].max()
I_promedio_max = curva_I_prom['I_Total'].max()
hora_max = curva_I_prom[curva_I_prom['I_Total'] == I_promedio_max]['HoraMinuto'].values[0]

# Definir rango de hora pico (> 90% del valor máximo)
umbral_pico = 0.9 * I_promedio_max
horas_pico = curva_I_prom[curva_I_prom['I_Total'] >= umbral_pico]['HoraMinuto'].tolist()

st.subheader("Corriente máxima promedio trifásica alcanzada")
st.write(f"{corriente_max_promedio:.2f} A")

if horas_pico:
    st.info(f"⏰ Rango de horas pico (corriente promedio ≥ 90% del valor máximo):")
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

    st.success(f"I pico estimado: {I_pico:.2f} A")
    st.success(f"I estimada a las {hora_objetivo}: {I_estimado:.2f} A")
except IndexError:
    st.error("Verifica que las horas ingresadas existan en los datos.")
