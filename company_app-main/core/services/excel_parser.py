import pandas as pd
import os
import re


class BudgetExcelParser:
    @staticmethod
    def parse_budget_file(file_path, anul=None):
        try:
            print(f"Starting Excel parsing for file: {file_path}")

            # 1. Если год не указан, пробуем определить из имени файла
            if anul is None:
                anul = BudgetExcelParser.extract_year_from_filename(file_path)
                print(f"Detected year from filename: {anul}")

            # 2. Получаем все доступные листы
            try:
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                sheet_names = excel_file.sheet_names
                print(f"Available sheets: {sheet_names}")
            except Exception as e:
                raise Exception(f"Cannot read Excel file: {e}")

            # 3. Ищем подходящий лист (учитываем год)
            target_sheet = BudgetExcelParser.find_best_sheet(sheet_names, anul)
            print(f"Selected sheet: '{target_sheet}'")

            # 4. Читаем данные
            df = pd.read_excel(file_path, sheet_name=target_sheet, header=None, engine='openpyxl')
            print(f"Sheet '{target_sheet}' loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            # 5. Определяем структуру данных (учитываем год в заголовках)
            code_col, name_col, amount_col = BudgetExcelParser.detect_columns(df, anul)
            print(f"Detected structure: Code col={code_col}, Name col={name_col}, Amount col={amount_col}")

            budget_lines = []
            processed_count = 0

            # 6. Парсим данные
            for index, row in df.iterrows():
                if code_col is not None and BudgetExcelParser.is_valid_budget_row(row, code_col):
                    cod_bugetar = str(row[code_col]).strip()
                    denumirea = str(row[name_col]) if name_col is not None and pd.notna(row[name_col]) else ""

                    # Получаем сумму (можем искать по году в заголовках)
                    suma_alocata = BudgetExcelParser.extract_amount_by_year(row, df, anul, amount_col)

                    if suma_alocata > 0 and denumirea and len(denumirea) > 3:
                        budget_lines.append({
                            'cod_bugetar': cod_bugetar,
                            'denumirea': denumirea,
                            'suma_alocata': suma_alocata,
                            'anul': anul
                        })
                        processed_count += 1

            print(f"Parsing completed. Found {processed_count} valid budget lines for year {anul}.")
            return budget_lines

        except Exception as e:
            print(f"Critical error in Excel parsing: {str(e)}")
            raise Exception(f"Eroare la parsarea fișierului Excel: {str(e)}")

    @staticmethod
    def extract_year_from_filename(file_path):
        """Извлекает год из имени файла"""
        filename = os.path.basename(file_path)

        # Ищем год в формате YYYY
        year_pattern = r'(20\d{2})'
        matches = re.findall(year_pattern, filename)

        if matches:
            return int(matches[-1])  # Берем последний найденный год

        # Если год не найден, используем текущий
        from datetime import datetime
        return datetime.now().year

    @staticmethod
    def find_best_sheet(sheet_names, target_year):
        """Находит лучший лист с учетом года"""
        sheet_priority = [
            # Приоритет: листы с указанием года
            lambda name: str(target_year) in name and any(word in name.lower() for word in ['buget', 'budget']),
            lambda name: str(target_year) in name,
            lambda name: any(word in name.lower() for word in ['buget', 'budget']) and any(
                str(year) in name for year in range(2020, 2030)),
            lambda name: any(word in name.lower() for word in ['buget', 'budget']),
            lambda name: any(word in name.lower() for word in ['date', 'linii', 'indicatori']),
            lambda name: True  # Берем первый лист как запасной вариант
        ]

        for priority_func in sheet_priority:
            for sheet_name in sheet_names:
                if priority_func(sheet_name):
                    return sheet_name

        return sheet_names[0]  # Первый лист по умолчанию

    @staticmethod
    def detect_columns(df, target_year):
        """Автоопределение колонок с учетом года"""
        code_col = None
        name_col = None
        amount_col = None

        sample_rows = min(20, df.shape[0])

        # Ищем колонку с кодами
        for col in range(min(10, df.shape[1])):
            numeric_count = 0
            for row in range(sample_rows):
                if pd.notna(df.iloc[row, col]) and str(df.iloc[row, col]).strip().isdigit():
                    numeric_count += 1

            if numeric_count >= sample_rows * 0.3:
                code_col = col
                break

        if code_col is None:
            code_col = 0

        # Ищем колонку с названиями
        if code_col + 1 < df.shape[1]:
            name_col = code_col + 1
        elif code_col > 0:
            name_col = code_col - 1
        else:
            name_col = 1

        # Ищем колонку с суммами для указанного года
        amount_col = BudgetExcelParser.find_amount_column(df, target_year, sample_rows)

        return code_col, name_col, amount_col

    @staticmethod
    def find_amount_column(df, target_year, sample_rows):
        """Находит колонку с суммами для указанного года"""
        # Сначала ищем по заголовкам (если они есть)
        header_year_col = BudgetExcelParser.find_column_by_header(df, str(target_year))
        if header_year_col is not None:
            return header_year_col

        # Ищем колонки с типичными названиями для бюджетов
        budget_headers = ['suma', 'amount', 'valoare', 'buget', 'alocat', 'planificat']
        for col in range(df.shape[1]):
            # Проверяем первую строку как возможный заголовок
            if pd.notna(df.iloc[0, col]) and any(header in str(df.iloc[0, col]).lower() for header in budget_headers):
                return col

        # Ищем по паттерну данных (большие числа)
        for col in range(df.shape[1]):
            amount_count = 0
            for row in range(1, sample_rows):  # Пропускаем возможный заголовок
                try:
                    val = df.iloc[row, col]
                    if pd.notna(val):
                        num_val = float(str(val).replace(' ', '').replace(',', '.'))
                        if num_val > 1000:
                            amount_count += 1
                except (ValueError, TypeError):
                    continue

            if amount_count >= (sample_rows - 1) * 0.2:
                return col

        # По умолчанию - колонка 5
        return 5 if df.shape[1] > 5 else min(2, df.shape[1] - 1)

    @staticmethod
    def find_column_by_header(df, year_str):
        """Ищет колонку по заголовку с указанием года"""
        if df.shape[0] == 0:
            return None

        # Проверяем первую строку как возможные заголовки
        for col in range(df.shape[1]):
            if pd.notna(df.iloc[0, col]):
                header = str(df.iloc[0, col])
                if year_str in header and any(
                        word in header.lower() for word in ['suma', 'amount', 'buget', 'valoare']):
                    return col

        return None

    @staticmethod
    def extract_amount_by_year(row, df, target_year, default_amount_col):
        """Извлекает сумму с учетом года"""
        # Если нашли колонку по заголовку года
        year_col = BudgetExcelParser.find_column_by_header(df, str(target_year))
        if year_col is not None and year_col < len(row):
            amount = BudgetExcelParser.extract_amount(row, year_col)
            if amount > 0:
                return amount

        # Используем колонку по умолчанию
        return BudgetExcelParser.extract_amount(row, default_amount_col)

    @staticmethod
    def is_valid_budget_row(row, code_col):
        """Проверяет, валидна ли строка для бюджетной линии"""
        if code_col >= len(row) or pd.isna(row[code_col]):
            return False

        code_str = str(row[code_col]).strip()
        return code_str.isdigit() and len(code_str) <= 10

    @staticmethod
    def extract_amount(row, amount_col):
        """Извлекает сумму из строки"""
        if amount_col is None or amount_col >= len(row) or pd.isna(row[amount_col]):
            return 0

        try:
            cell_value = row[amount_col]
            if isinstance(cell_value, str):
                cell_value = cell_value.replace(' ', '').replace(',', '.')
                cell_value = ''.join(ch for ch in cell_value if ch.isdigit() or ch in '.-')

            amount = float(cell_value)
            return amount if amount > 0 else 0
        except (ValueError, TypeError):
            return 0