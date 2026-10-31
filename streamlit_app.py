import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

# Constants
F = 96485
n = 2
M_Cu = 63.546
M_CuSO4_5H2O = 249.68
density_copper = 8.96
density_solution = 1.15
viscosity = 0.01
conductivity_base = 0.08

st.title("⚡ Copper Electrolytic Powder Lab")

st.sidebar.header("⚙️ Power Settings")

current = st.sidebar.slider("Current (A)", 1.0, 40.0, 12.0)
voltage = st.sidebar.slider("Voltage (V)", 1.0, 20.0, 10.0)
hours = st.sidebar.slider("Run Time (hours)", 0.1, 5.0, 1.0)

st.sidebar.header("🔩 Geometry")

width = st.sidebar.slider("Plate Width (cm)", 5.0, 30.0, 16.0)
height = st.sidebar.slider("Plate Height (cm)", 5.0, 30.0, 20.0)
sides = st.sidebar.selectbox("Active Sides", [1,2])
sub = st.sidebar.slider("Submersion %", 10,100,50)
spacing = st.sidebar.slider("Electrode Gap (cm)",1.0,15.0,9.0)

st.sidebar.header("🧪 Chemistry")

cuso4 = st.sidebar.slider("CuSO4·5H2O (g)",100,2000,500)
volume = st.sidebar.slider("Solution Volume (L)",1.0,10.0,4.0)
acid = st.sidebar.slider("Battery Acid 37% (mL)",0,600,300)
temp = st.sidebar.slider("Starting Temp °C",10,60,25)

nano_mode = st.sidebar.checkbox("Activate Nano Mode (<1 µm)")

# Area
area = width*height*sides*(sub/100)
eff_area = area*1.1
current_density = (current*1000)/eff_area

# Conductivity estimate
pure_H2SO4 = acid*1.28*0.37
acid_gL = pure_H2SO4/volume
conductivity = conductivity_base + acid_gL*0.002
conductivity *= (1+(temp-25)*0.02)

cell_resistance = spacing/(conductivity*eff_area)

max_current = voltage/cell_resistance

# Particle estimate
if current_density < 30:
    particle = 40
elif current_density < 60:
    particle = 10
elif current_density < 90:
    particle = 3
else:
    particle = 0.8

# Settling velocity
r_cm = (particle*1e-4)/2
v = (2/9)*(density_copper-density_solution)*980*(r_cm**2)/viscosity
settling_time = 10/v if v>0 else 0

# Copper production
seconds = hours*3600
efficiency = 0.9
grams = (current*M_Cu/(n*F))*efficiency*seconds

st.header("📊 Results")

col1,col2,col3 = st.columns(3)

col1.metric("Current Density",f"{current_density:.1f} mA/cm²")
col2.metric("Particle Size",f"{particle} µm")
col3.metric("Copper Produced",f"{grams:.1f} g")

st.write("Settling time for 10 cm fall:",round(settling_time/60,2),"minutes")

st.write("Cell Resistance:",round(cell_resistance,3),"Ω")

st.write("Max Possible Current:",round(max_current,1),"A")

# Warnings
st.header("⚠ Live Warnings")

if spacing > 6:
    st.warning("Electrode gap too large for ultrafine powder")

if current_density < 40:
    st.warning("Current density too low — coarse powder likely")

if current > max_current:
    st.error("Power supply clipping!")

if nano_mode:
    target_density = 90
    optimal_current = (target_density*eff_area)/1000
    st.info(f"Nano Mode Target Current ≈ {optimal_current:.1f} A")

# Plot
st.header("📈 Current Density Regime")

x = np.linspace(0,120,200)

y = np.piecewise(x,
                 [x<30,(x>=30)&(x<60),(x>=60)&(x<90),x>=90],
                 [40,10,3,0.8])

fig,ax = plt.subplots()

ax.plot(x,y)
ax.scatter(current_density,particle,color="red")

ax.set_xlabel("Current Density (mA/cm²)")
ax.set_ylabel("Particle Size (µm)")
ax.set_title("Copper Powder Regime Map")

st.pyplot(fig)
