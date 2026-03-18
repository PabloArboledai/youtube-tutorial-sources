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
    Write-Host "Ventana encontrada: $($proc.MainWindowTitle)"
    [Win32]::ShowWindow($proc.MainWindowHandle, 9) # SW_RESTORE
    [Win32]::SetForegroundWindow($proc.MainWindowHandle)
    Start-Sleep -Milliseconds 1000
    
    Add-Type -AssemblyName System.Windows.Forms
    
    # Ejecutar todas las celdas (Ctrl + F9)
    [System.Windows.Forms.SendKeys]::SendWait("^{F9}")
    Write-Host "Comando Run All enviado. Esperando 40s para estabilizacion del tunel..."
    Start-Sleep -Seconds 40
    
    # Salir de modo edición, seleccionar todo y copiar
    [System.Windows.Forms.SendKeys]::SendWait("{ESC}")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 1000
    [System.Windows.Forms.SendKeys]::SendWait("^c")
    Start-Sleep -Milliseconds 1000
    
    # Leer el portapapeles y buscar el link de cloudflare
    $clip = Get-Clipboard -Raw
    $match = [regex]::Match($clip, 'https://[a-zA-Z0-9-]+\.trycloudflare\.com')
    if ($match.Success) {
        Write-Host "[HOSTNAME_SUCCESS]: $($match.Value)"
    } else {
        Write-Host "[NOT_FOUND]: Hostname no encontrado en el texto."
    }
} else {
    Write-Host "[ERROR]: No se encontro la ventana."
}
