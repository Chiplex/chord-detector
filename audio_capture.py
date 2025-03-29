import pyaudio
import numpy as np
import threading
import time

class AudioCapture:
    def __init__(self, callback, rate=44100, chunk_size=4096, device_index=None):
        self.callback = callback
        self.rate = rate
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        self.thread = None
    
    @staticmethod
    def list_audio_devices():
        """Listar todos los dispositivos de audio disponibles."""
        p = pyaudio.PyAudio()
        devices = []
        
        print("\nDispositivos de audio disponibles:")
        print("----------------------------------")
        
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            dev_name = dev_info['name']
            
            # Corregir la codificación de caracteres en los nombres de dispositivos
            try:
                # Intentar decodificar correctamente el nombre del dispositivo
                if isinstance(dev_name, bytes):
                    dev_name = dev_name.decode('utf-8')
                # Si ya es string, asegurar que los caracteres especiales se manejen correctamente
                elif isinstance(dev_name, str):
                    # Intentar normalizar caracteres problemáticos comunes
                    dev_name = dev_name.replace('Ã³', 'ó')
                    dev_name = dev_name.replace('Ã©', 'é')
                    dev_name = dev_name.replace('Ã¡', 'á')
                    dev_name = dev_name.replace('Ã­', 'í')
                    dev_name = dev_name.replace('Ãº', 'ú')
                    dev_name = dev_name.replace('Ã±', 'ñ')
            except UnicodeError:
                # Si hay un error, usar el nombre tal cual
                pass
            
            inputs = dev_info['maxInputChannels']
            
            # Solo nos interesan dispositivos con entrada (para captura)
            if inputs > 0:
                devices.append((i, dev_name))
                print(f"{i}: {dev_name} (Canales de entrada: {inputs})")
        
        p.terminate()
        return devices
    
    def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        try:
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            
        except Exception as e:
            self.is_running = False
            print(f"Error al iniciar la captura de audio: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        data = np.frombuffer(in_data, dtype=np.float32)
        self.callback(data)
        return (in_data, pyaudio.paContinue)
    
    def _run(self):
        self.stream.start_stream()
        while self.is_running and self.stream.is_active():
            time.sleep(0.1)
    
    def stop(self):
        if not self.is_running:
            return
        
        self.is_running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.thread:
            self.thread.join(timeout=1.0)
        
        self.p.terminate()
