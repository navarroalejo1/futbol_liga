# Proyecto Boxscore Fútbol

Recolecta datos de partidos de fútbol en CSV y genera un boxscore estadístico.

## Instrucciones

1. Coloca tus archivos CSV en la carpeta `data/`.
2. Instala dependencias:  
   ```
   pip install -r requirements.txt
   ```
3. Ejecuta el script:
   ```
   python src/main.py data/partido1.csv
   ```
4. El boxscore aparecerá en la carpeta `output/`.

## Formato CSV esperado

```
fecha,local,visitante,nombre,numero,tiempo,pases,recuperaciones,perdidas,asistencia,centro,tiro directo,tiro desviado,gol,tarjetas
2025-06-21,EquipoA,EquipoB,Juan Perez,10,90,45,7,3,1,2,4,1,2,amarilla
```# futbol_liga
recoleccion de datos futbol liga
