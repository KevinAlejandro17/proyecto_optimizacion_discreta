## Proyecto de optimización discreta en MiniZinc (MinPol)

### Archivos entregados
- El archivo proyecto_gui.py en el directorio ProyectoGUIFuentes con la interfaz gráfica
- El archivo Proyecto.mzn con el modelo implementado en MiniZinc
- El archivo Informe.pdf

### Requisitos para la ejecución
- Tener instalado MiniZinc, puedes instalarlo desde https://www.minizinc.org/
- Agregar la ruta de MiniZinc en el PATH del sistema
- Tener instalado Python
- Agregar la ruta de Python en el PATH del sistema

### Ejecución
En la carpeta raíz, donde se encuentra el directorio ProyectoGUIFuentes ejecutar:
```
python ProyectoGUIFuentes/proyecto_gui.py
```
Se abrirá la interfaz gráfica, en ella 
1. Selecciona el archivo .mpl con los datos de entrada
2. Haz click en el botón "Convertir y Ejecutar"

Se generará el archivo .dzn convirtiendo los datos de entrada a un formato que pueda leer MiniZinc

Se ejecutará el modelo .mzn con el archivo de los datos generado
