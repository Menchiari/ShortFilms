"""RIFE v4.26 frame interpolation (inference only), for rebuilding single frames at film quality.

The network below follows the published RIFE v4.26 architecture (hzwer/Practical-RIFE, MIT).
Only its weights are downloaded, never code: the model file is plain tensors, loaded with
torch.load(weights_only=True).

Setup once (about 250 MB, kept out of git in tools/media/_models/):
  pip install torch numpy opencv-python-headless
  python tools/media/rife.py setup
Use:
  python tools/media/rife.py frame take.mp4 out.mp4 12        rebuild frame 12 from frames 11 and 13
  python tools/media/rife.py frame take.mp4 out.mp4 2 12 --drop-last
Frame numbers start at 0. Every other frame stays the original; timing and audio are kept.
"""
import os, sys, zipfile, urllib.request, urllib.error
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, '_models', 'RIFEv4.26')
WEIGHTS = os.path.join(MODEL_DIR, 'flownet.pkl')
URL = 'https://huggingface.co/hzwer/RIFE/resolve/main/RIFEv4.26_0921.zip'

_grid = {}
def warp(img, flow):
    k = (str(flow.device), str(flow.size()))
    if k not in _grid:
        n, _, h, w = flow.shape
        hor = torch.linspace(-1.0, 1.0, w, device=flow.device).view(1, 1, 1, w).expand(n, -1, h, -1)
        ver = torch.linspace(-1.0, 1.0, h, device=flow.device).view(1, 1, h, 1).expand(n, -1, -1, w)
        _grid[k] = torch.cat([hor, ver], 1)
    flow = torch.cat([flow[:, 0:1] / ((img.shape[3] - 1.0) / 2.0), flow[:, 1:2] / ((img.shape[2] - 1.0) / 2.0)], 1)
    g = (_grid[k] + flow).permute(0, 2, 3, 1)
    return F.grid_sample(img, g, mode='bilinear', padding_mode='border', align_corners=True)

def conv(i, o, k=3, s=1, p=1, d=1):
    return nn.Sequential(nn.Conv2d(i, o, k, s, p, dilation=d, bias=True), nn.LeakyReLU(0.2, True))

class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.cnn0 = nn.Conv2d(3, 16, 3, 2, 1); self.cnn1 = nn.Conv2d(16, 16, 3, 1, 1)
        self.cnn2 = nn.Conv2d(16, 16, 3, 1, 1); self.cnn3 = nn.ConvTranspose2d(16, 4, 4, 2, 1)
        self.relu = nn.LeakyReLU(0.2, True)
    def forward(self, x):
        x = self.relu(self.cnn0(x)); x = self.relu(self.cnn1(x)); x = self.relu(self.cnn2(x))
        return self.cnn3(x)

class ResConv(nn.Module):
    def __init__(self, c, d=1):
        super().__init__()
        self.conv = nn.Conv2d(c, c, 3, 1, d, dilation=d, groups=1)
        self.beta = nn.Parameter(torch.ones((1, c, 1, 1)), requires_grad=True)
        self.relu = nn.LeakyReLU(0.2, True)
    def forward(self, x):
        return self.relu(self.conv(x) * self.beta + x)

class IFBlock(nn.Module):
    def __init__(self, in_planes, c=64):
        super().__init__()
        self.conv0 = nn.Sequential(conv(in_planes, c // 2, 3, 2, 1), conv(c // 2, c, 3, 2, 1))
        self.convblock = nn.Sequential(*[ResConv(c) for _ in range(8)])
        self.lastconv = nn.Sequential(nn.ConvTranspose2d(c, 4 * 13, 4, 2, 1), nn.PixelShuffle(2))
    def forward(self, x, flow=None, scale=1):
        x = F.interpolate(x, scale_factor=1. / scale, mode='bilinear', align_corners=False)
        if flow is not None:
            flow = F.interpolate(flow, scale_factor=1. / scale, mode='bilinear', align_corners=False) / scale
            x = torch.cat((x, flow), 1)
        feat = self.convblock(self.conv0(x))
        tmp = F.interpolate(self.lastconv(feat), scale_factor=scale, mode='bilinear', align_corners=False)
        return tmp[:, :4] * scale, tmp[:, 4:5], tmp[:, 5:]

class IFNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.block0 = IFBlock(7 + 8, c=192); self.block1 = IFBlock(8 + 4 + 8 + 8, c=128)
        self.block2 = IFBlock(8 + 4 + 8 + 8, c=96); self.block3 = IFBlock(8 + 4 + 8 + 8, c=64)
        self.block4 = IFBlock(8 + 4 + 8 + 8, c=32); self.encode = Head()
    def forward(self, img0, img1, timestep, scale_list):
        t = (img0[:, :1].clone() * 0 + 1) * timestep
        f0, f1 = self.encode(img0), self.encode(img1)
        w0, w1, flow, mask, feat = img0, img1, None, None, None
        for i, blk in enumerate([self.block0, self.block1, self.block2, self.block3, self.block4]):
            if flow is None:
                flow, mask, feat = blk(torch.cat((img0, img1, f0, f1, t), 1), None, scale=scale_list[i])
            else:
                fd, mask, feat = blk(torch.cat((w0, w1, warp(f0, flow[:, :2]), warp(f1, flow[:, 2:4]), t, mask, feat), 1),
                                     flow, scale=scale_list[i])
                flow = flow + fd
            w0, w1 = warp(img0, flow[:, :2]), warp(img1, flow[:, 2:4])
        m = torch.sigmoid(mask)
        return w0 * m + w1 * (1 - m)

_net = None
def net():
    global _net
    if _net is None:
        if not os.path.exists(WEIGHTS): raise SystemExit('Model missing: run  python tools/media/rife.py setup')
        sd = torch.load(WEIGHTS, map_location='cpu', weights_only=True)
        _net = IFNet(); _net.load_state_dict({k.replace('module.', ''): v for k, v in sd.items()}, strict=False); _net.eval()
    return _net

def interp(A, B, t=0.5, scale=1.0):
    """A, B: HxWx3 uint8 BGR frames. Returns the frame at time t between them."""
    h, w = A.shape[:2]; m = max(128, int(128 / scale)); ph, pw = ((h - 1) // m + 1) * m, ((w - 1) // m + 1) * m
    def tt(x): return F.pad(torch.from_numpy(x[:, :, ::-1].copy()).permute(2, 0, 1).float().unsqueeze(0) / 255., (0, pw - w, 0, ph - h))
    with torch.no_grad():
        out = net()(tt(A), tt(B), t, [16 / scale, 8 / scale, 4 / scale, 2 / scale, 1 / scale])
    out = out[0, :, :h, :w].clamp(0, 1).permute(1, 2, 0).numpy()[:, :, ::-1] * 255
    return np.ascontiguousarray(out.round().astype(np.uint8))

def setup():
    os.makedirs(MODEL_DIR, exist_ok=True)
    z = os.path.join(MODEL_DIR, 'rife.zip')
    try: urllib.request.urlretrieve(URL, z)
    except urllib.error.URLError:  # Python from python.org on a Mac has no certificates: the Mac's own curl has them
        import subprocess; subprocess.run(['curl', '-fL', '-o', z, URL], check=True)
    with zipfile.ZipFile(z) as f, open(WEIGHTS, 'wb') as out:
        out.write(f.read('RIFEv4.26_0921/flownet.pkl'))  # weights only, no code is extracted
    os.remove(z); net(); print('RIFE ready:', WEIGHTS)

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'setup': setup()
    elif len(sys.argv) >= 5 and sys.argv[1] == 'frame':
        sys.path.insert(0, HERE)
        from fixframes import read, write
        src, dst = sys.argv[2], sys.argv[3]
        ks = [int(x) for x in sys.argv[4:] if not x.startswith('--')]
        fr, fps = read(src); out = list(fr)
        for k in ks: out[k] = interp(fr[k - 1], fr[k + 1], 0.5)
        if '--drop-last' in sys.argv: out = out[:-1]
        write(out, fps, src, dst); print('rebuilt frames', ks, '- wrote', dst)
    else: print(__doc__)
