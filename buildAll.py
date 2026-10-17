import sqlite3
from dbBuilder import dbBuilder

db_name = "foci_elo.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

print("1. LÉPÉS: SQL Táblák szerkezetének létrehozása...")
# Biztosra megyünk, dobunk mindent az új szerkezethez
cursor.execute("DROP TABLE IF EXISTS lineups;")
cursor.execute("DROP TABLE IF EXISTS matches;")
cursor.execute("DROP TABLE IF EXISTS players;")

# Játékosok tábla (Generálja a player_id-t)
cursor.execute("""
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT UNIQUE,
    current_elo REAL DEFAULT 1500.0
)
""")

# Meccsek tábla (8 karakteres game_id-val)
cursor.execute("""
CREATE TABLE matches (
    game_id TEXT PRIMARY KEY,
    date TEXT,
    home_team TEXT,
    away_team TEXT,
    result TEXT
)
""")

# JAVÍTÁS A 22 JÁTÉKOSHOZ: Kivettem a szigorú PRIMARY KEY (game_id, player_id) korlátot, 
# így az SQL már nem fogja letiltani és ignorálni a vendégcsapat tagjait!
cursor.execute("""
CREATE TABLE lineups (
    game_id TEXT,
    player_id INTEGER,
    team_name TEXT,
    is_starter INTEGER,
    position TEXT,
    minutes_played INTEGER,
    FOREIGN KEY (game_id) REFERENCES matches(game_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
)
""")
conn.commit()

evek=[]

for year in range(2019, 2026):
    next_year = year+1

    start_str = str(year)[2:]
    end_str = str(next_year)[2:]

    szezon_kod = f"{start_str}{end_str}"
    evek.append(szezon_kod)

for ev in evek:
    print("=" * 60)
    print(f" AZ ADATBÁZIS ÉPíTÉSE ELINDULT A(Z) {ev} SZEZONHOZ...")
    print("=" * 60)
    
    try:
        # Meghívjuk a te builder osztályodat, ami a konstruktor miatt azonnal elindul
        dbBuilder(year=ev)
        print(f"\n[SIKER] A(z) {ev} szezon sikeresen az adatbázisban van.\n")
        
    except Exception as e:
        print(f"\n[HIBA] Megszakadt az adatbázisba töltés a(z) {ev} szezon közben: {e}")
        print("Biztonsági okokból továbblépünk a következő évre...\n")
