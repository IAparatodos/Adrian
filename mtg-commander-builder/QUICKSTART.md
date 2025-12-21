# 🚀 Guía de Inicio Rápido

## Instalación en 3 Pasos

### Linux / macOS

```bash
# 1. Navega al directorio
cd mtg-commander-builder

# 2. Ejecuta el script de inicio (instala y arranca automáticamente)
./run.sh
```

### Windows

```cmd
# 1. Navega al directorio
cd mtg-commander-builder

# 2. Ejecuta el script de inicio
run.bat
```

## Instalación Manual

Si los scripts no funcionan, sigue estos pasos:

```bash
# 1. Crea un entorno virtual
python3 -m venv venv

# 2. Activa el entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Inicia el servidor
cd backend
python app.py
```

## Primer Uso

1. Abre tu navegador en `http://localhost:5000`

2. **Busca un comandante**:
   - Escribe "Atraxa, Praetors' Voice" en el primer campo
   - Haz click en "Buscar"
   - O prueba "Comandante Aleatorio"

3. **Define presupuesto** (opcional):
   - Ejemplo: "5.00" para cartas de máximo 5 EUR

4. **Añade algunas cartas** que ya tengas en mente:
   - "Sol Ring"
   - "Command Tower"
   - "Arcane Signet"

5. **Obtén recomendaciones**:
   - Click en "Obtener Recomendaciones"
   - Revisa las cartas sugeridas con sus scores de sinergia
   - Añade las que te gusten al mazo

## Ejemplos de Comandantes Populares

- **Atraxa, Praetors' Voice** (4 colores - Proliferar)
- **Edgar Markov** (Vampiros tribal)
- **Ur-Dragon** (Dragones tribal)
- **Kess, Dissident Mage** (Spellslinger)
- **Korvold, Fae-Cursed King** (Sacrifice/Treasures)
- **Yuriko, the Tiger's Shadow** (Ninjas/Evasion)

## Solución de Problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
Edita `backend/app.py` y cambia:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Usa otro puerto
```

### Error: "Connection refused" al buscar cartas
Verifica tu conexión a internet. La app requiere acceso a api.scryfall.com

### Las recomendaciones tardan mucho
- La API de Scryfall tiene rate limiting
- Es normal que tome 5-10 segundos para 20+ recomendaciones
- Reduce el número de recomendaciones si es muy lento

## Comandos Útiles

### Ejecutar tests
```bash
# Test de API de Scryfall
python tests/test_scryfall_api.py

# Test de analizador de sinergias
python tests/test_synergy_analyzer.py
```

### Detener el servidor
- Presiona `Ctrl + C` en la terminal

## Próximos Pasos

- Lee el [README.md](README.md) completo para documentación detallada
- Explora la [API de Scryfall](https://scryfall.com/docs/api)
- Revisa [EDHREC](https://edhrec.com) para inspiración de mazos

## ¿Necesitas Ayuda?

- Revisa la documentación en README.md
- Consulta los comentarios en el código
- Abre un issue en el repositorio

¡Disfruta construyendo mazos! 🎴✨
