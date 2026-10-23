from connection import Koneksi

DB_NAME = Koneksi.DATABASE
TABLE_NAME = "posts"
SELECT_COLUMNS = "id, title, content, category, status, created_date, updated_date"

SQL_CREATE_DATABASE = (
    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
    "DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"
)

SQL_CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
  id INT NOT NULL AUTO_INCREMENT,
  title VARCHAR(200) NOT NULL,
  content TEXT NOT NULL,
  category VARCHAR(100) DEFAULT NULL,
  created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_date TIMESTAMP NULL DEFAULT NULL,
  status VARCHAR(100) NOT NULL DEFAULT 'Publish',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
"""

# MySQL 5.1 hanya mengizinkan 1 kolom TIMESTAMP CURRENT_TIMESTAMP,
# jadi updated_date diisi otomatis lewat trigger.
TRIGGERS = {
    "trg_posts_before_insert": (
        f"BEFORE INSERT ON `{TABLE_NAME}` FOR EACH ROW SET NEW.updated_date = NOW()"
    ),
    "trg_posts_before_update": (
        f"BEFORE UPDATE ON `{TABLE_NAME}` FOR EACH ROW SET NEW.updated_date = NOW()"
    ),
}


def database_exists():
    conn = Koneksi.get_server_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (DB_NAME,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def table_exists():
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE %s", (TABLE_NAME,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def trigger_exists(trigger_name):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TRIGGERS")
        return any(row[0] == trigger_name for row in cursor.fetchall())
    finally:
        conn.close()


def create_database():
    conn = Koneksi.get_server_connection()
    try:
        conn.cursor().execute(SQL_CREATE_DATABASE)
        conn.commit()
    finally:
        conn.close()
    print(f"Database '{DB_NAME}' dibuat.")


def create_table():
    conn = Koneksi.get_connection()
    try:
        conn.cursor().execute(SQL_CREATE_TABLE)
        conn.commit()
    finally:
        conn.close()
    print(f"Table '{DB_NAME}.{TABLE_NAME}' dibuat.")


def create_trigger(trigger_name):
    conn = Koneksi.get_connection()
    try:
        conn.cursor().execute(f"CREATE TRIGGER `{trigger_name}` {TRIGGERS[trigger_name]}")
        conn.commit()
    finally:
        conn.close()
    print(f"Trigger '{trigger_name}' dibuat.")


def migrate():
    print("=== Migrasi dimulai ===")

    if database_exists():
        print(f"Database '{DB_NAME}' sudah ada, skip create.")
    else:
        create_database()

    if table_exists():
        print(f"Table '{DB_NAME}.{TABLE_NAME}' sudah ada, skip create.")
    else:
        create_table()

    for name in TRIGGERS:
        if trigger_exists(name):
            print(f"Trigger '{name}' sudah ada, skip create.")
        else:
            create_trigger(name)

    print("=== Migrasi selesai ===")


def list_articles(status=None, limit=None, offset=None):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        sql = f"SELECT {SELECT_COLUMNS} FROM `{TABLE_NAME}`"
        params = []
        if status:
            sql += " WHERE status = %s"
            params.append(status)
        sql += " ORDER BY id DESC"
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)
            if offset is not None:
                sql += " OFFSET %s"
                params.append(offset)
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    finally:
        conn.close()


def get_article(article_id):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {SELECT_COLUMNS} FROM `{TABLE_NAME}` WHERE id = %s",
            (article_id,),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def insert_article(data):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO `{TABLE_NAME}` (title, content, category, status) "
            "VALUES (%s, %s, %s, %s)",
            (data["title"], data["content"], data["category"], data["status"]),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_article(article_id, data):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE `{TABLE_NAME}` SET title = %s, content = %s, "
            "category = %s, status = %s WHERE id = %s",
            (data["title"], data["content"], data["category"],
             data["status"], article_id),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def set_status(article_id, status):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE `{TABLE_NAME}` SET status = %s WHERE id = %s",
            (status, article_id),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_article(article_id):
    conn = Koneksi.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM `{TABLE_NAME}` WHERE id = %s", (article_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
