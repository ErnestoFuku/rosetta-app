# -*- coding: utf-8 -*-
"""
Módulo para procesar archivos .tab de Rosetta
Adaptado del código de Colab para funcionar con archivos en memoria
"""
import re
import os
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from io import BytesIO, StringIO


# -------------------------
# Helpers
# -------------------------
def _to_int(x):
    try:
        if x is None:
            return None
        return int(str(x).split()[0])
    except Exception:
        return None


def _strip_c_comments(s):
    return re.sub(r'/\*.*?\*/', '', s, flags=re.DOTALL).strip()


def _find_label_value(header, key):
    """
    Busca la línea 'key = valor' con tolerancia:
    - espacios al inicio
    - insensible a mayúsculas
    - guarda todo el RHS para luego limpiar comentarios
    """
    pat = r'^\s*' + re.escape(key) + r'\s*=\s*(.+)$'
    m = re.search(pat, header, flags=re.MULTILINE | re.IGNORECASE)
    return _strip_c_comments(m.group(1)) if m else None


def _parse_pointer_rhs(rhs):
    """
    Interpreta RHS de punteros PDS3, devuelve sólo el filename cuando aplique:
      ("FNAME.FMT", n) -> FNAME.FMT
      "FNAME.FMT"      -> FNAME.FMT
      FNAME.FMT        -> FNAME.FMT
    """
    if rhs is None:
        return None
    s = rhs.strip()
    # ("file", n)
    m = re.match(r'^\(\s*["\']?([^,"\')]+)["\']?\s*(?:,\s*\d+)?\s*\)$', s)
    if m:
        return m.group(1)
    # "file"
    m = re.match(r'^["\']([^"\']+)["\']$', s)
    if m:
        return m.group(1)
    # plain token
    return s.split()[0]


# -------------------------
# Lectura del encabezado PDS3 desde BytesIO
# -------------------------
def read_label_header_from_stream(file_stream):
    """
    Lee el encabezado PDS3 desde un stream (BytesIO o StringIO).
    Retorna un diccionario con los metadatos.
    """
    # Resetear el stream al inicio
    file_stream.seek(0)
    
    # Leer como texto
    if isinstance(file_stream, BytesIO):
        content = file_stream.read().decode('latin-1', errors='ignore')
    else:
        content = file_stream.read()
    
    # Crear un nuevo stream de texto
    text_stream = StringIO(content)
    
    hdr_lines = []
    for line in text_stream:
        hdr_lines.append(line.rstrip('\n'))
        if line.strip().upper() == 'END':
            break
    
    header = '\n'.join(hdr_lines)

    out = {
        'RECORD_BYTES': _to_int(_find_label_value(header, 'RECORD_BYTES')),
        'LABEL_RECORDS': _to_int(_find_label_value(header, 'LABEL_RECORDS')),
        'INSTRUMENT_ID': (_find_label_value(header, 'INSTRUMENT_ID') or '').strip(),
        'DETECTOR_ID': (_find_label_value(header, 'DETECTOR_ID') or '').strip(),
        'INSTRUMENT_MODE_ID': (_find_label_value(header, 'INSTRUMENT_MODE_ID') or '').strip(),
        'PRODUCT_ID': (_find_label_value(header, 'PRODUCT_ID') or '').strip(),
        'START_TIME': (_find_label_value(header, 'START_TIME') or '').strip(),
        'STOP_TIME': (_find_label_value(header, 'STOP_TIME') or '').strip(),
        'DATA_QUALITY_ID': (_find_label_value(header, 'DATA_QUALITY_ID') or '').strip(),
        'ROWS': _to_int(_find_label_value(header, 'ROWS')),
        'COLUMNS': _to_int(_find_label_value(header, 'COLUMNS')),
        'ROW_BYTES': _to_int(_find_label_value(header, 'ROW_BYTES')),
        '__HEADER': header
    }

    # ^STRUCTURE
    struct_raw = _find_label_value(header, '^STRUCTURE') or _find_label_value(header, 'STRUCTURE')
    struct_file = _parse_pointer_rhs(struct_raw) if struct_raw else None
    out['STRUCTURE_RAW'] = struct_raw or ''
    out['STRUCTURE_FILE'] = struct_file or ''

    return out


# -------------------------
# Parseo de columnas (desde .FMT o inline)
# -------------------------
def parse_fmt_columns_from_text(fmt_text):
    cols = []
    for m in re.finditer(r'COLUMN\s*=\s*\{(.*?)\}', fmt_text, flags=re.DOTALL | re.IGNORECASE):
        blk = m.group(1)

        def grab(k):
            mm = re.search(rf'{k}\s*=\s*(.+)', blk, flags=re.IGNORECASE)
            if not mm:
                return None
            v = _strip_c_comments(mm.group(1)).strip().strip('"')
            return v

        name = grab('NAME') or grab('COLUMN_NAME') or ''
        start = grab('START_BYTE') or '1'
        width = grab('BYTES') or '0'
        cols.append({
            'name': name,
            'start_byte': int(str(start).split()[0]),
            'bytes': int(str(width).split()[0])
        })
    return cols


def parse_fmt_columns_from_header(header_dict):
    """
    Intenta parsear columnas desde el header inline.
    Si no encuentra, usa fallback genérico.
    """
    # 1) Inline (algunos productos traen COLUMN={...} en el label)
    header = header_dict.get('__HEADER', '')
    cols = parse_fmt_columns_from_text(header)
    if cols:
        return cols

    # 2) Fallback genérico si hay COLUMNS/ROW_BYTES
    C = header_dict.get('COLUMNS')
    W = header_dict.get('ROW_BYTES')
    if C and W and C > 0:
        width = max(1, int(W // C))
        return [{'name': f'COL_{i+1}', 'start_byte': i*width+1, 'bytes': width} for i in range(C)]

    return []


# -------------------------
# Lectura de tabla desde stream
# -------------------------
def read_fixed_table_stream(file_stream, fmt_cols, record_bytes, start_record, rows=None, encoding='latin-1'):
    """
    Lee la tabla de datos desde un stream.
    """
    data = []
    rec0 = max(int(start_record or 1), 1) - 1
    read_max = int(rows) if rows is not None else None
    
    # Resetear stream
    file_stream.seek(0)
    
    # Leer todo el contenido
    if isinstance(file_stream, BytesIO):
        content = file_stream.read()
    else:
        content = file_stream.read().encode(encoding)
    
    # Calcular offset inicial
    offset = rec0 * int(record_bytes)
    content = content[offset:]
    
    # Procesar registros
    n = 0
    rec_size = int(record_bytes)
    for i in range(0, len(content), rec_size):
        blob = content[i:i+rec_size]
        if len(blob) < rec_size:
            break
        
        try:
            rec = blob.decode(encoding, errors='ignore').rstrip('\r\n')
        except:
            continue

        row = {}
        # Si hay comas, parsear como CSV por orden de columnas
        if ',' in rec and len(fmt_cols) > 0:
            fields = next(csv.reader([rec]))
            # normalizar longitud
            if len(fields) < len(fmt_cols):
                fields = fields + [''] * (len(fmt_cols) - len(fields))
            if len(fields) > len(fmt_cols):
                fields = fields[:len(fmt_cols)]
            for i, col in enumerate(fmt_cols):
                row[col.get('name') or f'COL_{i+1}'] = fields[i].strip().strip('"')
        else:
            # Corte por posiciones (fallback)
            for col in fmt_cols:
                name = col.get('name') or 'COL'
                start = int(col.get('start_byte', 1)) - 1
                width = int(col.get('bytes', 0))
                val = rec[start:start+width] if width > 0 else ''
                row[name] = val.strip()

        data.append(row)
        n += 1
        if read_max is not None and n >= read_max:
            break
    
    return pd.DataFrame(data)


# -------------------------
# Heurística X/Y
# -------------------------
def pick_xy_columns(df):
    """
    Infiere las columnas x (m/z) e y (intensidad) del DataFrame.
    """
    cols = [c.strip() for c in df.columns]
    lc = [c.lower() for c in cols]
    x_keys = ['mass', 'm/z', 'mz', 'amu', 'bin', 'chan', 'channel', 'x']
    y_keys = ['intens', 'counts', 'cps', 'signal', 'y', 'amp', 'height']

    def find(keys):
        for k in keys:
            for i, c in enumerate(lc):
                if k in c:
                    return cols[i]
        return None

    xcol = find(x_keys) or (cols[0] if len(cols) > 0 else None)
    ycol = find(y_keys) or (cols[1] if len(cols) > 1 else None)
    
    if not xcol or not ycol:
        raise ValueError(f"No pude inferir x/y en columnas: {cols}")
    
    return xcol, ycol


# -------------------------
# Funciones auxiliares para lectura post-END (como en Colab)
# -------------------------
def _is_numeric_line(s):
    """Descarta etiquetas (contienen '=') y acepta notación científica"""
    if '=' in s or not s.strip():
        return False
    nums = re.findall(r"[-+]?\d*\.\d+(?:[EeDd][-+]?\d+)?|\d+(?:[EeDd][-+]?\d+)?", s)
    return len(nums) >= 3

def _split_numbers(s):
    """Divide una línea en números, manejando comas y espacios"""
    if ',' in s:
        parts = [p.strip() for p in s.split(',') if p.strip()]
    else:
        parts = s.split()
    if len(parts) < 2:
        parts = re.findall(r"[-+]?\d*\.\d+(?:[EeDd][-+]?\d+)?|\d+(?:[EeDd][-+]?\d+)?", s)
    return parts

def _slice_numeric_blocks(lines):
    """Encuentra bloques de líneas numéricas consecutivas"""
    blocks, i, n = [], 0, len(lines)
    while i < n:
        while i < n and not _is_numeric_line(lines[i]): 
            i += 1
        start = i
        while i < n and _is_numeric_line(lines[i]): 
            i += 1
        if i - start >= 3: 
            blocks.append(lines[start:i])
    return blocks

def _xy_from_block(block_lines, detector="RTOF"):
    """
    Extrae x e y de un bloque de líneas numéricas.
    Basado en DETECTOR_COLS del código de Colab: {"DFMS": (1, 2), "RTOF": (1, 3)}
    En el código de Colab, estos valores se usan directamente como índices (basados en 0),
    así que RTOF usa índices 0 y 2, DFMS usa 0 y 1.
    """
    xs, ys = [], []
    det = detector.upper()
    # DETECTOR_COLS del código de Colab: {"DFMS": (1, 2), "RTOF": (1, 3)}
    # En el código original se usan directamente: parts[ix_x] donde ix_x viene de DETECTOR_COLS
    # Si DETECTOR_COLS = (1, 2), entonces parts[1] accede al segundo elemento (índice 1)
    # Esto significa que DETECTOR_COLS usa índices basados en 0 directamente
    # Así que (1, 2) significa índices 1 y 2, (1, 3) significa índices 1 y 3
    detector_cols = {"DFMS": (1, 2), "RTOF": (1, 3)}
    ix_x, ix_y = detector_cols.get(det, (1, 2))
    
    for s in block_lines:
        parts = _split_numbers(s)
        if len(parts) > max(ix_x, ix_y):
            try:
                x = float(parts[ix_x].replace("D", "E").replace("d", "e"))
                y = float(parts[ix_y].replace("D", "E").replace("d", "e"))
                xs.append(x)
                ys.append(y)
            except:
                continue
        elif len(parts) >= 2:
            try:
                x = float(parts[0].replace("D", "E").replace("d", "e"))
                y = float(parts[1].replace("D", "E").replace("d", "e"))
                xs.append(x)
                ys.append(y)
            except:
                continue
    
    if not xs:
        return pd.DataFrame(columns=["x", "y"])
    
    df = pd.DataFrame({"x": xs, "y": ys})
    df["scan_i"] = np.arange(len(df), dtype=int)
    return df.replace([np.inf, -np.inf], np.nan).dropna()

def _read_post_end_lines(file_stream):
    """Lee líneas después de END, similar a Colab"""
    file_stream.seek(0)
    if isinstance(file_stream, BytesIO):
        content = file_stream.read().decode('latin-1', errors='ignore')
    else:
        content = file_stream.read()
    
    lines_after, found_end = [], False
    for line in content.split('\n'):
        stripped = line.strip()
        if found_end:
            if not stripped or stripped.startswith('"'):
                continue
            lines_after.append(stripped)
        if stripped.upper() == "END":
            found_end = True
    
    return lines_after

def _robust_clean_simple(df, detector="RTOF", filter_level="high", **filter_params):
    """
    Limpieza robusta simplificada basada en el código de Colab.
    
    Args:
        df: DataFrame con columnas 'x' e 'y'
        detector: Tipo de detector ("RTOF" o "DFMS")
        filter_level: Nivel de filtrado ("high" para alto grado, "low" para bajo grado)
        **filter_params: Parámetros opcionales de filtrado:
            - head_drop: Número de filas iniciales a descartar (default: 10 para RTOF, 5 para DFMS)
            - mad_multiplier_rtof: Multiplicador MAD para RTOF (default: 10 para alto, 1000 para bajo)
            - cps_threshold_rtof: Umbral absoluto de cps para RTOF (default: 5 para alto, 500 para bajo)
            - mad_multiplier_dfms: Multiplicador MAD para DFMS (default: 8 para alto, 800 para bajo)
            - cps_threshold_dfms: Umbral absoluto de cps para DFMS (default: 1e4 para alto, 1e8 para bajo)
    
    Para RTOF (alto grado): descarta primeras filas, centra cps, filtra outliers estrictos (ajustable).
    Para DFMS (alto grado): descarta primeras filas, centra cps, filtra outliers estrictos (ajustable).
    
    Para bajo grado: descarta primeras filas y aplica filtros más permisivos (ajustable).
    """
    if df.empty:
        return df
    
    det = detector.upper()
    is_high_filter = filter_level.lower() == "high"
    
    # Configurar parámetros según el nivel de filtrado
    # Usar parámetro personalizado o default
    if "head_drop" in filter_params:
        head_drop = filter_params["head_drop"]
    else:
        head_drop = 10 if det == "RTOF" else 5
    
    # Descartar primeras filas
    if len(df) > head_drop:
        df = df.iloc[head_drop:].copy()
    
    # Filtrar x > 0 (siempre aplicamos este filtro básico)
    df = df[df["x"] > 0].copy()
    
    if df.empty:
        return df
    
    if is_high_filter:
        # ALTO GRADO: Versión original del código de Colab (sin modificaciones)
        # Convertir y a float y centrar (restar mediana) - exactamente como en el código original
        y = df["y"].astype(float)
        med = np.median(y)
        cps = y - med
        df["cps"] = cps
        
        # Filtrar outliers usando MAD
        mad = np.median(np.abs(cps - np.median(cps))) + 1e-12
        
        if det == "RTOF":
            # RTOF: usar parámetros personalizados o defaults
            mad_mult = filter_params.get("mad_multiplier_rtof", 10)
            cps_thresh = filter_params.get("cps_threshold_rtof", 5)
            df = df[(df["cps"].abs() <= mad_mult * mad) & (df["cps"].abs() <= cps_thresh)].copy()
        else:
            # DFMS: usar parámetros personalizados o defaults
            mad_mult = filter_params.get("mad_multiplier_dfms", 8)
            cps_thresh = filter_params.get("cps_threshold_dfms", 1e4)
            df = df[(df["cps"].abs() <= mad_mult * mad) & (df["cps"].abs() <= cps_thresh)].copy()
    else:
        # BAJO GRADO: Versión mejorada con filtrado mínimo
        # Convertir y a float y eliminar valores negativos de intensidad original
        y = df["y"].astype(float)
        df = df[y >= 0].copy()
        
        if df.empty:
            return df
        
        # Recalcular y después del filtrado
        y = df["y"].astype(float)
        
        # Centrar (restar mediana)
        med = np.median(y)
        cps = y - med
        df["cps"] = cps
        
        # Eliminar valores negativos después del centrado (cps < 0)
        df = df[df["cps"] >= 0].copy()
        
        # Filtrar outliers usando MAD
        mad = np.median(np.abs(cps - np.median(cps))) + 1e-12
        
        if det == "RTOF":
            # RTOF: usar parámetros personalizados o defaults
            mad_mult = filter_params.get("mad_multiplier_rtof", 1000)
            cps_thresh = filter_params.get("cps_threshold_rtof", 500)
            df = df[(df["cps"].abs() <= mad_mult * mad) & (df["cps"].abs() <= cps_thresh)].copy()
        else:
            # DFMS: usar parámetros personalizados o defaults
            mad_mult = filter_params.get("mad_multiplier_dfms", 800)
            cps_thresh = filter_params.get("cps_threshold_dfms", 1e8)
            df = df[(df["cps"].abs() <= mad_mult * mad) & (df["cps"].abs() <= cps_thresh)].copy()
    
    return df[["x", "cps"]].copy()

# -------------------------
# Función principal para procesar archivo .tab
# -------------------------
def process_tab_file(file_stream, filter_level="high", **filter_params):
    """
    Procesa un archivo .tab desde un stream (BytesIO) y retorna un DataFrame
    con columnas 'x' (m/z) e 'cps' (intensidad).
    Sigue la lógica del código de Colab: lee datos después de END.
    
    Args:
        file_stream: BytesIO con el contenido del archivo .tab
        filter_level: Nivel de filtrado ("high" para alto grado, "low" para bajo grado)
        **filter_params: Parámetros opcionales de filtrado:
            - head_drop: Número de filas iniciales a descartar
            - mad_multiplier_rtof: Multiplicador MAD para RTOF
            - cps_threshold_rtof: Umbral absoluto de cps para RTOF
            - mad_multiplier_dfms: Multiplicador MAD para DFMS
            - cps_threshold_dfms: Umbral absoluto de cps para DFMS
    
    Returns:
        DataFrame con columnas 'x' y 'cps'
    """
    # Leer encabezado para detectar el detector
    meta = read_label_header_from_stream(file_stream)
    detector_id = meta.get('DETECTOR_ID', '').upper()
    detector = "RTOF" if "RTOF" in detector_id else "DFMS" if "DFMS" in detector_id else "RTOF"
    
    # Leer líneas después de END
    lines_after = _read_post_end_lines(file_stream)
    
    if not lines_after:
        raise ValueError("No se encontraron datos después de la línea END")
    
    # Buscar bloques numéricos
    blocks = _slice_numeric_blocks(lines_after)
    
    if not blocks:
        raise ValueError("No se encontraron bloques numéricos válidos en el archivo")
    
    # Intentar extraer datos de cada bloque y usar el mejor
    best_df = pd.DataFrame(columns=["x", "y"])
    best_count = 0
    
    for block in blocks:
        df_block = _xy_from_block(block, detector)
        if len(df_block) > best_count:
            best_df = df_block
            best_count = len(df_block)
    
    if best_df.empty:
        raise ValueError("No se pudieron extraer datos numéricos válidos")
    
    # Aplicar limpieza robusta con el nivel de filtrado especificado
    df_clean = _robust_clean_simple(best_df, detector, filter_level, **filter_params)
    
    if df_clean.empty:
        raise ValueError("No quedaron datos válidos después de la limpieza")
    
    return df_clean

