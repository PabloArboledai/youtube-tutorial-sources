const puppeteer = require('puppeteer');

async function launch() {
    const userDataDir = 'C:/FastProfile';
    console.log('[ColabBot] Iniciando con perfil de usuario (Headless)...');
    
    const browser = await puppeteer.launch({
        headless: "new",
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        userDataDir: userDataDir,
        args: [
            '--profile-directory=Default',
            '--no-sandbox',
            '--disable-setuid-sandbox'
        ]
    });

    const page = await browser.newPage();
    try {
        // Usar la URL que obtuvimos antes o una generica de Colab
        console.log('[ColabBot] Navegando a Google Colab (Notebook Exacto)...');
        await page.goto('https://colab.research.google.com/drive/1YoznxnZiBOQEhkrcFJwsbJ7fUGIwHKv3', { waitUntil: 'networkidle2', timeout: 60000 });
        
        console.log('[ColabBot] Intentando ejecutar celdas (Ctrl+F9)...');
        // Este comando asume que el notebook ya esta abierto o es el ultimo usado
        await page.keyboard.down('Control');
        await page.keyboard.press('F9');
        await page.keyboard.up('Control');
        
        console.log('[ColabBot] Esperando 45 segundos para que el tunel se estabilice...');
        await new Promise(r => setTimeout(r, 45000));
        
        const bodyText = await page.evaluate(() => document.body.innerText);
        const match = bodyText.match(/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/);
        
        if (match) {
            console.log(`[HOSTNAME_SUCCESS]: ${match[0]}`);
        } else {
            console.log('[NOT_FOUND]: El hostname no aparecio en el texto de la pagina.');
            // Capturar pantalla para debug interno (si fuera posible)
        }
    } catch (e) {
        console.error(`[ERROR]: ${e.message}`);
    } finally {
        await browser.close();
        console.log('[ColabBot] Navegador cerrado.');
    }
}

launch();
