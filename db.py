from config import logger
from database import DatabasePool


class DatabaseOperations:
    def __init__(self):
        try:
            self.db_pool = DatabasePool.get_pool()
        except RuntimeError as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def get_messages_in_range(self, chat_id, start_time, end_time):
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_name, text, timestamp FROM messages
                WHERE chat_id = %s AND timestamp >= %s AND timestamp < %s
                ORDER BY timestamp ASC
            """, (chat_id, start_time, end_time))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            logger.error(f"Failed to query database: {e}")
            return None
        finally:
            if conn:
                self.db_pool.putconn(conn)

    def get_user_messages_in_range(self, chat_id, user_id, start_time, end_time):
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_name, text, timestamp FROM messages
                WHERE chat_id = %s AND user_id = %s AND timestamp >= %s AND timestamp < %s
                ORDER BY timestamp ASC
            """, (chat_id, int(user_id), start_time, end_time))
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            logger.error(f"Failed to query database: {e}")
            return None
        finally:
            if conn:
                self.db_pool.putconn(conn)