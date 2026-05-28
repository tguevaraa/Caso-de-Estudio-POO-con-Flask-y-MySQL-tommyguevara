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
