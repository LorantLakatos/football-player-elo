import soccerdata as sd
from time import sleep

class scraper:

    def __init__(self, year: str):
        self.year = year
        
        fbref = sd.FBref('ENG-Premier League', year)

        # Fetch data
        games = fbref.read_schedule()
        #team_season_stats = fbref.read_team_season_stats(stat_type="standard")
        #player_season_stats = fbref.read_player_season_stats(stat_type="standard")


        #Retrieve lineups for the selected leagues and seasons.
        match_ids = games['game_id'].tolist()
        
        for id in match_ids:
            print(f"{id} letöltése")
            match_lineup = fbref.read_lineup(id, force_cache=False)
            
        #ebből a lekérdezésből mindent megkapok ami kell, de meg kell keresnem az id-kat
        #testmatch_lineup = fbref.read_lineup(match_ids, force_cache=False)