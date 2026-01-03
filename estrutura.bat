REM ==== Criar pastas principais ====
mkdir config
mkdir src

REM ==== Config ====
type nul > config\database.json

REM ==== Backend ====
mkdir src\backend
type nul > src\backend\__init__.py
type nul > src\backend\data_loader.py
type nul > src\backend\analyzer.py

REM ==== Frontend ====
mkdir src\frontend
type nul > src\frontend\__init__.py
type nul > src\frontend\app.py
type nul > src\frontend\components.py

REM ==== Utils ====
mkdir src\utils
type nul > src\utils\security.py

REM ==== Arquivos raiz ====
type nul > main.py
type nul > requirements.txt
type nul > README.md
