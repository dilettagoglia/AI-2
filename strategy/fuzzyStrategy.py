from data_structure import gameStatus
from data_structure.gameStatus import *
from strategy.pathFinder import findPath
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# karen.fuzzyStrategy chiama inputFuzzy
# creare una funzione fuzzyValues che generi i valori di input per FuzzyControlSystem (calcolando i vari pathfinder verso tutte le possibili destinazioni).
# Dopo aver chiamato la funzione FuzzyControlSystem, aspetta il return sim.output e in base a questo valore sceglie verso dove muoversi.
# a questo punto fuzzyValues restituisce a karen.fuzzystrategy le coordinate scelte.


def fuzzyValues(me, mapSize):
    num_enemies = 0
    d_SafeZone = [mapSize, mapSize, mapSize]

    enemyDistances = dict()

    nearestEnemyDistance = mapSize
    # nearestRecharge [distance, xCoordinate, yCoordinate]
    nearestRecharge = [mapSize * 2, mapSize, mapSize]
    for k in gameStatus.game.enemies.keys():
        # for each enemy retrieve the min coordinate distance (x or y)
        if gameStatus.game.enemies[k].state == "ACTIVE":
            enemyDistances[gameStatus.game.enemies[k].symbol] = min(len(findPath(gameStatus.game.weightedMap, me, me.x, gameStatus.game.enemies[k].y)),
                                                         len(findPath(gameStatus.game.weightedMap, me, gameStatus.game.enemies[k].x, me.y)))

            # distance from the nearest enemy firing line
            if nearestEnemyDistance > enemyDistances[gameStatus.game.enemies[k].symbol]:
                nearestEnemyDistance = enemyDistances[gameStatus.game.enemies[k].symbol]

    for k in enemyDistances.keys():
        if enemyDistances[k] < int(mapSize / 6):
            num_enemies += 1

    for i in range(0, len(gameStatus.game.serverMap[0])):
        for j in range(0, len(gameStatus.game.serverMap[0])):
            # print(gameStatus.game.serverMap[i][j])
            if gameStatus.game.serverMap[i][j] == "$":
                tmp = len(findPath(gameStatus.game.weightedMap, me, i, j))
                if tmp < nearestRecharge[0]:
                    nearestRecharge[0] = tmp
                    nearestRecharge[1] = j
                    nearestRecharge[2] = i

    d_flag = len(findPath(gameStatus.game.weightedMap, me, gameStatus.game.wantedFlagX, gameStatus.game.wantedFlagY))

    # d_SafeZone = 0 means that I'm in a safeZone
    # d_SafeZone = 1 or 2 means that i need to do 1 or 2 movement to be in a safeZone
    if gameStatus.game.weightedMap[me.y][me.x] == 1:
        d_SafeZone[0] = 0
        d_SafeZone[1] = me.y
        d_SafeZone[2] = me.x
    else:
        if gameStatus.game.weightedMap[me.y - 1][me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = me.y - 1
            d_SafeZone[2] = me.x

        elif gameStatus.game.weightedMap[me.y][me.x - 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = me.y
            d_SafeZone[2] = me.x - 1

        elif gameStatus.game.weightedMap[me.y][me.x + 1] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = me.y
            d_SafeZone[2] = me.x + 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x] == 1:
            d_SafeZone[0] = 1
            d_SafeZone[1] = me.y + 1
            d_SafeZone[2] = me.x

        elif gameStatus.game.weightedMap[me.y - 1][me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = me.y - 1
            d_SafeZone[2] = me.x - 1

        elif gameStatus.game.weightedMap[me.y - 1][me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = me.y - 1
            d_SafeZone[2] = me.x + 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x - 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = me.y + 1
            d_SafeZone[2] = me.x - 1

        elif gameStatus.game.weightedMap[me.y + 1][me.x + 1] == 1:
            d_SafeZone[0] = 2
            d_SafeZone[1] = me.y + 1
            d_SafeZone[2] = me.x + 1

        else:
            d_SafeZone[0] = 3

    return d_flag, num_enemies, enemyDistances, nearestRecharge, me.energy, d_SafeZone, nearestEnemyDistance


def FuzzyControlSystem(me, mapSize):
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

    flagDistance, numberOfEnemies, enemyDistances, nearestRecharge, myEnergy, safeZoneDistance, nearestEnemyDistance = fuzzyValues(
        me,
        mapSize)

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
