import os
import sqlite3
import pandas as pd
import soccerdata as sd
from tqdm import tqdm

class dbBuildersafe:

    def __init__(self, year: str):

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


        # 2. Adatok beolvasása a helyi cache-ből
        print("\n2. LÉPÉS: Menetrend beolvasása a helyi cache-ből...")
        fbref = sd.FBref('ENG-Premier League', year)
        games = fbref.read_schedule()
        scores = games['score'].tolist()

        print("Meccsek adatai mentése a TISZTA 8 karakteres ID-kkal...")
        score_iter = 0
        for game_id_raw, row in games.iterrows():
            score_string = scores[score_iter]
            result = "DRAW"
            if score_string[0] > score_string[2]:
                result = "HOME"
            elif score_string[2] > score_string[0]:
                result = "AWAY"
            
            # A tiszta 8 karakteres FBref kód az oszlopból
            tiszta_game_id = row['game_id']
            
            cursor.execute("""
            INSERT OR REPLACE INTO matches (game_id, date, home_team, away_team, result)
            VALUES (?, ?, ?, ?, ?)
            """, (tiszta_game_id, str(row.get('date', '')), row['home_team'], row['away_team'], result))
            score_iter += 1
        conn.commit()

        # Kigyűjtjük a tiszta string azonosítókat az SQL-ből
        nyers_id_list = cursor.execute("SELECT game_id FROM matches;").fetchall()
        match_ids = [m[0] for m in nyers_id_list]

        print(f"Sikeresen rögzítve {len(match_ids)} mérkőzés a 'matches' táblában.")


        # 3. Lineupok és Játékosok feltöltése (ID-alapú összekötéssel)
        print("\n3. LÉPÉS: Felállások feldolgozása a player_id-k alapján...")
        for m_id in tqdm(match_ids, desc="SQL Adatbázis építése", unit="meccs"):
            try:
                lineup = fbref.read_lineup(m_id, force_cache=False)
                
                if lineup.empty:
                    continue
                    
                for _, row in lineup.iterrows():
                    p_name = row['player']
                    t_name = row['team'] 
                    is_start = 1 if row['is_starter'] else 0
                    
                    # JAVÍTÁS A NAType HIBÁRA: Ha a cella üres (pd.isna), biztonságos alapértéket kap az SQL helyettük
                    pos = "" if pd.isna(row['position']) else str(row['position'])
                    mins = 0 if pd.isna(row['minutes_played']) else int(row['minutes_played'])
                    
                    # A) Először regisztráljuk a játékost a neve alapján (ha még nem létezik)
                    cursor.execute("INSERT OR IGNORE INTO players (player_name) VALUES (?)", (p_name,))
                    
                    # B) KIKERESSÜK az SQL-ből a játékoshoz tartozó automatikus ID számot
                    cursor.execute("SELECT player_id FROM players WHERE player_name = ?;", (p_name,))
                    p_id = cursor.fetchone()[0] # Kiemeljük a számot a zárójelből
                    
                    # C) A lineups táblába már a tiszta p_id számot szúrjuk be a név helyett!
                    cursor.execute("""
                    INSERT OR IGNORE INTO lineups (game_id, player_id, team_name, is_starter, position, minutes_played)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (m_id, p_id, t_name, is_start, pos, mins))
                    
            except Exception as e:
                print(f"Hiba a(z) {m_id} meccs feldolgozásakor: {e}")

        conn.commit()
        conn.close()

        print(f"\n Sikeres folyamat! A '{db_name}' adatbázis hibátlanul feltöltődött (player_id-kkal).")

