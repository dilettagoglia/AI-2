from pathFinder import findPath
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from matplotlib import pyplot as plt


# karen.fuzzyStrategy chiama inputFuzzy
# creare una funzione fuzzyValues che generi i valori di input per FuzzyControlSystem (calcolando i vari pathfinder verso tutte le possibili destinazioni).
# Dopo aver chiamato la funzione FuzzyControlSystem, aspetta il return sim.output e in base a questo valore sceglie verso dove muoversi.
# a questo punto fuzzyValues restituisce a karen.fuzzystrategy le coordinate scelte.

# OTTIMIZZAZIONE: fuzzyValues calcola già tutti i pathfinder, quindi anche quello prescelto. karen.fuzzystrategy passerà ad act già la "direction" e non le coordinate.

def fuzzyValues(me, game):
    # game.serverMap
    # game.weightedMap

    num_enemies = 0
    enemyDistance = dict()

    # nearestRecharge [distance, xCoordinate, yCoordinate]
    nearestRecharge = [32, 32, 32]
    possibleAction = dict()
    for enemy in game.enemies:
        # for each enemy retrieve the min coordinate distance (x or y)
        enemyDistance[enemy.symbol] = min(len(findPath(game.weightedMap, me, me.x, enemy.y)),
                                          len(me.movement.move(game.weightedMap, me, enemy.x, me.y)))

    for enemy in enemyDistance:
        if enemyDistance[enemy] < 5:
            num_enemies += 1
        else:
            enemyDistance.pop(enemy)

    for i in range(0, len(game.serverMap[0])):
        for j in range(0, len(game.serverMap[0])):

            if game.serverMap[i][j] == "$":
                tmp = len(findPath(game.weightedMap, me, i, j))
                if tmp < nearestRecharge[0]:
                    nearestRecharge[0] = tmp
                    nearestRecharge[1] = i
                    nearestRecharge[2] = j

    d_flag = findPath(game.weightedMap, me, game.wantedFlagX, game.wantedFlagY)


    # possible action avrà anche possibleAction['recharge'] min del pathfinder di tutti i recharge.
    # idem i muri ecc

    # pathfinder(mex, mey, enemyx, mey)
    # pathfinder(mex, mey, mex, enemy)


def FuzzyControlSystem(me, game):
    """
    Output values:
    -goToRecharge,  0-10
    -hideBehindTheWall 10-20
    -useTheBarrier 20-30
    -goToFlag, 30-40
    -goToKill, 40-50

    """

    # New Antecedent/Consequent objects hold universe variables and membership functions

    energy = ctrl.Antecedent(np.arange(0, 256, 10), 'energy')
    d_flag = ctrl.Antecedent(np.arange(0, 32, 1), 'd_flag')
    d_recharge = ctrl.Antecedent(np.arange(0, 32, 1), 'd_recharge')
    num_enemies = ctrl.Antecedent(np.arange(0, 20, 1), 'num_enemies')
    d_safeZone = ctrl.Antecedent(np.arange(0, 32, 1), 'd_safeZone')
    # d_barrier = ctrl.Antecedent(np.arange(0, 32, 1), 'd_barrier')
    # d_nearestEnemy = ctrl.Antecedent(np.arange(0, 32, 1), 'd_nearestEnemy')

    output = ctrl.Consequent(np.arange(0, 50, 1), 'output')

    output['goToRecharge'] = fuzz.trimf(output.universe, [0, 10, 10])
    output['hideBehindTheWall'] = fuzz.trimf(output.universe, [10, 20, 20])
    output['useTheBarrier'] = fuzz.trimf(output.universe, [20, 30, 30])
    output['goToFlag'] = fuzz.trimf(output.universe, [30, 40, 40])
    output['goToKill'] = fuzz.trimf(output.universe, [40, 50, 50])

    # Auto-membership function population is possible with .automf(3, 5, or 7)

    energy.automf(3)
    d_recharge.automf(3)
    d_barrier.automf(3)
    d_flag.automf(3)
    d_safeZone.automf(3)
    num_enemies.automf(3)

    # poor mediocre average decent good
    rule1 = ctrl.Rule((energy['poor'] & d_flag['average'] & (num_enemies['good'] | num_enemies['average'])) |
                      (energy['poor'] & d_flag['good']) |
                      (energy['poor'] & d_recharge['poor']) |
                      (energy['average'] & d_recharge['poor'])
                      , output['goToRecharge'])

    rule2 = ctrl.Rule((energy['poor'] & d_safeZone['poor']) |
                      (energy['average'] & (num_enemies['average'] | num_enemies['good']) & d_safeZone['average']) |
                      (d_safeZone['poor'] & (num_enemies['average'] | num_enemies['good']))
                      , output['hideBehindTheWall'])

    rule3 = ctrl.Rule(d_barrier['poor'] |
                      (energy['average'] & (num_enemies['average'] | num_enemies['good']) & (
                              d_barrier['poor'] | d_barrier['average']))
                      , output['useTheBarrier'])

    rule4 = ctrl.Rule(d_flag['poor'] |
                      ((d_flag['poor'] | d_flag['average']) & num_enemies['poor']) |
                      num_enemies['poor'] |
                      (energy['good'] & num_enemies['poor']) & (d_safeZone['good'] | d_safeZone['average'])
                      , output['goToFlag'])

    rule5 = ctrl.Rule(num_enemies['poor'] & (energy['average'] | energy['good']) |
                      (num_enemies['good'] & (d_barrier['good']) & d_safeZone['good'])
                      , output['goToKill'])

    system = ctrl.ControlSystem(rules=[rule1, rule2, rule3, rule4, rule5])

    # Later we intend to run this system with a 21*21 set of inputs, so we almediocre
    # that many plus one unique runs before results are flushed.
    # Subsequent runs would return in 1/8 the time!
    sim = ctrl.ControlSystemSimulation(system)

    # Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
    # Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
    sim.input['energy'] = 20
    sim.input['d_flag'] = 32
    sim.input['d_recharge'] = 32
    sim.input['num_enemies'] = 20
    sim.input['d_safeZone'] = 30
    sim.input['d_barrier'] = 32

    # Crunch the numbers
    sim.compute()
    print(sim.output)


FuzzyStrategy()
