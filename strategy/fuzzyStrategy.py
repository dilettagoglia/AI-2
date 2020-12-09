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


def fuzzyValues(maxWeight):
    num_enemies = 0
    num_allies = len(gameStatus.game.allies)
    # print('Number of allies' + str(num_allies)) # ok
    num_walls_flag = 0
    num_walls_me = 0
    d_SafeZone = [maxWeight, maxWeight, maxWeight]
    enemyDistances = dict()
    allies = [maxWeight, maxWeight, maxWeight]
    wall_flag_dist = [maxWeight, maxWeight, maxWeight]
    wall_me_dist = [maxWeight, maxWeight, maxWeight]
    nearestRecharge = [maxWeight * 2, maxWeight, maxWeight]  # nearestRecharge [distance, xCoordinate, yCoordinate]
    d_flag_barr = [maxWeight * 2, maxWeight, maxWeight]  # utile per avanzare dopo i 7 secondi
    nearestEnemyDistance = [maxWeight, maxWeight, maxWeight]
    myenergy = gameStatus.game.me.energy

    for k in gameStatus.game.enemies.keys():
        # for each enemy retrieve the min coordinate distance (x or y)
        if gameStatus.game.enemies[k].state == "ACTIVE":
            enemyDistances[gameStatus.game.enemies[k].symbol] = min(
                len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.me.x,
                             gameStatus.game.enemies[k].y)),
                len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.enemies[k].x,
                             gameStatus.game.me.y)))

            # distance from the nearest enemy firing line
            if nearestEnemyDistance[0] > enemyDistances[gameStatus.game.enemies[k].symbol]:
                nearestEnemyDistance[0] = enemyDistances[gameStatus.game.enemies[k].symbol]
                nearestEnemyDistance[1] = gameStatus.game.enemies[k].x
                nearestEnemyDistance[2] = gameStatus.game.enemies[k].y

    for k in enemyDistances.keys():
        if enemyDistances[k] < int(maxWeight / 6):
            num_enemies += 1

    for k in gameStatus.game.allies.keys():
        if gameStatus.game.allies[k].state == "ACTIVE":
            all = min(len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.me.x,
                                   gameStatus.game.allies[k].y)),
                      len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.allies[k].x,
                                   gameStatus.game.me.y)))
            if all < allies[0]:
                allies[0] = all
                allies[1] = gameStatus.game.allies[k].x  # todo controllare correttezza coordinate x e y
                allies[2] = gameStatus.game.allies[k].y
        else:
            num_allies -= 1
    # print('Allies' + str(allies)) # ok

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

        # controllo che il nemico è alla mia destra o alla mia sinistra. In stage 0 sicuramente il mio nemico è opposto rispetto alla mia fazione
        # print("nearestEnemyD: " + str(nearestEnemyDistance[0]))
        if gameStatus.game.me.x < int(nearestEnemyDistance[1]):
            # if gameStatus.game.me.x <= int(gameStatus.game.mapWidth/2):
            if (wallx > 0) and (gameStatus.game.weightedMap[wally][wallx - 1] != 0):
                x = wallx - 1
                wall = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, x, wally))
                # print('Muro x'+str(wall))
                if wall < wall_me_dist[0] and wall != 0:
                    wall_me_dist[0] = wall
                    wall_me_dist[1] = x
                    wall_me_dist[2] = wally
        else:
            try:
                if (wallx < gameStatus.game.mapWidth - 1) and (gameStatus.game.weightedMap[wally][wallx + 1] != 0):
                    x = wallx + 1
                    wall = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, x, wally))

                    # print('Muro x'+str(wall))
                    if wall < wall_me_dist[0] and wall != 0:
                        wall_me_dist[0] = wall
                        wall_me_dist[1] = x
                        wall_me_dist[2] = wally
            except:

                print("EXCEPTION X " + str(wallx) + " Y " + str(wally))

    # todo: non va bene rifare
    for w in range(len(gameStatus.game.walls)):
        # controllo le x e le y del muro
        if (wall_me_dist[1] == gameStatus.game.walls[w][0]) | (
                wall_me_dist[2] == gameStatus.game.walls[w][1]):  # controllo se muri hanno la stessa ascissa o ordinata
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
            

            # barriera più vicina alla bandiera
            if gameStatus.game.serverMap[i][j] == "&":
                barr = len(findPath4Fuzzy(gameStatus.game.weightedMap, gameStatus.game.wantedFlagX,
                                          gameStatus.game.wantedFlagY, i, j))
                if barr < d_flag_barr[0]:
                    d_flag_barr[0] = barr
                    d_flag_barr[1] = j
                    d_flag_barr[2] = i
            """
            # recharge più vicino alla mia posizione corrente
            if gameStatus.game.serverMap[i][j] == "$":
                tmp = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, i, j))
                if tmp < nearestRecharge[0]:
                    nearestRecharge[0] = tmp
                    nearestRecharge[1] = j
                    nearestRecharge[2] = i

            # non inserisco qui i controlli sui muri perchè sono immmobili quindi ho recuperato le loro coordinate alla prima look

    # distanza tra me e la bandiera
    d_flag = len(findPath(gameStatus.game.weightedMap, gameStatus.game.me, gameStatus.game.wantedFlagX,
                          gameStatus.game.wantedFlagY))

    # d_SafeZone = 0 means that I'm in a safeZone
    # d_SafeZone = 1 or 2 means that i need to do 1 or 2 movement to be in a safeZone
    if gameStatus.game.weightedMap[gameStatus.game.me.y][gameStatus.game.me.x] == 1:
        d_SafeZone[0] = 0
        d_SafeZone[1] = gameStatus.game.me.y
        d_SafeZone[2] = gameStatus.game.me.x
    else:
        if gameStatus.game.weightedMap[gameStatus.game.me.y - 1][gameStatus.game.me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x

        elif gameStatus.game.weightedMap[gameStatus.game.me.y][gameStatus.game.me.x - 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[gameStatus.game.me.y][gameStatus.game.me.x + 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y
            d_SafeZone[2] = gameStatus.game.me.x + 1

        elif gameStatus.game.weightedMap[gameStatus.game.me.y + 1][gameStatus.game.me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x

        elif gameStatus.game.weightedMap[gameStatus.game.me.y - 1][gameStatus.game.me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[gameStatus.game.me.y - 1][gameStatus.game.me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y - 1
            d_SafeZone[2] = gameStatus.game.me.x + 1

        elif gameStatus.game.weightedMap[gameStatus.game.me.y + 1][gameStatus.game.me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x - 1

        elif gameStatus.game.weightedMap[gameStatus.game.me.y + 1][gameStatus.game.me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = gameStatus.game.me.y + 1
            d_SafeZone[2] = gameStatus.game.me.x + 1

        else:
            d_SafeZone[0] = 3

    return d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, myenergy, d_SafeZone, nearestEnemyDistance, num_allies, allies


def FuzzyControlSystemStage0(maxWeight):
    # New Antecedent/Consequent objects hold universe variables and membership functions

    d_flag = ctrl.Antecedent(np.arange(0, 16, 1), 'd_flag')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    num_walls_flag = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_flag')
    num_walls_me = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_me')
    wall_flag_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_flag_dist')
    wall_me_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_me_dist')

    # d_flag_barr = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_flag_barr')
    # d_barrier = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_barrier') # usare barriera nel secondFuzzyCS per avanzare

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

    """
    
    1. mi nascondo dietro al muro più vicino alla bandiera se:
    - non sono troppo lontano (max 14 passi per stare safe)
    - c'è più di un muro vicino alla bandiera (almeno 2)

    2. mi nascondo dietro il muro più vicino a me se:
    - la bandiera è troppo lontana
    - c'è più di un muro vicino a me (almeno 2)

    3. mi sposto in zona sicura solo se:
    - le prime due opzioni sono escluse
    - sono in pericolo, ovvero ho nemici vicini

    MIGLIORAMENTI:
    - controllare muri al bordo della mappa
    - trovare agglomerati di muri nella mappa
    
    """

    behindFlagWall = ctrl.Rule((d_flag['poor'] | d_flag['average']) & wall_flag_dist['poor'] & (
            num_walls_flag['average'] | num_walls_flag['good']) |
                               (d_flag['poor'] | d_flag['average']) & (wall_me_dist['good']) & (
                                       num_walls_flag['average'] | num_walls_flag['good'])
                               , output['hideBehindFlagWall'])

    behindMyWall = ctrl.Rule((d_flag['good'] & wall_me_dist['poor']) |
                             (d_flag['good'] & wall_me_dist['poor'] & num_walls_me['good']) |
                             (d_flag['good'] & num_walls_flag['poor'])
                             , output['hideBehindMyWall'])

    staysafe = ctrl.Rule((num_enemies['average'] | num_enemies['good']) &  # ci sono molti nemici
                         (d_safeZone['poor']) &  # non sono al sicuro
                         (num_walls_flag['poor'] | num_walls_me[
                             'poor']) &  # non ci sono agglomerati di muri né vicino a me né vicino alla bandiera
                         (wall_me_dist['good'] | wall_flag_dist['good'])  # sono troppo lontano da qualsiasi muro
                         , output['goToSafePlace'])

    # barrier = ctrl.Rule( d_flag_barr['poor'] , output['useTheBarrier'])

    system = ctrl.ControlSystem(rules=[behindFlagWall, behindMyWall, staysafe])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    # d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, myenergy, d_SafeZone, nearestEnemyDistance
    flagDistance, flagWallDist, meWallDist, numOfFlagWalls, numOfMeWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance, numberOfAllies, allies = fuzzyValues(
        maxWeight)

    sim.input['d_flag'] = flagDistance
    sim.input['num_walls_flag'] = numOfFlagWalls
    sim.input['num_walls_me'] = numOfMeWalls
    sim.input['wall_flag_dist'] = flagWallDist[0]
    sim.input['wall_me_dist'] = meWallDist[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

        # output.view(sim=sim)

    except:
        # crisp case: mi nascondo dietro al muro più vicino a me
        print("EXCEPTION FUZZY")

        outputValue = 15

    if outputValue in range(0, 10):

        x = safeZoneDistance[1]
        y = safeZoneDistance[2]

        # print(gameStatus.game.me.name + " vado in safeZone: " + str(x) + " " + str(y))


    elif outputValue in range(20, 30):

        x = flagWallDist[1]
        y = flagWallDist[2]

        # print(gameStatus.game.me.name + " vado al muro più vicino alla bandiera: " + str(x) + " " + str(y))

    else:

        x = meWallDist[1]
        y = meWallDist[2]

        # print(gameStatus.game.me.name + " vado al muro più vicino a me: " + str(x) + " " + str(y))

    if x == maxWeight and y == maxWeight:
        x = safeZoneDistance[1]
        y = safeZoneDistance[2]

    return x, y, nearestEnemyDistance[0]


def FuzzyControlSystemStage1(maxWeight):
    # New Antecedent/Consequent objects hold universe variables and membership functions

    d_flag = ctrl.Antecedent(np.arange(0, 16, 1), 'd_flag')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    num_walls_flag = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_flag')
    num_walls_me = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_me')
    wall_flag_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_flag_dist')
    wall_me_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_me_dist')
    energy = ctrl.Antecedent(np.arange(0, 256, 10), 'energy')
    d_recharge = ctrl.Antecedent(np.arange(0, int(maxWeight * 3), 1), 'd_recharge')

    # d_flag_barr = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_flag_barr')
    # d_barrier = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_barrier') # usare barriera nel secondFuzzyCS per avanzare

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToSafePlace'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['hideBehindMyWall'] = fuzz.trimf(output.universe, [10, 20, 20])
    output['hideBehindFlagWall'] = fuzz.trimf(output.universe, [20, 30, 30])
    output['goToKill'] = fuzz.trimf(output.universe, [30, 40, 40])
    output['goToFlag'] = fuzz.trimf(output.universe, [40, 50, 50])
    output['goToRecharge'] = fuzz.trimf(output.universe, [50, 60, 60])

    # output['useTheBarrier'] = fuzz.trimf(output.universe, [20, 30, 30])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    d_flag.automf(3)
    num_enemies.automf(3)
    d_safeZone.automf(3)
    num_walls_flag.automf(3)
    wall_flag_dist.automf(3)
    wall_me_dist.automf(3)
    num_walls_me.automf(3)
    energy.automf(3)
    d_recharge.automf(3)

    # d_flag_barr.automf(3)
    # d_barrier.automf(3)

    # poor mediocre average decent good

    behindFlagWall = ctrl.Rule((d_flag['poor'] | d_flag['average']) & wall_flag_dist['poor'] & (
            num_walls_flag['average'] | num_walls_flag['good'])
                               , output['hideBehindFlagWall'])

    behindMyWall = ctrl.Rule((d_flag['good'] & (num_enemies['good'] | num_enemies['average']) & wall_me_dist['poor'] & num_walls_me['good']), output['hideBehindMyWall'])

    staysafe = ctrl.Rule((num_enemies['average'] | num_enemies['good']) &  # ci sono molti nemici
                         (d_safeZone['good']) &  # non sono al sicuro
                         (num_walls_flag['poor'] | num_walls_me[
                             'poor']) &  # non ci sono agglomerati di muri né vicino a me né vicino alla bandiera
                         (wall_me_dist['good'] | wall_flag_dist['good'])  # sono troppo lontano da qualsiasi muro
                         , output['goToSafePlace'])

    needEnergy = ctrl.Rule(((energy['poor'] | energy['average']) & d_recharge['poor']) |
                           (energy['poor'] | d_recharge['poor']) |
                           ((energy['poor'] | energy['average']) & d_recharge['poor'] & num_enemies['good'])
                           , output['goToRecharge'])

    goToKill = ctrl.Rule((num_enemies['poor'] | num_enemies['average']) & (energy["average"] | energy["good"]) & d_flag['good'],
                            output['goToKill'])
    goToFlag = ctrl.Rule(d_flag['poor'] |
                        ((d_safeZone['poor'] | d_safeZone['average']) & (d_flag['poor'] | d_flag['average']) & energy['good'] &
                        num_enemies['poor']), output["goToFlag"])

    # barrier = ctrl.Rule( d_flag_barr['poor'] , output['useTheBarrier'])

    system = ctrl.ControlSystem(rules=[behindFlagWall, behindMyWall, staysafe, needEnergy, goToKill, goToFlag])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    # d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, myenergy, d_SafeZone, nearestEnemyDistance
    flagDistance, flagWallDist, meWallDist, numOfFlagWalls, numOfMeWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance, numberOfAllies, allies = fuzzyValues(
        maxWeight)

    sim.input['d_flag'] = flagDistance
    sim.input['num_walls_flag'] = numOfFlagWalls
    sim.input['num_walls_me'] = numOfMeWalls
    sim.input['wall_flag_dist'] = flagWallDist[0]
    sim.input['wall_me_dist'] = meWallDist[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['energy'] = int(myEnergy)

    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

        # output.view(sim=sim)

    except:
        # crisp case: mi nascondo dietro al muro più vicino a me
        print("EXCEPTION FUZZY")

        outputValue = 15

    if outputValue in range(0, 10):

        x = safeZoneDistance[1]
        y = safeZoneDistance[2]

        print(gameStatus.game.me.name + " vado in safeZone: " + str(x) + " " + str(y))

    elif outputValue in range(10, 20):

        x = meWallDist[1]
        y = meWallDist[2]

        print(gameStatus.game.me.name + " vado al muro più vicino a me: " + str(x) + " " + str(y))


    elif outputValue in range(20, 30):

        x = flagWallDist[1]
        y = flagWallDist[2]

        print(gameStatus.game.me.name + " vado al muro più vicino alla bandiera: " + str(x) + " " + str(y))

    elif outputValue in range(30, 40):

        x = nearestEnemyDistance[1]
        y = nearestEnemyDistance[2]

        print(gameStatus.game.me.name + " vado ad ammazzare: " + str(x) + " " + str(y))

    elif outputValue in range(40, 50):

        x = gameStatus.game.wantedFlagX
        y = gameStatus.game.wantedFlagY

        print(gameStatus.game.me.name + " vado alla bandiera: " + str(x) + " " + str(y))

    else:
        x = nearestRecharge[1]
        y = nearestRecharge[2]
        print(gameStatus.game.me.name + " vado a ricaricarmi: " + str(x) + " " + str(y))

    if x == maxWeight and y == maxWeight:
        x = safeZoneDistance[1]
        y = safeZoneDistance[2]
        print(gameStatus.game.me.name + " vado in safe zone: " + str(x) + " " + str(y))

    return x, y, nearestEnemyDistance[0]


def FuzzyControlSystemStage2(maxWeight):
    # New Antecedent/Consequent objects hold universe variables and membership functions

    d_flag = ctrl.Antecedent(np.arange(0, 16, 1), 'd_flag')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')
    num_walls_flag = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_flag')
    num_walls_me = ctrl.Antecedent(np.arange(0, len(gameStatus.game.walls), 1), 'num_walls_me')
    wall_flag_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_flag_dist')
    wall_me_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'wall_me_dist')
    energy = ctrl.Antecedent(np.arange(0, 256, 10), 'energy')
    d_recharge = ctrl.Antecedent(np.arange(0, int(maxWeight * 3), 1), 'd_recharge')

    # d_flag_barr = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_flag_barr')
    # d_barrier = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'd_barrier') # usare barriera nel secondFuzzyCS per avanzare

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToSafePlace'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['hideBehindMyWall'] = fuzz.trimf(output.universe, [10, 20, 20])
    output['hideBehindFlagWall'] = fuzz.trimf(output.universe, [20, 30, 30])
    output['goToKill'] = fuzz.trimf(output.universe, [30, 40, 40])
    output['goToFlag'] = fuzz.trimf(output.universe, [40, 50, 50])
    output['goToRecharge'] = fuzz.trimf(output.universe, [50, 60, 60])

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
    energy.automf(3)
    d_recharge.automf(3)
    # poor mediocre average decent good

    behindFlagWall = ctrl.Rule((d_flag['poor'] | d_flag['average']) & wall_flag_dist['poor'] & (num_walls_flag['average'] | num_walls_flag['good'])
                               , output['hideBehindFlagWall'])

    behindMyWall = ctrl.Rule((d_flag['good'] & (num_enemies['good'] | num_enemies['average']) & wall_me_dist['poor'] & num_walls_me['good'] & num_walls_flag['poor']), output['hideBehindMyWall'])

    staysafe = ctrl.Rule((num_enemies['average'] | num_enemies['good']) &  # ci sono molti nemici
                         (d_safeZone['good']) &  # non sono al sicuro
                         (num_walls_flag['poor'] | num_walls_me['poor']) &  # non ci sono agglomerati di muri né vicino a me né vicino alla bandiera
                         (wall_me_dist['good'] | wall_flag_dist['good'])  # sono troppo lontano da qualsiasi muro
                         , output['goToSafePlace'])

    needEnergy = ctrl.Rule(((energy['poor'] | energy['average']) & d_recharge['poor']) |
                           (energy['poor'] | d_recharge['poor']) |
                           ((energy['poor'] | energy['average']) & d_recharge['poor'] & num_enemies['good'])
                           , output['goToRecharge'])

    goToKill = ctrl.Rule((num_enemies['poor'] | num_enemies['average']) & (energy["average"] | energy["good"]),
                         output['goToKill'])
    goToFlag = ctrl.Rule(d_flag['poor'] |
                         ((d_safeZone['poor'] | d_safeZone['average']) & (d_flag['poor'] | d_flag['average']) & energy[
                             'good']), output["goToFlag"])

    # barrier = ctrl.Rule( d_flag_barr['poor'] , output['useTheBarrier'])

    system = ctrl.ControlSystem(rules=[behindFlagWall, behindMyWall, staysafe, needEnergy, goToKill, goToFlag])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    # d_flag, wall_flag_dist, wall_me_dist, num_walls_flag, num_walls_me, d_flag_barr, num_enemies, enemyDistances, nearestRecharge, myenergy, d_SafeZone, nearestEnemyDistance
    flagDistance, flagWallDist, meWallDist, numOfFlagWalls, numOfMeWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance, numberOfAllies, allies = fuzzyValues(
        maxWeight)

    sim.input['d_flag'] = flagDistance
    sim.input['num_walls_flag'] = numOfFlagWalls
    sim.input['num_walls_me'] = numOfMeWalls
    sim.input['wall_flag_dist'] = flagWallDist[0]
    sim.input['wall_me_dist'] = meWallDist[0]
    sim.input['num_enemies'] = numberOfEnemies
    sim.input['d_safeZone'] = safeZoneDistance[0]
    sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['energy'] = int(myEnergy)

    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")

        # output.view(sim=sim)

    except:
        # crisp case: go to flag
        print("EXCEPTION FUZZY")

        outputValue = 45

    if outputValue in range(0, 10):

        x = safeZoneDistance[1]
        y = safeZoneDistance[2]

        print(gameStatus.game.me.name + " vado in safeZone: " + str(x) + " " + str(y))

    elif outputValue in range(10, 20):

        x = meWallDist[1]
        y = meWallDist[2]

        print(gameStatus.game.me.name + " vado al muro più vicino a me: " + str(x) + " " + str(y))


    elif outputValue in range(20, 30):

        x = flagWallDist[1]

        y = flagWallDist[2]

        print(gameStatus.game.me.name + " vado al muro più vicino alla bandiera: " + str(x) + " " + str(y))

    elif outputValue in range(30, 40):

        x = nearestEnemyDistance[1]
        y = nearestEnemyDistance[2]

        print(gameStatus.game.me.name + " vado ad ammazzare: " + str(x) + " " + str(y))

    elif outputValue in range(40, 50):

        x = gameStatus.game.wantedFlagX
        y = gameStatus.game.wantedFlagY

        print(gameStatus.game.me.name + " vado alla bandiera: " + str(x) + " " + str(y))

    else:

        x = nearestRecharge[1]
        y = nearestRecharge[2]

        print(gameStatus.game.me.name + " vado a ricaricarmi : " + str(x) + " " + str(y))

    if x == maxWeight and y == maxWeight:
        x = gameStatus.game.wantedFlagX
        y = gameStatus.game.wantedFlagY

        print(gameStatus.game.me.name + " vado alla bandiera: " + str(x) + " " + str(y))

    return x, y, nearestEnemyDistance[0]



def FuzzyControlSystemImpostor(maxWeight):  # nuovo
    """
    - Finchè sono in vita piu di un terzo degli alleati --> stai in difesa o comunque nasconditi o muoviti evitando i nemici.
    - Quando ci sono meno di un terzo degli alleati o stanno rubando la flag --> endx endy saranno le coordinate degli alleati --> kill them

    - num_allies
    - allies (coordinates)
    - safeZone

    Output
    - staySafe
    - goToKill

    """

    # New Antecedent/Consequent objects hold universe variables and membership functions

    energy = ctrl.Antecedent(np.arange(0, 256), 'energy')
    num_enemies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.enemies), 1), 'num_enemies')
    d_recharge = ctrl.Antecedent(np.arange(0, int(maxWeight * 3), 1), 'd_recharge')
    num_allies = ctrl.Antecedent(np.arange(0, len(gameStatus.game.allies), 1), 'num_allies')  # how many
    allies_dist = ctrl.Antecedent(np.arange(0, int(maxWeight), 1), 'allies')  # coordinates
    # d_safeZone = ctrl.Antecedent(np.arange(0, 3, 1), 'd_safeZone')

    output = ctrl.Consequent(np.arange(0, 30, 1), 'output')

    output['goToRecharge'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['goToSafePlace'] = fuzz.trimf(output.universe, [10, 20, 20])
    output['goToKill'] = fuzz.trimf(output.universe, [20, 30, 30])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    energy.automf(3)
    d_recharge.automf(3)
    # d_safeZone.automf(3)
    num_allies.automf(3)
    allies_dist.automf(3)
    num_enemies.automf(3)

    """
    1. vado a ricaricarmi se:
        - ho energia bassa/media
        - la ricarica è molto vicina
        - ci sono molti nemici 
    2. resto in zona sicura se:
        - sono in vita più di un terzo degli allies | ho gli enemies vicini 
    3. vado ad uccidere se
        - sono vivi un terzo degli alleati o meno | il gioco è allo stage 2
    """

    # poor mediocre average decent good

    # todo modellare le rules
    needEnergy = ctrl.Rule(((energy['poor'] | energy['average']) & d_recharge['poor']) |
                           (energy['poor'] | d_recharge['poor']) |
                           ((energy['poor'] | energy['average']) & d_recharge['poor'] & num_enemies['good'])
                           , output['goToRecharge'])

    staySafe = ctrl.Rule((num_allies['average'] | num_allies['good']) |
                         (num_enemies['average'] | num_enemies['good'])
                         , output['goToSafePlace'])

    kill = ctrl.Rule(((allies_dist['poor'] | allies_dist['average'] | allies_dist['good']) & (num_allies['poor'])),
                     output['goToKill'])

    system = ctrl.ControlSystem(rules=[needEnergy, staySafe, kill])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

    flagDistance, flagWallDist, meWallDist, numOfFlagWalls, numOfMeWalls, flagBarrDist, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance, numberOfAllies, allies = fuzzyValues(
        maxWeight)

    sim.input['energy'] = int(myEnergy)
    sim.input['d_recharge'] = nearestRecharge[0]
    sim.input['num_allies'] = numberOfAllies
    sim.input['allies'] = allies[0]
    sim.input['num_enemies'] = numberOfEnemies
    # sim.input['d_barrier'] = 32

    # Crunch the numbers
    try:
        sim.compute()
        outputValue = sim.output.get("output")
        output.view(sim=sim)

    except:
        # crisp case, stay safe
        print("EXCEPTION FUZZY")
        outputValue = 15

    if outputValue in range(0, 10):
        # recharge

        if nearestRecharge[0] != maxWeight:
            x = nearestRecharge[1]
            y = nearestRecharge[2]
        else:
            x = safeZoneDistance[1]
            y = safeZoneDistance[2]

        print("IMPOSTOR : " + gameStatus.game.me.name + " vado in rech" + str(x) + " " + str(y))

    elif outputValue in range(10, 20):
        # safe

        x = safeZoneDistance[1]
        y = safeZoneDistance[2]
        print("IMPOSTOR : " + gameStatus.game.me.name + " vado in safeZone" + str(x) + " " + str(y))

    else:
        # kill
        x = allies[1]
        y = allies[2]
        print("IMPOSTOR : " + gameStatus.game.me.name + " vado ad uccidere " + str(x) + " " + str(y))
    # Check if i will be in safeZone after this movement

    if x == maxWeight and y == maxWeight:
        x = safeZoneDistance[1]
        y = safeZoneDistance[2]
    return x, y, nearestEnemyDistance[0]
