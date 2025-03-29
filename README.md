# Detector de Acordes en Tiempo Real

Un sistema de detección de acordes musicales en tiempo real que captura audio desde tu micrófono, analiza las frecuencias, identifica notas musicales y muestra los acordes detectados con una visualización gráfica.

![Detector de Acordes](https://via.placeholder.com/800x400?text=Detector+de+Acordes)

## Características

- 🎵 Detección de notas musicales en tiempo real
- 🎸 Identificación de múltiples tipos de acordes (mayor, menor, 7a, sus4, etc.)
- 📊 Visualización de la forma de onda del audio en tiempo real
- 🎯 Selección flexible del dispositivo de entrada de audio
- 🔧 Ajustes de sensibilidad para adaptarse a diferentes instrumentos y entornos
- 🎛️ Control del umbral de confianza para la detección de acordes
- 🖥️ Interfaz gráfica optimizada con bajo consumo de CPU

## Requisitos

- Python 3.7 o superior
- Dispositivo de entrada de audio (micrófono)
- Las dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/Chiplex/chord-detector.git
cd chord-detector
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Ejecuta el programa principal:
```bash
python main.py
```

2. Selecciona el dispositivo de entrada de audio cuando se te solicite
3. Toca un instrumento o reproduce música cerca del micrófono
4. Observa la visualización y los acordes detectados
5. Cierra la ventana gráfica o presiona Ctrl+C en la terminal para salir

## Opciones de línea de comandos

- `-l, --list`: Listar todos los dispositivos de audio disponibles y salir
- `-d, --device DEVICE`: Especificar el ID del dispositivo de audio a utilizar
- `-r, --rate RATE`: Frecuencia de muestreo en Hz (por defecto: 44100)
- `-c, --chunk CHUNK`: Tamaño del fragmento de audio (por defecto: 4096)
- `-s, --sensitivity SENSITIVITY`: Sensibilidad de detección de notas (0.01-1.0, por defecto: 0.1)
- `-t, --threshold THRESHOLD`: Umbral de confianza para detección de acordes (0.0-1.0, por defecto: 0.6)
- `-nv, --no-visual`: Ejecutar sin visualización gráfica (experimental)

Ejemplo:
```bash
# Listar dispositivos disponibles
python main.py --list

# Usar un dispositivo específico
python main.py --device 1

# Ajustar sensibilidad para instrumentos más suaves
python main.py --sensitivity 0.05

# Aumentar umbral de confianza para detección más precisa
python main.py --threshold 0.7

# Combinación de parámetros para entornos ruidosos
python main.py --device 2 --sensitivity 0.2 --threshold 0.5
```

## Componentes

El proyecto está organizado en varios módulos:

- `main.py`: Punto de entrada principal y coordinación de componentes
- `audio_capture.py`: Maneja la captura de audio desde dispositivos de entrada
- `frequency_analyzer.py`: Analiza las frecuencias para detectar notas musicales
- `chord_detector.py`: Identifica acordes basados en las notas detectadas
- `visualizer.py`: Proporciona una visualización gráfica del audio y los acordes

## Cómo funciona

1. **Captura de audio**: El sistema captura muestras de audio desde el micrófono
2. **Análisis de frecuencias**: Las muestras se procesan mediante FFT con ventana Hanning para identificar las frecuencias dominantes
3. **Detección de notas**: Las frecuencias se mapean a notas musicales con algoritmos de tolerancia adaptativa
4. **Reconocimiento de acordes**: Se aplica un sistema de puntuación ponderada para identificar patrones de acordes basados en las notas detectadas
5. **Estabilización**: Se implementa persistencia temporal para evitar cambios bruscos entre acordes
6. **Visualización**: Se muestra la forma de onda y los acordes en tiempo real con optimizaciones de rendimiento

## Ajuste para diferentes situaciones

- **Guitarras acústicas**: Sensibilidad 0.05-0.1, Umbral 0.5-0.6
- **Pianos/Teclados**: Sensibilidad 0.1-0.15, Umbral 0.6-0.7
- **Ambientes ruidosos**: Sensibilidad 0.15-0.2, Umbral 0.4-0.5
- **Detección de acordes complejos**: Sensibilidad 0.05, Umbral 0.4

## Contribución

Las contribuciones son bienvenidas. Por favor, siente libre de:

1. Fork este repositorio
2. Crear una rama (`git checkout -b feature/nueva-caracteristica`)
3. Hacer cambios y commit (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).
