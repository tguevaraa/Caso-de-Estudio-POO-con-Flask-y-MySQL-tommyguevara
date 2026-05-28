from datetime import date, time as time_type
from flask import Blueprint, request, jsonify
from ..domain.exceptions import DomainError


def _parse_dto(data: dict) -> dict:
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