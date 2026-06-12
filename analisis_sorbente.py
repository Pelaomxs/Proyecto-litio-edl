# ============================================================
# ANALISIS DE DEGRADACION DEL SORBENTE Y COSTO REAL EDL
# Lee datos desde Excel y genera dashboard de due diligence
# Desarrollado por Ricardo Ferron
# ============================================================
#
# QUE RESUELVE:
# Los vendedores de EDL muestran la recuperacion con sorbente NUEVO.
# Esta herramienta calcula el COSTO REAL a lo largo del tiempo,
# considerando la degradacion del sorbente y sus reemplazos.
#
# COMO FUNCIONA:
# Lee los parametros desde "datos_sorbente.xlsx". Para cambiar un
# escenario, edita el Excel y vuelve a correr este codigo.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── 1. LEER PARAMETROS DESDE EXCEL ──────────────────────────
ARCHIVO = "datos_sorbente.xlsx"
df = pd.read_excel(ARCHIVO, sheet_name="Parametros", skiprows=2)

def get(nombre):
    return float(df[df["Parametro"] == nombre]["Valor"].values[0])

precio_sorbente   = get("Precio del sorbente")
masa_sorbente     = get("Masa de sorbente")
vida_util         = get("Vida util")
ciclos_por_dia    = get("Ciclos por dia")
umbral            = get("Umbral de reemplazo")
recup_inicial     = get("Recuperacion inicial")
prod_diaria       = get("Produccion diaria")
precio_litio      = get("Precio litio")
horizonte         = int(get("Horizonte evaluacion"))

print("=" * 64)
print("   ANALISIS DE DEGRADACION DEL SORBENTE - Costo Real EDL")
print("   Desarrollado por Ricardo Ferron")
print("=" * 64)
print(f"\n  Datos leidos desde: {ARCHIVO}")

# ── 2. MODELO DE DEGRADACION ────────────────────────────────
ciclos_totales = int(ciclos_por_dia * 365 * horizonte)
caida_por_ciclo = (1 - umbral) / vida_util
dias_horizonte = 365 * horizonte

cap_diaria = []
ciclo_actual = 0
for dia in range(dias_horizonte):
    cap = 1 - caida_por_ciclo * ciclo_actual
    if cap <= umbral:
        ciclo_actual = 0
        cap = 1.0
    cap_diaria.append(cap)
    ciclo_actual += ciclos_por_dia
cap_diaria = np.array(cap_diaria)

# ── 3. METRICAS ─────────────────────────────────────────────
vida_meses = (vida_util / ciclos_por_dia) / 30
num_reemplazos = int(ciclos_totales / vida_util)
costo_unitario = precio_sorbente * masa_sorbente
costo_total_sorb = costo_unitario * (num_reemplazos + 1)

recup_efectiva = recup_inicial * cap_diaria
recup_prom = recup_efectiva.mean()
prod_real = prod_diaria * cap_diaria.sum()
prod_ideal = prod_diaria * dias_horizonte
litio_perdido = prod_ideal - prod_real
valor_litio_perdido = litio_perdido * precio_litio
costo_total = costo_total_sorb + valor_litio_perdido
costo_por_ton = costo_total / prod_real

print(f"\n[ VIDA UTIL DEL SORBENTE ]")
print(f"   Vida util          : {vida_util:.0f} ciclos = {vida_meses:.1f} meses")
print(f"   Reemplazos en {horizonte} años : {num_reemplazos} veces")
print(f"\n[ COSTO DEL SORBENTE ]")
print(f"   Costo por carga    : ${costo_unitario:,.0f} USD")
print(f"   Costo total        : ${costo_total_sorb:,.0f} USD")
print(f"\n[ IMPACTO EN PRODUCCION ]")
print(f"   Recuperacion inicial : {recup_inicial*100:.1f}%")
print(f"   Recuperacion real    : {recup_prom*100:.1f}%")
print(f"   Litio perdido        : {litio_perdido:,.0f} t LCE")
print(f"   Valor perdido        : ${valor_litio_perdido:,.0f} USD")
print(f"\n[ COSTO REAL OCULTO ]")
print(f"   Total oculto       : ${costo_total:,.0f} USD en {horizonte} años")
print(f"   Sobrecosto/tonelada: ${costo_por_ton:,.0f} USD/t LCE")
print(f"\n   >> Lo que el vendedor de EDL no destaca <<")

# ── 4. DASHBOARD ────────────────────────────────────────────
fig = plt.figure(figsize=(16, 9))
fig.patch.set_facecolor('#F8F9FA')
gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.32)

TEAL='#1D9E75'; ROJO='#E24B4A'; NARANJA='#EF9F27'; AZUL='#185FA5'; GRIS='#888780'

# G1: Curva de degradacion (diente de sierra)
ax1 = fig.add_subplot(gs[0, :2])
años_x = np.arange(dias_horizonte) / 365
ax1.plot(años_x, recup_efectiva*100, color=TEAL, linewidth=1.5, label='Recuperacion efectiva')
ax1.axhline(y=recup_inicial*umbral*100, color=ROJO, linestyle='--', linewidth=1.2, label='Umbral de reemplazo')
ax1.axhline(y=recup_inicial*100, color=GRIS, linestyle=':', linewidth=1, alpha=0.7, label='Recuperacion nominal (vendedor)')
ax1.set_title('Curva de degradacion del sorbente — cada caida es un reemplazo',
              fontsize=12, fontweight='bold')
ax1.set_xlabel('Años de operacion'); ax1.set_ylabel('Recuperacion (%)')
ax1.set_ylim(0, 100); ax1.set_facecolor('white'); ax1.legend(fontsize=9, loc='lower left')
ax1.spines[['top','right']].set_visible(False)

# G2: Recuperacion nominal vs real
ax2 = fig.add_subplot(gs[0, 2])
b2 = ax2.bar(['Nominal\n(vendedor)', 'Real\n(con degradacion)'],
             [recup_inicial*100, recup_prom*100], color=[GRIS, TEAL], width=0.5)
ax2.set_title('Recuperacion: promesa vs realidad', fontsize=12, fontweight='bold')
ax2.set_ylabel('Recuperacion (%)'); ax2.set_ylim(0, 100); ax2.set_facecolor('white')
for bar, val in zip(b2, [recup_inicial*100, recup_prom*100]):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2, f'{val:.0f}%',
             ha='center', fontweight='bold')
ax2.spines[['top','right']].set_visible(False)

# G3: Composicion del costo oculto
ax3 = fig.add_subplot(gs[1, 0])
costos = [costo_total_sorb/1e6, valor_litio_perdido/1e6]
b3 = ax3.bar(['Sorbente\n(reemplazos)', 'Litio perdido\n(degradacion)'],
             costos, color=[NARANJA, ROJO], width=0.5)
ax3.set_title('Composicion del costo oculto', fontsize=12, fontweight='bold')
ax3.set_ylabel('Millones USD'); ax3.set_facecolor('white')
for bar, val in zip(b3, costos):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+max(costos)*0.02,
             f'${val:.0f}M', ha='center', fontweight='bold')
ax3.spines[['top','right']].set_visible(False)

# G4: Reemplazos acumulados en el tiempo
ax4 = fig.add_subplot(gs[1, 1])
reemplazos_año = []
for año in range(1, horizonte+1):
    ciclos_año = ciclos_por_dia * 365 * año
    reemplazos_año.append(int(ciclos_año / vida_util))
ax4.step(range(1, horizonte+1), reemplazos_año, color=AZUL, linewidth=2, where='post')
ax4.fill_between(range(1, horizonte+1), reemplazos_año, step='post', alpha=0.15, color=AZUL)
ax4.set_title('Reemplazos acumulados', fontsize=12, fontweight='bold')
ax4.set_xlabel('Año'); ax4.set_ylabel('N° de reemplazos'); ax4.set_facecolor('white')
ax4.spines[['top','right']].set_visible(False)

# G5: Sobrecosto por tonelada (gauge-like)
ax5 = fig.add_subplot(gs[1, 2])
ax5.barh(['Sobrecosto\nreal/t'], [costo_por_ton], color=ROJO, height=0.4)
ax5.set_title('Sobrecosto oculto por tonelada', fontsize=12, fontweight='bold')
ax5.set_xlabel('USD por t LCE'); ax5.set_facecolor('white')
ax5.text(costo_por_ton, 0, f'  ${costo_por_ton:,.0f}', va='center', fontweight='bold', fontsize=13)
ax5.spines[['top','right']].set_visible(False)

fig.suptitle('Dashboard de Degradacion del Sorbente y Costo Real EDL — por Ricardo Ferron',
             fontsize=15, fontweight='bold', y=0.98)
plt.savefig('dashboard_sorbente.png', dpi=150, bbox_inches='tight', facecolor='#F8F9FA')
plt.close()
print(f"\n  Dashboard guardado: dashboard_sorbente.png")
print("=" * 64)
