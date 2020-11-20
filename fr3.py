import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from matplotlib import pyplot as plt

# New Antecedent/Consequent objects hold universe variables and membership
# functions
energia = ctrl.Antecedent(np.arange(0, 26, 1), 'energia')
d_flag = ctrl.Antecedent(np.arange(0, 32, 1), 'd_flag')

output = ctrl.Consequent(np.arange(0, 20, 1), 'output')

output['ricarica'] = fuzz.trimf(output.universe, [0, 10, 15])
output['no'] = fuzz.trimf(output.universe, [10, 20, 20])

# Auto-membership function population is possible with .automf(3, 5, or 7)
energia.automf(3)
d_flag.automf(3)


rule1 = ctrl.Rule((energia['poor'] & d_flag['good']) |
                  (energia['poor'] & d_flag['average']), output['ricarica'])
rule2 = ctrl.Rule((energia['poor'] & d_flag['poor']) |
                  (energia['average'] & d_flag['poor']) |
                  (energia['good'] & d_flag['poor']) |
                  (energia['average'] & d_flag['average']) |
                  (energia['average'] & d_flag['good']) |
                  (energia['good'] & d_flag['good']), output['no'] )
system = ctrl.ControlSystem(rules=[rule1, rule2])

# Later we intend to run this system with a 21*21 set of inputs, so we allow
# that many plus one unique runs before results are flushed.
# Subsequent runs would return in 1/8 the time!
sim = ctrl.ControlSystemSimulation(system)

# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
sim.input['energia'] = 26
sim.input['d_flag'] = 1

# Crunch the numbers
sim.compute()

print (sim.output['output'])



# We can simulate at higher resolution with full accuracy
upsampled = np.linspace(0, 26, 21)
x1, y1 = np.meshgrid(upsampled, upsampled)

upsampled = np.linspace(0, 32, 21)
x2, y2 = np.meshgrid(upsampled, upsampled)
z = np.zeros_like(20)


# Loop through the system 21*21 times to collect the control surface
for i in range(21):
    for j in range(21):
        sim.input['energia'] = x1[i, j]
        sim.input['d_flag'] = y2[i, j]
        sim.compute()
        z[i, j] = sim.output['output']


# Plot the result in pretty 3D with alpha blending
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap='viridis',
                       linewidth=0.4, antialiased=True)

cset = ax.contourf(x, y, z, zdir='z', offset=-2.5, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='x', offset=3, cmap='viridis', alpha=0.5)
cset = ax.contourf(x, y, z, zdir='y', offset=3, cmap='viridis', alpha=0.5)

ax.view_init(30, 200)
plt.show()