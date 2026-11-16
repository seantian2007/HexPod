"""WiFi link quality test (stage 8, test W2). Pings the robot at 50 Hz and reports how
many answers were lost and how long the round trip took.

Run from code/, with the computer on the hexapod-xxxx WiFi and the robot powered:
    python3 link_test.py                  # 1000 pings = 20 s
    python3 link_test.py --n 3000 --rate 50

Goal: loss < 1 %, p99 round trip < 50 ms. The robot does not need to stand up for this;
pings are answered by the comm task at once and do not touch the servos.
"""
import argparse
import time

from utils.esp_link import ROBOT_IP, UdpLink


def percentile(sorted_values, q):
    if not sorted_values:
        return float('nan')
    k = min(len(sorted_values) - 1, round(q / 100 * (len(sorted_values) - 1)))
    return sorted_values[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default=ROBOT_IP)
    ap.add_argument('--n', type=int, default=1000, help='number of pings')
    ap.add_argument('--rate', type=float, default=50, help='pings per second')
    args = ap.parse_args()

    link = UdpLink(args.host)
    link.on_line = lambda text: None   # keep the screen for the ping results
    period = 1.0 / args.rate
    rtts = []
    lost = 0
    t0 = time.perf_counter()
    try:
        for i in range(1, args.n + 1):
            # wait for this ping's slot (if an answer was slow, the next ping goes at once)
            while time.perf_counter() < t0 + (i - 1) * period:
                time.sleep(0.001)
            rtt = link.ping(i, timeout=0.2)    # no answer in 200 ms counts as lost
            if rtt is None:
                lost += 1
            else:
                rtts.append(rtt)
            if i % args.rate == 0:
                print(f'\r{i}/{args.n} sent, {lost} lost', end='', flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()
    sent = len(rtts) + lost
    print()
    if sent == 0:
        return
    rtts.sort()
    loss = lost / sent * 100
    p99 = percentile(rtts, 99)
    print(f'sent {sent}, lost {lost} ({loss:.2f} %)')
    print(f'round trip ms: median {percentile(rtts, 50):.1f}, p95 {percentile(rtts, 95):.1f}, '
          f'p99 {p99:.1f}, max {rtts[-1] if rtts else float("nan"):.1f}')
    ok = loss < 1 and p99 < 50
    print('PASS' if ok else 'FAIL', '(goal: loss < 1 %, p99 < 50 ms)')


if __name__ == '__main__':
    main()
