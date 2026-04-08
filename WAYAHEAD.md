# WAYAHEAD — narrative-radar

## 2026-04-08

### Bugs cerrados hoy
- **fix fecha %H:%M→%H:%M:%S** en `detect_ideology.py`, `agenda_setting.py`, `government_coverage.py`, `detect_coordination.py` — filas nuevas dejaban de parsear (NaT) por formato sin segundos
- **format="mixed"** añadido en `check_freshness.py`, `audit_quality.py`, `audit_tab.py` — mix de fechas con/sin `+00:00` en CSVs históricos
- **purge_history.py** — `pd.Timestamp(HOY, tz="UTC")` → `pd.Timestamp.now(tz="UTC")` — double-tzinfo ValueError en cada ejecución (rc=1 desde siempre)
- Retroarreglo CSVs: 2235 filas con fecha sin segundos normalizadas (`+":00"`)

### Pendiente
1. **L2R tab en auditoría** — tabla lecciones aprendidas: fecha, impacto, fix, CSV `lessons_learned.csv` acumulativo
2. **Narrative Radar Light** — versión pública sin paywall, en inglés, 4-5 tabs (headlines, narratives, sentiment, disinfo), repo separado Streamlit Cloud
3. **Historiales desbloqueados** — revisar retención y gaps históricos
4. **Semáforo activo** — indicador visual de estado del pipeline en dashboard
