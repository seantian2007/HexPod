import numpy as np
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
        
