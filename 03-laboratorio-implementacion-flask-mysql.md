# Laboratorio: Implementación de API REST con Flask y MySQL (sin ORM)

**Asignatura:** Programación Orientada a Objetos
**Formato:** Guía de laboratorio paso a paso
**Referencia UML:** [01-caso-estudio-poo-enunciado-uml.md](01-caso-estudio-poo-enunciado-uml.md)
**Referencia Base de Datos:** [02-modelado-clases-vs-tablas-fisicas.md](02-modelado-clases-vs-tablas-fisicas.md)

---

## Objetivo del Laboratorio

Implementar el sistema de reservas de laboratorio aplicando arquitectura en capas con buenas prácticas SOLID, partiendo del modelo UML hasta obtener una API REST funcional con Flask y MySQL sin ORM.

---

## Paso 1: Configuración del Entorno de Desarrollo

### 1.1 Prerrequisitos

| Herramienta         | Verificación                                                  |
|---------------------|---------------------------------------------------------------|
| Python 3.12+        | `python3.12 --version` / `py --version`                      |
| pip                 | `python3.12 -m pip --version` / `py -m pip --version`        |
| MySQL 8.x           | `mysql --version`                                             |
| Git Bash / CMD / PS | Terminal disponible                                          |

> **Nota:** En Windows, si el comando `python` no responde, usa `py` — es el lanzador oficial de Python para Windows.

### 1.2 Crear el Entorno Virtual

```bash
# Crear el entorno virtual en la carpeta del proyecto
py -3.12 -m venv .venv
```

> Si tu sistema tiene `python3.12` disponible directamente, puedes usar también:
>
> ```bash
> python3.12 -m venv .venv
> ```
>
> En Linux/macOS, si `python3.12` no está disponible, usa:
>
> ```bash
> python3 -m venv .venv
> ```

### 1.3 Activar el Entorno Virtual

```bash
# Linux / macOS
source .venv/bin/activate
```

```bash
# Git Bash (Windows)
source .venv/Scripts/activate
```

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
```

```cmd
:: CMD
.\.venv\Scripts\activate.bat
```

> **Si PowerShell bloquea la ejecución de scripts**, ejecuta esto una vez como administrador:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

### 1.4 Verificar la Activación

```bash
# Linux / macOS / Git Bash
which python
# Resultado esperado: .../Scripts/python
```

```powershell
# PowerShell o CMD
where python
```

El prompt debe mostrar `(.venv)` al inicio de la línea.

### 1.5 Instalar Dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```txt
Flask==3.0.2
mysqlclient==2.2.4
python-dotenv==1.0.1
```

### 1.6 Configurar Variables de Entorno

Copia la plantilla de ejemplo y actualiza los valores locales:

```bash
cp .env.example .env
```

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=local_reservas_db
FLASK_ENV=development
```

> Si usas CMD en Windows:
>
> ```cmd
> copy .env.example .env
> ```

> **Importante:** El archivo `.env` nunca debe subirse al repositorio. Ya está incluido en `.gitignore`.

### 1.7 Desactivar el Entorno

```bash
deactivate
```

---

## Paso 2: Estructura del Proyecto

La estructura refleja la arquitectura en capas diseñada en el UML.

```text
proyecto/
├── app/
│   ├── __init__.py                         ← Bootstrap: inicializa Flask y dependencias
│   ├── api/
│   │   ├── __init__.py                     ← (vacío)
│   │   └── reserva_controller.py           ← Capa de interfaz REST (HTTP)
│   ├── domain/
│   │   ├── __init__.py                     ← (vacío)
│   │   ├── entities.py                     ← Entidades y objetos de valor
│   │   ├── exceptions.py                   ← Excepciones de dominio
│   │   └── repository.py                   ← Interfaz abstracta del repositorio
│   ├── infrastructure/
│   │   ├── __init__.py                     ← (vacío)
│   │   ├── db_pool.py                      ← Pool de conexiones MySQL
│   │   ├── reserva_dao.py                  ← Acceso a datos (SQL puro)
│   │   └── mysql_reserva_repository.py     ← Implementación del repositorio
│   └── application/
│       ├── __init__.py                     ← (vacío)
│       └── reserva_service.py              ← Casos de uso / lógica de aplicación
├── .env                                    ← Variables de entorno (no subir)
├── .gitignore
├── requirements.txt
├── schema.sql                              ← DDL de la base de datos
└── run.py                                  ← Punto de entrada de la aplicación
```

> **Importante:** Crea los archivos `__init__.py` **vacíos** en cada subcarpeta (`api/`, `domain/`, `infrastructure/`, `application/`). Son necesarios para que Python trate cada carpeta como paquete y funcionen los imports relativos (`from ..domain.entities import ...`).

---

## Paso 3: UML vs Implementación Python

> **Nota:** Las secciones 3.1, 3.2 y 3.3 definen clases que van todas en el **mismo archivo** `app/domain/entities.py`. Los imports consolidados al inicio del archivo son:
> ```python
> from enum import Enum
> from dataclasses import dataclass
> from datetime import date, datetime, time, timedelta
> from .exceptions import DomainError
> ```

### 3.1 Enumeración `EstadoReserva`

| UML                  | Python                          |
|----------------------|---------------------------------|
| `enum EstadoReserva` | `class EstadoReserva(str, Enum)` |

**Archivo:** `app/domain/entities.py`

```python
from enum import Enum

class EstadoReserva(str, Enum):
    PENDIENTE  = "PENDIENTE"
    APROBADA   = "APROBADA"
    RECHAZADA  = "RECHAZADA"
    CANCELADA  = "CANCELADA"
```

### 3.2 Objeto de Valor `RangoHorario`

| UML                                       | Python                              |
|-------------------------------------------|-------------------------------------|
| `class RangoHorario <<value object>>`     | `@dataclass(frozen=True)`           |
| `+ es_valido(): bool`                     | `def es_valido(self) -> bool`       |
| `+ solapa(otro): bool`                    | `def solapa(self, otro) -> bool`    |
| `+ duracion(): timedelta`                 | `def duracion(self) -> timedelta`   |

**Archivo:** `app/domain/entities.py`

```python
from dataclasses import dataclass
from datetime import time

@dataclass(frozen=True)
class RangoHorario:
    hora_inicio: time
    hora_fin: time

    def es_valido(self) -> bool:
        return self.hora_inicio < self.hora_fin

    def solapa(self, otro: "RangoHorario") -> bool:
        return self.hora_inicio < otro.hora_fin and self.hora_fin > otro.hora_inicio

    def duracion(self) -> timedelta:
        inicio = datetime.combine(datetime.min, self.hora_inicio)
        fin = datetime.combine(datetime.min, self.hora_fin)
        return fin - inicio
```

> **SOLID — SRP:** `RangoHorario` solo conoce el rango horario. No conoce reservas ni laboratorios.

### 3.3 Entidad `ReservaLaboratorio`

| UML                                           | Python                                              |
|-----------------------------------------------|-----------------------------------------------------|
| `# id: int \| None`                           | `id: int \| None = None`                            |
| `+ aprobar(): void`                           | `def aprobar(self)` — precond. `PENDIENTE`          |
| `+ rechazar(): void`                          | `def rechazar(self)` — precond. `PENDIENTE`         |
| `+ cancelar(): void`                          | `def cancelar(self)` — precond. `PENDIENTE` o `APROBADA` |
| `- rango: RangoHorario` (composición)         | `rango: RangoHorario`                               |

**Archivo:** `app/domain/entities.py`

```python
from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class ReservaLaboratorio:
    laboratorio_id: int
    docente_id: int
    curso_codigo: str
    fecha_reserva: date
    rango: RangoHorario
    estado: EstadoReserva = EstadoReserva.PENDIENTE
    aprobada_en: datetime | None = None
    id: int | None = None

    def aprobar(self):
        if self.estado != EstadoReserva.PENDIENTE:
            raise DomainError("Solo se puede aprobar una reserva PENDIENTE")
        self.estado = EstadoReserva.APROBADA
        self.aprobada_en = datetime.utcnow()

    def rechazar(self):
        if self.estado != EstadoReserva.PENDIENTE:
            raise DomainError("Solo se puede rechazar una reserva PENDIENTE")
        self.estado = EstadoReserva.RECHAZADA

    def cancelar(self):
        if self.estado not in (EstadoReserva.PENDIENTE, EstadoReserva.APROBADA):
            raise DomainError(f"No se puede cancelar una reserva en estado {self.estado.value}")
        self.estado = EstadoReserva.CANCELADA
```

> **SOLID — OCP:** Para agregar nuevas transiciones de estado, se extiende la entidad sin modificar el servicio.

### 3.4 Interfaz `ReservaRepository`

| UML                                     | Python                           |
|-----------------------------------------|----------------------------------|
| `interface ReservaRepository`           | `class ReservaRepository(ABC)`   |
| `+ crear(reserva): int`                 | `@abstractmethod def crear`      |

**Archivo:** `app/domain/repository.py`

```python
from abc import ABC, abstractmethod

class ReservaRepository(ABC):

    @abstractmethod
    def crear(self, reserva) -> int:
        pass

    @abstractmethod
    def obtener_por_id(self, reserva_id: int):
        pass

    @abstractmethod
    def listar(self, filtros: dict):
        pass

    @abstractmethod
    def actualizar(self, reserva) -> None:
        pass

    @abstractmethod
    def eliminar(self, reserva_id: int) -> None:
        pass

    @abstractmethod
    def existe_conflicto(self, laboratorio_id, fecha_reserva,
                         hora_inicio, hora_fin, excluir_id=None) -> bool:
        pass
```

> **SOLID — DIP:** El servicio de aplicación depende de esta abstracción, no de MySQL directamente.

### 3.5 Excepciones de Dominio `DomainError`

**Archivo:** `app/domain/exceptions.py`

```python
class DomainError(Exception):
    """Error de regla de negocio: condición inválida del dominio."""
    pass
```

> **SOLID — SRP:** Las excepciones de dominio viven en la capa de dominio, no en el servicio ni en el controlador.

### 3.6 Pool de Conexiones `ConnectionPool`

**Archivo:** `app/infrastructure/db_pool.py`

```python
import os
import MySQLdb
import MySQLdb.cursors


class ConnectionPool:
    _config: dict | None = None

    @classmethod
    def initialize(cls):
        if cls._config is None:
            cls._config = dict(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "3306")),
                user=os.getenv("DB_USER", "root"),
                passwd=os.getenv("DB_PASSWORD", "root"),
                db=os.getenv("DB_NAME", "local_reservas_db"),
                charset="utf8mb4",
                autocommit=False,
            )

    @classmethod
    def get_connection(cls):
        if cls._config is None:
            cls.initialize()
        return MySQLdb.connect(**cls._config)
```

### 3.7 DAO `ReservaDAO`

**Archivo:** `app/infrastructure/reserva_dao.py`

```python
import MySQLdb.cursors


class ReservaDAO:
    def __init__(self, pool):
        self.pool = pool

    def query_one(self, sql, params=()):
        conn = self.pool.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql, params)
            return cursor.fetchone()
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def query_all(self, sql, params=()):
        conn = self.pool.get_connection()
        cursor = None
        try:
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def execute(self, sql, params=()):
        conn = self.pool.get_connection()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            conn.close()
```

### 3.8 Repositorio MySQL `MySQLReservaRepository`

**Archivo:** `app/infrastructure/mysql_reserva_repository.py`

```python
from datetime import datetime, time as time_type
from ..domain.entities import ReservaLaboratorio, RangoHorario, EstadoReserva
from ..domain.repository import ReservaRepository


class MySQLReservaRepository(ReservaRepository):
    def __init__(self, dao):
        self.dao = dao

    def crear(self, reserva: ReservaLaboratorio) -> int:
        sql = """
            INSERT INTO reservas_laboratorio
                (laboratorio_id, docente_id, curso_codigo,
                 fecha_reserva, hora_inicio, hora_fin, estado, aprobada_en)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.dao.execute(sql, (
            reserva.laboratorio_id, reserva.docente_id, reserva.curso_codigo,
            reserva.fecha_reserva, reserva.rango.hora_inicio,
            reserva.rango.hora_fin, reserva.estado.value, reserva.aprobada_en,
        ))

    def obtener_por_id(self, reserva_id: int):
        row = self.dao.query_one(
            "SELECT * FROM reservas_laboratorio WHERE id = %s AND deleted_at IS NULL",
            (reserva_id,),
        )
        return self._map_row_to_entity(row) if row else None

    def listar(self, filtros: dict):
        sql = "SELECT * FROM reservas_laboratorio WHERE deleted_at IS NULL"
        params = []
        if filtros.get("estado"):
            sql += " AND estado = %s"
            params.append(filtros["estado"])
        if filtros.get("fecha_reserva"):
            sql += " AND fecha_reserva = %s"
            params.append(filtros["fecha_reserva"])
        if filtros.get("laboratorio_id"):
            sql += " AND laboratorio_id = %s"
            params.append(filtros["laboratorio_id"])
        sql += " ORDER BY fecha_reserva, hora_inicio"
        rows = self.dao.query_all(sql, tuple(params))
        return [self._map_row_to_entity(r) for r in rows]

    def actualizar(self, reserva: ReservaLaboratorio) -> None:
        sql = """
            UPDATE reservas_laboratorio
               SET laboratorio_id = %s, docente_id = %s, curso_codigo = %s,
                   fecha_reserva = %s, hora_inicio = %s, hora_fin = %s,
                   estado = %s, aprobada_en = %s, updated_at = %s
             WHERE id = %s AND deleted_at IS NULL
        """
        self.dao.execute(sql, (
            reserva.laboratorio_id, reserva.docente_id, reserva.curso_codigo,
            reserva.fecha_reserva, reserva.rango.hora_inicio,
            reserva.rango.hora_fin, reserva.estado.value,
            reserva.aprobada_en, datetime.utcnow(), reserva.id,
        ))

    def eliminar(self, reserva_id: int) -> None:
        self.dao.execute(
            "UPDATE reservas_laboratorio SET deleted_at = NOW() WHERE id = %s",
            (reserva_id,),
        )

    def existe_conflicto(self, laboratorio_id, fecha_reserva,
                         hora_inicio, hora_fin, excluir_id=None) -> bool:
        sql = """
            SELECT COUNT(*) AS total
              FROM reservas_laboratorio
             WHERE laboratorio_id = %s
               AND fecha_reserva = %s
               AND deleted_at IS NULL
               AND estado NOT IN ('CANCELADA', 'RECHAZADA')
               AND (%s < hora_fin AND %s > hora_inicio)
        """
        params = [laboratorio_id, fecha_reserva, hora_inicio, hora_fin]
        if excluir_id:
            sql += " AND id <> %s"
            params.append(excluir_id)
        row = self.dao.query_one(sql, tuple(params))
        return row["total"] > 0

    def _map_row_to_entity(self, row) -> ReservaLaboratorio:
        return ReservaLaboratorio(
            id=row["id"],
            laboratorio_id=row["laboratorio_id"],
            docente_id=row["docente_id"],
            curso_codigo=row["curso_codigo"],
            fecha_reserva=row["fecha_reserva"],
            rango=RangoHorario(
                self._td_to_time(row["hora_inicio"]),
                self._td_to_time(row["hora_fin"]),
            ),
            estado=EstadoReserva(row["estado"]),
            aprobada_en=row["aprobada_en"],
        )

    @staticmethod
    def _td_to_time(value):
        """mysqlclient devuelve TIME como timedelta; lo convierte a time."""
        if isinstance(value, time_type):
            return value
        total = int(value.total_seconds())
        h, remainder = divmod(total, 3600)
        m, s = divmod(remainder, 60)
        return time_type(h, m, s)
```

> **SOLID — LSP:** `MySQLReservaRepository` puede sustituir a `ReservaRepository` en cualquier contexto sin alterar el comportamiento esperado.

### 3.9 Servicio de Aplicación `ReservaService`

**Archivo:** `app/application/reserva_service.py`

```python
from datetime import date, timedelta
from ..domain.entities import ReservaLaboratorio, RangoHorario, EstadoReserva
from ..domain.repository import ReservaRepository
from ..domain.exceptions import DomainError


class ReservaService:
    def __init__(self, reserva_repository: ReservaRepository):
        self.repo = reserva_repository

    def crear_reserva(self, dto: dict) -> int:
        rango = RangoHorario(dto["hora_inicio"], dto["hora_fin"])
        if not rango.es_valido():
            raise DomainError("El rango horario es inválido: hora_inicio debe ser menor que hora_fin")
        dur = rango.duracion()
        if dur < timedelta(hours=1) or dur > timedelta(hours=4):
            raise DomainError("El bloque de reserva debe ser entre 1 y 4 horas")
        if dto["fecha_reserva"] < date.today():
            raise DomainError("No se permiten reservas en fechas pasadas")
        if self.repo.existe_conflicto(
            dto["laboratorio_id"], dto["fecha_reserva"],
            dto["hora_inicio"], dto["hora_fin"]
        ):
            raise DomainError("Conflicto de horario: el laboratorio ya está reservado en ese bloque")
        reserva = ReservaLaboratorio(
            laboratorio_id=dto["laboratorio_id"],
            docente_id=dto["docente_id"],
            curso_codigo=dto["curso_codigo"],
            fecha_reserva=dto["fecha_reserva"],
            rango=rango,
        )
        return self.repo.crear(reserva)

    def obtener_reserva(self, reserva_id: int) -> ReservaLaboratorio:
        reserva = self.repo.obtener_por_id(reserva_id)
        if not reserva:
            raise DomainError("Reserva no encontrada")
        return reserva

    def listar_reservas(self, filtros: dict):
        return self.repo.listar(filtros)

    def actualizar_reserva(self, reserva_id: int, dto: dict) -> None:
        reserva = self.repo.obtener_por_id(reserva_id)
        if not reserva:
            raise DomainError("Reserva no encontrada")
        rango = RangoHorario(dto["hora_inicio"], dto["hora_fin"])
        if not rango.es_valido():
            raise DomainError("El rango horario es inválido: hora_inicio debe ser menor que hora_fin")
        dur = rango.duracion()
        if dur < timedelta(hours=1) or dur > timedelta(hours=4):
            raise DomainError("El bloque de reserva debe ser entre 1 y 4 horas")
        if dto["fecha_reserva"] < date.today():
            raise DomainError("No se permiten reservas en fechas pasadas")
        if self.repo.existe_conflicto(
            dto["laboratorio_id"], dto["fecha_reserva"],
            dto["hora_inicio"], dto["hora_fin"], excluir_id=reserva_id
        ):
            raise DomainError("Conflicto de horario: el laboratorio ya está reservado en ese bloque")
        reserva.laboratorio_id = dto["laboratorio_id"]
        reserva.docente_id = dto["docente_id"]
        reserva.curso_codigo = dto["curso_codigo"]
        reserva.fecha_reserva = dto["fecha_reserva"]
        reserva.rango = rango
        estado_dto = dto.get("estado")
        if estado_dto == EstadoReserva.APROBADA.value:
            reserva.aprobar()
        elif estado_dto == EstadoReserva.RECHAZADA.value:
            reserva.rechazar()
        elif estado_dto == EstadoReserva.CANCELADA.value:
            reserva.cancelar()
        self.repo.actualizar(reserva)

    def eliminar_reserva(self, reserva_id: int) -> None:
        reserva = self.repo.obtener_por_id(reserva_id)
        if not reserva:
            raise DomainError("Reserva no encontrada")
        self.repo.eliminar(reserva_id)
```

> **SOLID — SRP:** El servicio orquesta los casos de uso. No contiene SQL ni manejo de HTTP.

### 3.10 Controlador Flask `ReservaController`

**Archivo:** `app/api/reserva_controller.py`

```python
from datetime import date, time as time_type
from flask import Blueprint, request, jsonify
from ..domain.exceptions import DomainError


def _parse_dto(data: dict) -> dict:
    """Convierte las cadenas ISO de fecha y hora del JSON a tipos Python."""
    return {
        **data,
        "fecha_reserva": date.fromisoformat(data["fecha_reserva"]),
        "hora_inicio": time_type.fromisoformat(data["hora_inicio"]),
        "hora_fin": time_type.fromisoformat(data["hora_fin"]),
    }


def create_reserva_blueprint(service):
    bp = Blueprint("reservas", __name__)

    @bp.post("/reservas")
    def create_reserva():
        try:
            reserva_id = service.crear_reserva(_parse_dto(request.get_json()))
            return jsonify({"success": True, "data": {"id": reserva_id}}), 201
        except (DomainError, KeyError, ValueError) as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.get("/reservas/<int:reserva_id>")
    def get_reserva(reserva_id):
        try:
            r = service.obtener_reserva(reserva_id)
            return jsonify({"success": True, "data": _serialize(r)}), 200
        except DomainError as e:
            return jsonify({"success": False, "error": str(e)}), 404

    @bp.get("/reservas")
    def list_reservas():
        filtros = {
            "estado": request.args.get("estado"),
            "fecha_reserva": request.args.get("fecha_reserva"),
            "laboratorio_id": request.args.get("laboratorio_id", type=int),
        }
        reservas = service.listar_reservas(filtros)
        return jsonify({"success": True, "data": [_serialize(r) for r in reservas]}), 200

    @bp.put("/reservas/<int:reserva_id>")
    def update_reserva(reserva_id):
        try:
            service.actualizar_reserva(reserva_id, _parse_dto(request.get_json()))
            return jsonify({"success": True}), 200
        except (DomainError, KeyError, ValueError) as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @bp.delete("/reservas/<int:reserva_id>")
    def delete_reserva(reserva_id):
        try:
            service.eliminar_reserva(reserva_id)
            return jsonify({"success": True}), 200
        except DomainError as e:
            return jsonify({"success": False, "error": str(e)}), 404

    def _serialize(r):
        return {
            "id": r.id,
            "laboratorio_id": r.laboratorio_id,
            "docente_id": r.docente_id,
            "curso_codigo": r.curso_codigo,
            "fecha_reserva": str(r.fecha_reserva),
            "hora_inicio": str(r.rango.hora_inicio),
            "hora_fin": str(r.rango.hora_fin),
            "estado": r.estado.value,
            "aprobada_en": str(r.aprobada_en) if r.aprobada_en else None,
        }

    return bp
```

### 3.11 Bootstrap de la Aplicación

**Archivo:** `app/__init__.py`

```python
from flask import Flask
from dotenv import load_dotenv
from .infrastructure.db_pool import ConnectionPool
from .infrastructure.reserva_dao import ReservaDAO
from .infrastructure.mysql_reserva_repository import MySQLReservaRepository
from .application.reserva_service import ReservaService
from .api.reserva_controller import create_reserva_blueprint


def create_app():
    load_dotenv()
    app = Flask(__name__)

    ConnectionPool.initialize()
    dao = ReservaDAO(ConnectionPool)
    repo = MySQLReservaRepository(dao)
    service = ReservaService(repo)

    app.register_blueprint(
        create_reserva_blueprint(service),
        url_prefix="/api/v1"
    )
    return app
```

**Archivo:** `run.py`

```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

---

## Paso 4: Preparar la Base de Datos

Antes de ejecutar la aplicación, la base de datos debe estar creada y cargada.

### 4.1 Crear la base de datos en MySQL

Conéctate a MySQL y ejecuta el archivo `schema.sql` (cuyo contenido completo está en [02-modelado-clases-vs-tablas-fisicas.md](02-modelado-clases-vs-tablas-fisicas.md)):

```bash
# Opción A: desde la terminal (Git Bash o CMD)
mysql -u root -p < schema.sql
```

O copia y ejecuta directamente el DDL en tu cliente MySQL (Workbench, DBeaver, HeidiSQL):

```sql
-- Paso mínimo para iniciar el laboratorio:
CREATE DATABASE IF NOT EXISTS local_reservas_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE local_reservas_db;
-- (continuar con el DDL completo del archivo 02)
```

### 4.2 Cargar datos de prueba

Una vez creadas las tablas, ejecuta los INSERT del archivo 03, sección DML:

```sql
INSERT INTO laboratorios (nombre, capacidad, tipo) VALUES
  ('Laboratorio A - Planta Baja', 30, 'COMPUTO'),
  ('Laboratorio B - Piso 1',      25, 'COMPUTO');

INSERT INTO docentes (nombre, email, departamento) VALUES
  ('Ana García',  'ana.garcia@unemi.edu.ec',  'Informática'),
  ('Luis Romero', 'luis.romero@unemi.edu.ec', 'Electrónica');
```

### 4.3 Verificar la conexión desde Python

Antes de correr el servidor, comprueba que las variables en `.env` coinciden con tu instalación de MySQL:

```bash
# Verificar que el archivo .env existe y tiene los datos correctos
cat .env
```

---

## Paso 5: Ejecutar la Aplicación

```bash
# Activar el entorno virtual (si no está activo)
# Linux / macOS
source .venv/bin/activate

# Git Bash (Windows)
source .venv/Scripts/activate

# Ejecutar la API
python run.py
```

La API estará disponible en `http://localhost:5000`.

---

## Paso 6: Verificar el CRUD con la API

### Crear reserva

```http
POST /api/v1/reservas
Content-Type: application/json

{
  "laboratorio_id": 3,
  "docente_id": 91,
  "curso_codigo": "INF-202",
  "fecha_reserva": "2026-06-10",
  "hora_inicio": "08:00:00",
  "hora_fin": "10:00:00"
}
```

Respuesta esperada `201 Created`:
```json
{ "success": true, "data": { "id": 1 } }
```

### Obtener reserva por ID

```http
GET /api/v1/reservas/1
```

### Listar con filtros

```http
GET /api/v1/reservas?estado=PENDIENTE&fecha_reserva=2026-06-10
```

### Actualizar y aprobar reserva

```http
PUT /api/v1/reservas/1
Content-Type: application/json

{
  "laboratorio_id": 3,
  "docente_id": 91,
  "curso_codigo": "INF-202-LAB",
  "fecha_reserva": "2026-06-10",
  "hora_inicio": "09:00:00",
  "hora_fin": "11:00:00",
  "estado": "APROBADA"
}
```

### Eliminar (borrado lógico)

```http
DELETE /api/v1/reservas/1
```

---

## Checklist del Laboratorio

Usa esta lista para verificar que completaste cada parte del laboratorio:

### Entorno y proyecto
- [ ] Entorno virtual `.venv` creado y activado correctamente.
- [ ] Dependencias instaladas con `pip install -r requirements.txt`.
- [ ] Archivo `.env` configurado con los datos de conexión a MySQL.
- [ ] Base de datos `local_reservas_db` creada y tablas inicializadas.
- [ ] Datos de prueba insertados (laboratorios y docentes).

### Código implementado
- [ ] `app/domain/entities.py` — entidad, objeto de valor y enum.
- [ ] `app/domain/exceptions.py` — excepción de dominio (`DomainError`).
- [ ] `app/domain/repository.py` — interfaz abstracta del repositorio.
- [ ] `app/infrastructure/db_pool.py` — pool de conexiones.
- [ ] `app/infrastructure/reserva_dao.py` — acceso a datos SQL.
- [ ] `app/infrastructure/mysql_reserva_repository.py` — implementación del repositorio.
- [ ] `app/application/reserva_service.py` — lógica de aplicación.
- [ ] `app/api/reserva_controller.py` — endpoints REST.
- [ ] `app/__init__.py` y `run.py` — bootstrap.

### API verificada
- [ ] `POST /api/v1/reservas` → responde `201 Created`.
- [ ] `GET /api/v1/reservas/1` → retorna la reserva creada.
- [ ] `GET /api/v1/reservas?estado=PENDIENTE` → lista filtrada.
- [ ] `PUT /api/v1/reservas/1` con estado `APROBADA` → actualiza correctamente.
- [ ] `DELETE /api/v1/reservas/1` → borrado lógico (registro permanece en DB con `deleted_at` lleno).
- [ ] Crear dos reservas con mismo laboratorio, fecha y bloque → API retorna error de conflicto.

### Análisis y comprensión
- [ ] Explica con tus palabras qué principio SOLID impide que el controlador llame al DAO directamente.
- [ ] Identifica dónde se aplica polimorfismo y para qué sirve en este sistema.
- [ ] Propón una regla de negocio adicional y describe en qué capa la implementarías.

---

## Resumen de Principios SOLID Aplicados

| Principio | Descripción                                    | Dónde se aplica                                          |
|-----------|------------------------------------------------|----------------------------------------------------------|
| **S**RP   | Una clase, una responsabilidad                 | `ReservaDAO`, `ReservaService`, `ReservaController`      |
| **O**CP   | Abierto para extensión, cerrado para modificación | `EstadoReserva`, métodos de entidad (`aprobar`, `cancelar`) |
| **L**SP   | Sustitución de Liskov                          | `MySQLReservaRepository` reemplaza a `ReservaRepository` |
| **I**SP   | Segregación de interfaces                      | `ReservaRepository` define solo lo necesario             |
| **D**IP   | Inversión de dependencias                      | `ReservaService` depende de la abstracción, no de MySQL  |
