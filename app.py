from flask import Flask, render_template, request, jsonify, abort
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent
DB = BASE / "saki.db"
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS anime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, title_jp TEXT DEFAULT '', description TEXT DEFAULT '',
            poster TEXT DEFAULT '', banner TEXT DEFAULT '', year INTEGER DEFAULT 2024,
            status TEXT DEFAULT 'Airing', rating REAL DEFAULT 0, genres TEXT DEFAULT '',
            episodes INTEGER DEFAULT 0, network TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        count = con.execute("SELECT COUNT(*) FROM anime").fetchone()[0]
        if count == 0:
            demo = [
              ("Demon Slayer","Kimetsu no Yaiba","Tanjiro joins the Demon Slayer Corps after a demon attack changes his family forever.","https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600","",2019,"Completed",8.7,"Action,Fantasy,Adventure",26,"Crunchyroll"),
              ("Attack on Titan","Shingeki no Kyojin","Humanity fights for survival behind enormous walls while uncovering the truth about the Titans.","https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600","",2013,"Completed",9.1,"Action,Drama,Fantasy",25,"Crunchyroll"),
              ("Jujutsu Kaisen","呪術廻戦","Yuji Itadori enters the dangerous world of curses after a fateful encounter.","https://images.unsplash.com/photo-1614583225154-5fcauce","",2020,"Airing",8.6,"Action,Supernatural",24,"Crunchyroll"),
              ("One Piece","ワンピース","Monkey D. Luffy sails toward the Grand Line in search of the legendary One Piece.","https://images.unsplash.com/photo-1601850494422-3cf14624b0b3?w=600","",1999,"Airing",9.0,"Adventure,Action,Comedy",1000,"Netflix"),
              ("Spy x Family","スパイファミリー","A spy, an assassin and a telepath form an unusual family.","https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?w=600","",2022,"Airing",8.4,"Comedy,Action",25,"Netflix"),
              ("My Hero Academia","Boku no Hero Academia","A boy born without powers aims to become the world's greatest hero.","https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600","",2016,"Airing",8.2,"Action,School",13,"Disney+ Hotstar")
            ]
            con.executemany("INSERT INTO anime(title,title_jp,description,poster,banner,year,status,rating,genres,episodes,network) VALUES(?,?,?,?,?,?,?,?,?,?,?)", demo)

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/anime")
def anime_list():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    with db() as con:
        sql = "SELECT * FROM anime WHERE 1=1"
        args = []
        if q:
            sql += " AND (title LIKE ? OR title_jp LIKE ? OR genres LIKE ?)"
            args += [f"%{q}%"] * 3
        if genre:
            sql += " AND genres LIKE ?"
            args.append(f"%{genre}%")
        sql += " ORDER BY rating DESC, id DESC"
        rows = con.execute(sql, args).fetchall()
        return jsonify([dict(x) for x in rows])

@app.get("/api/anime/<int:anime_id>")
def anime_detail(anime_id):
    with db() as con:
        row = con.execute("SELECT * FROM anime WHERE id=?", (anime_id,)).fetchone()
        if not row:
            abort(404)
        return jsonify(dict(row))

@app.post("/api/anime")
def add_anime():
    data = request.get_json(silent=True) or {}
    required = ["title"]
    if not all(data.get(k) for k in required):
        return jsonify(error="Title is required"), 400
    with db() as con:
        cur = con.execute("""INSERT INTO anime(title,title_jp,description,poster,banner,year,status,rating,genres,episodes,network)
          VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
          (data.get("title"),data.get("title_jp",""),data.get("description",""),data.get("poster",""),
           data.get("banner",""),int(data.get("year") or 2024),data.get("status","Airing"),
           float(data.get("rating") or 0),data.get("genres",""),int(data.get("episodes") or 0),data.get("network","")))
        return jsonify(id=cur.lastrowid, message="Anime added"), 201

@app.delete("/api/anime/<int:anime_id>")
def delete_anime(anime_id):
    with db() as con:
        cur = con.execute("DELETE FROM anime WHERE id=?", (anime_id,))
        if not cur.rowcount:
            abort(404)
    return jsonify(message="Deleted")

@app.get("/health")
def health():
    return jsonify(status="ok", app="Saki Anime")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
