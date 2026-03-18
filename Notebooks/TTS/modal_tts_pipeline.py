import modal
import os

# Configuración de la imagen de Modal
image = (
    modal.Image.debian_slim()
    .apt_install("git", "wget")
    .pip_install(
        "qwen-tts",
        "soundfile",
        "torch",
        "transformers",
        "accelerate"
    )
)

app = modal.App("qwen3-tts-pipeline")

@app.function(image=image, gpu="T4", timeout=600)
def generate_tts():
    from qwen_tts import Qwen3TTSModel
    import torch
    import soundfile as sf
    import time
    
    # 1. Cargar Modelo
    print("📥 Cargando Qwen3-TTS-12Hz-1.7B-CustomVoice...")
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        device_map="auto",
        dtype=torch.bfloat16
    )
    
    # 2. Generación
    text = "¡Hola! Esta es una demostración de Qwen3-TTS ejecutada en Modal desde la terminal local."
    print(f"🔊 Generando audio: {text}")
    
    wavs, sr = model.generate_custom_voice(
        text=text,
        language="Spanish",
        speaker="Sohee",
        instruct="Feliz y profesional"
    )
    
    # 3. Guardar y retornar bytes
    output_path = "output_modal_sohee.wav"
    sf.write(output_path, wavs[0], sr)
    
    with open(output_path, "rb") as f:
        return f.read()

@app.local_entrypoint()
def main():
    print("🚀 Iniciando pipeline en Modal (GPU T4)...")
    audio_bytes = generate_tts.remote()
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    save_path = os.path.join(output_dir, "output_modal_sohee.wav")
    with open(save_path, "wb") as f:
        f.write(audio_bytes)
        
    print(f"✅ ¡Éxito! El audio se ha guardado en: {save_path}")
