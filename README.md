# Detector de Acordes en Tiempo Real

Un sistema de detección de acordes musicales en tiempo real que captura audio desde tu micrófono, analiza las frecuencias, identifica notas musicales y muestra los acordes detectados con una visualización gráfica.

![Detector de Acordes](https://via.placeholder.com/800x400?text=Detector+de+Acordes)

## Características

- 🎵 Detección de notas musicales en tiempo real
- 🎸 Identificación de múltiples tipos de acordes (mayor, menor, disminuido, aumentado, etc.)
- 📊 Visualización de la forma de onda del audio
- 🎯 Selección del dispositivo de entrada de audio
- 🖥️ Interfaz gráfica intuitiva

## Requisitos

- Python 3.7 o superior
- Dispositivo de entrada de audio (micrófono)

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

- `-l, --list` : Listar todos los dispositivos de audio disponibles y salir
- `-d, --device DEVICE` : Especificar el ID del dispositivo de audio a utilizar

Ejemplo:
```bash
# Listar dispositivos disponibles
python main.py --list

# Usar un dispositivo específico
python main.py --device 1
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
2. **Análisis de frecuencias**: Las muestras se procesan mediante FFT para identificar las frecuencias dominantes
3. **Detección de notas**: Las frecuencias se mapean a notas musicales
4. **Reconocimiento de acordes**: Se identifican patrones de acordes basados en las notas detectadas
5. **Visualización**: Se muestra la forma de onda y los acordes en tiempo real

## Contribución

Las contribuciones son bienvenidas. Por favor, siente libre de:

1. Fork este repositorio
2. Crear una rama (`git checkout -b feature/nueva-caracteristica`)
3. Hacer cambios y commit (`git commit -am 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).
