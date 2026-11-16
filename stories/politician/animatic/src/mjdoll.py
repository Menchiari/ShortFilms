"""MuJoCo ragdoll: a humanoid with anatomical joint limits, built on the 18-joint skeleton of puppet.py.
A leg cannot swing out sideways past ~45 degrees, a knee bends one way, the body has real mass and weight.

d = Doll(scale=1.0, wide=1.0, rope=anchor_or_None)
d.place(pos=(x, y, z), yaw=deg, lying=None|"back"|"front", q={joint: deg}, vel=(vx, vy, vz))
JA = d.run(T, ctrl=fn(t, doll) -> {joint: (target_deg, kp)}, tone=default kp, kd=..., forces=fn(t, doll))
JA: (frames at core.FPS, 18, 3) world positions of HEAD..NOSE, ready for Actor.joints()."""
import math
import numpy as np
import mujoco
import core

SITES = ["HEAD", "NECK", "PELVIS", "LSH", "LEL", "LHA", "RSH", "REL", "RHA",
         "LHIP", "LKN", "LAN", "LTO", "RHIP", "RKN", "RAN", "RTO", "NOSE"]

# hinge joints: name -> (axis, lo, hi) in degrees. Facing +y, up +z, the figure's left is -x.
# x: flexion (forward is + for hips, shoulders, elbows; - for waist, neck; knees bend -); y: sideways; z: twist
JOINTS = {
    "waist_x": ((1, 0, 0), -80, 25), "waist_y": ((0, 1, 0), -35, 35), "waist_z": ((0, 0, 1), -45, 45),
    "neck_x": ((1, 0, 0), -60, 40), "neck_y": ((0, 1, 0), -40, 40), "neck_z": ((0, 0, 1), -75, 75),
    "lsh_x": ((1, 0, 0), -60, 170), "lsh_y": ((0, 1, 0), -20, 170), "lsh_z": ((0, 0, 1), -80, 80), "lel_x": ((1, 0, 0), 0, 150),
    "rsh_x": ((1, 0, 0), -60, 170), "rsh_y": ((0, 1, 0), -170, 20), "rsh_z": ((0, 0, 1), -80, 80), "rel_x": ((1, 0, 0), 0, 150),
    "lhip_x": ((1, 0, 0), -25, 120), "lhip_y": ((0, 1, 0), -15, 45), "lhip_z": ((0, 0, 1), -40, 40), "lkn_x": ((1, 0, 0), -150, 0), "lan_x": ((1, 0, 0), -40, 40),
    "rhip_x": ((1, 0, 0), -25, 120), "rhip_y": ((0, 1, 0), -45, 15), "rhip_z": ((0, 0, 1), -40, 40), "rkn_x": ((1, 0, 0), -150, 0), "ran_x": ((1, 0, 0), -40, 40),
}
DAMP = {"waist": 6.0, "neck": 1.5, "lsh": 1.2, "rsh": 1.2, "lel": 0.6, "rel": 0.6, "lhip": 3.0, "rhip": 3.0, "lkn": 1.5, "rkn": 1.5, "lan": 0.5, "ran": 0.5}


def _xml(s, w, rope, sidewalks):
    def v(*a, k=s):
        return " ".join(f"{x * k:.4f}" for x in a)
    def joints(*names):
        out = []
        for n in names:
            ax, lo, hi = JOINTS[n]
            out.append(f'<joint name="{n}" type="hinge" axis="{ax[0]} {ax[1]} {ax[2]}" range="{lo} {hi}" damping="{DAMP[n.split("_")[0]]}" armature="0.02"/>')
        return "".join(out)
    def cap(a, b, r, k=1.0):
        return f'<geom type="capsule" fromto="{v(*a)} {v(*b)}" size="{r * s * k:.4f}"/>'
    side = lambda m: (-1 if m == "l" else 1)
    arms = ""
    for m in "lr":
        sx = side(m)
        arms += (f'<body name="{m}uarm" pos="{v(0.19 * sx, 0.026, 0.414)}">{joints(m + "sh_x", m + "sh_y", m + "sh_z")}'
                 f'{cap((0, 0, 0), (0.03 * sx, 0.006, -0.27), 0.045, w ** 0.5)}<site name="{m.upper()}SH" pos="0 0 0"/>'
                 f'<body name="{m}farm" pos="{v(0.03 * sx, 0.006, -0.288)}">{joints(m + "el_x")}'
                 f'{cap((0, 0, 0), (0.027 * sx, 0.06, -0.25), 0.038, w ** 0.5)}<site name="{m.upper()}EL" pos="0 0 0"/>'
                 f'<site name="{m.upper()}HA" pos="{v(0.027 * sx, 0.06, -0.262)}"/></body></body>')
    legs = ""
    for m in "lr":
        sx = side(m)
        legs += (f'<body name="{m}thigh" pos="{v(0.095 * sx, 0, -0.06)}">{joints(m + "hip_x", m + "hip_y", m + "hip_z")}'
                 f'{cap((0, 0, 0), (0.023 * sx, 0, -0.42), 0.075, w ** 0.7)}<site name="{m.upper()}HIP" pos="0 0 0"/>'
                 f'<body name="{m}shin" pos="{v(0.023 * sx, 0, -0.44)}">{joints(m + "kn_x")}'
                 f'{cap((0, 0, 0), (0.023 * sx, -0.015, -0.42), 0.052)}<site name="{m.upper()}KN" pos="0 0 0"/>'
                 f'<body name="{m}foot" pos="{v(0.023 * sx, -0.015, -0.439)}">{joints(m + "an_x")}'
                 f'{cap((0, -0.03, -0.03), (0.0, 0.15, -0.035), 0.032)}<site name="{m.upper()}AN" pos="0 0 0"/>'
                 f'<site name="{m.upper()}TO" pos="{v(0.0, 0.149, -0.035)}"/></body></body></body>')
    walls = "".join(f'<geom type="box" pos="{(x0 + x1) / 2:.3f} {(y0 + y1) / 2:.3f} 0.075" size="{(x1 - x0) / 2:.3f} {(y1 - y0) / 2:.3f} 0.075"/>'
                    for (x0, x1, y0, y1) in sidewalks)
    anchor = ""; tendon = ""
    if rope is not None:
        anchor = f'<body name="anchor" mocap="true" pos="{rope[0]:.3f} {rope[1]:.3f} {rope[2]:.3f}"><site name="ANCHOR" pos="0 0 0"/></body>'
        tendon = ('<tendon><spatial name="rope" limited="true" range="0 100" width="0.01" solreflimit="0.004 1" solimplimit="0.95 0.99 0.001">'
                  '<site site="ANCHOR"/><site site="RAN"/></spatial></tendon>')
    return f"""<mujoco model="doll">
<option timestep="{1 / 480:.6f}" iterations="60" integrator="implicitfast"/>
<default><geom condim="3" friction="1.0 0.05 0.01" density="985" solref="0.005 1"/></default>
<worldbody>
<geom name="floor" type="plane" size="400 400 0.1"/>
{walls}{anchor}
<body name="pelvis" pos="0 0 {1.004 * s:.4f}"><freejoint name="root"/>
{cap((-0.085, 0, 0.02), (0.085, 0, 0.02), 0.105, w)}<site name="PELVIS" pos="0 0 0"/>
<body name="torso" pos="{v(0, 0, 0.09)}">{joints("waist_x", "waist_y", "waist_z")}
{cap((0, 0, 0.06), (0, 0.02, 0.33), 0.125, w)}<site name="NECK" pos="{v(0, 0.029, 0.459)}"/>
<body name="head" pos="{v(0, 0.029, 0.459)}">{joints("neck_x", "neck_y", "neck_z")}
{cap((0, 0, 0.0), (0, 0.012, 0.07), 0.05)}<geom type="sphere" pos="{v(0, 0.019, 0.169)}" size="{0.1 * s:.4f}"/>
<site name="HEAD" pos="{v(0, 0.019, 0.169)}"/><site name="NOSE" pos="{v(0, 0.139, 0.163)}"/></body>
{arms}</body>
{legs}</body>
</worldbody>
<contact><exclude body1="torso" body2="lthigh"/><exclude body1="torso" body2="rthigh"/><exclude body1="lthigh" body2="rthigh"/>
<exclude body1="pelvis" body2="luarm"/><exclude body1="pelvis" body2="ruarm"/></contact>
{tendon}
</mujoco>"""


class Doll:
    def __init__(self, scale=1.0, wide=1.0, rope=None, sidewalks=None):
        sw = core.SIDEWALKS if sidewalks is None else sidewalks
        self.m = mujoco.MjModel.from_xml_string(_xml(scale, min(1.5, wide), rope, sw))
        self.d = mujoco.MjData(self.m)
        self.sid = [mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, n) for n in SITES]
        self.jid = {n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, n) for n in JOINTS}
        self.qadr = {n: self.m.jnt_qposadr[j] for n, j in self.jid.items()}
        self.vadr = {n: self.m.jnt_dofadr[j] for n, j in self.jid.items()}
        self.bid = {n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, n) for n in
                    ("pelvis", "torso", "head", "luarm", "lfarm", "ruarm", "rfarm", "lthigh", "lshin", "lfoot", "rthigh", "rshin", "rfoot")}
        self.rope = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_TENDON, "rope") if rope is not None else -1
        self.t = 0.0

    def place(self, pos, yaw=0.0, lying=None, q=None, vel=None):
        d = self.d; mujoco.mj_resetData(self.m, d)
        qy = np.array((math.cos(math.radians(yaw) / 2), 0, 0, math.sin(math.radians(yaw) / 2)))
        if lying is None:
            qr = qy
        else:
            a = math.radians(90 if lying == "back" else -90)
            qx = np.array((math.cos(a / 2), math.sin(a / 2), 0, 0)); qr = np.zeros(4); mujoco.mju_mulQuat(qr, qy, qx)
        d.qpos[0:3] = pos; d.qpos[3:7] = qr
        for n, deg in (q or {}).items():
            d.qpos[self.qadr[n]] = math.radians(deg)
        if vel is not None:
            d.qvel[0:3] = vel
        mujoco.mj_forward(self.m, d); self.t = 0.0

    def set_rope(self, length):
        if self.rope >= 0:
            self.m.tendon_range[self.rope] = (0.0, float(length))

    def state(self):
        return self.d.qpos.copy(), self.d.qvel.copy()

    def set_state(self, st):
        self.d.qpos[:] = st[0]; self.d.qvel[:] = st[1]; mujoco.mj_forward(self.m, self.d); self.t = 0.0

    def joints(self):
        return np.array([self.d.site_xpos[i].copy() for i in self.sid])

    def q(self, n):
        return math.degrees(self.d.qpos[self.qadr[n]])

    def step(self, ctrl=None, tone=4.0, kd=0.6, forces=None, rope_fn=None):
        d = self.d; d.qfrc_applied[:] = 0; d.xfrc_applied[:] = 0
        tg = ctrl(self.t, self) if ctrl else {}
        for n in JOINTS:
            target, kp = tg.get(n, (0.0, tone))
            qa, va = self.qadr[n], self.vadr[n]
            d.qfrc_applied[va] = kp * (math.radians(target) - d.qpos[qa]) - kd * kp * 0.05 * d.qvel[va]
        if forces:
            for body, f in forces(self.t, self):
                d.xfrc_applied[self.bid[body], :3] += f
        if rope_fn:
            self.set_rope(rope_fn(self.t))
        mujoco.mj_step(self.m, d); self.t += self.m.opt.timestep

    def run(self, T, ctrl=None, tone=4.0, kd=0.6, forces=None, rope_fn=None, settle=0.0):
        """Simulate T seconds (after an unrecorded settle), return joint positions at core.FPS."""
        every = int(round(1.0 / (core.FPS * self.m.opt.timestep)))
        for _ in range(int(round(settle / self.m.opt.timestep))):
            self.step(ctrl, tone, kd, forces, rope_fn)
        self.t = 0.0; out = []
        n = int(round(T / self.m.opt.timestep))
        for k in range(n + 1):
            if k % every == 0:
                out.append(self.joints())
            self.step(ctrl, tone, kd, forces, rope_fn)
        return np.array(out)


def pulse(t, t0, dur):
    """0..1..0 bump between t0 and t0 + dur."""
    if t < t0 or t > t0 + dur:
        return 0.0
    return math.sin(math.pi * (t - t0) / dur)
