# ============================================================
# ANALISIS DE EXTRACCION DIRECTA DE LITIO (EDL)
# Version 2.0 - Lee los datos desde un Excel externo
# Desarrollado por Ricardo Ferron
# ============================================================
#
# COMO FUNCIONA:
# Este codigo NO tiene los datos escritos adentro. Los LEE
# desde el archivo "datos_edl.xlsx". Si quieres cambiar un
# valor (precio, recuperacion, etc.), editas el Excel y vuelves
# a correr este codigo. Asi separamos los datos de la logica.
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── 1. LEER DATOS DESDE EL EXCEL ────────────────────────────
ARCHIVO_DATOS = r"C:\Users\WindowsX\Desktop\Proyecto Litio Pelao\datos_edl.xlsx"

# Leemos las dos hojas del Excel
df_param = pd.read_excel(ARCHIVO_DATOS, sheet_name="Parametros", skiprows=2)
df_eco = pd.read_excel(ARCHIVO_DATOS, sheet_name="Supuestos_Economicos", skiprows=2)

# Funcion auxiliar: busca un parametro por su nombre y devuelve su valor
def obtener(df, nombre):
    fila = df[df["Parámetro"] == nombre]
    if fila.empty:
        disponibles = df["Parámetro"].dropna().tolist()
        raise ValueError(f"Parámetro '{nombre}' no encontrado en el Excel.\nDisponibles: {disponibles}")
    return float(fila["Valor"].values[0])

# Cargamos cada dato desde el Excel
rec_edl          = obtener(df_param, "Recuperación EDL")
rec_evaporacion  = obtener(df_param, "Recuperación evaporación")
agua_edl         = obtener(df_param, "Consumo agua EDL")
agua_evap_prom   = obtener(df_param, "Consumo agua evaporación")
superficie_edl   = obtener(df_param, "Superficie EDL")
superficie_evap  = obtener(df_param, "Superficie evaporación")

produccion_anual = obtener(df_eco, "Producción anual")
precio_litio     = obtener(df_eco, "Precio litio")

print("=" * 64)
print("   ANALISIS EDL - Datos leidos desde Excel")
print("   Desarrollado por Ricardo Ferron")
print("=" * 64)
print(f"\n  Datos cargados desde: {ARCHIVO_DATOS}")
print(f"  (Para cambiar un escenario, edita el Excel y vuelve a correr)")

# ── 2. INDICADORES TECNICOS ─────────────────────────────────
print(f"\nINDICADORES CLAVE")
print(f"   {'Indicador':<32}{'EDL':>12}{'Evaporacion':>15}")
print("   " + "-" * 56)
print(f"   {'Recuperacion litio (%)':<32}{rec_edl:>11.1f}%{rec_evaporacion:>14.1f}%")
print(f"   {'Consumo agua (m3/t LCE)':<32}{agua_edl:>12.0f}{agua_evap_prom:>15.0f}")
print(f"   {'Superficie (hectareas)':<32}{superficie_edl:>12.0f}{superficie_evap:>15.0f}")

# ── 3. VENTAJAS CALCULADAS ──────────────────────────────────
mejora_recuperacion = (rec_edl - rec_evaporacion) / rec_evaporacion * 100
ahorro_agua = agua_evap_prom / agua_edl
reduccion_superficie = superficie_evap / superficie_edl

print(f"\nVENTAJAS CUANTIFICADAS")
print(f"   Mejora recuperacion : +{mejora_recuperacion:.0f}% mas litio")
print(f"   Ahorro de agua      : {ahorro_agua:.0f}x menos consumo")
print(f"   Reduccion superficie: {reduccion_superficie:.0f}x menos terreno")

# ── 4. IMPACTO ECONOMICO ────────────────────────────────────
litio_equiv_evap = produccion_anual * (rec_evaporacion / rec_edl)
litio_adicional = produccion_anual - litio_equiv_evap
ingreso_adicional = litio_adicional * precio_litio

print(f"\nIMPACTO ECONOMICO (planta {produccion_anual:,.0f} t/año)")
print(f"   Produccion con EDL        : {produccion_anual:,.0f} t LCE/año")
print(f"   Equivalente evaporacion   : {litio_equiv_evap:,.0f} t LCE/año")
print(f"   Litio adicional capturado : {litio_adicional:,.0f} t LCE/año")
print(f"   Ingreso adicional         : ${ingreso_adicional:,.0f} USD/año")
print(f"   (precio litio: ${precio_litio:,.0f} USD/t)")

# ── 5. VISUALIZACION ────────────────────────────────────────
fig = plt.figure(figsize=(16, 6))
fig.patch.set_facecolor('#F8F9FA')
gs = GridSpec(1, 3, figure=fig, wspace=0.3)

TEAL = '#1D9E75'; ROJO = '#E24B4A'; GRIS = '#888780'

ax1 = fig.add_subplot(gs[0, 0])
b1 = ax1.bar(['EDL', 'Evaporacion'], [rec_edl, rec_evaporacion], color=[TEAL, ROJO], width=0.5)
ax1.set_title('Recuperacion de litio (%)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 100); ax1.set_facecolor('white')
for bar, val in zip(b1, [rec_edl, rec_evaporacion]):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2, f'{val:.1f}%', ha='center', fontweight='bold')
ax1.spines[['top','right']].set_visible(False)

ax2 = fig.add_subplot(gs[0, 1])
b2 = ax2.bar(['EDL', 'Evaporacion'], [agua_edl, agua_evap_prom], color=[TEAL, ROJO], width=0.5)
ax2.set_title('Consumo agua (m3/t LCE)', fontsize=12, fontweight='bold')
ax2.set_facecolor('white')
for bar, val in zip(b2, [agua_edl, agua_evap_prom]):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+30, f'{val:.0f}', ha='center', fontweight='bold')
ax2.text(0.5, -0.18, f'{ahorro_agua:.0f}x menos agua', transform=ax2.transAxes, ha='center', color=TEAL, fontweight='bold')
ax2.spines[['top','right']].set_visible(False)

ax3 = fig.add_subplot(gs[0, 2])
b3 = ax3.bar(['EDL', 'Equiv.\nevaporacion'], [produccion_anual, litio_equiv_evap], color=[TEAL, GRIS], width=0.5)
ax3.set_title(f'Litio capturado (t/año)', fontsize=12, fontweight='bold')
ax3.set_facecolor('white')
for bar, val in zip(b3, [produccion_anual, litio_equiv_evap]):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+300, f'{val:,.0f}', ha='center', fontweight='bold')
ax3.text(0.5, -0.18, f'+${ingreso_adicional/1e6:.0f}M USD/año', transform=ax3.transAxes, ha='center', color=TEAL, fontweight='bold')
ax3.spines[['top','right']].set_visible(False)

fig.suptitle('Analisis EDL vs Evaporacion - por Ricardo Ferron', fontsize=14, fontweight='bold', y=1.02)
plt.savefig(r'C:\Users\WindowsX\Desktop\Proyecto Litio Pelao\analisis_edl_resultado.png', dpi=150, bbox_inches='tight', facecolor='#F8F9FA')
plt.close()
print(f"\n  Grafico guardado: analisis_edl_resultado.png")
print("=" * 64)
