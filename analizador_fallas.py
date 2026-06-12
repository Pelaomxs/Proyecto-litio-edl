import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# ANALIZADOR DE FALLAS - OPERACIONES MINERAS
# Proyecto: Inteligencia Operacional Minería de Litio
# ============================================================

df = pd.read_excel(r"C:\Users\WindowsX\Desktop\Proyecto Litio Pelao\ordenes_trabajo_minera.xlsx")
df['Fecha_Deteccion'] = pd.to_datetime(df['Fecha_Deteccion'])
df['Mes'] = df['Fecha_Deteccion'].dt.to_period('M')

print("=" * 60)
print("   ANALIZADOR DE FALLAS - OPERACIONES MINERAS")
print("=" * 60)

# ── 1. KPIs GENERALES ──────────────────────────────────────
total_ot = len(df)
criticas = len(df[df['Criticidad'] == 'Crítica'])
sin_repuesto = len(df[df['Repuesto_Disponible'] == 'No'])
tiempo_prom = df['Tiempo_Total_Detencion_min'].mean()
costo_total = df['Costo_Reparacion_CLP'].sum()
tasa_reintervencion = len(df[df['Reparacion_Exitosa'] == 'No']) / total_ot * 100

print(f"\n📊 KPIs GENERALES")
print(f"   Total Órdenes de Trabajo : {total_ot}")
print(f"   Fallas Críticas          : {criticas} ({criticas/total_ot*100:.1f}%)")
print(f"   Sin repuesto en bodega   : {sin_repuesto} ({sin_repuesto/total_ot*100:.1f}%)")
print(f"   Tiempo prom. detención   : {tiempo_prom:.0f} min ({tiempo_prom/60:.1f} hrs)")
print(f"   Costo total reparaciones : ${costo_total:,.0f} CLP")
print(f"   Tasa de reintervención   : {tasa_reintervencion:.1f}%")

# ── 2. MTBF y MTTR POR EQUIPO ──────────────────────────────
print(f"\n🔧 MTBF Y MTTR POR EQUIPO")
print(f"   {'Equipo':<35} {'N° Fallas':>9} {'MTTR (hrs)':>10} {'Disponib.':>10}")
print("   " + "-" * 68)

equipo_stats = df.groupby('Equipo').agg(
    n_fallas=('ID_OT', 'count'),
    mttr_min=('Tiempo_Total_Detencion_min', 'mean')
).reset_index()

dias_operacion = 730
horas_totales = dias_operacion * 24

for _, row in equipo_stats.sort_values('n_fallas', ascending=False).iterrows():
    mttr_hrs = row['mttr_min'] / 60
    horas_detencion = row['n_fallas'] * mttr_hrs
    disponibilidad = max(0, (horas_totales - horas_detencion) / horas_totales * 100)
    equipo_corto = row['Equipo'][:33]
    print(f"   {equipo_corto:<35} {row['n_fallas']:>9} {mttr_hrs:>10.1f} {disponibilidad:>9.1f}%")

# ── 3. RANKING DE FALLAS MÁS COSTOSAS ──────────────────────
print(f"\n💰 RANKING FALLAS MÁS COSTOSAS")
falla_costo = df.groupby('Tipo_Falla')['Costo_Reparacion_CLP'].agg(['sum','mean','count'])
falla_costo.columns = ['Costo_Total', 'Costo_Promedio', 'Frecuencia']
falla_costo = falla_costo.sort_values('Costo_Total', ascending=False)

for tipo, row in falla_costo.iterrows():
    print(f"   {tipo:<45} ${row['Costo_Total']:>15,.0f} CLP ({row['Frecuencia']:.0f} casos)")

# ── 4. IMPACTO DEL DESABASTECIMIENTO ───────────────────────
print(f"\n⚠️  IMPACTO DEL DESABASTECIMIENTO DE REPUESTOS")
con = df[df['Repuesto_Disponible'] == 'Sí']['Tiempo_Total_Detencion_min'].mean()
sin = df[df['Repuesto_Disponible'] == 'No']['Tiempo_Total_Detencion_min'].mean()
impacto = (sin - con) / con * 100
print(f"   Tiempo prom. CON repuesto  : {con:.0f} min ({con/60:.1f} hrs)")
print(f"   Tiempo prom. SIN repuesto  : {sin:.0f} min ({sin/60:.1f} hrs)")
print(f"   Incremento en tiempo       : +{impacto:.0f}% más de detención")
print(f"   Casos afectados            : {sin_repuesto} de {total_ot} ({sin_repuesto/total_ot*100:.1f}%)")

# ── 5. ALERTA DE EQUIPOS CRÍTICOS ──────────────────────────
print(f"\n🚨 EQUIPOS EN ZONA DE RIESGO (más de 20 fallas)")
equipos_riesgo = equipo_stats[equipo_stats['n_fallas'] >= 20].sort_values('n_fallas', ascending=False)
if len(equipos_riesgo) > 0:
    for _, row in equipos_riesgo.iterrows():
        print(f"   ⚠ {row['Equipo']} → {row['n_fallas']} fallas registradas")
else:
    alto_riesgo = equipo_stats.nlargest(3, 'n_fallas')
    for _, row in alto_riesgo.iterrows():
        print(f"   ⚠ {row['Equipo']} → {row['n_fallas']} fallas registradas")

# ── 6. ANÁLISIS POR TURNO ──────────────────────────────────
print(f"\n🌙 FALLAS POR TURNO")
turno_stats = df.groupby('Turno').agg(
    n_fallas=('ID_OT','count'),
    costo_prom=('Costo_Reparacion_CLP','mean'),
    tiempo_prom=('Tiempo_Total_Detencion_min','mean')
).reset_index()
for _, row in turno_stats.iterrows():
    print(f"   Turno {row['Turno']:<7}: {row['n_fallas']} fallas | "
          f"Costo prom: ${row['costo_prom']:,.0f} | "
          f"Tiempo prom: {row['tiempo_prom']/60:.1f} hrs")

# ── 7. VISUALIZACIONES ─────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor('#F8F9FA')
gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)

AZUL      = '#185FA5'
VERDE     = '#1D9E75'
NARANJA   = '#EF9F27'
ROJO      = '#E24B4A'
GRIS      = '#888780'
BG        = '#F8F9FA'
CARD_BG   = 'white'

# Gráfico 1: Fallas por tipo
ax1 = fig.add_subplot(gs[0, 0])
falla_count = df['Tipo_Falla'].value_counts().head(6)
labels = [t.replace(' - ', '\n').replace('programado','prog.') for t in falla_count.index]
colores = [ROJO if i < 2 else NARANJA if i < 4 else AZUL for i in range(len(falla_count))]
bars = ax1.barh(labels, falla_count.values, color=colores, edgecolor='none', height=0.6)
ax1.set_title('Fallas más frecuentes', fontsize=12, fontweight='bold', pad=12)
ax1.set_xlabel('N° de casos', fontsize=10)
ax1.tick_params(axis='y', labelsize=8)
ax1.set_facecolor(CARD_BG)
for bar, val in zip(bars, falla_count.values):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, str(val),
             va='center', fontsize=9, fontweight='bold')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Gráfico 2: Disponibilidad por equipo
ax2 = fig.add_subplot(gs[0, 1])
equipo_stats_sorted = equipo_stats.copy()
equipo_stats_sorted['disponibilidad'] = equipo_stats_sorted.apply(
    lambda r: max(0, (horas_totales - r['n_fallas'] * r['mttr_min']/60) / horas_totales * 100), axis=1)
equipo_stats_sorted = equipo_stats_sorted.sort_values('disponibilidad')
nombres_cortos = [e.split(' ')[0] + ' ' + e.split(' ')[1] for e in equipo_stats_sorted['Equipo']]
colores_disp = [ROJO if d < 85 else NARANJA if d < 92 else VERDE for d in equipo_stats_sorted['disponibilidad']]
bars2 = ax2.barh(nombres_cortos, equipo_stats_sorted['disponibilidad'], color=colores_disp, edgecolor='none', height=0.6)
ax2.axvline(x=85, color=ROJO, linestyle='--', linewidth=1.5, alpha=0.7, label='Mín. aceptable 85%')
ax2.set_title('Disponibilidad mecánica por equipo', fontsize=12, fontweight='bold', pad=12)
ax2.set_xlabel('Disponibilidad (%)', fontsize=10)
ax2.set_xlim(70, 100)
ax2.tick_params(axis='y', labelsize=8)
ax2.set_facecolor(CARD_BG)
ax2.legend(fontsize=8)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Gráfico 3: Costo por tipo de falla (top 5)
ax3 = fig.add_subplot(gs[0, 2])
top5_costo = falla_costo.head(5)
labels3 = [t.replace(' - ','\n').replace('programado','prog.') for t in top5_costo.index]
bars3 = ax3.bar(range(len(top5_costo)), top5_costo['Costo_Total']/1e6,
                color=[ROJO, NARANJA, AZUL, VERDE, GRIS], edgecolor='none', width=0.6)
ax3.set_xticks(range(len(top5_costo)))
ax3.set_xticklabels(labels3, fontsize=7, rotation=15, ha='right')
ax3.set_title('Costo total por tipo de falla', fontsize=12, fontweight='bold', pad=12)
ax3.set_ylabel('Millones CLP', fontsize=10)
ax3.set_facecolor(CARD_BG)
for bar, val in zip(bars3, top5_costo['Costo_Total']/1e6):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'${val:.0f}M', ha='center', fontsize=8, fontweight='bold')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# Gráfico 4: Impacto repuesto
ax4 = fig.add_subplot(gs[1, 0])
categorias = ['Con repuesto\nen bodega', 'Sin repuesto\nen bodega']
tiempos = [con/60, sin/60]
colores4 = [VERDE, ROJO]
bars4 = ax4.bar(categorias, tiempos, color=colores4, edgecolor='none', width=0.5)
ax4.set_title('Impacto desabastecimiento\nde repuestos', fontsize=12, fontweight='bold', pad=12)
ax4.set_ylabel('Horas de detención promedio', fontsize=10)
ax4.set_facecolor(CARD_BG)
for bar, val in zip(bars4, tiempos):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f} hrs', ha='center', fontsize=11, fontweight='bold')
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)
ax4.text(0.5, -0.18, f'+{impacto:.0f}% más tiempo sin repuesto',
         transform=ax4.transAxes, ha='center', fontsize=10,
         color=ROJO, fontweight='bold')

# Gráfico 5: Fallas por criticidad (dona)
ax5 = fig.add_subplot(gs[1, 1])
crit_count = df['Criticidad'].value_counts()
colores_crit = [ROJO, NARANJA, VERDE]
wedges, texts, autotexts = ax5.pie(
    crit_count.values, labels=crit_count.index,
    colors=colores_crit, autopct='%1.1f%%',
    startangle=90, pctdistance=0.75,
    wedgeprops=dict(width=0.5))
for text in texts: text.set_fontsize(10)
for autotext in autotexts: autotext.set_fontsize(9); autotext.set_fontweight('bold')
ax5.set_title('Distribución por criticidad', fontsize=12, fontweight='bold', pad=12)
ax5.set_facecolor(CARD_BG)

# Gráfico 6: Fallas por técnico
ax6 = fig.add_subplot(gs[1, 2])
tec_stats = df.groupby('Tecnico_Responsable').agg(
    n_fallas=('ID_OT','count'),
    costo_prom=('Costo_Reparacion_CLP','mean')
).reset_index().sort_values('n_fallas', ascending=True)
nombres_tec = [n.split(' ')[0] for n in tec_stats['Tecnico_Responsable']]
bars6 = ax6.barh(nombres_tec, tec_stats['n_fallas'], color=AZUL, edgecolor='none', height=0.5)
ax6.set_title('Carga de trabajo por técnico', fontsize=12, fontweight='bold', pad=12)
ax6.set_xlabel('N° de intervenciones', fontsize=10)
ax6.set_facecolor(CARD_BG)
for bar, val in zip(bars6, tec_stats['n_fallas']):
    ax6.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             str(val), va='center', fontsize=9, fontweight='bold')
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

fig.suptitle('Dashboard de Análisis de Fallas — Operaciones Mineras\n2023-2024',
             fontsize=16, fontweight='bold', y=0.98, color='#2C2C2A')

plt.savefig(r'C:\Users\WindowsX\Desktop\Proyecto Litio Pelao\dashboard_fallas.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
plt.close()
print("\n✅ Dashboard guardado exitosamente")
