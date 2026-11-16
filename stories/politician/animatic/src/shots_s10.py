from sh import *

CAR = (0.0, 1.0); YAW = 90.0

def S10_SH010(nf):
    """Inside the empty car: the helicopter rises and banks away into the sunset, open sky behind it. A gust brings a few
    certificates down the street; the bobblehead only comes into frame at the end, wobbling, held for five seconds."""
    eye = np.array(PR.car_world(CAR, YAW, 0.4, -0.3, 1.2))
    reset("sunset"); sets.avenue(tuple(eye), towers=False)
    c = PR.car("car", door_open=1.0); PR.place(c, (CAR[0], CAR[1], 0), YAW)
    h = PR.heli("heli")
    keys = [(0.0, (-250, 2.0, 44), 170), (3.0, (-300, 1.5, 58), 175), (8.0, (-480, -4.0, 72), 182), (15.0, (-760, -12.0, 82), 185)]
    def hpath(t):
        ts = [k[0] for k in keys]
        pos = np.array([np.interp(t, ts, [k[1][i] for k in keys]) for i in range(3)])
        yaw = float(np.interp(t, ts, [k[2] for k in keys])); bank = 12 * math.sin(min(1, t / 8) * math.pi)
        return pos, yaw, bank
    bob = np.array(PR.car_world(CAR, YAW, 0.38, 1.08, 1.13))
    aim = bob + (bob - eye) / np.linalg.norm(bob - eye) * 40 + np.array((0, 0, 3.2))     # the bobblehead low in frame, sky above
    def camfn(t):
        hp = hpath(t)[0] + np.array((0, 0, -1.5))
        if t < 9.8: return eye, hp, 62, 0
        u = min(1.0, (t - 9.8) / 1.3); u = u * u * (3 - 2 * u)
        return eye, hp * (1 - u) + aim * u, 62 - 12 * u, 0
    paper = PR.papers("bond", 14, (CAR[0] - 7.0, CAR[1]), 2.5, 8.6, 12.0, rise=1.4, seed=21, drift=(6.5, -0.5), hidden_before=True)
    wob = lambda t: 0.0 if t < 10.0 else 26 * math.exp(-(t - 10.0) / 7.0) + 6
    return {"cam": {"fn": camfn}, "callbacks": [PR.heli_cb(h, hpath), paper, PR.bob_nod(c, wob)],
            "cues": [[0, 4, "THE ROTOR FAR AWAY"], [4, 8.5, "IT FADES"], [8.6, 10, "A GUST, PAPER"], [10, 15, "THE BOBBLEHEAD WOBBLES. SILENCE"]]}
