import time
import numpy as np
import os
import argparse
import matplotlib
import matplotlib.pyplot as plt  # Añadida la importación correcta de pyplot
from colorama import Fore, Back, Style, init
from audio_capture import AudioCapture
from frequency_analyzer import FrequencyAnalyzer
from chord_detector import ChordDetector
from visualizer import AudioVisualizer

class ChordDetectorApp:
    def __init__(self, device_index=None, sensitivity=0.1, confidence_threshold=0.6, rate=44100, chunk_size=4096):
        self.current_audio_data = None
        # Usar los parámetros de sensibilidad y confianza
        self.analyzer = FrequencyAnalyzer(sampling_rate=rate, sensitivity=sensitivity)
        self.detector = ChordDetector(confidence_threshold=confidence_threshold)
        
        # Inicializar el visualizador
        self.visualizer = AudioVisualizer()
        
        # Inicializar el capturador de audio con el dispositivo seleccionado
        self.audio_capture = AudioCapture(self.process_audio, rate=rate, chunk_size=chunk_size, device_index=device_index)
        
        # Estado actual
        self.current_chord = "N/A"
        self.current_notes = []
        
        # Guardar configuración
        self.sensitivity = sensitivity
        self.confidence_threshold = confidence_threshold
        
    def process_audio(self, audio_data):
        self.current_audio_data = audio_data
        
        # Analizar las notas presentes en el audio
        self.current_notes = self.analyzer.analyze(audio_data)
        
        if self.current_notes:
            # Detectar el acorde basado en las notas
            self.current_chord = self.detector.detect_chord(self.current_notes)
            
        # Actualizar el visualizador con los nuevos datos
        self.visualizer.update_data(audio_data, self.current_chord, self.current_notes)
            
    def run(self):
        # Inicializar colorama para usar colores en Windows
        init()
        
        print(f"{Fore.CYAN}=== Detector de Acordes en Tiempo Real ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Usando visualización gráfica. Cierre la ventana para salir.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Configuración: Sensibilidad={self.sensitivity}, Umbral de confianza={self.confidence_threshold}{Style.RESET_ALL}")
        
        try:
            # Iniciar visualizador
            self.visualizer.start()
            
            # Iniciar captura de audio
            self.audio_capture.start()
            
            # Mantener la aplicación corriendo
            plt.show()
                
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Deteniendo el detector de acordes...{Style.RESET_ALL}")
        finally:
            self.visualizer.stop()
            self.audio_capture.stop()
            print(f"{Fore.CYAN}¡Hasta luego!{Style.RESET_ALL}")

def choose_audio_device():
    """Permite al usuario elegir un dispositivo de audio para la captura"""
    devices = AudioCapture.list_audio_devices()
    
    if not devices:
        print(f"{Fore.RED}No se encontraron dispositivos de entrada de audio disponibles.{Style.RESET_ALL}")
        return None
    
    print(f"\n{Fore.YELLOW}Seleccione un dispositivo de audio ingresando su número:{Style.RESET_ALL}")
    
    try:
        choice = int(input(f"{Fore.GREEN}> {Style.RESET_ALL}"))
        
        # Verificar si el dispositivo existe en la lista
        device_dict = {dev[0]: dev[1] for dev in devices}
        if choice in device_dict:
            print(f"{Fore.GREEN}Dispositivo seleccionado: {device_dict[choice]}{Style.RESET_ALL}")
            return choice
        
        print(f"{Fore.RED}Dispositivo no válido. Usando el dispositivo predeterminado.{Style.RESET_ALL}")
        return None
        
    except ValueError:
        print(f"{Fore.RED}Entrada no válida. Usando el dispositivo predeterminado.{Style.RESET_ALL}")
        return None

def parse_args():
    parser = argparse.ArgumentParser(description="Detector de Acordes en Tiempo Real")
    parser.add_argument("-l", "--list", action="store_true", 
                        help="Listar dispositivos de audio disponibles y salir")
    parser.add_argument("-d", "--device", type=int, 
                        help="ID del dispositivo de audio a utilizar")
    parser.add_argument("-r", "--rate", type=int, default=44100,
                        help="Frecuencia de muestreo en Hz (por defecto: 44100)")
    parser.add_argument("-c", "--chunk", type=int, default=4096,
                        help="Tamaño del fragmento de audio (por defecto: 4096)")
    parser.add_argument("-s", "--sensitivity", type=float, default=0.1,
                        help="Sensibilidad de detección de notas (0.01-1.0, por defecto: 0.1)")
    parser.add_argument("-t", "--threshold", type=float, default=0.6,
                        help="Umbral de confianza para detección de acordes (0.0-1.0, por defecto: 0.6)")
    parser.add_argument("-nv", "--no-visual", action="store_true",
                        help="Ejecutar sin visualización gráfica")
    return parser.parse_args()

if __name__ == "__main__":
    # Inicializar colorama para usar colores en Windows
    init(autoreset=True)  # Autoreset para no tener que resetear el estilo manualmente
    
    args = parse_args()
    
    # Si se solicitó solo listar los dispositivos
    if args.list:
        devices = AudioCapture.list_audio_devices()
        if not devices:
            print(f"{Fore.RED}No se encontraron dispositivos de entrada de audio.{Style.RESET_ALL}")
        exit(0)
    
    # Validar los valores de sensibilidad y umbral
    sensitivity = max(0.01, min(1.0, args.sensitivity))
    confidence = max(0.3, min(1.0, args.threshold))
    
    device_id = args.device
    
    # Si no se especificó un dispositivo, permitir elegirlo
    if device_id is None:
        print(f"{Fore.CYAN}=== Detector de Acordes en Tiempo Real ==={Style.RESET_ALL}")
        device_id = choose_audio_device()
    
    try:
        # Crear y configurar la aplicación con los parámetros especificados
        app = ChordDetectorApp(
            device_index=device_id,
            sensitivity=sensitivity,
            confidence_threshold=confidence,
            rate=args.rate,
            chunk_size=args.chunk
        )
        
        # Si se especificó ejecutar sin visualización, modificar comportamiento
        if args.no_visual:
            print(f"{Fore.YELLOW}Modo sin visualización no implementado aún. Usando visualización estándar.{Style.RESET_ALL}")
        
        app.run()
    except Exception as e:
        print(f"{Fore.RED}Error al ejecutar la aplicación: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        exit(1)
