"""Helpers de analytics para o dashboard administrativo."""

from collections import Counter
from datetime import datetime, timedelta


COUNTRY_CODE_MAP = {
    'AR': 'Argentina',
    'AU': 'Australia',
    'BR': 'Brasil',
    'CA': 'Canada',
    'DE': 'Germany',
    'ES': 'Spain',
    'FR': 'France',
    'GB': 'United Kingdom',
    'IN': 'India',
    'IT': 'Italy',
    'JP': 'Japan',
    'MX': 'Mexico',
    'PT': 'Portugal',
    'US': 'United States',
}


def _parse_visit_datetime(visita):
    """Converte o timestamp da visita para datetime quando possivel."""
    raw_value = visita.get('data') or visita.get('timestamp')
    if not raw_value:
        return None

    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue

    return None


def _build_rolling_average(values, window_size=3):
    """Calcula media movel simples para suavizar tendencia."""
    averages = []
    for index in range(len(values)):
        start = max(0, index - window_size + 1)
        window = values[start:index + 1]
        averages.append(round(sum(window) / len(window), 2))
    return averages


def _normalize_country_name(visita):
    """Extrai um pais consistente a partir do registro salvo no contador."""
    raw_country = visita.get('pais') or visita.get('country')
    if not raw_country:
        localizacao = visita.get('local')
        if localizacao:
            raw_country = localizacao.split(',')[-1].strip()

    if not raw_country:
        return None

    if raw_country in ('Desconhecido', 'Localhost', 'Rede Local'):
        return None

    return COUNTRY_CODE_MAP.get(raw_country.upper(), raw_country)


def _resolve_period_days(period_days):
    """Limita o periodo de analise a opcoes seguras para o dashboard."""
    allowed_periods = {7, 14, 30}
    if period_days in allowed_periods:
        return period_days
    return 30


def build_dashboard_analytics(visitas, period_days=30):
    """Gera series prontas para os graficos do dashboard."""
    period_days = _resolve_period_days(period_days)
    visitas_por_dia = Counter()
    downloads_por_dia = Counter()
    visitas_por_hora = Counter({hour: 0 for hour in range(24)})
    paises = set()
    today = datetime.now().date()
    first_day = today - timedelta(days=period_days - 1)

    for visita in visitas:
        visit_datetime = _parse_visit_datetime(visita)
        if visit_datetime:
            event_date = visit_datetime.date()
            evento = visita.get('evento') or 'visita'
            if event_date >= first_day:
                dia = event_date.strftime('%Y-%m-%d')
                if evento in ('download',):
                    downloads_por_dia[dia] += 1
                elif evento in ('visita_download',):
                    visitas_por_dia[dia] += 1
                    downloads_por_dia[dia] += 1
                else:
                    visitas_por_dia[dia] += 1
                visitas_por_hora[visit_datetime.hour] += 1

        pais = _normalize_country_name(visita)
        if pais:
            paises.add(pais)

    timeline = [first_day + timedelta(days=offset) for offset in range(period_days)]
    visitas_labels = [day.strftime('%Y-%m-%d') for day in timeline]
    visitas_data = [visitas_por_dia[label] for label in visitas_labels]
    downloads_data = [downloads_por_dia[label] for label in visitas_labels]
    visitas_tendencia = _build_rolling_average(visitas_data) if visitas_data else []

    horas_labels = [f'{hour:02d}:00' for hour in range(24)]
    horas_data = [visitas_por_hora[hour] for hour in range(24)]

    hora_pico = None
    total_pico = 0
    if horas_data and any(horas_data):
        indice_pico = max(range(24), key=lambda hour: horas_data[hour])
        hora_pico = horas_labels[indice_pico]
        total_pico = horas_data[indice_pico]

    return {
        'visitas_labels': visitas_labels,
        'visitas_data': visitas_data,
        'downloads_data': downloads_data,
        'visitas_tendencia': visitas_tendencia,
        'horas_labels': horas_labels,
        'horas_data': horas_data,
        'hora_pico': hora_pico,
        'hora_pico_total': total_pico,
        'period_days': period_days,
        'paises': sorted(paises),
    }