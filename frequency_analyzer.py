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
    
    def __init__(self, sampling_rate=44100, sensitivity=0.1, freq_tolerance=10.0):
        self.sampling_rate = sampling_rate
        self.sensitivity = sensitivity  # Sensibilidad de detección (0.01-1.0)
        self.freq_tolerance = freq_tolerance  # Tolerancia en Hz para identificación de notas
        
        # Inicializar arrays para todas las octavas (de 1 a 8)
        self.all_notes = {}
        for octave in range(1, 9):
            for note, freq in self.NOTE_FREQUENCIES.items():
                # Ajustar la frecuencia para cada octava
                adjusted_freq = freq * (2 ** (octave - 4)) if octave != 4 else freq
                self.all_notes[f"{note}{octave}"] = adjusted_freq
    
    def analyze(self, audio_data, min_amplitude=0.005):
        # Normalización del audio para mejorar la detección
        amplitude = np.max(np.abs(audio_data))
        if amplitude > min_amplitude:
            # Normalizar la señal para mejorar detección con señales débiles
            normalized_data = audio_data / (amplitude + 1e-10)  # Evita división por cero
            
            # Aplicar ventana Hanning para reducir fugas espectrales
            window = np.hanning(len(normalized_data))
            windowed_data = normalized_data * window
            
            # Realizar la FFT para obtener el espectro de frecuencias
            fft_data = np.abs(np.fft.rfft(windowed_data))
            freqs = np.fft.rfftfreq(len(windowed_data), 1/self.sampling_rate)
            
            # Calcular el umbral dinámico basado en la sensibilidad
            # Ajustamos un poco para ser menos restrictivos con señales débiles
            threshold = np.max(fft_data) * self.sensitivity
            
            # Encontrar picos en el espectro con umbral dinámico
            # Disminuir distancia mínima para captar notas cercanas
            peaks, properties = find_peaks(fft_data, height=threshold, distance=15)
            
            # Ordenar picos por amplitud (de mayor a menor)
            peak_heights = properties['peak_heights']
            sorted_indices = np.argsort(-peak_heights)  # Orden descendente
            sorted_peaks = peaks[sorted_indices]
            
            # Ajustamos el número máximo de notas según la complejidad del audio
            max_notes = min(12, max(3, int(len(sorted_peaks) * 0.3)))
            sorted_peaks = sorted_peaks[:max_notes]
            
            detected_notes = []
            for peak_idx in sorted_peaks:
                if peak_idx < len(freqs):
                    freq = freqs[peak_idx]
                    # Ampliar rango para captar más notas
                    if 50 <= freq <= 5000:  # Rango más amplio
                        note = self._find_closest_note(freq)
                        if note != "Unknown":
                            # Eliminar duplicados por octava pero preservar notas importantes
                            base_note = note[:-1]  # Eliminar número de octava
                            if not any(base_note == n[:-1] for n in detected_notes):
                                detected_notes.append(note)
            
            return detected_notes
        return []
    
    def _find_closest_note(self, frequency):
        # Encuentra la nota más cercana a una frecuencia dada
        min_distance = float('inf')
        min_relative_distance = float('inf')
        closest_note = None
        
        for note, note_freq in self.all_notes.items():
            # Cálculo de distancia absoluta
            distance = abs(frequency - note_freq)
            
            # Cálculo de distancia relativa (porcentaje de la frecuencia)
            relative_distance = distance / note_freq
            
            # Usar distancia relativa para notas más altas y absolutas para más bajas
            # Mayor tolerancia para frecuencias más altas
            tolerance = self.freq_tolerance * (1 + 0.1 * (note_freq / 440))
            
            if relative_distance < min_relative_distance and distance < tolerance:
                min_relative_distance = relative_distance
                min_distance = distance
                closest_note = note
        
        return closest_note if closest_note else "Unknown"
