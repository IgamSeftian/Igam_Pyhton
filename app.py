from flask import Flask, request, jsonify
from mysql.connector import Error

import CRUD

app = Flask(__name__)

VALID_STATUS = ("publish", "draft", "thrash")
ARTICLE_KEYS = ("id", "title", "content", "category", "status")


def validate(data):
    errors = []
    cleaned = {}

    if not isinstance(data.get("title"), str) or not data.get("title").strip():
        errors.append("title: required")
    elif len(data["title"].strip()) < 20:
        errors.append("title: minimal 20 karakter")
    else:
        cleaned["title"] = data["title"].strip()

    if not isinstance(data.get("content"), str) or not data.get("content").strip():
        errors.append("content: required")
    elif len(data["content"].strip()) < 200:
        errors.append("content: minimal 200 karakter")
    else:
        cleaned["content"] = data["content"].strip()

    if not isinstance(data.get("category"), str) or not data.get("category").strip():
        errors.append("category: required")
    elif len(data["category"].strip()) < 3:
        errors.append("category: minimal 3 karakter")
    else:
        cleaned["category"] = data["category"].strip()

    status = data.get("status")
    if not isinstance(status, str) or not status.strip():
        errors.append("status: required")
    elif status.strip().lower() not in VALID_STATUS:
        errors.append("status: harus salah satu dari publish, draft, thrash")
    else:
        cleaned["status"] = status.strip().lower()

    return errors, cleaned


def get_json():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return None
    return data


def article_json(row):
    return {key: row[key] for key in ARTICLE_KEYS}


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint tidak ditemukan"}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"error": "Method tidak diizinkan"}), 405


@app.route("/article/", methods=["POST"], strict_slashes=False)
def create_article():
    data = get_json()
    if data is None:
        return jsonify({"error": "Request body harus JSON"}), 400

    errors, cleaned = validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        CRUD.insert_article(cleaned)
        return jsonify({}), 200
    except Error as e:
        return jsonify({"error": f"Gagal menyimpan article: {e}"}), 500


@app.route("/article/<int:limit>/<int:offset>", methods=["GET"])
def list_articles(limit, offset):
    try:
        rows = CRUD.list_articles(limit=limit, offset=offset)
        return jsonify([article_json(row) for row in rows]), 200
    except Error as e:
        return jsonify({"error": f"Gagal membaca article: {e}"}), 500


@app.route("/article/<int:article_id>", methods=["GET"])
def get_article(article_id):
    try:
        row = CRUD.get_article(article_id)
    except Error as e:
        return jsonify({"error": f"Gagal membaca article: {e}"}), 500

    if row is None:
        return jsonify({"error": "Article tidak ditemukan"}), 404
    return jsonify(article_json(row)), 200


@app.route("/article/<int:article_id>", methods=["POST", "PUT", "PATCH"])
def update_article(article_id):
    data = get_json()
    if data is None:
        return jsonify({"error": "Request body harus JSON"}), 400

    errors, cleaned = validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        if CRUD.get_article(article_id) is None:
            return jsonify({"error": "Article tidak ditemukan"}), 404
        CRUD.update_article(article_id, cleaned)
        return jsonify({}), 200
    except Error as e:
        return jsonify({"error": f"Gagal mengubah article: {e}"}), 500


@app.route("/article/<int:article_id>", methods=["DELETE"])
def delete_article(article_id):
    try:
        if CRUD.get_article(article_id) is None:
            return jsonify({"error": "Article tidak ditemukan"}), 404
        CRUD.delete_article(article_id)
        return jsonify({}), 200
    except Error as e:
        return jsonify({"error": f"Gagal menghapus article: {e}"}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
