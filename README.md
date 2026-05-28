# Caso de Estudio POO — Sistema de Reservas de Laboratorio

**Asignatura:** Programación Orientada a Objetos — UNEMI, Periodo Abril-Junio 2026
**Stack:** Python 3.12 · Flask 3.0.2 · MySQL 8.x · mysqlclient 2.2.4 · python-dotenv

---

## Documentación

| # | Archivo | Contenido |
|---|---------|-----------|
| 1 | [01-caso-estudio-poo-enunciado-uml.md](01-caso-estudio-poo-enunciado-uml.md) | Enunciado, análisis, UML (clases y secuencia) |
| 2 | [02-modelado-clases-vs-tablas-fisicas.md](02-modelado-clases-vs-tablas-fisicas.md) | Mapeo OO → MySQL, DDL completo, DML de prueba |
| 3 | [03-laboratorio-implementacion-flask-mysql.md](03-laboratorio-implementacion-flask-mysql.md) | Guía paso a paso de implementación en Python |

---

## Requisitos Previos

| Herramienta    | Verificación                                      |
|----------------|---------------------------------------------------|
| Python 3.12    | `python3.12 --version` (Windows: `py --version`)   |
| pip            | `python3.12 -m pip --version` (Windows: `py -m pip --version`) |
| MySQL 8.x      | `mysql --version`                                 |
| Git Bash / Bash| Terminal recomendada                              |

---

## Levantar el Proyecto

### 1. Clonar y entrar al directorio

```bash
git clone <url-del-repositorio>
cd Caso-de-Estudio-POO-con-Flask-y-MySQL
```

### 2. Crear y activar el entorno virtual

```bash
# Crear con el mismo Python que se usará para ejecutar la app
python3.12 -m venv .venv
```

> En Windows, si `python3.12` no está disponible, usa:
>
> ```bash
> py -3.12 -m venv .venv
> ```
>
> En Linux/macOS, si `python3.12` no está disponible, usa:
>
> ```bash
> python3 -m venv .venv
> ```

```bash
# Activar en Linux / macOS
source .venv/bin/activate
```

```bash
# Activar en Git Bash sobre Windows
source .venv/Scripts/activate
```

```powershell
# Activar en Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```cmd
:: Activar en Windows CMD
.\.venv\Scripts\activate.bat
```

> Si el servicio falla con `ModuleNotFoundError: No module named 'flask'`, puede ser porque el entorno virtual quedó inconsistente. En ese caso elimina `.venv` y vuelve a crearlo con:
>
> ```bash
> rm -rf .venv
> python3.12 -m venv .venv
> source .venv/bin/activate
> ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia la plantilla y actualiza los valores locales:

```bash
cp .env.example .env
```

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=local_reservas_db
DB_USER=root
DB_PASSWORD=tu_password
```

> Si usas Windows y prefieres copiar con CMD:
>
> ```cmd
> copy .env.example .env
> ```

### 5. Preparar la base de datos

```bash
# Opción A: cargar el schema desde terminal
mysql -u root -p < schema.sql

# Opción B (Recomendada): copiar el DDL desde 02-modelado-clases-vs-tablas-fisicas.md
# y ejecutarlo en Workbench, DBeaver o HeidiSQL
```

Luego inserta datos de prueba (ver sección DML en [02-modelado-clases-vs-tablas-fisicas.md](02-modelado-clases-vs-tablas-fisicas.md)).

### 6. Ejecutar la API

```bash
python run.py
```

La API queda disponible en `http://localhost:5000`.

### 7. Verificar

```bash
# Listar reservas
curl http://localhost:5000/api/v1/reservas

# Crear una reserva
curl -X POST http://localhost:5000/api/v1/reservas \
  -H "Content-Type: application/json" \
  -d '{"laboratorio_id": 1, "docente_id": 1, "curso_codigo": "INF-202", "fecha_reserva": "2026-06-01", "hora_inicio": "08:00", "hora_fin": "10:00"}'
```

---

## Estructura del Proyecto

```
.
├── app/
│   ├── domain/          # Entidades y repositorio abstracto
│   ├── application/     # Servicios (lógica de negocio)
│   ├── infrastructure/  # DAO, ConnectionPool, MySQLRepository
│   └── api/             # Controladores Flask (blueprints)
├── run.py               # Punto de entrada
├── schema.sql           # DDL de la base de datos
├── requirements.txt
├── .env                 # Variables de entorno (no incluido en git)
└── .env.example         # Plantilla de variables de entorno
```
