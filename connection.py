import mysql.connector
from mysql.connector import Error


class Koneksi:
    HOST = "localhost"
    PORT = 3306
    USER = "root"
    PASSWORD = "tdUlgx7+RRlCOcjnu8GrjFNIqrl68DHEE=fOD5mdDlQ5"
    DATABASE = "article"
    CHARSET = "utf8"

    _BASE_CONFIG = {
        "host": HOST,
        "port": PORT,
        "user": USER,
        "password": PASSWORD,
        "charset": CHARSET,
    }

    @classmethod
    def get_server_connection(cls):
        """Koneksi ke MySQL tanpa database (untuk CREATE DATABASE)."""
        try:
            return mysql.connector.connect(**cls._BASE_CONFIG)
        except Error as e:
            raise ConnectionError(f"Gagal koneksi ke MySQL: {e}") from e

    @classmethod
    def get_connection(cls, database=None):
        """Koneksi ke database (default: database article)."""
        config = dict(cls._BASE_CONFIG)
        config["database"] = database or cls.DATABASE
        try:
            return mysql.connector.connect(**config)
        except Error as e:
            raise ConnectionError(f"Gagal koneksi ke database: {e}") from e


if __name__ == "__main__":
    conn = Koneksi.get_connection()
    print(f"Koneksi OK - MySQL {conn.server_info}")
    conn.close()
