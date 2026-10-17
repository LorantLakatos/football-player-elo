from scraper import scraper

evek=[]

for year in range(2019, 2025):
    next_year = year+1

    start_str = str(year)[2:]
    end_str = str(next_year)[2:]

    szezon_kod = f"{start_str}{end_str}"
    evek.append(szezon_kod)

for ev in evek:
    print("=" * 60)
    print(f" AZ ADATOK GYŰJTÉSE ELINDULT A(Z) {ev} SZEZONHOZ...")
    print("=" * 60)
    
    try:
        # Meghívjuk a te scraper osztályodat, ami a konstruktor miatt azonnal elindul
        scraper(year=ev)
        print(f"\n[SIKER] A(z) {ev} szezon sikeresen a gyorsítótárban van.\n")
        
    except Exception as e:
        print(f"\n[HIBA] Megszakadt a letöltés a(z) {ev} szezon közben: {e}")
        print("Biztonsági okokból továbblépünk a következő évre...\n")
