import json
import os
from datetime import datetime
from urllib.parse import urlencode

import pandas as pd
import requests
from dotenv import load_dotenv
import logging
load_dotenv()

URL = os.getenv("URL")
TOKEN = os.getenv("TOKEN")
TOKEN_TYPE = os.getenv("TOKEN_TYPE")

async def get_stats_from_yandex():
    headers = {
        'Authorization': f"{TOKEN_TYPE} {TOKEN}",
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json',
        'accept-encoding': 'gzip, deflate, br, zstd',
    }

    response = requests.get(url=create_correct_yandex_url_v2(), headers=headers)
    if response.status_code != 200:
        logging.info(response.text)
        return "error {}".format(response.status_code)
    logging.info("stats get from yandex")
    logging.info(response.text)
    return response.json()




def create_correct_yandex_url_v2():
    """Создает правильный URL с использованием urlencode"""

    base_url = URL + '?stat_type=main&order_by=[{"field":"date","dir":"desc"}]&'

    # Параметры как список кортежей (ключ, значение)
    params = [
        ("currency", "RUB"),
        ("lang", "ru"),
        ("levels", "payment"),
        ("entity_field", "page_id"),
        ("entity_field", "page_caption"),
        ("dimension_field", "date|day"),
        ("field", "cpmv_partner_wo_nds"),
        ("field", "clicks_direct"),
        ("field", "partner_wo_nds"),
        ("field", "clicks"),
        ("field", "impressions"),
        ("field", "ecpm_partner_wo_nds"),
        ("pretty", "1"),
        ("stat_type", "main"),
        ("timezone", "Europe/Moscow"),
        ("period", "7days"),
        ("limits", '{"offset":0,"limit":500}'),
    ]

    # Кодируем параметры
    query_string = urlencode(params)
    logging.info(f"{base_url}?{query_string}")
    return f"{base_url}?{query_string}"


def save_json_to_excel(json_data):
    """
       Создает Excel-таблицу из JSON с автоматическим добавлением строки "Итого"
       для числовых полей.
       """

    # Если данные переданы как строка, преобразуем в словарь
    filename = datetime.now().strftime("%Y%m%d-%H%M%S") + ".xlsx"
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    # Извлекаем точки данных
    points = data.get('data', {}).get('points', [])

    if not points:
        logging.info("Нет данных для обработки")
        return None

    rows = []

    for point in points:
        row = {}

        # Обрабатываем dimensions (измерения: дата, ID сайта и т.д.)
        dimensions = point.get('dimensions', {})
        for key, value in dimensions.items():
            if isinstance(value, list):
                row[key] = value[0] if value else ''
            else:
                row[key] = value

        # Обрабатываем measures (метрики: показы, клики и т.д.)
        measures_list = point.get('measures', [])
        if measures_list:
            measures = measures_list[0]
            for key, value in measures.items():
                row[key] = value

        rows.append(row)

    # Создаем DataFrame
    df = pd.DataFrame(rows)

    # Переименовываем колонки
    column_mapping = {}
    if 'dimensions' in data.get('data', {}):
        for key, info in data['data']['dimensions'].items():
            if 'title' in info and key in df.columns:
                column_mapping[key] = info['title']

    if 'measures' in data.get('data', {}):
        for key, info in data['data']['measures'].items():
            if 'title' in info and key in df.columns:
                title = info['title']
                if 'currency' in info:
                    title = f"{title} ({info['currency']})"
                column_mapping[key] = title

    if column_mapping:
        df = df.rename(columns=column_mapping)

    # Добавляем строку "Итого"
    # Определяем, какие колонки являются числовыми и можно суммировать
    numeric_cols = []
    for col in df.columns:
        # Проверяем, является ли колонка числовой
        if pd.api.types.is_numeric_dtype(df[col]):
            # Пропускаем ID и подобные числовые поля, которые не нужно суммировать
            if not any(name in col.lower() for name in ['id', 'номер', 'index', 'индекс']):
                numeric_cols.append(col)

    # Создаем строку с итогами
    totals_row = {}
    for col in df.columns:
        if col in numeric_cols:
            # Суммируем числовые колонки
            totals_row[col] = df[col].sum()
        else:
            # Для нечисловых колонок ставим "Итого"
            totals_row[col] = 'Итого'

    # Добавляем строку итогов в DataFrame
    totals_df = pd.DataFrame([totals_row])
    df_with_totals = pd.concat([df, totals_df], ignore_index=True)

    # Форматируем числовые колонки для лучшего отображения
    for col in numeric_cols:
        # Для денежных значений оставляем 2 знака после запятой
        if any(word in col.lower() for word in ['cpm', 'ecpm', 'вознаграждение', 'руб', 'деньги']):
            df_with_totals[col] = df_with_totals[col].apply(
                lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x
            )
        # Для больших чисел добавляем разделители тысяч
        elif df[col].max() > 1000:
            df_with_totals[col] = df_with_totals[col].apply(
                lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x
            )

    # Сохраняем в Excel
    df_with_totals.to_excel(filename, index=False)

    logging.info(f"✅ Таблица сохранена в файл: {filename}")
    logging.info(f"📊 Всего строк: {len(df_with_totals)} (включая итоги)")
    logging.info(f"💰 Суммированные колонки: {', '.join(numeric_cols)}")

    return filename


async def generate_report():
    stats_json = await get_stats_from_yandex()
    return save_json_to_excel(stats_json)

