import psycopg2
from psycopg2 import pool
from config import DB_URL, logger

# PostgreSQL connection pool
db_pool = None


def init_db_pool():
    global db_pool
    if db_pool is not None:
        logger.info("Database pool already initialized")
        return
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, dsn=DB_URL)
        if db_pool:
            logger.info("Database pool initialized successfully")
        else:
            raise ValueError("Database pool initialization returned None")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise RuntimeError(f"Database pool initialization failed: {e}")


def init_db():
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    conn = None
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                user_id TEXT,
                user_name TEXT,
                text TEXT,
                timestamp TIMESTAMP
            )
        """)
        conn.commit()
        logger.info("Database schema initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise
    finally:
        if conn:
            db_pool.putconn(conn)


async def log_message(update, context):
    if update.message and update.message.text:
        chat_id = update.message.chat_id
        user = update.message.from_user
        message = update.message.text
        timestamp = update.message.date

        user_name = user.first_name if user.first_name else '唔知邊條粉蛋'
        if user.last_name:
            user_name += " " + user.last_name

        user_id = user.id

        logger.info(f"Received message in chat {chat_id} from {user_name}: {message}")

        if db_pool is None:
            logger.error("Database pool not initialized")
            await update.message.reply_text("哎呀，資料庫未準備好，請稍後再試！")
            return

        conn = None
        try:
            conn = db_pool.getconn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, user_name, user_id, text, timestamp) VALUES (%s, %s, %s, %s, %s)",
                (chat_id, user_name, user_id, message, timestamp)
            )
            conn.commit()
            logger.info(f"Message saved to database for chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to log message to database: {e}")
            await update.message.reply_text("哎呀，儲存訊息時出錯！請稍後再試。")
        finally:
            if conn:
                db_pool.putconn(conn)
