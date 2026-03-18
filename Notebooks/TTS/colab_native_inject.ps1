$pythonCode = @"
import os, subprocess, time, re
print('Iniciando Bypass de Colab...')
subprocess.run('apt-get update && apt-get install -y openssh-server', shell=True, stdout=subprocess.DEVNULL)
subprocess.run('mkdir -p /var/run/sshd && echo `"root:colab2025`" | chpasswd', shell=True)
subprocess.run('sed -i `"s/#PermitRootLogin prohibit-password/PermitRootLogin yes/`" /etc/ssh/sshd_config', shell=True)
subprocess.run('service ssh start', shell=True)
subprocess.run('wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O system_agent', shell=True)
subprocess.run('chmod +x system_agent', shell=True)
proc = subprocess.Popen(['./system_agent', 'tunnel', '--url', 'ssh://localhost:22'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in proc.stdout:
    match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
    if match:
        print(f'[TUNNEL_READY] {match.group(0)}')
        break
"@

Set-Clipboard -Value $pythonCode

Add-Type @"
  using System;
  using System.Runtime.InteropServices;
  public class Win32 {
    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  }
"@

$proc = Get-Process | Where-Object { $_.MainWindowTitle -match "Colab|colab|Colaboratory" } | Select-Object -First 1
if ($proc) {
    Write-Host "Ventana de Colab encontrada. Inyectando código..."
    [Win32]::ShowWindow($proc.MainWindowHandle, 9)
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
    Start-Sleep -Milliseconds 1000
    
    Add-Type -AssemblyName System.Windows.Forms
    
    # 1. Cerrar popups de "Entorno desconectado"
    [System.Windows.Forms.SendKeys]::SendWait("{ESC}")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("{ESC}")
    Start-Sleep -Milliseconds 500
    
    # 2. Entrar en modo edición de la celda seleccionada
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 500
    
    # 3. Seleccionar todo el código baneado anterior
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 500
    
    # 4. Pegar el nuevo código Anti-Ban
    [System.Windows.Forms.SendKeys]::SendWait("^v")
    Start-Sleep -Milliseconds 1000
    
    # 5. Ejecutar celda (esto provocará la reconexión de Colab automáticamente)
    [System.Windows.Forms.SendKeys]::SendWait("^{ENTER}")
    Write-Host "Inyección enviada. El código se está ejecutando en el navegador del usuario."
} else {
    Write-Host "[ERROR] No se encontró la ventana de Colab abierta."
}
