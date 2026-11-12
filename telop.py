from utils.gamepad import GamePad
from utils.walker import Walker
from utils.link import Link
from utils.planner import make_plan_feet, solve_frame
import numpy as np
import time
from utils.sim_view import LiveView, KeyboardPad          # [Claude 新增] 可视化 + 键盘替身


SIM = False # default to be True; Tunable
GAIT, T, H, RATE = 'tripod', 2.5, 30, 50
HOME = np.array([0, 30, 105] * 6, dtype=float)                        
prev = HOME.copy()
joy = GamePad(accel=50)                                           # 💬 手柄还读不到的话，先换成 joy = KeyboardPad()（W/S A/D Q/E，Esc 退出；要点一下 SIM 窗口让它在前台）
walker = Walker(GAIT, T, H)                                   
view = LiveView(rate=RATE, v_max=joy.v_max, w_max=joy.w_max) if SIM else None
                                    


log = {'t': [], 'cmd': [], 'feet': [], 'stance': [], 'thetas': []}
reason = ''                                              
# ===========================================================================
link = None
i = 0

try:
    if not SIM:
        link = Link()
        link.move_to(HOME, 1)
        time.sleep(2)
    t0 = time.perf_counter()
    while True:
        while time.perf_counter() < t0 + i / RATE:       
            continue                                   

        cmd = joy.read(dt=1/RATE)
        if joy.quit_pressed():
            reason = 'quit'                             
            break

        feet = walker.step(cmd[0], cmd[1], cmd[2], 1/RATE) # (6, 3) matrix of cmd feet pose
        (thetas, reason) = solve_frame(feet, prev, RATE)
        if thetas is None:
            print(f"At frame {i}, failure reason: {reason}")
            break
        else:
            if SIM == True:
                pass
            else:                                     
                link.send_angles(thetas)
                                      

        log['t'].append(i / RATE)
        log['cmd'].append(cmd)
        log['feet'].append(feet)                         
        log['stance'].append(walker.was_stance.copy()) 
        log['thetas'].append(thetas)
        if view is not None:
            view.update(feet, walker.was_stance, cmd, thetas, prev)  
            if view.closed:
                reason = 'quit'
                break
        
        prev = thetas 
        i += 1                                        
except KeyboardInterrupt:                           
    reason = 'quit (Ctrl-C)'
finally:
    # need Claude's effort: how to record a log
    if link is not None:
        link.move_to(HOME, 1)
        link.close()

    # np.savez 把多个数组存进一个文件；读的时候 L = np.load('teleop_log.npz')，L['thetas'] 就是 (N, 18)。
    np.savez('teleop_log.npz',
             t=np.array(log['t']),               # (N,)        s
             cmd=np.array(log['cmd']),           # (N, 3)      vx, vy (mm/s), w (°/s)
             feet=np.array(log['feet']),         # (N, 6, 3)   机身系脚位 mm
             stance=np.array(log['stance']),     # (N, 6)      True = 着地
             thetas=np.array(log['thetas']),     # (N, 18)     发出去的角度 °
             reason=reason, sim=SIM, gait=GAIT, T=T, H=H, rate=RATE)   # 单个值也能存，方便以后知道这份 log 是什么参数跑的
    print(f"saved teleop_log.npz: {len(log['t'])} frames, stop reason: {reason or 'none'}")
    print("回放: python3 -m utils.sim_view")
    # ===========================================================================



