from enum import Enum
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from .exceptions import DomainError


class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"
    CANCELADA = "CANCELADA"


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