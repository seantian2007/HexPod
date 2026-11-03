import numpy as np
from .dancesFunc import wave_dance
from .body_ik import body_ik

# INPUT: pose_fn - pose function defined in dancesFunc.py, duration - in seconds, rate - the rate of discretion
def make_plan(pose_fn, duration, rate=50):
    init_pose = pose_fn(0)
    final_pose = pose_fn(duration)
    # allocate one extra second to go from Home position to start pose, and from final position to Home position
    ramp_time = 1 # second
    ticks_ramp = ramp_time * rate # 50 ticks for each
    times = np.arange(duration * rate) / rate
    poses = np.zeros((len(times), 6))
    thetas = np.zeros((len(times), 18))

    # start with initial ramping
    for i in range(len(times)):
        t = times[i]
        if i < ticks_ramp: # initial ramping
            A_eff = 1 - np.cos(np.pi * t / 2)
            cur_pose = A_eff * pose_fn(t)
        elif len(times) - i <= ticks_ramp:
            A_eff = 1 - np.cos(np.pi * times[len(times) - i] / 2)
            cur_pose = A_eff * pose_fn(t)
        else:
            cur_pose = pose_fn(t)
        
        poses[i, :] = cur_pose
        thetas_i, status_i = body_ik(cur_pose)

        if False in status_i[:, 0]:
            index_err = [l for l, val in enumerate(status_i[:, 0]) if not val]
            raise ValueError(f"frame {i}, t={times[i]:.2f}s, leg_num {index_err}, code {status_i[index_err[0], 1].item()}")
        else:
            thetas_i_flatten = thetas_i.flatten()
            if i != 0:
                theta_rate = (thetas_i_flatten - thetas[i-1, :]) / (1/rate)
                if False in abs(theta_rate) <= 100:
                    raise ValueError(f"frame {i}, t={times[i]:.2f}s, theta rate too large")
                else:
                    thetas[i, :] = thetas_i_flatten
            else:
                thetas[i, :] = thetas_i_flatten

    return times, poses, thetas

times, poses, thetas = make_plan(wave_dance, 10)
print(times)
print(poses)
print(thetas)


