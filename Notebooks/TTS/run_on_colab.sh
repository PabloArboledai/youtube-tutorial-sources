#!/bin/bash
# =============================================================
# Script de ejecución del pipeline Qwen3-TTS en Google Colab
# =============================================================

echo "============================================="
echo "🚀 Iniciando pipeline Qwen3-TTS en GPU Colab"
echo "============================================="
echo ""

# Verificar GPU
echo "🖥️  Verificando GPU..."
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "⚠️ nvidia-smi no disponible"
echo ""

# Crear directorio de trabajo
mkdir -p /content/tts_output
cd /content/tts_output

# Copiar el script si no está ya aquí
if [ ! -f "qwen3_tts_pipeline.py" ]; then
    echo "⚠️ qwen3_tts_pipeline.py no encontrado en /content/tts_output/"
    echo "Cópialo primero: cp /ruta/al/archivo/qwen3_tts_pipeline.py ."
    exit 1
fi

# Ejecutar el pipeline
echo "▶️  Ejecutando pipeline..."
echo ""
python3 qwen3_tts_pipeline.py

echo ""
echo "============================================="
echo "📁 Archivos generados:"
echo "============================================="
ls -lh /content/tts_output/output_*.wav 2>/dev/null || echo "No se encontraron archivos .wav"
