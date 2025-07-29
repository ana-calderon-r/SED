import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Ruta a la carpeta con tus archivos
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

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
df['I_Total'] = df['I1Avg'] + df['I2Avg'] + df['I3Avg']

def normalizar_dia(grupo):
    max_corriente = grupo['I_Total'].max()
    grupo['I_Norm'] = grupo['I_Total'] / max_corriente
    return grupo

df_norm = df.groupby('Fecha', group_keys=False).apply(normalizar_dia)
curva_promedio = df_norm.groupby('HoraMinuto')['I_Norm'].mean().reset_index()

# Gráfica
st.subheader("Curva promedio normalizada")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(curva_promedio['HoraMinuto'], curva_promedio['I_Norm'])
ax.set_title('Curva promedio normalizada')
ax.set_xlabel('Hora')
ax.set_ylabel('Corriente normalizada')
ax.grid(True)
plt.xticks(rotation=90)
st.pyplot(fig)

# Entrada del usuario
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

# Rango de horas pico
st.subheader("Rango de horas pico")
umbral = 0.90 * curva_promedio['I_Norm'].max()
horas_pico = curva_promedio[curva_promedio['I_Norm'] >= umbral]
st.dataframe(horas_pico)
