import os
import soccerdata as sd

fbref = sd.FBref('ENG-Premier League', '2021')
testmatch_lineup = fbref.read_lineup(match_id="77f4164b", force_cache=False)

# Megkeressük a jelenlegi script mappájának az útvonalát
script_dir = os.path.dirname(os.path.abspath(__file__))
teljes_utvonal = os.path.join(script_dir, "meccs_felallas.csv")

# Elmentjük a fájlt közvetlenül a kódod mellé
testmatch_lineup.to_csv(teljes_utvonal)
print(f"A fájl sikeresen elmentve ide: {teljes_utvonal}")
