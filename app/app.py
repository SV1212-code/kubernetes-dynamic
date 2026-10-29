import os
import pymysql
from flask import Flask, request, render_template_string

app = Flask(__name__)

PROFESSIONS = ["Engineer", "Doctor", "Teacher", "Artist", "Other"]

PAGE = """
<h2>Add Person</h2>
<form method="post" action="/add">
  Name: <input name="name" required>
  Profession:
  <select name="profession">
    {% for p in professions %}<option>{{ p }}</option>{% endfor %}
  </select>
  <button type="submit">Add</button>
</form>
<p>{{ msg }}</p>
<form method="get" action="/all">
  <button type="submit">Complete</button>
</form>
{% if rows is not none %}
<h3>All Records</h3>
<table border="1" cellpadding="5">
  <tr><th>ID</th><th>Name</th><th>Profession</th></tr>
  {% for r in rows %}<tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td></tr>{% endfor %}
</table>
{% endif %}
"""


def get_db():
    conn = pymysql.connect(
        host=os.environ.get("DB_HOST", "mysql"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "password"),
        database=os.environ.get("DB_NAME", "demo"),
    )
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS people ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "name VARCHAR(100), profession VARCHAR(50))"
        )
    return conn


def show(msg="", rows=None):
    return render_template_string(PAGE, professions=PROFESSIONS, msg=msg, rows=rows)


@app.route("/")
def index():
    return show()


@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO people (name, profession) VALUES (%s, %s)",
            (request.form["name"], request.form["profession"]),
        )
    conn.commit()
    conn.close()
    return show(msg="Record added.")


@app.route("/all")
def all_records():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, profession FROM people")
        rows = cur.fetchall()
    conn.close()
    return show(rows=rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
