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