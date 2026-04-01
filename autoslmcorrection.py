import numpy as np
import cv2
import socket
import struct
import time
from screeninfo import get_monitors

# =========================
# SELECT SLM MONITOR
# =========================

def get_slm_monitor():
    monitors = get_monitors()
    
    print("Detected monitors:")
    for i, m in enumerate(monitors):
        print(f"{i}: {m}")

    # Usually SLM is second monitor → index 1
    return monitors[1]


# =========================
# FULLSCREEN SLM WINDOW
# =========================

class SLMDisplay:
    def __init__(self, monitor):
        self.monitor = monitor
        self.window_name = "SLM"

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.moveWindow(self.window_name, monitor.x, monitor.y)
        cv2.resizeWindow(self.window_name, monitor.width, monitor.height)

        cv2.setWindowProperty(
            self.window_name,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

    def send(self, phase):
        phase_norm = (phase % (2*np.pi)) / (2*np.pi)
        img = (phase_norm * 255).astype(np.uint8)

        cv2.imshow(self.window_name, img)
        cv2.waitKey(1)


# =========================
# UDP CAMERA RECEIVER
# =========================

class CameraReceiver:
    def __init__(self, port=5000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port))
        self.buffer = {}

    def receive(self):
        while True:
            data, _ = self.sock.recvfrom(4096)

            if len(data) < 32:
                continue

            header = struct.unpack("IIIIIIII", data[:32])
            width, height, _, frameID, chunkIndex, totalChunks, offset, size = header

            payload = data[32:]
            self.buffer[chunkIndex] = payload

            if len(self.buffer) == totalChunks:
                frame = bytearray(width * height)

                for i in range(totalChunks):
                    chunk = self.buffer[i]
                    start = i * len(chunk)
                    frame[start:start+len(chunk)] = chunk

                self.buffer = {}

                img = np.frombuffer(frame, dtype=np.uint8)
                return img.reshape((height, width))


# =========================
# METRIC
# =========================

def metric(img):
    img = img.astype(np.float32)
    img /= (img.max() + 1e-6)

    y, x = np.indices(img.shape)
    total = img.sum()

    x_mean = (x * img).sum() / total
    y_mean = (y * img).sum() / total

    sx = np.sqrt(((x - x_mean)**2 * img).sum() / total)
    sy = np.sqrt(((y - y_mean)**2 * img).sum() / total)

    ellipticity = abs(sx - sy)
    size = sx + sy
    peak = img.max()

    return size + 2*ellipticity - 3*peak


# =========================
# ZERNIKE MODES
# =========================

def zernike_modes(X, Y, coeffs):
    return (
        coeffs["defocus"] * (X**2 + Y**2) +
        coeffs["astig_x"] * (X**2 - Y**2) +
        coeffs["astig_45"] * (2*X*Y)
    )


# =========================
# AUTO OPTIMIZATION LOOP
# =========================

def optimize(camera, slm, base_phase, X, Y):

    coeffs = {"defocus":0.0, "astig_x":0.0, "astig_45":0.0}
    step = 0.3

    prev_score = None

    for iteration in range(20):

        print(f"\nIteration {iteration}")

        for key in coeffs:

            best_val = coeffs[key]
            best_score = None

            for delta in [-step, step]:

                test = coeffs.copy()
                test[key] += delta

                phase = base_phase + zernike_modes(X, Y, test)

                slm.send(phase)
                time.sleep(0.05)

                img = camera.receive()
                score = metric(img)

                print(f"{key} {delta:+} → {score:.4f}")

                if best_score is None or score < best_score:
                    best_score = score
                    best_val = test[key]

            coeffs[key] = best_val

        print("Current:", coeffs)

        if prev_score is not None and abs(prev_score - best_score) < 1e-3:
            print("Converged ✅")
            break

        prev_score = best_score

        step *= 0.7  # refine step size

    return coeffs


# =========================
# MAIN
# =========================

def main():

    monitor = get_slm_monitor()
    slm = SLMDisplay(monitor)
    camera = CameraReceiver(port=5000)

    size = 512
    x = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, x)

    base_phase = np.zeros((size, size))

    print("Starting auto correction...")

    coeffs = optimize(camera, slm, base_phase, X, Y)

    print("\nFinal correction:", coeffs)

    # Apply final correction continuously
    while True:
        phase = base_phase + zernike_modes(X, Y, coeffs)
        slm.send(phase)


if __name__ == "__main__":
    main()
