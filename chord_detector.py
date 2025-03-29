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
    # Aumentamos significativamente el peso de las terceras para favorecer acordes mayores/menores
    INTERVAL_WEIGHTS = {
        0: 1.0,   # Raíz (tónica)
        3: 1.2,   # Tercera menor - Aumentamos su peso
        4: 1.2,   # Tercera mayor - Aumentamos su peso
        7: 0.8,   # Quinta justa
        10: 0.6,  # Séptima menor
        11: 0.6,  # Séptima mayor
        2: 0.4,   # Segunda (para sus2) - Reducimos su peso
        5: 0.4,   # Cuarta (para sus4) - Reducimos su peso
    }
    
    # Prioridad de tipos de acordes (mayor valor = mayor prioridad)
    CHORD_TYPE_PRIORITY = {
        'major': 10,     # Mayor prioridad para acordes mayores
        'minor': 9,      # Alta prioridad para acordes menores
        'dominant7': 8,  
        'major7': 7,
        'minor7': 7,
        'major6': 6,
        'minor6': 6,
        'diminished': 5,
        'augmented': 4,
        'add9': 3,
        'sus4': 2,       # Baja prioridad para sus4
        'sus2': 1,       # La prioridad más baja para sus2
    }
    
    # Notas musicales en orden cromático
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self, confidence_threshold=0.6):
        self.confidence_threshold = confidence_threshold
        # Para evitar cambios bruscos de acordes (memoria)
        self.previous_chord = None
        self.persistence_count = 0
        # Umbral especial para acordes sus (debe ser más alto para evitar falsos positivos)
        self.sus_threshold = confidence_threshold * 1.2
    
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
        chord_candidates = []
        
        for root_idx, root_note in enumerate(unique_notes):
            # Reorganizar notas para que la posible raíz sea la primera
            reordered_notes = unique_notes[root_idx:] + unique_notes[:root_idx]
            
            # Convertir a intervalos relativos (semitonos desde la raíz)
            intervals = self._notes_to_intervals(reordered_notes)
            
            # Verificar contra patrones de acordes
            for chord_type, pattern in self.CHORD_PATTERNS.items():
                match_score = self._calculate_match_score(intervals, pattern)
                
                # Si tiene buena puntuación, agregarlo como candidato
                if match_score > 0.3:  # Umbral mínimo para considerar un candidato
                    # Para acordes sus, requerir una puntuación más alta
                    if chord_type.startswith('sus') and match_score < self.sus_threshold:
                        continue
                    
                    # Aplicar bono de prioridad por tipo de acorde
                    priority_bonus = self.CHORD_TYPE_PRIORITY.get(chord_type, 0) * 0.01
                    adjusted_score = match_score + priority_bonus
                    
                    chord_candidates.append((f"{root_note} {chord_type}", adjusted_score))
        
        # Ordenar candidatos por puntuación (de mayor a menor)
        chord_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Seleccionar el mejor candidato
        if chord_candidates:
            best_chord, best_score = chord_candidates[0]
        
        # Solo actualizar el acorde anterior si tenemos suficiente confianza
        if best_score >= self.confidence_threshold:
            # Verificación adicional: si el mejor acorde es "sus" y hay un acorde mayor/menor cercano,
            # favorecer el acorde mayor/menor si la diferencia de puntuación es pequeña
            if best_chord and ('sus' in best_chord):
                for candidate, score in chord_candidates:
                    if ('major' in candidate or 'minor' in candidate) and not 'sus' in candidate:
                        if best_score - score < 0.1:  # Si la diferencia es pequeña
                            best_chord = candidate
                            break
            
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
        pattern_matches = 0
        for interval in pattern_intervals:
            if interval in detected_intervals:
                # Usar pesos para darle más importancia a ciertos intervalos
                weight = self.INTERVAL_WEIGHTS.get(interval, 0.5)
                score += weight
                pattern_matches += 1
        
        # Fuerte penalización si falta la raíz o la quinta
        if 0 not in detected_intervals:  # Falta la raíz
            score -= 1.0
        if 7 not in detected_intervals and 7 in pattern_intervals:  # Falta la quinta
            score -= 0.5
            
        # Verificar si hay una tercera (3 o 4) para diferenciar mejor sus vs mayor/menor
        has_third = (3 in detected_intervals) or (4 in detected_intervals)
        has_sus_note = (2 in detected_intervals) or (5 in detected_intervals)
        
        # Si el patrón incluye una tercera y la detección incluye una tercera
        if (3 in pattern_intervals or 4 in pattern_intervals) and has_third:
            # Bono adicional para reforzar la detección de la tercera
            score += 0.3
            
        # Si el patrón es sus pero hay una tercera, penalizar
        if (2 in pattern_intervals or 5 in pattern_intervals) and has_third:
            score -= 0.2
        
        # Si detectamos muy pocos de los intervalos del patrón, fuerte penalización
        if pattern_matches < len(pattern_intervals) * 0.6:
            score *= 0.7
        
        # Normalizar puntuación por el número de intervalos en el patrón
        normalized_score = score / len(pattern_intervals)
        
        # Bonus si todos los intervalos esenciales están presentes
        essential_intervals = [i for i in pattern_intervals if i in [0, 3, 4, 7]]  # Tónica, 3ra, 5ta
        if essential_intervals and all(i in detected_intervals for i in essential_intervals):
            normalized_score += 0.15
            
        return normalized_score
