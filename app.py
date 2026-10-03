import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Configuración de la página
st.set_page_config(page_title="Gemelo Digital - Aula", layout="wide")

st.title("🏫 Gemelo Digital: Control Térmico de Aula")
st.markdown("Simulación física de la temperatura en tiempo real según la ocupación y el uso de aire acondicionado.")

# ==========================================
# BARRA LATERAL: PARÁMETROS DE ENTRADA
# ==========================================
st.sidebar.header("⚙️ Parámetros del Aula")

# Dimensiones del aula
largo = st.sidebar.number_input("Largo del aula (m)", value=8.0, step=0.5)
ancho = st.sidebar.number_input("Ancho del aula (m)", value=6.0, step=0.5)
alto = st.sidebar.number_input("Alto del aula (m)", value=3.0, step=0.5)
volumen = largo * ancho * alto

# Ocupación y ambiente
n_alumnos = st.sidebar.slider("Número de alumnos", min_value=0, max_value=50, value=25)
temp_ext = st.sidebar.slider("Temperatura Exterior (°C)", min_value=10.0, max_value=45.0, value=32.0)
temp_ini = st.sidebar.slider("Temperatura Inicial del Aula (°C)", min_value=10.0, max_value=40.0, value=28.0)

st.sidebar.header("❄️ Configuración del Aire Acondicionado")
ac_on = st.sidebar.toggle("Encender Aire Acondicionado", value=True)
potencia_btu = st.sidebar.selectbox("Potencia del AC (BTU)", [9000, 12000, 18000, 24000], index=2)
setpoint = st.sidebar.slider("Temperatura Objetivo / Setpoint (°C)", min_value=16, max_value=26, value=22)

# ==========================================
# MOTOR DE SIMULACIÓN FÍSICA
# ==========================================
# Constantes físicas
DENSIDAD_AIRE = 1.2  # kg/m3
CALOR_ESPECIFICO_AIRE = 1005  # J/(kg*°C)
C_aula = volumen * DENSIDAD_AIRE * CALOR_ESPECIFICO_AIRE  # Capacidad térmica Cap (J/°C)

Q_alumno = 100  # Watts que genera 1 alumno
U_paredes = 15.0  # W/°C conductancia térmica global aproximada
potencia_w = (potencia_btu / 3.41214)  # Conversión BTU/h a Watts

# Parámetros del tiempo
dt = 1.0  # Paso de tiempo en segundos
minutos = 60
pasos = minutos * 60

# Vectores para almacenar resultados
tiempo = np.linspace(0, minutos, pasos)
temperaturas = np.zeros(pasos)
temperaturas[0] = temp_ini

# Bucle de simulación Euler
for i in range(1, pasos):
    T_actual = temperaturas[i-1]
    
    # Fuentes de calor (Watts)
    q_alumnos = n_alumnos * Q_alumno
    q_ambiente = U_paredes * (temp_ext - T_actual)
    
    # Lógica del termostato del AC
    q_ac = 0.0
    if ac_on and T_actual > setpoint:
        q_ac = potencia_w  # Enfria a máxima potencia
        
    # Balance térmico neto (dQ/dt)
    q_neto = q_alumnos + q_ambiente - q_ac
    
    # Actualizar temperatura
    dT = (q_neto / C_aula) * dt
    temperaturas[i] = T_actual + dT

# ==========================================
# VISUALIZACIÓN Y MÉTRICAS
# ==========================================
temp_final = temperaturas[-1]

# Tarjetas con datos clave
col1, col2, col3, col4 = st.columns(4)
col1.metric("Temp. Final Alcanzada", f"{temp_final:.1f} °C", delta=f"{temp_final - temp_ini:.1f} °C")
col2.metric("Ocupantes", f"{n_alumnos} personas")
col3.metric("Carga Térmica Humana", f"{n_alumnos * Q_alumno} W")
col4.metric("Estado del AC", "Encendido" if ac_on else "Apagado")

# Gráfica dinámica
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(tiempo, temperaturas, color="#1f77b4", linewidth=2.5, label="Temp. Aula")
ax.axhline(temp_ext, color="orange", linestyle="--", alpha=0.7, label=f"Temp. Exterior ({temp_ext}°C)")

if ac_on:
    ax.axhline(setpoint, color="green", linestyle=":", alpha=0.9, label=f"Setpoint AC ({setpoint}°C)")

ax.set_xlabel("Tiempo (minutos)")
ax.set_ylabel("Temperatura (°C)")
ax.set_title("Evolución de la Temperatura en el Tiempo")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper right")

st.pyplot(fig)