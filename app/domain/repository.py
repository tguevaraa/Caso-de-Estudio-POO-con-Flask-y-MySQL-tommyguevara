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