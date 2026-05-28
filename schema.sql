-- ============================================================
-- SCHEMA: local_reservas_db
-- Sistema de Reservas de Laboratorio
-- ============================================================

CREATE DATABASE IF NOT EXISTS local_reservas_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE local_reservas_db;

-- ------------------------------------------------------------
-- Tabla: laboratorios
-- ------------------------------------------------------------
CREATE TABLE laboratorios (
  id          INT           NOT NULL AUTO_INCREMENT,
  nombre      VARCHAR(100)  NOT NULL,
  capacidad   INT           NOT NULL DEFAULT 30,
  tipo        VARCHAR(50)   NOT NULL DEFAULT 'COMPUTO',
  activo      TINYINT(1)    NOT NULL DEFAULT 1,
  created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                             ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE INDEX uq_laboratorio_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Tabla: docentes
-- ------------------------------------------------------------
CREATE TABLE docentes (
  id            INT           NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(150)  NOT NULL,
  email         VARCHAR(150)  NOT NULL,
  departamento  VARCHAR(100)  NULL,
  activo        TINYINT(1)    NOT NULL DEFAULT 1,
  created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE INDEX uq_docente_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- Tabla: reservas_laboratorio
-- ------------------------------------------------------------
CREATE TABLE reservas_laboratorio (
  id              INT           NOT NULL AUTO_INCREMENT,
  laboratorio_id  INT           NOT NULL,
  docente_id      INT           NOT NULL,
  curso_codigo    VARCHAR(30)   NOT NULL,
  fecha_reserva   DATE          NOT NULL,
  hora_inicio     TIME          NOT NULL,
  hora_fin        TIME          NOT NULL,
  estado          VARCHAR(20)   NOT NULL DEFAULT 'PENDIENTE',
  aprobada_en     DATETIME      NULL,
  deleted_at      DATETIME      NULL,
  created_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_reserva_laboratorio
    FOREIGN KEY (laboratorio_id) REFERENCES laboratorios (id),
  CONSTRAINT fk_reserva_docente
    FOREIGN KEY (docente_id) REFERENCES docentes (id),
  CONSTRAINT chk_estado
    CHECK (estado IN ('PENDIENTE', 'APROBADA', 'RECHAZADA', 'CANCELADA')),
  INDEX idx_reserva_lookup   (laboratorio_id, fecha_reserva, hora_inicio, hora_fin),
  INDEX idx_estado_fecha      (estado, fecha_reserva),
  INDEX idx_docente_fecha     (docente_id, fecha_reserva)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
