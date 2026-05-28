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