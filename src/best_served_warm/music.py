"""Music playback and frequency measurements from the bundled lo-fi track."""
import numpy as np
import pygame
from .paths import asset_path


class Music:
    def __init__(self, analyze: bool = False):
        self.path = asset_path("audio", "chill-lofi.mp3")
        self.energies = None
        self.available = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            pygame.mixer.music.load(str(self.path))
            pygame.mixer.music.play(-1, fade_ms=2400)
            self.available = True
            if analyze:
                self._analyze()
        except pygame.error:
            pass

    def _analyze(self) -> None:
        sound = pygame.mixer.Sound(str(self.path))
        samples = pygame.sndarray.array(sound).astype(np.float32) / 32768.0
        if samples.ndim == 2:
            samples = samples.mean(axis=1)
        sample_rate = pygame.mixer.get_init()[0]
        self.duration = len(samples) / sample_rate
        self.hop = 1024
        self.rate = sample_rate / self.hop
        size = 2048
        window = np.hanning(size).astype(np.float32)
        frequencies = np.fft.rfftfreq(size, 1 / sample_rate)
        edges = np.geomspace(65, 6500, 29)
        bands = [(max(1, int(np.searchsorted(frequencies, edges[i]))), max(2, int(np.searchsorted(frequencies, edges[i+1])))) for i in range(28)]
        self.energies = np.empty((max(1, (len(samples)-size)//self.hop + 1), 28), dtype=np.float32)
        for i in range(len(self.energies)):
            spectrum = np.abs(np.fft.rfft(samples[i*self.hop:i*self.hop+size] * window))
            self.energies[i] = [np.sqrt(np.mean(spectrum[a:max(a+1,b)]**2)) for a,b in bands]
        reference = np.maximum(np.percentile(self.energies, 90, axis=0), 0.01)
        self.energies = np.clip((self.energies / reference) ** 0.65, 0, 1.3)

    def set_volume(self, volume: float) -> None:
        if self.available:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)) * 0.55)

    def levels(self) -> np.ndarray:
        if self.energies is None or not self.available or not pygame.mixer.music.get_busy():
            return np.zeros(28, dtype=np.float32)
        position = max(0, pygame.mixer.music.get_pos()) / 1000.0 % self.duration
        index = min(len(self.energies)-1, int(position*self.rate))
        return self.energies[index]

    def close(self) -> None:
        if self.available:
            pygame.mixer.music.stop()
