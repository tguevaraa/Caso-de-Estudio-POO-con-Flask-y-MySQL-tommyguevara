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
        if isinstance(value, time_type):
            return value
        total = int(value.total_seconds())
        h, remainder = divmod(total, 3600)
        m, s = divmod(remainder, 60)
        return time_type(h, m, s)