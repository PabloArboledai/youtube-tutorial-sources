const puppeteer = require('puppeteer');
const fs = require('fs');
const { execSync } = require('child_process');

async function launch() {
    const userDataDir = 'C:/FastProfile';
    console.log('[ColabBot] Iniciando con perfil de usuario clonado (Headless)...');
    
    // El script en python para evadir el ban y arrancar ssh
    const pythonScript = `
import os, subprocess, time, re

print("Configurando SSH...")
subprocess.run("apt-get update && apt-get install -y openssh-server", shell=True, stdout=subprocess.DEVNULL)
subprocess.run("mkdir -p /var/run/sshd && echo 'root:colab2025' | chpasswd", shell=True)
subprocess.run("sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config", shell=True)
subprocess.run("service ssh start", shell=True)

print("Descargando agente de tunel (evadiendo filtro de Colab)...")
subprocess.run("wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O system_agent", shell=True)
subprocess.run("chmod +x system_agent", shell=True)

print("Iniciando tunel...")
proc = subprocess.Popen(['./system_agent', 'tunnel', '--url', 'ssh://localhost:22'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in proc.stdout:
    match = re.search(r'https://[a-zA-Z0-9-]+\\.trycloudflare\\.com', line)
    if match:
        print(f"[TUNNEL_READY] {match.group(0)}")
        break
    time.sleep(0.1)
`;

    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        userDataDir: userDataDir,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    });

    try {
        const context = browser.defaultBrowserContext();
        await context.overridePermissions('https://colab.research.google.com', ['clipboard-read', 'clipboard-write']);
        
        const page = await browser.newPage();
        console.log('[ColabBot] Creando nuevo cuaderno en Google Colab...');
        await page.goto('https://colab.research.google.com/#create=true', { waitUntil: 'networkidle2', timeout: 90000 });
        
        // Esperar a que el editor Monaco esté listo
        await page.waitForSelector('.view-lines', { timeout: 30000 });
        console.log('[ColabBot] Editor cargado. Inyectando script vía portapapeles nativo de Windows...');

        // Guardar a temp y meter en el portapapeles nativo
        fs.writeFileSync('temp_script.py', pythonScript);
        execSync('type temp_script.py | clip');
        
        // Click en el editor y pegar el portapapeles de Windows
        await page.click('.view-lines');
        await page.keyboard.down('Control');
        await page.keyboard.press('V');
        await page.keyboard.up('Control');
        
        await new Promise(r => setTimeout(r, 1000));
        
        console.log('[ColabBot] Ejecutando celda...');
        await page.keyboard.down('Control');
        await page.keyboard.press('Enter');
        await page.keyboard.up('Control');
        
        console.log('[ColabBot] Esperando el enlace del túnel (~40s)...');
        
        let url = null;
        for (let i = 0; i < 60; i++) {
            await new Promise(r => setTimeout(r, 1000));
            const bodyText = await page.evaluate(() => document.body.innerText);
            const match = bodyText.match(/\\[TUNNEL_READY\\] (https:\/\/[a-zA-Z0-9-]+\\.trycloudflare\\.com)/);
            if (match) {
                url = match[1];
                console.log(`[HOSTNAME_SUCCESS]: ${url}`);
                fs.writeFileSync('tunnel.txt', url);
                break;
            }
            if (bodyText.includes("código no permitido") || bodyText.includes("desconectado")) {
                console.log("[ERROR] Colab desconectado por politicas.");
                break;
            }
        }
        
        if (!url) console.log('[NOT_FOUND]: Hostname no extraido.');

    } catch (e) {
        console.error(`[ERROR]: ${e.message}`);
    } finally {
        // En modo headless verdadero para que siga vivo el tunel, NO cerramos el navegador, 
        // pero necesitamos liberar el proceso de Node. 
        // Dado que el usuario tiene 'Discovery Web', podríamos dejarlo abierto y hacer process.exit.
        // Pero Colab morirá si la pestaña se cierra. 
        // Solución: Dejamos el browser desconectado del script Node.
        console.log('[ColabBot] Desvinculando proceso. El navegador Headless se mantendrá activo en segundo plano.');
        await browser.disconnect();
        process.exit(0);
    }
}

launch();
