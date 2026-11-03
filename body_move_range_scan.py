import numpy as np
import matplotlib.pyplot as plt
from utils.body_ik import body_ik

output = np.zeros((6, 3), dtype=object)
pose = np.zeros(6)

# postive direction
for i in range(6):
    reachFailure = False
    new_pose = np.copy(pose)
    old_pose = np.copy(pose)

    while not reachFailure:
        new_pose[i] += 0.1
        thetas, status = body_ik(new_pose)
        if False in status[:, 0]:
            reachFailure = True
            output[i, 0] = old_pose[i].item()
            index = [i for i, val in enumerate(status[:, 0]) if not val] # return the array of index where status is False
            output[i, 1] = index
            output[i, 2] =  status[index[0], 1].item()
        else:
            old_pose[i] += 0.1


print(output)

# construct a combination diagram for all possible combination of roll & pitch
rolls = np.arange(-14.9, 15.0, 0.1)
pitchs = np.arange(-17, 17.1, 0.1)
output_1 = np.zeros((len(rolls), len(pitchs)))

for i in range(len(rolls)):
    for j in range(len(pitchs)):
        pose = [0, 0, 0, rolls[i], pitchs[j], 0]
        thetas, status = body_ik(pose)
        if False in status[:, 0]:
            index = [i for i, val in enumerate(status[:, 0]) if not val] # return the array of index where status is False
            output_1[i, j] = status[index[0], 1].item()
        else:
            output_1[i, j] = 0

# fist plot
fig, ax = plt.subplots()
im = ax.imshow(output_1, cmap="inferno", interpolation="nearest", aspect="equal", origin='lower', extent=[pitchs[0], pitchs[-1], rolls[0], rolls[-1]])

fig.colorbar(im, ax=ax, label="Intensity Scale")
ax.set_title("Possibility Graph for Roll vs Pitch", fontsize=14, pad=15)

plt.show()

        
