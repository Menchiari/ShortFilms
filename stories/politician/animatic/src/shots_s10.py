from sh import *

CAR = (0.0, 1.0); YAW = 90.0

def S10_SH010(nf):
    eye = tuple(PR.car_world(CAR, YAW, 0.4, -0.3, 1.2))
    reset("sunset"); sets.avenue(eye)
    c = PR.car("car", door_open=1.0); PR.place(c, (CAR[0], CAR[1], 0), YAW)
    h = PR.heli("heli")
    keys = [(0.0, (-330, 18, 18), 170), (3.0, (-345, 15, 52), 175), (7.0, (-520, 5, 68), 182), (12.0, (-950, -5, 84), 185)]
    def hpath(t):
        ts = [k[0] for k in keys]
        pos = np.array([np.interp(t, ts, [k[1][i] for k in keys]) for i in range(3)])
        yaw = float(np.interp(t, ts, [k[2] for k in keys])); bank = 12 * math.sin(min(1, t / 7) * math.pi)
        return pos, yaw - 90 + 90, bank
    camkeys = [(0, eye, (-330, 12, 24), 45), (3, eye, (-345, 15, 50), 45), (7, eye, (-520, 5, 62), 40), (12, eye, (-400, 1.5, 2.2), 30)]
    return {"cam": move(camkeys, ease="io", spline=True), "callbacks": [PR.heli_cb(h, hpath)],
            "cues": [[0, 4, "THE ROTOR FAR AWAY"], [4, 9, "IT FADES"], [9, 12, "SILENCE. SUNSET"]]}
