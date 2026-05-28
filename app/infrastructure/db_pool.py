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
                passwd=os.getenv("DB_PASSWORD", ""),
                db=os.getenv("DB_NAME", "local_reservas_db"),
                charset="utf8mb4",
                autocommit=False,
            )

    @classmethod
    def get_connection(cls):
        if cls._config is None:
            cls.initialize()
        return MySQLdb.connect(**cls._config)
