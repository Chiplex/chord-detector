import re
import numpy as np

class ChordDetector:
    # Patrones básicos de acordes (intervalos relativos)
    CHORD_PATTERNS = {
        'major': [0, 4, 7],          # Ejemplo: C, E, G
        'minor': [0, 3, 7],          # Ejemplo: C, Eb, G
        'diminished': [0, 3, 6],     # Ejemplo: C, Eb, Gb
        'augmented': [0, 4, 8],      # Ejemplo: C, E, G#
        'sus2': [0, 2, 7],           # Ejemplo: C, D, G
        'sus4': [0, 5, 7],           # Ejemplo: C, F, G
        'major7': [0, 4, 7, 11],     # Ejemplo: C, E, G, B
        'minor7': [0, 3, 7, 10],     # Ejemplo: C, Eb, G, Bb
        'dominant7': [0, 4, 7, 10],  # Ejemplo: C, E, G, Bb
        '7sus4': [0, 5, 7, 10],      # Ejemplo: C, F, G, Bb
        'minor6': [0, 3, 7, 9],      # Ejemplo: C, Eb, G, A
        'major6': [0, 4, 7, 9],      # Ejemplo: C, E, G, A
        'add9': [0, 4, 7, 14],       # Ejemplo: C, E, G, D(+1 octava)
    }
    
    # Importancia relativa de cada intervalo para identificación de acordes
    INTERVAL_WEIGHTS = {
        0: 1.0,   # Raíz (tónica)
        3: 0.8,   # Tercera menor
        4: 0.8,   # Tercera mayor
        7: 0.7,   # Quinta justa
        10: 0.6,  # Séptima menor
        11: 0.6,  # Séptima mayor
    }
    
    # Notas musicales en orden cromático
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, confidence_threshold=0.6):
        self.confidence_threshold = confidence_threshold
        # Para evitar cambios bruscos de acordes (memoria)
        self.previous_chord = None
        self.persistence_count = 0
    
    def detect_chord(self, notes):
        if not notes or len(notes) < 2:  # Permitir detección con solo 2 notas
            if self.previous_chord and self.persistence_count < 3:
                self.persistence_count += 1
                return self.previous_chord  # Mantener el acorde anterior por estabilidad
            self.previous_chord = None
            return "Insuficientes notas para detectar acorde"
        
        # Extraer solo los nombres de las notas (sin octava)
        note_names = [self._extract_note_name(note) for note in notes]
        
        # Eliminar duplicados y ordenar
        unique_notes = sorted(list(set(note_names)), key=lambda x: self.NOTES.index(x) if x in self.NOTES else -1)
        
        if len(unique_notes) < 2:  # Permitir acordes con solo 2 notas
            if self.previous_chord:
                self.persistence_count += 1
                if self.persistence_count < 3:
                    return self.previous_chord
            self.previous_chord = None
            return "Insuficientes notas únicas para detectar acorde"
        
        # Probar cada nota como raíz potencial del acorde
        best_score = 0
        best_chord = None
        
        for root_idx, root_note in enumerate(unique_notes):
            # Reorganizar notas para que la posible raíz sea la primera
            reordered_notes = unique_notes[root_idx:] + unique_notes[:root_idx]
            
            # Convertir a intervalos relativos (semitonos desde la raíz)
            intervals = self._notes_to_intervals(reordered_notes)
            
            # Verificar contra patrones de acordes
            for chord_type, pattern in self.CHORD_PATTERNS.items():
                match_score = self._calculate_match_score(intervals, pattern)
                
                # Si la puntuación es mayor que la mejor hasta ahora
                if match_score > best_score:
                    best_score = match_score
                    best_chord = f"{root_note} {chord_type}"
        
        # Solo actualizar el acorde anterior si tenemos suficiente confianza
        if best_score >= self.confidence_threshold:
            self.previous_chord = best_chord
            self.persistence_count = 0
            return best_chord
        elif self.previous_chord and self.persistence_count < 3:
            # Mantener el acorde anterior por estabilidad
            self.persistence_count += 1
            return self.previous_chord
        else:
            self.persistence_count = 0
            if best_chord:
                return f"{best_chord} (baja confianza)"
            return "Acorde no reconocido"
    
    def _extract_note_name(self, note_with_octave):
        # Extraer solo el nombre de la nota (C, C#, D, etc.) sin el número de octava
        if note_with_octave == "Unknown":
            return None
            
        match = re.match(r'([A-G][#b]?)\d?', note_with_octave)
        if match:
            return match.group(1)
        return note_with_octave
    
    def _notes_to_intervals(self, notes):
        intervals = []
        if not notes or notes[0] is None:
            return intervals
            
        try:
            root_idx = self.NOTES.index(notes[0])
            
            for note in notes:
                if note is None:
                    continue
                note_idx = self.NOTES.index(note)
                # Calcular intervalo (0-11) relativo a la raíz
                interval = (note_idx - root_idx) % 12
                intervals.append(interval)
        except ValueError:
            # En caso de problemas con el índice
            pass
        
        return intervals
    
    def _calculate_match_score(self, detected_intervals, pattern_intervals):
        """Calcula una puntuación de coincidencia entre los intervalos detectados y un patrón de acorde"""
        if not detected_intervals or not pattern_intervals:
            return 0.0
            
        score = 0.0
        
        # Verificar cuántos intervalos del patrón están presentes
        for interval in pattern_intervals:
            if interval in detected_intervals:
                # Usar pesos para darle más importancia a ciertos intervalos
                weight = self.INTERVAL_WEIGHTS.get(interval, 0.5)
                score += weight
        
        # Penalizar por intervalos adicionales que no pertenecen al patrón
        extra_intervals = [i for i in detected_intervals if i not in pattern_intervals]
        if extra_intervals:
            # Penalizar menos si son intervalos posibles de extensiones
            for interval in extra_intervals:
                if interval in [2, 9, 13, 14]:  # 9ª, 2ª, 13ª, etc.
                    score -= 0.1
                else:
                    score -= 0.2
        
        # Normalizar puntuación por el número de intervalos en el patrón
        normalized_score = score / len(pattern_intervals)
        
        # Bonus si todos los intervalos esenciales están presentes
        essential_intervals = [i for i in pattern_intervals if i in [0, 3, 4, 7]]  # Tónica, 3ra, 5ta
        if all(i in detected_intervals for i in essential_intervals):
            normalized_score += 0.2
        
        return normalized_score
