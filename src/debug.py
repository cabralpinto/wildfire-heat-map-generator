import warnings

import requests
import spacy

tweets = [
    '⚠\ud83d\udd25 Novo incêndio em Porto, Vila Nova De Gaia, Pedroso E Seixezelo - Mato https://t.co/Q6lSLZXEde #IRVilaNovaDeGaia #FogosPT  \ud83d\udd25⚠ https://t.co/IcwAGVARi3',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Ponte Da Barca, Sampriz - Mato https://t.co/GrdI5BWlkj #IRPonteDaBarca #FogosPT  \ud83d\udd25⚠ https://t.co/BdI6UoGvld',
    'Vídeos - Incêndio em Ponte da Barca com dois meios aéreos no combate às chamas  https://t.co/HC2I8GaEa3',
    '⚠\ud83d\udd25 Novo incêndio em Braga, Guimarães, Arosa E Castelões - Mato https://t.co/eyzV4sEBYn #IRGuimarães #FogosPT  \ud83d\udd25⚠ https://t.co/GgjbIJyZg3',
    '⚠\ud83d\udd25 Novo incêndio em Braga, Vieira Do Minho, Anjos E Vilar Do Chão - Mato https://t.co/hYu4axbPBZ #IRVieiraDoMinho #FogosPT  \ud83d\udd25⚠ https://t.co/XTGXPhIkiK',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Arcos De Valdevez, Grade E Carralcova - Mato https://t.co/abZgJyZjrH #IRArcosDeValdevez #FogosPT  \ud83d\udd25⚠ https://t.co/I1xmw4uU7q',
    '⚠\ud83d\udd25 Novo incêndio em Lisboa, Mafra, Ericeira - Povoamento Florestal https://t.co/4aPmxAF1i0 #IRMafra #FogosPT  \ud83d\udd25⚠ https://t.co/2lcwUMsaMz',
    '⚠\ud83d\udd25 Novo incêndio em Porto, Vila Nova De Gaia, Sandim, Olival, Lever E Crestuma - Mato https://t.co/EORDTnHG4b #IRVilaNovaDeGaia #FogosPT  \ud83d\udd25⚠ https://t.co/5fDwjO1Thj',
    '⚠\ud83d\udd25 Novo incêndio em Vila Real, Vila Real, Parada De Cunhos - Mato https://t.co/ZLoXCIhDlw #IRVilaReal #FogosPT  \ud83d\udd25⚠ https://t.co/cRGXPG0TZv',
    '⚠\ud83d\udd25 Novo incêndio em Porto, Maia, São Pedro Fins - Mato https://t.co/3VNCSYAJQ9 #IRMaia #FogosPT  \ud83d\udd25⚠ https://t.co/gUs6Dapmr6',
    '⚠\ud83d\udd25 Novo incêndio em Porto, Paredes, Cristelo - Mato https://t.co/761lvVmCJn #IRParedes #FogosPT  \ud83d\udd25⚠ https://t.co/jhoFxtsMBv',
    '⚠\ud83d\udd25 Novo incêndio em Porto, Vila Nova De Gaia, Pedroso E Seixezelo - Mato https://t.co/Q6lSLZXEde #IRVilaNovaDeGaia #FogosPT  \ud83d\udd25⚠ https://t.co/IcwAGVARi3',
    '⚠\ud83d\udd25 Novo incêndio em Porto, Maia, São Pedro Fins - Mato https://t.co/GXckW0acsn #IRMaia #FogosPT  \ud83d\udd25⚠ https://t.co/bIs9Mde7ts',
    '⚠\ud83d\udd25 Novo incêndio em Setúbal, Almada, Laranjeiro E Feijó - Mato https://t.co/tVWazj9HzW #IRAlmada #FogosPT  \ud83d\udd25⚠ https://t.co/D198jvXIlw',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Ponte Da Barca, Sampriz - Mato https://t.co/GrdI5BWlkj #IRPonteDaBarca #FogosPT  \ud83d\udd25⚠ https://t.co/BdI6UoGvld',
    'Vídeos - Incêndio em Ponte da Barca com dois meios aéreos no combate às chamas  https://t.co/HC2I8GaEa3',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Viana Do Castelo, Santa Marta De Portuzelo - Agrícola https://t.co/vz3cuHlkpy #IRVianaDoCastelo #FogosPT  \ud83d\udd25⚠ https://t.co/qAFeA09N6B',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Ponte De Lima, Calheiros - Mato https://t.co/Ur3tFagscC #IRPonteDeLima #FogosPT  \ud83d\udd25⚠ https://t.co/PuEWq0qkio',
    '⚠\ud83d\udd25 Novo incêndio em Viana Do Castelo, Arcos De Valdevez, Grade E Carralcova - Mato https://t.co/abZgJyZjrH #IRArcosDeValdevez #FogosPT  \ud83d\udd25⚠ https://t.co/I1xmw4uU7q',
    '⚠\ud83d\udd25 Novo incêndio em Vila Real, Vila Real, Parada De Cunhos - Mato https://t.co/ZLoXCIhDlw #IRVilaReal #FogosPT  \ud83d\udd25⚠ https://t.co/cRGXPG0TZv'
]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ner = spacy.load("pt_core_news_lg")
for tweet in tweets:
    tweet = tweet.encode("utf-8", "replace").decode()
    geocode = ", ".join(str(ne) for ne in ner(tweet).ents if ne.label_ == "LOC")
    location = requests.get(
        "https://nominatim.openstreetmap.org/search",
        {
            "q": geocode,
            "addressdetails": 1,
            "format": "json",
            "polygon_geojson": 1,
            "limit": 1
        },
    ).json()
    print(geocode, location[0]["display_name"], sep="  ->  ")
