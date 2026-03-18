#!/usr/bin/env python3
"""
Qwen3-TTS Pipeline Completo
============================
Script que ejecuta todo el pipeline de Qwen3-TTS:
- Custom Voice (1.7B)
- Voice Design (1.7B)
- Voice Cloning (1.7B Base)
- Modelo Ligero (0.6B)

Diseñado para ejecutarse en una GPU de Google Colab.
"""

import os
import sys
import gc
import time
import subprocess

# ============================================================
# PASO 1: Instalación de dependencias
# ============================================================
print("=" * 60)
print("📦 PASO 1: Instalando dependencias...")
print("=" * 60)

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "qwen-tts", "soundfile"],
    check=True
)

# Intentar instalar flash-attn (puede fallar, no es crítico)
print("\n🔧 Intentando instalar flash-attn (opcional)...")
flash_attn_available = False
try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "flash-attn", "--no-build-isolation"],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode == 0:
        flash_attn_available = True
        print("✅ flash-attn instalado correctamente.")
    else:
        print("⚠️ flash-attn no se pudo instalar. Continuando sin él.")
except Exception as e:
    print(f"⚠️ flash-attn no disponible: {e}. Continuando sin él.")

print("\n✅ Dependencias instaladas.")

# ============================================================
# PASO 1b: Configuración del dispositivo
# ============================================================
import torch
import soundfile as sf

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"\n🖥️  Usando dispositivo: {device}")

if device == "cuda":
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 VRAM total: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
else:
    print("⚠️ Advertencia: Ejecutando en CPU. La generación será MUY lenta.")

dtype = torch.bfloat16 if device == "cuda" else torch.float32

# Determinar attn_implementation
attn_impl = None
if device == "cuda" and flash_attn_available:
    attn_impl = "flash_attention_2"
    print("⚡ Usando Flash Attention 2")
else:
    print("ℹ️  Usando atención estándar (sin flash-attn)")


def load_model(model_name):
    """Carga un modelo Qwen3-TTS con manejo de errores para flash_attention."""
    from qwen_tts import Qwen3TTSModel
    
    global attn_impl
    
    print(f"\n📥 Cargando {model_name}...")
    start = time.time()
    
    try:
        model = Qwen3TTSModel.from_pretrained(
            model_name,
            device_map="auto",
            dtype=dtype,
            attn_implementation=attn_impl,
        )
    except Exception as e:
        if "flash" in str(e).lower():
            print(f"⚠️ Error con flash_attention_2, reintentando sin él: {e}")
            attn_impl = None  # Desactivar para futuros loads
            model = Qwen3TTSModel.from_pretrained(
                model_name,
                device_map="auto",
                dtype=dtype,
            )
        else:
            raise
    
    elapsed = time.time() - start
    print(f"✅ Modelo cargado en {elapsed:.1f}s")
    return model


def cleanup_model(model_var_name, model_obj):
    """Limpia un modelo de la GPU."""
    print(f"\n🧹 Limpiando {model_var_name} de la GPU...")
    del model_obj
    gc.collect()
    if device == "cuda":
        torch.cuda.empty_cache()
    print("✅ Memoria GPU liberada.")


def save_and_report(wavs, sr, output_path):
    """Guarda audio y reporta."""
    sf.write(output_path, wavs[0], sr)
    file_size = os.path.getsize(output_path) / 1024
    duration = len(wavs[0]) / sr
    print(f"💾 Guardado: {output_path} ({file_size:.1f} KB, {duration:.1f}s)")


# ============================================================
# PASO 2: Generación de Voz Personalizada (Custom Voice 1.7B)
# ============================================================
print("\n" + "=" * 60)
print("🎤 PASO 2: Voz Personalizada (Custom Voice 1.7B)")
print("=" * 60)

custom_voice_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice")

text_input = "¡Hola! Esta es una demostración de Qwen3-TTS. Puedo hablar con emociones claras."
speaker_name = "Sohee"
instruction = "Feliz y enérgica"

print(f"\n🔊 Generando audio con speaker '{speaker_name}'...")
start = time.time()
wavs, sr = custom_voice_model.generate_custom_voice(
    text=text_input,
    language="Auto",
    speaker=speaker_name,
    instruct=instruction
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_custom_voice_sohee.wav")

cleanup_model("custom_voice_model", custom_voice_model)


# ============================================================
# PASO 3: Diseño de Voz (Voice Design 1.7B)
# ============================================================
print("\n" + "=" * 60)
print("🎨 PASO 3: Diseño de Voz (Voice Design 1.7B)")
print("=" * 60)

voice_design_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")

text_to_speak = "No puedo creer que finalmente llegamos a la cima de la montaña. ¡La vista es increíble!"

# --- Voz 1: Hombre grave ---
voice_desc_male = """gender: Male
pitch: Deep and resonant with subtle downward inflections suggesting gravity
speed: Deliberately slow with extended pauses between sentences
volume: Moderate to soft, creating an intimate atmosphere
age: Middle-aged to older adult
clarity: Crystal clear enunciation with careful articulation
fluency: Smooth and controlled with intentional dramatic pauses
accent: Standard American English
texture: Rich and velvety with a slightly smoky quality
emotion: Contemplative and intriguing
tone: Mysterious, philosophical, and atmospheric
personality: Introspective, wise, and captivating"""

print("\n🔊 Diseñando voz masculina grave...")
start = time.time()
wavs, sr = voice_design_model.generate_voice_design(
    text=text_to_speak, language="Spanish", instruct=voice_desc_male
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_voice_design_male.wav")

# --- Voz 2: Mujer suave ---
voice_desc_female = """gender: Female
pitch: Medium-low female pitch with gentle, soothing fluctuations
speed: Very slow and measured, allowing time for mental processing
volume: Soft and calming, never raising above comfortable levels
age: Adult (30s-40s)
clarity: Exceptionally clear with soft consonants
fluency: Perfectly fluid with mindful breathing pauses
accent: Neutral North American with slight California influence
texture: Warm and breathy, incredibly smooth
emotion: Peaceful and nurturing
tone: Gentle, encouraging, and meditative
personality: Compassionate, patient, and serene"""

print("\n🔊 Diseñando voz femenina suave...")
start = time.time()
wavs, sr = voice_design_model.generate_voice_design(
    text=text_to_speak, language="Spanish", instruct=voice_desc_female
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_voice_design_female.wav")

# --- Voz 3: Niño ---
voice_desc_child = """gender: Male
pitch: High child's voice with wide pitch variations for storytelling
speed: Variable - rushing through exciting parts, slowing for details
volume: Moderate with sudden louder bursts during exciting moments
age: Child (8-10 years old)
clarity: Generally clear but with occasional word stumbles
fluency: Enthusiastic flow with natural childlike interruptions
accent: American English (General American)
texture: Bright and youthful with slight breathiness
emotion: Wonder and excitement mixed with nervousness
tone: Animated, imaginative, and earnest
personality: Innocent, creative, and eager to share"""

print("\n🔊 Diseñando voz de niño...")
start = time.time()
wavs, sr = voice_design_model.generate_voice_design(
    text=text_to_speak, language="Spanish", instruct=voice_desc_child
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_voice_design_child.wav")

cleanup_model("voice_design_model", voice_design_model)


# ============================================================
# PASO 4: Clonación de Voz (Voice Clone - Base 1.7B)
# ============================================================
print("\n" + "=" * 60)
print("🧬 PASO 4: Clonación de Voz (Base 1.7B)")
print("=" * 60)

base_model = load_model("Qwen/Qwen3-TTS-12Hz-1.7B-Base")

ref_audio_path = "https://drive.google.com/uc?export=download&id=1dYl1634xT4UBAclsNboRMCbq-7EWTOj_"
ref_audio_text = "Hola, esta es una prueba de mi voz... el objetivo es ver si este modelo puede realmente clonar mi voz como espero que lo haga, y  suene ¡Al menos! muy similar a mi"

print("\n🔊 Creando prompt de clonación desde audio de referencia...")
start = time.time()
voice_clone_prompt = base_model.create_voice_clone_prompt(
    ref_audio=ref_audio_path,
    ref_text=ref_audio_text
)
elapsed = time.time() - start
print(f"⏱️  Prompt creado en {elapsed:.1f}s")

# --- Clon en Español ---
target_text_es = "Esto es lo que sucede cuando clonas una voz. El parecido es bastante asombroso, ¿no?"
print("\n🔊 Generando voz clonada (Español)...")
start = time.time()
wavs, sr = base_model.generate_voice_clone(
    text=target_text_es, language="Spanish", voice_clone_prompt=voice_clone_prompt
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_cloned_spanish.wav")

# --- Clon en Inglés ---
target_text_en = "This is another example of voice cloning. The resemblance is quite amazing, isn't it?"
print("\n🔊 Generando voz clonada (Inglés)...")
start = time.time()
wavs, sr = base_model.generate_voice_clone(
    text=target_text_en, language="English", voice_clone_prompt=voice_clone_prompt
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_cloned_english.wav")

cleanup_model("base_model", base_model)


# ============================================================
# PASO 5: Modelo Ligero (0.6B)
# ============================================================
print("\n" + "=" * 60)
print("🪶 PASO 5: Modelo Ligero (0.6B Custom Voice)")
print("=" * 60)

model_06b = load_model("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")

print("\n🔊 Generando audio con modelo 0.6B...")
start = time.time()
wavs, sr = model_06b.generate_custom_voice(
    text="¡Hola! Soy la versión 0.6B, soy más rápida y ligera.",
    language="Spanish",
    speaker="Ryan"
)
elapsed = time.time() - start
print(f"⏱️  Generación completada en {elapsed:.1f}s")
save_and_report(wavs, sr, "output_06b_ryan.wav")

cleanup_model("model_06b", model_06b)


# ============================================================
# RESUMEN FINAL
# ============================================================
print("\n" + "=" * 60)
print("🎉 ¡PIPELINE COMPLETADO!")
print("=" * 60)

output_files = [f for f in os.listdir(".") if f.startswith("output_") and f.endswith(".wav")]
print(f"\n📁 Archivos generados ({len(output_files)}):")
for f in sorted(output_files):
    size = os.path.getsize(f) / 1024
    print(f"   📄 {f} ({size:.1f} KB)")

print("\n✅ Todos los pasos completados exitosamente.")
