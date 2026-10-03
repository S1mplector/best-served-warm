"""Music playback and frequency measurements from the same bundled WAV."""
import wave
import numpy as np
import pygame
from .paths import asset_path


class Music:
    def __init__(self):
        self.path = asset_path("audio", "moon-unit.wav")
        with wave.open(str(self.path), "rb") as source:
            sample_rate = source.getframerate()
            assert source.getnchannels() == 1 and source.getsampwidth() == 2
            samples = np.frombuffer(source.readframes(source.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
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
        self.available = False
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            pygame.mixer.music.load(str(self.path))
            pygame.mixer.music.play(-1, fade_ms=2400)
            self.available = True
        except pygame.error:
            pass

    def set_volume(self, volume: float) -> None:
        if self.available:
            pygame.mixer.music.set_volume(volume)

    def levels(self) -> np.ndarray:
        if not self.available or not pygame.mixer.music.get_busy():
            return np.zeros(28, dtype=np.float32)
        position = max(0, pygame.mixer.music.get_pos()) / 1000.0 % self.duration
        index = min(len(self.energies)-1, int(position*self.rate))
        return self.energies[index]

    def close(self) -> None:
        if self.available:
            pygame.mixer.music.stop()
