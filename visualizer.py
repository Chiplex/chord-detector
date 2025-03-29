import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import time

class AudioVisualizer:
    def __init__(self):
        # Configurar la ventana de visualización
        plt.style.use('dark_background')  # Mejor estilo para visualización
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        
        # Para la forma de onda
        self.line, = self.ax.plot([], [], lw=2, color='cyan')
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1000)  # Ajustar según el tamaño de chunk
        self.ax.set_title('Forma de Onda de Audio', color='white', fontsize=14)
        self.ax.set_xlabel('Muestras', color='white')
        self.ax.set_ylabel('Amplitud', color='white')
        self.ax.grid(True, alpha=0.3)
        
        # Cambiar el color de los ejes para mejor visibilidad
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        
        # Para mostrar el acorde detectado y las notas
        self.chord_text = self.ax.text(0.5, 0.95, '', transform=self.ax.transAxes,
                                       ha='center', va='top', fontsize=16, color='yellow',
                                       bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        # Para animación
        self.anim = None
        
        # Datos actuales
        self.audio_data = np.zeros(1000)
        self.current_chord = "N/A"
        self.current_notes = []
        
        # Control de tiempo para limitar FPS
        self.last_update = time.time()
        self.fps_limit = 30  # Limitar a 30 FPS para reducir uso de CPU
    
    def update_plot(self, frame):
        # Limitar la tasa de actualización para reducir uso de CPU
        current_time = time.time()
        if current_time - self.last_update < 1.0/self.fps_limit:
            return self.line, self.chord_text
            
        self.last_update = current_time
        
        # Actualizar la forma de onda
        x = np.arange(len(self.audio_data))
        y = self.audio_data
        self.line.set_data(x, y)
        
        # Actualizar el texto del acorde y notas
        notes_str = ", ".join(self.current_notes[:5]) if self.current_notes else "Ninguna nota detectada"
        display_text = f"Acorde: {self.current_chord}\nNotas: {notes_str}"
        self.chord_text.set_text(display_text)
        
        return self.line, self.chord_text
    
    def update_data(self, audio_data, chord, notes):
        self.audio_data = audio_data
        self.current_chord = chord
        self.current_notes = notes
    
    def start(self):
        # Iniciar la animación con save_count para evitar la advertencia
        self.anim = FuncAnimation(self.fig, self.update_plot, 
                                  frames=None, 
                                  interval=50, 
                                  blit=True,
                                  cache_frame_data=False)  # Evita la memoria ilimitada
        plt.show(block=False)
        plt.pause(0.1)  # Pequeña pausa para que la ventana aparezca
    
    def stop(self):
        if self.anim:
            self.anim.event_source.stop()
            plt.close(self.fig)
