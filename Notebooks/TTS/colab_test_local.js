const puppeteer = require('C:\\Users\\allisoneverest09\\node-v22\\node_modules\\puppeteer');

(async () => {
  console.log('[Puppeteer] Iniciando Chrome Headless...');
  const browser = await puppeteer.launch({ 
    headless: true, 
    args: ['--no-sandbox', '--disable-setuid-sandbox'] 
  });
  const page = await browser.newPage();
  
  // Usar el notebook de setup del usuario
  const notebookUrl = 'https://colab.research.google.com/drive/1d9I8r8f0o3O-Y4W6u7V7f5v6x5w5p5z5'; // Placeholder, usaremos el del proyecto
  
  console.log(`[Puppeteer] Navegando a Colab...`);
  await page.goto('https://colab.research.google.com/', { waitUntil: 'networkidle2' });
  
  // Aquí faltaría el login o usar el profile del usuario. 
  // Para esta prueba, solo verificamos si carga.
  const title = await page.title();
  console.log(`[Puppeteer] Pagina cargada: ${title}`);
  
  await browser.close();
  console.log('[Puppeteer] Proceso finalizado.');
})();
