from strategy.pathFinder import findPath, findPath4Fuzzy
from data_structure import gameStatus
from data_structure.gameStatus import *
from karen import *
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl



# karen.fuzzyStrategy chiama inputFuzzy
# creare una funzione fuzzyValues che generi i valori di input per FuzzyControlSystem (calcolando i vari pathfinder verso tutte le possibili destinazioni).
# Dopo aver chiamato la funzione FuzzyControlSystem, aspetta il return sim.output e in base a questo valore sceglie verso dove muoversi.
# a questo punto fuzzyValues restituisce a karen.fuzzystrategy le coordinate scelte.

""" Funzione unica per tutti i Control Systems"""
"""
    RETURN

    d_flag = distanza tra me e la bandiera
    wall_flag_dist = muro più vicino alla bandiera (quanto dista + coordinate)
    wall_me_dist = muro più vicino a me (quanto dista + coordinate)
    num_walls_flag = quanti muri vicini alla bandiera
    num_walls_me = quanti muri vicino a me
    d_flag_barr = barriera più vicina alla bandiera
    num_enemies = quanti nemici vicini
    enemyDistances =
    me.energy = io livello di energia
    nearestRecharge = recharge più vicino a me
    d_SafeZone = zona in cui non sono il linea di tiro
    nearestEnemyDistance = distanza dal nemico più vicino

    """

def fuzzyValues(me, mapSize):
    num_enemies = 0
    num_walls_flag = 0
    num_walls_me = 0
    d_SafeZone = [mapSize, mapSize, mapSize]
    enemyDistances = dict()
    wall_flag_dist = [mapSize, mapSize, mapSize]
    wall_me_dist = [mapSize, mapSize, mapSize]
    nearestRecharge = [mapSize * 2, mapSize, mapSize] # nearestRecharge [distance, xCoordinate, yCoordinate]
    d_flag_barr = [mapSize * 2, mapSize, mapSize] # utile per avanzare dopo i 7 secondi
    nearestEnemyDistance = mapSize


    for k in gameStatus.game.enemies.keys():
        # for each enemy retrieve the min coordinate distance (x or y)
        if gameStatus.game.enemies[k].state == "ACTIVE":
            enemyDistances[gameStatus.game.enemies[k].symbol] = min(
                len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.me.x, gameStatus.game.enemies[k].y)),
                len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.enemies[k].x, gameStatus.game.me.y)))

            # distance from the nearest enemy firing line
            if nearestEnemyDistance > enemyDistances[gameStatus.game.enemies[k].symbol]:
                nearestEnemyDistance = enemyDistances[gameStatus.game.enemies[k].symbol]


    for k in enemyDistances.keys():
        if enemyDistances[k] < int(mapSize / 6):
            num_enemies += 1


    """
    Compute distance flag - nearest wall
    Non solo devo trovare il più vicino ma devo salvare le coordinate

    gameStatus.game.walls[w] identify which wall I'm considering ([wallx, wally])
    gameStatus.game.walls[w][0] is the x coordinate of the wall
    gameStatus.game.walls[w][1] is the y coordinate of the wall
    
    wall_flag_dist[0] corrisponde al minor numero di passi bandiera-muro (ovvero il muro più vicino)
    wall_flag_dist[1] la x del muro
    wall_flag_dist[2] la y del muro
    """
    for w in range(len(gameStatus.game.walls)):
        # print('Muro: ' + str(gameStatus.game.walls[w][0]) + str(gameStatus.game.walls[w][1])) # OK
        # min distance is equal to min steps to reach it

        """ 
        Since I cannot pass the walls' coordinates to findPath function because they're non walkable (i.e. zero value into the weightedMap)
        I check all the sides of the wall to find a walkable cell, tha will be my end direction.
        If no sides are free, it means that this is not the nearest wall.
        """
        wally = gameStatus.game.walls[w][1]
        wallx = gameStatus.game.walls[w][0]
        if (gameStatus.game.weightedMap[wallx - 1][wally] != 0):
            x = wallx - 1
            wall = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY, x, wally))
            # print('Muro x'+str(wall))
            if (wall < wall_flag_dist[0]):
                wall_flag_dist[0] = wall
                wall_flag_dist[1] = x  # todo controllare coordinate x e y
                wall_flag_dist[2] = wally
        # print('posizione' + str(gameStatus.game.weightedMap[wallx][wally]))
        if (gameStatus.game.weightedMap[wallx + 1][wally] != 0):
            x = wallx + 1
            wall = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY, x, wally))
            # print('Muro x'+str(wall))
            if (wall < wall_flag_dist[0]):
                wall_flag_dist[0] = wall
                wall_flag_dist[1] = x  # todo controllare coordinate x e y
                wall_flag_dist[2] = wally
        if (gameStatus.game.weightedMap[wallx][wally - 1] != 0):
            y = wally - 1
            wall = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY, wallx, y))
            # print('Muro y' + str(wall))
            if (wall < wall_flag_dist[0]):
                wall_flag_dist[0] = wall
                wall_flag_dist[1] = wallx  # todo controllare coordinate x e y
                wall_flag_dist[2] = y
        if (gameStatus.game.weightedMap[wallx][wally + 1] != 0):
            y = wally + 1
            wall = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY, wallx, y))
            # print('Muro y' + str(wall))
            if (wall < wall_flag_dist[0]):
                wall_flag_dist[0] = wall
                wall_flag_dist[1] = wallx  # todo controllare coordinate x e y
                wall_flag_dist[2] = y

    # ulteriore controllo: quanti altri muri ci sono intorno al muro più vicino alla bandiera
    # todo: non va bene rifare
    for w in range(len(gameStatus.game.walls)):
        # controllo le x e le y del muro
        if (wall_flag_dist[1] == gameStatus.game.walls[w][0]) | (wall_flag_dist[2] == gameStatus.game.walls[w][1]) : # controllo se muri hanno la stessa ascissa o ordinata
            num_walls_flag += 1
    # print ('Quanti muri:' + str(num_walls_flag))

    """
    Compute distance me - nearest wall
    
    wall_me_dist[0] corrisponde al minor numero di passi tra me e il muro (ovvero il muro più vicino)
    wall_me_dist[1] la x del muro più vicino
    wall_me_dist[2] la y del muro più vicino
    """
    for w in range(len(gameStatus.game.walls)):
        # min distance is equal to min steps to reach it
        wally = gameStatus.game.walls[w][1]
        wallx = gameStatus.game.walls[w][0]
        if (wallx != 0) & (gameStatus.game.weightedMap[wallx - 1][wally] != 0):
            x = wallx - 1
            wall = len(findPath(gameStatus.game.weightedMap,gameStatus.game.me, x, wally))
            #print('Muro x'+str(wall))
            if (wall < wall_me_dist[0]):
                wall_me_dist[0] = wall
                wall_me_dist[1] = x  # todo controllare coordinate x e y
                wall_me_dist[2] = wally
        if (wallx != mapSize) & (gameStatus.game.weightedMap[wallx + 1][wally] != 0) :
            x = wallx + 1
            wall = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, x, wally))
            #print('Muro x'+str(wall))
            if (wall < wall_me_dist[0]):
                wall_me_dist[0] = wall
                wall_me_dist[1] = x  # todo controllare coordinate x e y
                wall_me_dist[2] = wally
        if (wally != 0) & (gameStatus.game.weightedMap[wallx][wally - 1] != 0):
            y = wally - 1
            wall = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, wallx, y))
            #print('Muro y' + str(wall))
            if (wall < wall_me_dist[0]):
                wall_me_dist[0] = wall
                wall_me_dist[1] = wallx  # todo controllare coordinate x e y
                wall_me_dist[2] = y
        if (wally != mapSize) & (gameStatus.game.weightedMap[wallx][wally + 1] != 0):
            y = wally + 1
            wall = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, wallx, y))
            #print('Muro y' + str(wall))
            if (wall < wall_me_dist[0]):
                wall_me_dist[0] = wall
                wall_me_dist[1] = wallx  # todo controllare coordinate x e y
                wall_me_dist[2] = y
        # print('Wall Distance: ' + str(wall_me_dist[0]) +' Coordinates: ' + str(wall_me_dist[1]) + ' '+ str(wall_me_dist[2]))


    # ulteriore controllo: quanti altri muri ci sono intorno al muro più vicino alla bandiera
    # todo: non va bene rifare
    for w in range(len(gameStatus.game.walls)):
        # controllo le x e le y del muro
        if (wall_me_dist[1] == gameStatus.game.walls[w][0]) | (wall_me_dist[2] == gameStatus.game.walls[w][1]) : # controllo se muri hanno la stessa ascissa o ordinata
            num_walls_me += 1

    # print ('Quanti muri:' + str(num_walls_me))

    """
    # trova agglomerati di muri
    h = len(gameStatus.game.weightedMap)
    w = len(gameStatus.game.weightedMap[0])
    top_left = [gameStatus.game.weightedMap[i][:h / 2] for i in range(w / 2)]
    top_right = [gameStatus.game.weightedMap[i][h / 2:] for i in range(w / 2)]
    bot_left = [gameStatus.game.weightedMap[i][:h / 2] for i in range(w / 2, w)]
    bot_right = [gameStatus.game.weightedMap[i][h / 2:] for i in range(w / 2, w)]
    quadrant=[0,0,0,0]
    for i in top_left:
        if i == "#":
            quadrant[0] +=1
    for i in top_right:
        if i == "#":
            quadrant[1] +=1
    for i in bot_left:
        if i == "#":
            quadrant[2] +=1
    for i in bot_right:
        if i == "#":
            quadrant[3] +=1

    # DA FINIRE
    # il quadrante con più muri è la mia fuzzy du default
    # max(quadrant)
    """

    # barriera più vicina alla bandiera
    for i in range(0, len(gameStatus.game.serverMap[0])):
        for j in range(0, len(gameStatus.game.serverMap[0])):
            # print(game.serverMap[i][j])

            """
            Barriers and recharge are walkable objects into the weightedMap, so they do not need the coordinate control on all the 4 sides.
            The end coordinates of the findPath function can be exaclty those of the barrier/recharge.
            """

            # barriera più vicina alla bandiera
            if gameStatus.game.serverMap[i][j] == "&":
                barr = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY, i, j))
                if barr < d_flag_barr[0]:
                    d_flag_barr[0] = barr
                    d_flag_barr[1] = j
                    d_flag_barr[2] = i

            # recharge più vicino alla mia posizione corrente
            if gameStatus.game.serverMap[i][j] == "$":
                tmp = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, i, j))
                if tmp < nearestRecharge[0]:
                    nearestRecharge[0] = tmp
                    nearestRecharge[1] = j
                    nearestRecharge[2] = i

            # non inserisco qui i controlli sui muri perchè sono immmobili quindi ho recuperato le loro coordinate alla prima look


    # distanza tra me e la bandiera
    d_flag = len(findPath(gameStatus.game.weightedMap,gameStatus.game.me, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY))

    # d_SafeZone = 0 means that I'm in a safeZone
    # d_SafeZone = 1 or 2 means that i need to do 1 or 2 movement to be in a safeZone
    if gameStatus.game.weightedMap[me.y][me.x] == 1:
        d_SafeZone[0] = 0
        d_SafeZone[1] = gameStatus.game.me.y
        d_SafeZone[2] = gameStatus.game.me.x
    else:
        if gameStatus.game.weightedMap[me.y - 1][me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x

        elif gameStatus.game.weightedMap[me.y][me.x - 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[me.y][me.x + 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y
            d_SafeZone[2] = gameStatus.game.me.x + 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x

        elif gameStatus.game.weightedMap[me.y - 1][me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[me.y - 1][me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x + 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x + 1

        else:
            d_SafeZone[0] = 3

    return d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, me.energy, d_SafeZone, nearestEnemyDistance

"""
# non modificato, aggiornato da GitHub
def defaultFuzzyControlSystem(me, mapSize):

    # New Antecedent/Consequent objects hold universe variables and membership functions

    energy = ctrl.Antecedent(np.arange(0, 256, 10), 'energy')
    d_flag = ctrl.Antecedent(np.arange(0, int(mapSize * 3), 1), 'd_flag')
    d_recharge = ctrl.Antecedent(np.arange(0, int(mapSize * 3), 1), 'd_recharge')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    # d_barrier = ctrl.Antecedent(np.arange(0, 32, 1), 'd_barrier')
    # d_nearestEnemy = ctrl.Antecedent(np.arange(0, 32, 1), 'd_nearestEnemy')

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToRecharge'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['goToSafePlace'] = fuzz.trimf(output.universe, [10, 20, 20])
    # output['useTheBarrier'] = fuzz.trimf(output.universe, [20, 30, 30])
    output['goToFlag'] = fuzz.trimf(output.universe, [20, 30, 30])
    # output['goToKill'] = fuzz.trimf(output.universe, [40, 50, 50])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    energy.automf(3)
    d_recharge.automf(3)
    # d_barrier.automf(3)
    d_flag.automf(3)
    d_safeZone.automf(3)
    num_enemies.automf(3)

    # poor mediocre average decent good
    needEnergy = ctrl.Rule(((energy['poor']) & (d_flag['average'] | d_flag['good']) & (
            num_enemies['good'] | num_enemies['average']) & d_recharge['poor'])
                           , output['goToRecharge'])

    hide = ctrl.Rule((energy['poor'] & d_safeZone['poor']) |
                     (energy['average'] & (num_enemies['average'] | num_enemies['good']) & d_safeZone['average']) |
                     (d_safeZone['poor'] & (num_enemies['average'] | num_enemies['good']))
                     , output['goToSafePlace'])

    ctf = ctrl.Rule((d_flag['poor']) &
                    ((energy['good'] | energy['average']) & (d_recharge['average'] | d_recharge['good']) & (
                            d_safeZone['average'] | d_safeZone['good'])) |
                    ((energy["good"] | energy["average"]) & num_enemies['poor'])
                    , output['goToFlag'])

    # distinguere concettualmente goToKill dall'azione semplice di uccidere:
    #       - se mi trovo il nemico in tiro allora sparo
    #           --> azione semplice
    #           --> già modellata nella startegia deterministica
    #       - vado di proposito sotto tiro del nemico per sparargli
    #           --> = goToKill
    #           --> decisa dalle fuzzyrules quando si presenta un certo contesto
    #               --> ovvero quando ho energia media/alta, sono distante da tutto il resto
    #               --> todo: quindi prescinde dal numero di nemici vicini ?
    #               --> todo: sarebbe meglio mettere un limite a questa azione! Es. massimo 2 volte poi vado alla bandiera

    # killer = ctrl.Rule((energy['average'] | energy['good'])|
    #                 ((d_flag['good'] & d_barrier['good']) & d_safeZone['good'])
    #              , output['goToKill'])

    # rule visualization example
    # killer.view() # todo: non funziona

    system = ctrl.ControlSystem(rules=[needEnergy, hide, ctf])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)


    # d_flag, wall_flag_dist, num_walls_flag, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, me.energy, d_SafeZone, nearestEnemyDistance
    flagDistance, wall_flag_dist, numberOfWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance = fuzzyValues(me, mapSize)

    # print("Flag Distance " + str(flagDistance))
    # print("numberOfEnemies " + str(numberOfEnemies))
    # print("nearestRecharge " + str(nearestRecharge[0]))
    # print("safeZoneDistance " + str(safeZoneDistance[0]))
    # print("myEnergy " + myEnergy)

    sim.input['energy'] = int(myEnergy)
    sim.input['d_flag'] = flagDistance
    sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

    except:
        # crisp case, go to flag
        print("EXCEPTION FUZZY")
        # print("Flag Distance " + str(flagDistance))
        # print("numberOfEnemies " + str(numberOfEnemies))
        # print("nearestRecharge " + str(nearestRecharge[0]))
        # print("safeZoneDistance " + str(safeZoneDistance[0]))
        # print("myEnergy " + myEnergy)

        outputValue = 25

    if outputValue in range(0, 10):
        # recharge

        x = nearestRecharge[1]
        y = nearestRecharge[2]
        print(me.name + " vado in rech" + str(x) + " " + str(y))

    elif outputValue in range(10, 20):
        # safe

        if safeZoneDistance[0] == 3:
            x = gameStatus.game.wantedFlagX
            y = gameStatus.game.wantedFlagY
        else:
            x = safeZoneDistance[1]
            y = safeZoneDistance[2]
            # print(me.name + " vado in safeZone" + str(x) + " " + str(y))

    else:
        # flag
        x = gameStatus.game.wantedFlagX
        y = gameStatus.game.wantedFlagY
        # print(me.name + " vado alla bandiera " + str(x) + " " + str(y))
    # Check if i will be in safeZone after this movement

    return x, y, nearestEnemyDistance
"""

# PER I PRIMI 7 SECONDI
def FuzzyControlSystem(me, mapSize):


    # New Antecedent/Consequent objects hold universe variables and membership functions

    d_flag = ctrl.Antecedent(np.arange(0, 16, 1), 'd_flag')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    num_walls_flag = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_flag')
    num_walls_me = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_me')
    wall_flag_dist = ctrl.Antecedent(np.arange(0, int(mapSize), 1), 'wall_flag_dist')
    wall_me_dist = ctrl.Antecedent(np.arange(0, int(mapSize), 1), 'wall_me_dist')

    # d_flag_barr = ctrl.Antecedent(np.arange(0, int(mapSize), 1), 'd_flag_barr')
    # d_barrier = ctrl.Antecedent(np.arange(0, int(mapSize), 1), 'd_barrier') # usare barriera nel secondFuzzyCS per avanzare

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToSafePlace'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['hideBehindMyWall'] = fuzz.trimf(output.universe, [10, 20, 20])
    output['hideBehindFlagWall'] = fuzz.trimf(output.universe, [20, 30, 30])
    # output['useTheBarrier'] = fuzz.trimf(output.universe, [20, 30, 30])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    d_flag.automf(3)
    num_enemies.automf(3)
    d_safeZone.automf(3)
    num_walls_flag.automf(3)
    wall_flag_dist.automf(3)
    wall_me_dist.automf(3)
    num_walls_me.automf(3)
    # d_flag_barr.automf(3)
    # d_barrier.automf(3)


    # poor mediocre average decent good

    # 1. mi nascondo dietro al muro più vicino alla bandiera se:
    #    - non sono troppo lontano (max 14 passi per stare safe)
    #    - c'è più di un muro vicino alla bandiera (almeno 2)

    # 2. mi nascondo dietro il muro più vicino a me se:
    #    - la bandiera è troppo lontana
    #    - c'è più di un muro vicino a me (almeno 2)

    # 3. mi sposto in zona sicura solo se:
    #    - le prime due opzioni sono escluse
    #    - sono in pericolo, ovvero ho nemici vicini

    # MIGLIORAMENTI:
    # - controllare muri al bordo della mappa
    # - trovare agglomerati di muri nella mappa




    behindFlagWall = ctrl.Rule((d_flag['poor'] | d_flag['average']) & wall_flag_dist['poor'] & (num_walls_flag['average'] | num_walls_flag['good']) |
                          (d_flag['poor'] | d_flag['average']) & (wall_me_dist['good']) & (num_walls_flag['average'] | num_walls_flag['good'])
                          , output['hideBehindFlagWall'])

    behindMyWall = ctrl.Rule((d_flag['good'] & wall_me_dist['poor'])  |
                            (d_flag['good'] & wall_me_dist['poor'] & num_walls_me['good']) |
                            (d_flag['good'] & num_walls_flag['poor'])
                             , output['hideBehindMyWall'])

    staysafe = ctrl.Rule((num_enemies['average'] | num_enemies['good']) & # ci sono molti nemici
                         (d_safeZone['poor']) & # non sono al sicuro
                         (num_walls_flag['poor'] | num_walls_me['poor']) & # non ci sono agglomerati di muri né vicino a me né vicino alla bandiera
                         (wall_me_dist['good'] | wall_flag_dist['good']) # sono troppo lontano da qualsiasi muro
                         , output['goToSafePlace'])


    # barrier = ctrl.Rule( d_flag_barr['poor'] , output['useTheBarrier'])


    system = ctrl.ControlSystem(rules=[behindFlagWall, behindMyWall, staysafe])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    # d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, me.energy, d_SafeZone, nearestEnemyDistance
    flagDistance, flagWallDist, meWallDist, numOfFlagWalls, numOfMeWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance = fuzzyValues(me, mapSize)

    # print("Flag Distance " + str(flagDistance))
    # print("numberOfEnemies " + str(numberOfEnemies))
    # print("nearestRecharge " + str(nearestRecharge[0]))
    # print("safeZoneDistance " + str(safeZoneDistance[0]))
    # print("myEnergy " + myEnergy)


    # sim.input['energy'] = int(myEnergy)
    sim.input['d_flag'] = flagDistance
    sim.input['num_walls_flag'] = numOfFlagWalls
    sim.input['num_walls_me'] = numOfMeWalls
    sim.input['wall_flag_dist'] = flagWallDist[0]
    sim.input['wall_me_dist'] = meWallDist[0]
    # sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

        # output.view(sim=sim)

    except:
        # crisp case, go to flag
        print("EXCEPTION FUZZY")
        # print("Flag Distance " + str(flagDistance))
        # print("numberOfEnemies " + str(numberOfEnemies))
        # print("nearestRecharge " + str(nearestRecharge[0]))
        # print("safeZoneDistance " + str(safeZoneDistance[0]))
        # print("myEnergy " + myEnergy)

        outputValue = 15 # default: mi nascondo dietro al muro più vicino al mio



    if outputValue in range(0, 10):
        # safe

        if safeZoneDistance[0] == 3:
            x = gameStatus.game.wantedFlagX
            y = gameStatus.game.wantedFlagY
        else:
            x = safeZoneDistance[1]
            y = safeZoneDistance[2]

        print(me.name + " vado in safeZone: " + str(x) + " " + str(y))


    elif outputValue in range(20, 30):

        x = flagWallDist[2]
        y = flagWallDist[1]

        print(me.name + " vado al muro più vicino alla bandiera: " + str(x) + " " + str(y))

    else:

        x = meWallDist[2]
        y = meWallDist[1]

        print(me.name + " vado al muro più vicino a me: " + str(x) + " " + str(y))


    return x, y, nearestEnemyDistance


# nuovo per l'impostor DA AGGIORNARE
def FuzzyControlSystemImpostor(me, mapSize): # nuovo
    """
    Output values:
    -goToRecharge,  0-10
    -goToSafePlace 10-20
    -useTheBarrier 20-30
    -goToFlag, 30-40
    -goToKill, 40-50
    """

    # New Antecedent/Consequent objects hold universe variables and membership functions

    energy = ctrl.Antecedent(np.arange(0, 256, 10), 'energy')
    d_flag = ctrl.Antecedent(np.arange(0, int(mapSize * 3), 1), 'd_flag')
    d_recharge = ctrl.Antecedent(np.arange(0, int(mapSize * 3), 1), 'd_recharge')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    # d_barrier = ctrl.Antecedent(np.arange(0, 32, 1), 'd_barrier')
    # d_nearestEnemy = ctrl.Antecedent(np.arange(0, 32, 1), 'd_nearestEnemy')

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToRecharge'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['goToSafePlace'] = fuzz.trimf(output.universe, [10, 20, 20])
    # output['useTheBarrier'] = fuzz.trimf(output.universe, [20, 30, 30])
    output['goToFlag'] = fuzz.trimf(output.universe, [20, 30, 30])
    # output['goToKill'] = fuzz.trimf(output.universe, [40, 50, 50])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    energy.automf(3)
    d_recharge.automf(3)
    # d_barrier.automf(3)
    d_flag.automf(3)
    d_safeZone.automf(3)
    num_enemies.automf(3)

    # poor mediocre average decent good
    needEnergy = ctrl.Rule(((energy['poor']) & (d_flag['average'] | d_flag['good']) & (
            num_enemies['good'] | num_enemies['average']) & d_recharge['poor'])
                           , output['goToRecharge'])

    hide = ctrl.Rule((energy['poor'] & d_safeZone['poor']) |
                     (energy['average'] & (num_enemies['average'] | num_enemies['good']) & d_safeZone['average']) |
                     (d_safeZone['poor'] & (num_enemies['average'] | num_enemies['good']))
                     , output['goToSafePlace'])

    ctf = ctrl.Rule((d_flag['poor']) &
                    ((energy['good'] | energy['average']) & (d_recharge['average'] | d_recharge['good']) & (
                            d_safeZone['average'] | d_safeZone['good'])) |
                    ((energy["good"] | energy["average"]) & num_enemies['poor'])
                    , output['goToFlag'])

    # distinguere concettualmente goToKill dall'azione semplice di uccidere:
    #       - se mi trovo il nemico in tiro allora sparo
    #           --> azione semplice
    #           --> già modellata nella startegia deterministica
    #       - vado di proposito sotto tiro del nemico per sparargli
    #           --> = goToKill
    #           --> decisa dalle fuzzyrules quando si presenta un certo contesto
    #               --> ovvero quando ho energia media/alta, sono distante da tutto il resto
    #               --> todo: quindi prescinde dal numero di nemici vicini ?
    #               --> todo: sarebbe meglio mettere un limite a questa azione! Es. massimo 2 volte poi vado alla bandiera

    # killer = ctrl.Rule((energy['average'] | energy['good'])|
    #                 ((d_flag['good'] & d_barrier['good']) & d_safeZone['good'])
    #              , output['goToKill'])

    # rule visualization example
    # killer.view() # todo: non funziona

    system = ctrl.ControlSystem(rules=[needEnergy, hide, ctf])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    flagDistance, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance = fuzzyValues(me,  mapSize)

    # print("Flag Distance " + str(flagDistance))
    # print("numberOfEnemies " + str(numberOfEnemies))
    # print("nearestRecharge " + str(nearestRecharge[0]))
    # print("safeZoneDistance " + str(safeZoneDistance[0]))
    # print("myEnergy " + myEnergy)

    sim.input['energy'] = int(myEnergy)
    sim.input['d_flag'] = flagDistance
    sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

    except:
        # crisp case, go to flag
        print("EXCEPTION FUZZY")
        # print("Flag Distance " + str(flagDistance))
        # print("numberOfEnemies " + str(numberOfEnemies))
        # print("nearestRecharge " + str(nearestRecharge[0]))
        # print("safeZoneDistance " + str(safeZoneDistance[0]))
        # print("myEnergy " + myEnergy)

        outputValue = 25

    if outputValue in range(0, 10):
        # recharge

        x = nearestRecharge[1]
        y = nearestRecharge[2]
        print(me.name + " vado in rech" + str(x) + " " + str(y))

    elif outputValue in range(10, 20):
        # safe

        if safeZoneDistance[0] == 3:
            x = gameStatus.game.wantedFlagX
            y = gameStatus.game.wantedFlagY
        else:
            x = safeZoneDistance[1]
            y = safeZoneDistance[2]
            # print(me.name + " vado in safeZone" + str(x) + " " + str(y))

    else:
        # flag
        x = gameStatus.game.wantedFlagX
        y = gameStatus.game.wantedFlagY
        # print(me.name + " vado alla bandiera " + str(x) + " " + str(y))
    # Check if i will be in safeZone after this movement

    return x, y, nearestEnemyDistance
