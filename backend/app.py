from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import pandas as pd
import numpy as np
import openai
import io
import os
import json
from dotenv import load_dotenv
from rosetta_pipeline import process_tab_file

# Cargar variables de entorno
load_dotenv()
# También intentar cargar desde config.env si existe
load_dotenv('config.env')

app = FastAPI(title="Rosetta Spectrum Analyzer")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringe a tu dominio frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT_ID = os.getenv("PROMPT_ID", "pmpt_691eb6347b388194bab33de01809fa1f0fb2b90b7c2f4bd5")
FT_MODEL = os.getenv("FT_MODEL_NAME", "ft:gpt-4o-mini:astroquimico-2025")

if not OPENAI_API_KEY:
    print("[WARNING] OPENAI_API_KEY no está configurada. Las conclusiones no funcionarán.")
else:
    print("[INFO] OpenAI API Key configurada correctamente")
    print(f"[INFO] Prompt ID: {PROMPT_ID}")


@app.get("/")
async def root():
    return {
        "message": "Rosetta Spectrum Analyzer API",
        "status": "running",
        "openai_configured": bool(OPENAI_API_KEY)
    }


@app.post("/process")
async def process(
    file: UploadFile = File(...),
    filter_level: str = Form("high"),
    head_drop: Optional[str] = Form(None),
    mad_multiplier_rtof: Optional[str] = Form(None),
    cps_threshold_rtof: Optional[str] = Form(None),
    mad_multiplier_dfms: Optional[str] = Form(None),
    cps_threshold_dfms: Optional[str] = Form(None)
):
    """
    Procesa un archivo .tab y genera un espectro resumido y una conclusión.
    
    Args:
        file: Archivo .tab a procesar
        filter_level: Nivel de filtrado ("high" para alto grado, "low" para bajo grado)
        head_drop: (Opcional) Número de filas iniciales a descartar
        mad_multiplier_rtof: (Opcional) Multiplicador MAD para RTOF
        cps_threshold_rtof: (Opcional) Umbral absoluto de cps para RTOF
        mad_multiplier_dfms: (Opcional) Multiplicador MAD para DFMS
        cps_threshold_dfms: (Opcional) Umbral absoluto de cps para DFMS
    """
    try:
        # Validar que sea un archivo .tab
        if not file.filename.endswith('.tab'):
            return JSONResponse(
                status_code=400,
                content={"error": "El archivo debe ser .tab"}
            )

        # Leer archivo en memoria
        contents = await file.read()
        tab_stream = io.BytesIO(contents)
        
        # Leer metadata del detector ANTES de procesar (para no perder el stream)
        from rosetta_pipeline import read_label_header_from_stream
        meta = read_label_header_from_stream(tab_stream)
        detector_id = meta.get('DETECTOR_ID', '').upper()
        detector = "RTOF" if "RTOF" in detector_id else "DFMS" if "DFMS" in detector_id else "RTOF"
        
        # Resetear el stream para procesar
        tab_stream.seek(0)

        # Validar filter_level
        if filter_level not in ["high", "low"]:
            filter_level = "high"  # Default a alto grado si es inválido
        
        print(f"[INFO] Nivel de filtrado: {filter_level}")
        print(f"[DEBUG] Detector detectado: {detector}")
        
        # Preparar parámetros de filtrado (aplican tanto para alto como bajo grado)
        filter_params = {}
        
        # Head drop
        try:
            if head_drop and head_drop != "None" and str(head_drop).strip():
                filter_params["head_drop"] = int(head_drop)
            else:
                filter_params["head_drop"] = 10 if detector == "RTOF" else 5
            print(f"[INFO] Head drop: {filter_params['head_drop']}")
        except (ValueError, TypeError) as e:
            filter_params["head_drop"] = 10 if detector == "RTOF" else 5
            print(f"[WARNING] Error parseando head_drop: {e}, usando default: {filter_params['head_drop']}")
        
        # MAD multiplier RTOF
        try:
            if mad_multiplier_rtof and mad_multiplier_rtof != "None" and str(mad_multiplier_rtof).strip():
                filter_params["mad_multiplier_rtof"] = float(mad_multiplier_rtof)
            else:
                # Default según el nivel
                filter_params["mad_multiplier_rtof"] = 10.0 if filter_level == "high" else 1000.0
            print(f"[INFO] MAD multiplier RTOF: {filter_params['mad_multiplier_rtof']}")
        except (ValueError, TypeError) as e:
            filter_params["mad_multiplier_rtof"] = 10.0 if filter_level == "high" else 1000.0
            print(f"[WARNING] Error parseando mad_multiplier_rtof: {e}, usando default: {filter_params['mad_multiplier_rtof']}")
        
        # CPS threshold RTOF
        try:
            if cps_threshold_rtof and cps_threshold_rtof != "None" and str(cps_threshold_rtof).strip():
                filter_params["cps_threshold_rtof"] = float(cps_threshold_rtof)
            else:
                # Default según el nivel
                filter_params["cps_threshold_rtof"] = 5.0 if filter_level == "high" else 500.0
            print(f"[INFO] CPS threshold RTOF: {filter_params['cps_threshold_rtof']}")
        except (ValueError, TypeError) as e:
            filter_params["cps_threshold_rtof"] = 5.0 if filter_level == "high" else 500.0
            print(f"[WARNING] Error parseando cps_threshold_rtof: {e}, usando default: {filter_params['cps_threshold_rtof']}")
        
        # MAD multiplier DFMS
        try:
            if mad_multiplier_dfms and mad_multiplier_dfms != "None" and str(mad_multiplier_dfms).strip():
                filter_params["mad_multiplier_dfms"] = float(mad_multiplier_dfms)
            else:
                # Default según el nivel
                filter_params["mad_multiplier_dfms"] = 8.0 if filter_level == "high" else 800.0
            print(f"[INFO] MAD multiplier DFMS: {filter_params['mad_multiplier_dfms']}")
        except (ValueError, TypeError) as e:
            filter_params["mad_multiplier_dfms"] = 8.0 if filter_level == "high" else 800.0
            print(f"[WARNING] Error parseando mad_multiplier_dfms: {e}, usando default: {filter_params['mad_multiplier_dfms']}")
        
        # CPS threshold DFMS
        try:
            if cps_threshold_dfms and cps_threshold_dfms != "None" and str(cps_threshold_dfms).strip():
                filter_params["cps_threshold_dfms"] = float(cps_threshold_dfms)
            else:
                # Default según el nivel
                filter_params["cps_threshold_dfms"] = 1e4 if filter_level == "high" else 1e8
            print(f"[INFO] CPS threshold DFMS: {filter_params['cps_threshold_dfms']}")
        except (ValueError, TypeError) as e:
            filter_params["cps_threshold_dfms"] = 1e4 if filter_level == "high" else 1e8
            print(f"[WARNING] Error parseando cps_threshold_dfms: {e}, usando default: {filter_params['cps_threshold_dfms']}")
        
        print(f"[DEBUG] Parámetros de filtrado finales: {filter_params}")

        # Procesar el archivo .tab con el nivel de filtrado especificado
        df = process_tab_file(tab_stream, filter_level=filter_level, **filter_params)

        if df.empty:
            return JSONResponse(
                status_code=400,
                content={"error": "El archivo está vacío o no contiene datos válidos"}
            )

        # Resumir el espectro en 100 bins
        # IMPORTANTE: Filtrar valores negativos antes del resumen
        df_summary = df[df['cps'] >= 0].copy()
        
        if df_summary.empty:
            return JSONResponse(
                status_code=400,
                content={"error": "No quedaron datos válidos (sin valores negativos) después del filtrado"}
            )
        
        x_vals = df_summary['x'].to_numpy()
        cps_vals = df_summary['cps'].to_numpy()

        bins = np.linspace(x_vals.min(), x_vals.max(), 101)
        spectrum_summary = []

        for i in range(100):
            mask = (x_vals >= bins[i]) & (x_vals < bins[i+1])
            if mask.any():
                # Calcular promedio solo de valores no negativos en este bin
                bin_cps = cps_vals[mask]
                bin_cps_positive = bin_cps[bin_cps >= 0]
                
                if len(bin_cps_positive) > 0:
                    spectrum_summary.append({
                        "x": float(x_vals[mask].mean()),
                        "cps": float(bin_cps_positive.mean())
                    })

        # Construir input para el modelo con los datos del espectro y metadata
        # Formato: pares x:cps como en Google Colab
        spectrum_pairs = " ".join([
            f"{p['x']:.3f}:{p['cps']:.3f}"
            for p in spectrum_summary
        ])
        
        # Construir el input completo con metadata del detector y datos del espectro
        input_text = f"Detector: {detector}\nEspectro (m/z:cps): {spectrum_pairs}"
        
        print(f"[DEBUG] ========== CONSTRUYENDO INPUT PARA OPENAI ==========")
        print(f"[DEBUG] Detector: {detector}")
        print(f"[DEBUG] Número de puntos en spectrum_summary: {len(spectrum_summary)}")
        print(f"[DEBUG] Primeros 200 caracteres del input: {input_text[:200]}...")
        print(f"[DEBUG] Longitud total del input: {len(input_text)} caracteres")
        
        # Verificar si el input es demasiado largo (limitar a ~100k caracteres para evitar errores)
        MAX_INPUT_LENGTH = 100000
        if len(input_text) > MAX_INPUT_LENGTH:
            print(f"[WARNING] Input muy largo ({len(input_text)} chars), truncando a {MAX_INPUT_LENGTH}...")
            input_text = input_text[:MAX_INPUT_LENGTH]

        # Llamar al modelo fine-tuneado de OpenAI usando el prompt ID
        conclusion = ""
        if OPENAI_API_KEY:
            try:
                import requests
                
                # Enviar el prompt con el input que contiene los datos del espectro
                # El input debe ser un array de objetos (input items) según la documentación de OpenAI
                # Intentemos primero con el formato correcto: array de objetos con type y content
                
                # Formato correcto según la documentación: input debe ser array de input items
                # El input item necesita type, role y content según el error
                request_payload = {
                    "prompt": {
                        "id": PROMPT_ID,
                        "version": "4"
                    },
                    "input": [
                        {
                            "type": "message",
                            "role": "user",  # Valores permitidos: 'assistant', 'system', 'developer', 'user'
                            "content": input_text
                        }
                    ]
                }
                
                print(f"[DEBUG] ========== ENVIANDO REQUEST A OPENAI CON INPUT ==========")
                print(f"[DEBUG] Payload keys: {list(request_payload.keys())}")
                print(f"[DEBUG] Input type: {type(request_payload['input'])}")
                print(f"[DEBUG] Input length: {len(request_payload['input'])} items")
                if len(request_payload['input']) > 0:
                    print(f"[DEBUG] Input[0] type: {type(request_payload['input'][0])}")
                    print(f"[DEBUG] Input[0] keys: {list(request_payload['input'][0].keys()) if isinstance(request_payload['input'][0], dict) else 'N/A'}")
                    if isinstance(request_payload['input'][0], dict) and 'content' in request_payload['input'][0]:
                        content_preview = str(request_payload['input'][0]['content'])[:200]
                        print(f"[DEBUG] Input[0] content preview: {content_preview}...")
                        print(f"[DEBUG] Input[0] content length: {len(str(request_payload['input'][0]['content']))} caracteres")
                
                response = requests.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {OPENAI_API_KEY}"
                    },
                    json=request_payload,
                    timeout=60
                )
                
                # Log del resultado
                print(f"[DEBUG] Status code: {response.status_code}")
                if response.status_code != 200:
                    print(f"[DEBUG] Response text: {response.text[:500]}")
                else:
                    print(f"[DEBUG] ✅ Request exitoso, input enviado correctamente")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[DEBUG] ========== INICIO ANÁLISIS DE RESPUESTA ==========")
                    print(f"[DEBUG] Tipo de resultado: {type(result)}")
                    
                    # La respuesta puede ser un dict con 'output' que contiene la lista
                    # O puede ser directamente una lista
                    items_to_process = None
                    
                    if isinstance(result, dict):
                        print(f"[DEBUG] Result es un dict con keys: {list(result.keys())}")
                        # Buscar la lista de items en 'output'
                        if 'output' in result:
                            output_value = result['output']
                            print(f"[DEBUG] Encontrado 'output' en result, tipo: {type(output_value)}")
                            if isinstance(output_value, list):
                                items_to_process = output_value
                                print(f"[DEBUG] 'output' es una lista con {len(items_to_process)} elementos")
                            else:
                                print(f"[DEBUG] 'output' no es una lista, es: {type(output_value)}")
                    elif isinstance(result, list):
                        print(f"[DEBUG] Result es directamente una lista con {len(result)} elementos")
                        items_to_process = result
                    
                    # Extraer la conclusión del response (formato puede variar)
                    conclusion = None
                    
                    print(f"[DEBUG] Estado antes de procesar: conclusion={conclusion}, conclusion_type={type(conclusion)}, items_to_process={items_to_process}, items_type={type(items_to_process) if items_to_process is not None else None}")
                    if items_to_process is not None:
                        print(f"[DEBUG] items_to_process tiene {len(items_to_process) if isinstance(items_to_process, list) else 'N/A'} elementos")
                    
                    # Procesar la lista de items para extraer el texto
                    # PRIORIDAD: procesar items_to_process primero si existe
                    print(f"[DEBUG] Verificando si procesar items_to_process: isinstance={isinstance(items_to_process, list)}, len={len(items_to_process) if isinstance(items_to_process, list) else 'N/A'}")
                    if isinstance(items_to_process, list) and len(items_to_process) > 0:
                        print(f"[DEBUG] ✅ ENTRANDO AL BLOQUE DE PROCESAMIENTO")
                        print(f"[DEBUG] ✅ PROCESANDO items_to_process (lista con {len(items_to_process)} elementos)")
                        print(f"[DEBUG] Procesando lista con {len(items_to_process)} elementos")
                        for idx, item in enumerate(items_to_process):
                            print(f"[DEBUG] Procesando item {idx}: tipo={type(item)}")
                            if isinstance(item, dict):
                                print(f"[DEBUG] Item {idx} keys: {list(item.keys())}")
                                # Buscar items de tipo 'message' con 'content'
                                if item.get('type') == 'message' and 'content' in item:
                                    print(f"[DEBUG] Item {idx} es de tipo 'message' con 'content'")
                                    content = item['content']
                                    print(f"[DEBUG] Content tipo: {type(content)}")
                                    if isinstance(content, list):
                                        print(f"[DEBUG] Content es lista con {len(content)} elementos")
                                        # Buscar el texto en el contenido
                                        for content_idx, content_item in enumerate(content):
                                            print(f"[DEBUG] Procesando content_item {content_idx}: tipo={type(content_item)}")
                                            if isinstance(content_item, dict):
                                                print(f"[DEBUG] Content_item {content_idx} keys: {list(content_item.keys())}")
                                                # Buscar 'text' en el item
                                                if 'text' in content_item:
                                                    conclusion = content_item['text']
                                                    print(f"[DEBUG] ✅ TEXTO EXTRAÍDO EXITOSAMENTE de content_item[{content_idx}]['text']")
                                                    print(f"[DEBUG] Tipo de conclusion: {type(conclusion)}")
                                                    print(f"[DEBUG] Longitud del texto: {len(conclusion) if isinstance(conclusion, str) else 'N/A'}")
                                                    break
                                            elif isinstance(content_item, str):
                                                conclusion = content_item
                                                print(f"[DEBUG] ✅ TEXTO EXTRAÍDO (string directo) de content_item[{content_idx}]")
                                                break
                                        if conclusion:
                                            break
                                    elif isinstance(content, str):
                                        conclusion = content
                                        print(f"[DEBUG] ✅ TEXTO EXTRAÍDO (content es string directo)")
                                # También buscar directamente 'text' o 'output' en cualquier item
                                if conclusion is None:
                                    if 'text' in item:
                                        conclusion = item['text']
                                        print(f"[DEBUG] ✅ TEXTO EXTRAÍDO de item['text']")
                                    elif 'output' in item:
                                        # NO asignar item['output'] directamente si es una lista
                                        output_val = item['output']
                                        if isinstance(output_val, str):
                                            conclusion = output_val
                                            print(f"[DEBUG] ✅ TEXTO EXTRAÍDO de item['output'] (string)")
                                        else:
                                            print(f"[DEBUG] ⚠️ item['output'] no es string, es {type(output_val)}, ignorando")
                    
                    # Si aún no encontramos conclusion y items_to_process no era una lista,
                    # intentar buscar directamente en result (dict)
                    if conclusion is None and isinstance(result, dict):
                        print(f"[DEBUG] Buscando conclusion en result (dict) directamente")
                        # NO usar result["output"] directamente porque es una lista
                        # Ya lo procesamos arriba
                        if "text" in result:
                            text_value = result["text"]
                            if isinstance(text_value, str):
                                conclusion = text_value
                                print(f"[DEBUG] ✅ TEXTO EXTRAÍDO de result['text'] (string)")
                            elif isinstance(text_value, list):
                                # Si text es una lista, buscar el texto dentro
                                for item in text_value:
                                    if isinstance(item, dict) and "text" in item:
                                        conclusion = item["text"]
                                        print(f"[DEBUG] ✅ TEXTO EXTRAÍDO de result['text'][item]['text']")
                                        break
                        elif "response" in result:
                            response_value = result["response"]
                            if isinstance(response_value, str):
                                conclusion = response_value
                                print(f"[DEBUG] ✅ TEXTO EXTRAÍDO de result['response']")
                    
                    # Asegurarse de que conclusion sea siempre un string
                    print(f"[DEBUG] ========== RESULTADO FINAL DE EXTRACCIÓN ==========")
                    print(f"[DEBUG] conclusion antes de validación: {type(conclusion)}")
                    if conclusion is not None:
                        conclusion_preview = str(conclusion)[:200] if isinstance(conclusion, str) else str(conclusion)[:200]
                        print(f"[DEBUG] conclusion valor (primeros 200 chars): {conclusion_preview}...")
                        print(f"[DEBUG] conclusion longitud: {len(conclusion) if isinstance(conclusion, str) else 'N/A'}")
                    
                    if conclusion is None:
                        print(f"[DEBUG] ⚠️ conclusion es None - estableciendo mensaje de error")
                        conclusion = "No se pudo extraer la conclusión de la respuesta"
                    elif isinstance(conclusion, str) and len(conclusion.strip()) == 0:
                        print(f"[DEBUG] ⚠️ conclusion es string vacío - estableciendo mensaje de error")
                        conclusion = "No se pudo extraer la conclusión de la respuesta (texto vacío)"
                    elif not isinstance(conclusion, str):
                        print(f"[DEBUG] ⚠️ conclusion NO es string (es {type(conclusion)}) - convirtiendo a string")
                        print(f"[DEBUG] Valor antes de conversión: {conclusion}")
                        conclusion = str(conclusion)
                        print(f"[DEBUG] Valor después de conversión: {conclusion[:200]}...")
                    
                    print(f"[DEBUG] ✅ CONCLUSIÓN FINAL (tipo: {type(conclusion)}, longitud: {len(conclusion)})")
                    if isinstance(conclusion, str) and len(conclusion) > 0:
                        print(f"[DEBUG] Primeros 300 caracteres: {conclusion[:300]}...")
                    else:
                        print(f"[DEBUG] ⚠️ CONCLUSIÓN VACÍA O INVÁLIDA")
                    print(f"[DEBUG] ========== FIN ANÁLISIS DE RESPUESTA ==========")
                else:
                    error_msg = f"Error en API: {response.status_code} - {response.text}"
                    print(f"[ERROR] {error_msg}")
                    conclusion = error_msg
                    
            except Exception as e:
                error_msg = f"Error al generar conclusión: {str(e)}"
                print(f"[ERROR] {error_msg}")
                conclusion = error_msg
        else:
            conclusion = "OPENAI_API_KEY no configurada. Por favor, configura tu API key en el archivo .env"

        return {
            "spectrum": spectrum_summary,
            "conclusion": conclusion,
            "total_points": len(df),
            "x_range": {
                "min": float(x_vals.min()),
                "max": float(x_vals.max())
            },
            "cps_range": {
                "min": float(cps_vals.min()),
                "max": float(cps_vals.max())
            }
        }

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error al procesar el archivo: {str(e)}"}
        )

