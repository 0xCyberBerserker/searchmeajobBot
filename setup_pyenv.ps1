# setup_pyenv.ps1
# -------------------------------------------------------
# OBJETIVO:
# 1) Asegurarnos de que pyenv-win está disponible.
# 2) Instalar la versión de Python deseada si no existe.
# 3) Asignar esa versión localmente a la carpeta.
# 4) Crear un entorno virtual con "python -m venv" (si no existe).
# 5) (Opcional) Activar el entorno virtual automáticamente.
# -------------------------------------------------------

# VARIABLES PERSONALIZABLES
# Ajusta la versión de Python y el nombre de tu carpeta venv:
$pythonVersion = "3.10.0"
$venvFolder    = "venv"

Write-Host "`n=== Iniciando setup_pyenv.ps1 ===`n"

# 1. Verificar si pyenv está en el PATH
if (!(Get-Command pyenv -ErrorAction SilentlyContinue)) {
    Write-Error "pyenv no está instalado o no está en el PATH. Instala pyenv-win antes de continuar."
    exit 1
}

# 2. Comprobar si la versión deseada de Python está instalada con pyenv
Write-Host "Verificando si Python $pythonVersion está instalado con pyenv-win..."
$installedVersions = pyenv versions --bare
if ($installedVersions -notcontains $pythonVersion) {
    Write-Host "Instalando Python $pythonVersion con pyenv..."
    pyenv install $pythonVersion
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Ocurrió un error al instalar Python $pythonVersion."
        exit 1
    }
}
else {
    Write-Host "Python $pythonVersion ya está instalado."
}

# 3. Configurar la versión local en la carpeta actual (genera .python-version)
Write-Host "`nEstableciendo Python $pythonVersion como local para esta carpeta..."
pyenv local $pythonVersion
if ($LASTEXITCODE -ne 0) {
    Write-Error "Ocurrió un error al ejecutar 'pyenv local $pythonVersion'."
    exit 1
}
Write-Host "Se creó/actualizó el archivo .python-version con $pythonVersion.`n"

# 4. Crear un entorno virtual con la versión asignada (si no existe)
Write-Host "Creando entorno virtual '$venvFolder' (si no existe)..."
if (!(Test-Path $venvFolder)) {
    # Asegurarnos de usar el 'python' recién asignado a la carpeta:
    pyenv rehash
    Write-Host "Ejecutando: python -m venv $venvFolder"
    python -m venv $venvFolder
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Ocurrió un error al crear el entorno virtual."
        exit 1
    }
    Write-Host "Entorno virtual '$venvFolder' creado."
}
else {
    Write-Host "El entorno virtual '$venvFolder' ya existe, no se creará de nuevo."
}

# 5. (Opcional) Activar automáticamente el venv
# Si prefieres que el script termine ya con el venv activo, descomenta:
#Write-Host "`nActivando entorno virtual '$venvFolder'..."
#. .\venv\Scripts\activate

Write-Host "`n============================================="
Write-Host "¡Configuración finalizada con éxito!"
Write-Host " - Python $pythonVersion está disponible localmente en esta carpeta."
Write-Host " - Se creó (o confirmó) el entorno virtual '$venvFolder'."
Write-Host " - Se generó el archivo '.python-version' para pyenv."
Write-Host "=============================================`n"
Write-Host "Para usar el entorno virtual, ejecuta:"
Write-Host " .\\$venvFolder\\Scripts\\activate"
Write-Host "`nLuego, 'python --version' te mostrará Python $pythonVersion (venv)."
Write-Host "=============================================`n"
