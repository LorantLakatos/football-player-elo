import sqlite3

# 1. Kapcsolódás a meglévő adatbázishoz
conn = sqlite3.connect("foci_elo.db")
cursor = conn.cursor()

# 2. EGYETLEN SQL PARANCS: Minden játékos eloját visszaírja 1500.0-ra
cursor.execute("UPDATE players SET current_elo = 1500.0;")

# 3. Véglegesítés és lezárás
conn.commit()
conn.close()

print(" Sikeres reset! Az összes játékos ELO pontszáma visszaállítva 1500.0-ra.")
