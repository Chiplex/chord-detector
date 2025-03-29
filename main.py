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
    def __init__(self, device_index=None):
        self.current_audio_data = None
        self.analyzer = FrequencyAnalyzer()
        self.detector = ChordDetector()
        
        # Inicializar el visualizador
        self.visualizer = AudioVisualizer()
        
        # Inicializar el capturador de audio con el dispositivo seleccionado
        self.audio_capture = AudioCapture(self.process_audio, device_index=device_index)
        
        # Estado actual
        self.current_chord = "N/A"
        self.current_notes = []
        
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
        selected_device = next((dev for dev in devices if dev[0] == choice), None)
        
        if (selected_device):
            device_id, device_name = selected_device
            print(f"{Fore.GREEN}Dispositivo seleccionado: {device_name}{Style.RESET_ALL}")
            return device_id
        
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
    return parser.parse_args()

if __name__ == "__main__":
    # Inicializar colorama para usar colores en Windows
    init()
    
    args = parse_args()
    
    # Si se solicitó solo listar los dispositivos
    if args.list:
        AudioCapture.list_audio_devices()
        exit(0)
    
    device_id = args.device
    
    # Si no se especificó un dispositivo, permitir elegirlo
    if device_id is None:
        print(f"{Fore.CYAN}=== Detector de Acordes en Tiempo Real ==={Style.RESET_ALL}")
        device_id = choose_audio_device()
    
    app = ChordDetectorApp(device_index=device_id)
    app.run()
