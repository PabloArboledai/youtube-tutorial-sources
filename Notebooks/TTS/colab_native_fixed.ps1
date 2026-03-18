$code = @"
import os, subprocess, time, re
print("Configurando SSH...")
subprocess.run("apt-get update && apt-get install -y openssh-server", shell=True, stdout=subprocess.DEVNULL)
subprocess.run("mkdir -p /var/run/sshd && echo 'root:colab2025' | chpasswd", shell=True)
subprocess.run("sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config", shell=True)
subprocess.run("service ssh start", shell=True)
print("Descargando agente de tunel...")
subprocess.run("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O system_agent", shell=True)
subprocess.run("chmod +x system_agent", shell=True)
print("Iniciando tunel...")
proc = subprocess.Popen(['./system_agent', 'tunnel', '--url', 'ssh://localhost:22'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in proc.stdout:
    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
    if match:
        print(f"\n[TUNNEL_READY] {match.group(0)}")
        break
    print(line, end='')
"@

Set-Clipboard -Value $code

Add-Type @"
  using System;
  using System.Runtime.InteropServices;
  public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  }
"@

$proc = Get-Process | Where-Object { $_.MainWindowTitle -match "Colab|colab|Colaboratory" } | Select-Object -First 1
if ($proc) {
    [Win32]::ShowWindow($proc.MainWindowHandle, 9)
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
    Start-Sleep -Milliseconds 1000
    Add-Type -AssemblyName System.Windows.Forms
    
    # Enfocar y limpiar
    [System.Windows.Forms.SendKeys]::SendWait("{ESC}")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("^a") # Seleccionar todo
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("{BACKSPACE}") # Borrar
    Start-Sleep -Milliseconds 500
    
    # Pegar y Ejecutar
    [System.Windows.Forms.SendKeys]::SendWait("^v")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("^{ENTER}")
    Write-Host "Inyeccion completada con exito."
} else {
    Write-Host "Error: Ventana no encontrada."
}
