# setup.ps1 - Script de configuración para ejecutar el bot de LinkedIn en Windows
# Autor: ChatGPT
# -------------------------------------------------------------------------
# 1. Detecta la versión de Chrome instalada y descarga ChromeDriver.
# 2. Configura Python con pyenv-win y crea un entorno virtual.
# 3. Instala las dependencias del proyecto (requirements.txt).
# 4. Verifica la instalación de Selenium en PowerShell (opcional).
# -------------------------------------------------------------------------

# Obtener automáticamente la versión actual de Chrome desde el Registro
$chromeRegPath = "HKCU:\Software\Google\Chrome\BLBeacon"
if (!(Test-Path $chromeRegPath)) {
    Write-Host "[ERROR] Google Chrome no está instalado o el registro no contiene información." -ForegroundColor Red
    exit 1
}

$version = (Get-ItemProperty -Path $chromeRegPath).version
Write-Host "[+] Versión detectada de Chrome: $version" -ForegroundColor Cyan

# Definir URLs y rutas
$driverZipUrl = "https://storage.googleapis.com/chrome-for-testing-public/$version/win64/chromedriver-win64.zip"
$zipPath = "./chromedriver.zip"
$extractPath = "./chromedriver-win64"
$driverExePath = "./chromedriver.exe"

# Descargar ChromeDriver correspondiente
Write-Host "[+] Descargando ChromeDriver versión $version..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $driverZipUrl -OutFile $zipPath -ErrorAction Stop
    Write-Host "[OK] Descarga completa." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] No se pudo descargar ChromeDriver: $_" -ForegroundColor Red
    exit 1
}

# Descomprimir el archivo descargado
Write-Host "[+] Descomprimiendo ChromeDriver..." -ForegroundColor Cyan
Expand-Archive -Path $zipPath -DestinationPath "." -Force

# Mover ejecutable y limpiar archivos temporales
Write-Host "[+] Moviendo ChromeDriver y eliminando archivos temporales..." -ForegroundColor Cyan
Move-Item "$extractPath/chromedriver.exe" $driverExePath -Force
Remove-Item $extractPath, $zipPath -Force -Recurse

Write-Host "[OK] ChromeDriver versión $version instalado exitosamente." -ForegroundColor Green

Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://pyenv-win.github.io/pyenv-win/install.ps1')
Write-Host "[OK] pyenv instalado"

# ----------------------------------------------
# Configuración de Python con pyenv
# ----------------------------------------------

# Ejecutar setup_pyenv.ps1
if (Test-Path ".\setup_pyenv.ps1") {
    Write-Host "[+] Ejecutando setup_pyenv.ps1 para configurar Python..." -ForegroundColor Cyan
    & .\setup_pyenv.ps1
}
else {
    Write-Host "[ERROR] No se encontró setup_pyenv.ps1. Asegúrate de que esté en la carpeta del proyecto." -ForegroundColor Red
    exit 1
}

# ----------------------------------------------
# Crear y activar el entorno virtual (venv)
# ----------------------------------------------

$venvPath = ".\venv"

if (!(Test-Path $venvPath)) {
    Write-Host "[+] Creando entorno virtual en $venvPath..." -ForegroundColor Cyan
    python -m venv $venvPath
}

Write-Host "[+] Activando entorno virtual..." -ForegroundColor Cyan
. .\venv\Scripts\activate

# ----------------------------------------------
# Instalar dependencias
# ----------------------------------------------

if (Test-Path "requirements.txt") {
    Write-Host "[+] Instalando dependencias desde requirements.txt..." -ForegroundColor Cyan
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "[OK] Dependencias instaladas correctamente." -ForegroundColor Green
}
else {
    Write-Host "[AVISO] No se encontró 'requirements.txt'. Saltando instalación de dependencias." -ForegroundColor Yellow
}

# ----------------------------------------------
# Instalar Selenium para PowerShell (opcional)
# ----------------------------------------------
If(-not(Get-InstalledModule Selenium -ErrorAction SilentlyContinue)){
    Write-Host "[+] Instalando módulo Selenium para PowerShell..." -ForegroundColor Cyan
    Install-Module Selenium -Confirm:$False -Force -Scope CurrentUser
    Write-Host "[OK] Módulo Selenium instalado correctamente." -ForegroundColor Green
}

Write-Host "`n🚀 Configuración completada con éxito. Ahora puedes ejecutar tu script.`n" -ForegroundColor Green
