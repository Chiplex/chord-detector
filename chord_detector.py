import re

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
    }
    
    # Notas musicales en orden cromático
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self):
        pass
    
    def detect_chord(self, notes):
        if not notes or len(notes) < 3:
            return "Insuficientes notas para detectar acorde"
        
        # Extraer solo los nombres de las notas (sin octava)
        note_names = [self._extract_note_name(note) for note in notes]
        
        # Eliminar duplicados y ordenar
        unique_notes = sorted(list(set(note_names)), key=lambda x: self.NOTES.index(x) if x in self.NOTES else -1)
        
        if len(unique_notes) < 3:
            return "Insuficientes notas únicas para detectar acorde"
        
        # Probar cada nota como raíz potencial del acorde
        possible_chords = []
        for root_idx, root_note in enumerate(unique_notes):
            # Reorganizar notas para que la posible raíz sea la primera
            reordered_notes = unique_notes[root_idx:] + unique_notes[:root_idx]
            
            # Convertir a intervalos relativos (semitonos desde la raíz)
            intervals = self._notes_to_intervals(reordered_notes)
            
            # Verificar contra patrones de acordes
            for chord_type, pattern in self.CHORD_PATTERNS.items():
                if self._match_pattern(intervals, pattern):
                    possible_chords.append(f"{root_note} {chord_type}")
        
        if possible_chords:
            return possible_chords[0]  # Devolver el primer acorde detectado
        else:
            return "Acorde no reconocido"
    
    def _extract_note_name(self, note_with_octave):
        # Extraer solo el nombre de la nota (C, C#, D, etc.) sin el número de octava
        match = re.match(r'([A-G][#b]?)', note_with_octave)
        if match:
            return match.group(1)
        return note_with_octave
    
    def _notes_to_intervals(self, notes):
        intervals = []
        root_idx = self.NOTES.index(notes[0])
        
        for note in notes:
            note_idx = self.NOTES.index(note)
            # Calcular intervalo (0-11) relativo a la raíz
            interval = (note_idx - root_idx) % 12
            intervals.append(interval)
        
        return intervals
    
    def _match_pattern(self, intervals, pattern):
        # Verificar si los intervalos detectados coinciden con el patrón del acorde
        # Permitir coincidencias parciales (el acorde puede tener notas adicionales)
        return all(interval in intervals for interval in pattern)
