import numpy as np
from scipy.signal import find_peaks

class FrequencyAnalyzer:
    # Frecuencias de referencia para cada nota (C4 = 261.63 Hz, etc.)
    NOTE_FREQUENCIES = {
        'C': 261.63, 'C#': 277.18, 'Db': 277.18, 
        'D': 293.66, 'D#': 311.13, 'Eb': 311.13,
        'E': 329.63, 
        'F': 349.23, 'F#': 369.99, 'Gb': 369.99,
        'G': 392.00, 'G#': 415.30, 'Ab': 415.30,
        'A': 440.00, 'A#': 466.16, 'Bb': 466.16,
        'B': 493.88
    }
    
    def __init__(self, sampling_rate=44100):
        self.sampling_rate = sampling_rate
        # Inicializar arrays para todas las octavas (de 1 a 8)
        self.all_notes = {}
        for octave in range(1, 9):
            for note, freq in self.NOTE_FREQUENCIES.items():
                # Ajustar la frecuencia para cada octava
                adjusted_freq = freq * (2 ** (octave - 4)) if octave != 4 else freq
                self.all_notes[f"{note}{octave}"] = adjusted_freq
    
    def analyze(self, audio_data):
        # Realizar la FFT para obtener el espectro de frecuencias
        fft_data = np.abs(np.fft.rfft(audio_data))
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sampling_rate)
        
        # Encontrar picos en el espectro
        peaks, _ = find_peaks(fft_data, height=np.max(fft_data)/10, distance=20)
        
        detected_notes = []
        for peak_idx in peaks:
            if peak_idx < len(freqs):
                freq = freqs[peak_idx]
                note = self._find_closest_note(freq)
                if note not in detected_notes:
                    detected_notes.append(note)
        
        return detected_notes
    
    def _find_closest_note(self, frequency):
        # Encuentra la nota más cercana a una frecuencia dada
        min_distance = float('inf')
        closest_note = None
        
        for note, note_freq in self.all_notes.items():
            distance = abs(frequency - note_freq)
            if distance < min_distance:
                min_distance = distance
                closest_note = note
        
        return closest_note
