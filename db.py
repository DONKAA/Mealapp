import sqlite3

DB_NAME = "meal_app.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipes(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT UNIQUE,
      meal_slot TEXT,
      ingredients TEXT,
      steps TEXT,
      kcal REAL, protein REAL, carbs REAL, fat REAL,
      ref_link TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plan(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      week INTEGER, day INTEGER, slot TEXT,
      recipe_id INTEGER, portions REAL DEFAULT 1.0,
      UNIQUE(week,day,slot),
      FOREIGN KEY(recipe_id) REFERENCES recipes(id)
    )""")
    conn.commit(); conn.close()

def list_recipes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM recipes ORDER BY title").fetchall()
    conn.close()
    return rows

def upsert_recipe(data):
    conn = get_conn(); cur = conn.cursor()
    if data.get("id"):
        cur.execute("""UPDATE recipes SET title=?, meal_slot=?, ingredients=?, steps=?, kcal=?, protein=?, carbs=?, fat=?, ref_link=?
                       WHERE id=?""",
                    (data["title"], data["meal_slot"], data["ingredients"], data["steps"],
                     data["kcal"], data["protein"], data["carbs"], data["fat"], data["ref_link"], data["id"]))
    else:
        cur.execute("""INSERT INTO recipes(title, meal_slot, ingredients, steps, kcal, protein, carbs, fat, ref_link)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (data["title"], data["meal_slot"], data["ingredients"], data["steps"],
                     data["kcal"], data["protein"], data["carbs"], data["fat"], data["ref_link"]))
    conn.commit(); conn.close()

def delete_recipe(recipe_id):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    cur.execute("DELETE FROM plan WHERE recipe_id=?", (recipe_id,))
    conn.commit(); conn.close()

def get_recipe_by_title(title):
    conn = get_conn()
    row = conn.execute("SELECT * FROM recipes WHERE title=?", (title,)).fetchone()
    conn.close()
    return row

def list_plan(week):
    conn = get_conn()
    rows = conn.execute("""
      SELECT p.*, r.title
      FROM plan p LEFT JOIN recipes r ON p.recipe_id=r.id
      WHERE p.week=? ORDER BY day,
        CASE slot
         WHEN 'Colazione' THEN 1 WHEN 'Spuntino' THEN 2 WHEN 'Pranzo' THEN 3
         WHEN 'Pre-Workout' THEN 4 WHEN 'Cena' THEN 5 WHEN 'Spuntino serale' THEN 6 ELSE 99 END
    """, (week,)).fetchall()
    conn.close()
    return rows

def set_plan(week, day, slot, recipe_id, portions=1.0):
    conn = get_conn(); cur = conn.cursor()
    if recipe_id is None:
        cur.execute("DELETE FROM plan WHERE week=? AND day=? AND slot=?", (week,day,slot))
    else:
        cur.execute("""INSERT INTO plan(week,day,slot,recipe_id,portions)
                       VALUES(?,?,?,?,?)
                       ON CONFLICT(week,day,slot) DO UPDATE SET recipe_id=excluded.recipe_id, portions=excluded.portions""",
                    (week, day, slot, recipe_id, portions))
    conn.commit(); conn.close()

def get_week_recipes(week):
    conn = get_conn(); cur = conn.cursor()
    rows = cur.execute("""SELECT DISTINCT r.* FROM plan p JOIN recipes r ON p.recipe_id=r.id WHERE p.week=?""",(week,)).fetchall()
    conn.close()
    return rows
