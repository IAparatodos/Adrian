# 🃏 Constructor de Mazos de Commander - Magic: The Gathering

Una aplicación web moderna para construir mazos de Commander con recomendaciones inteligentes basadas en sinergia y gestión de presupuesto.

## Características

- 🔍 **Búsqueda de Cartas**: Busca cualquier carta de Magic usando la API de Scryfall
- 🎯 **Recomendaciones de Sinergia**: Algoritmo inteligente que analiza:
  - Colores e identidad de color
  - Tipos de carta y supertypes
  - Palabras clave y mecánicas
  - Texto de habilidades
  - Curva de maná
  - Temas y arquetipos (tribal, tokens, graveyard, etc.)
- 💰 **Gestión de Presupuesto**:
  - Precios en tiempo real de CardMarket (EUR)
  - Filtro por precio máximo por carta
  - Cálculo automático del costo total del mazo
- 🎲 **Comandante Aleatorio**: Descubre nuevos comandantes
- 🎨 **Interfaz Moderna**: Diseño responsive con tema oscuro

## Tecnologías

### Backend
- **Python 3.8+**
- **Flask**: Framework web
- **Requests**: Cliente HTTP para API de Scryfall
- **Flask-CORS**: Manejo de CORS

### Frontend
- **HTML5/CSS3**: Interfaz moderna y responsive
- **JavaScript (Vanilla)**: Sin frameworks pesados
- **Gradientes y Animaciones**: UX fluida

### API
- **Scryfall API**: Base de datos completa de Magic
  - Más de 25,000 cartas
  - Precios actualizados diariamente
  - Múltiples formatos y legalities

## Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clona el repositorio**
```bash
git clone <tu-repositorio>
cd mtg-commander-builder
```

2. **Crea un entorno virtual (recomendado)**
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instala las dependencias**
```bash
pip install -r requirements.txt
```

4. **Inicia el servidor**
```bash
cd backend
python app.py
```

5. **Abre tu navegador**
```
http://localhost:5000
```

## Uso

### 1. Selecciona un Comandante

Hay dos formas de elegir tu comandante:

- **Búsqueda manual**: Escribe el nombre del comandante (ej: "Atraxa, Praetors' Voice")
- **Aleatorio**: Haz click en "Comandante Aleatorio" para descubrir opciones

### 2. Define tu Presupuesto (Opcional)

- Establece un precio máximo por carta en EUR
- Las recomendaciones solo mostrarán cartas dentro de tu presupuesto
- Deja vacío para ver todas las opciones

### 3. Añade Cartas al Mazo

- Escribe el nombre de cartas que ya sabes que quieres incluir
- Estas cartas se usarán como referencia para las recomendaciones
- El presupuesto total se calcula automáticamente

### 4. Obtén Recomendaciones

- Haz click en "Obtener Recomendaciones"
- El algoritmo analizará sinergias y mostrará:
  - **Score de Sinergia**: 0-100% basado en compatibilidad
  - **Temas**: Mecánicas y arquetipos compartidos
  - **Precio**: Costo actual en EUR
  - **Imagen**: Visualización de la carta

### 5. Construye tu Mazo

- Añade cartas recomendadas con un click
- Elimina cartas que no te convenzan
- Máximo 100 cartas (estándar de Commander)

## Estructura del Proyecto

```
mtg-commander-builder/
├── backend/
│   ├── app.py                 # Servidor Flask principal
│   ├── scryfall_api.py        # Cliente de API de Scryfall
│   └── synergy_analyzer.py    # Motor de análisis de sinergias
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css     # Estilos de la aplicación
│   │   └── js/
│   │       └── app.js         # Lógica del frontend
│   └── templates/
│       └── index.html         # Página principal
├── requirements.txt           # Dependencias de Python
└── README.md                  # Este archivo
```

## API Endpoints

### `GET /api/search-card`
Busca una carta por nombre
- **Query params**: `name` (string)
- **Respuesta**: Datos completos de la carta

### `POST /api/get-recommendations`
Obtiene recomendaciones de cartas
- **Body**:
  ```json
  {
    "deck_cards": ["carta1", "carta2"],
    "commander": "nombre_comandante",
    "budget_max": 5.0,
    "num_recommendations": 20
  }
  ```
- **Respuesta**: Lista de cartas recomendadas con scores

### `POST /api/calculate-deck-cost`
Calcula el costo total del mazo
- **Body**:
  ```json
  {
    "deck_cards": ["carta1", "carta2"],
    "currency": "eur"
  }
  ```
- **Respuesta**: Costo total y desglose

### `GET /api/random-commander`
Obtiene un comandante aleatorio

### `GET /api/search-commanders`
Busca comandantes por colores
- **Query params**: `colors` (string, ej: "W,U,B")

## Algoritmo de Sinergias

El analizador de sinergias evalúa múltiples factores:

1. **Colores (10%)**: Identidad de color compartida usando similitud de Jaccard
2. **Tipos (15%)**: Compatibilidad de tipos de carta (criatura, instant, artefacto, etc.)
3. **Palabras Clave (40%)**: Mecánicas compartidas (Flying, Trample, etc.)
4. **Texto Oracle (25%)**: Análisis de habilidades y temas mediante regex:
   - Draw/Card advantage
   - Ramp/Mana acceleration
   - Removal
   - Tribal synergies
   - Tokens
   - Graveyard interactions
   - Counters (+1/+1, proliferate)
   - Combat abilities
   - ETB effects
   - Sacrifice/aristocrats
   - Cost reduction
   - Storm/spellslinger
5. **Curva de Maná (10%)**: Equilibrio de costes de maná

**Score final**: 0-100% indicando compatibilidad total

## Limitaciones y Consideraciones

- **Rate Limiting**: La API de Scryfall tiene límite de ~10 requests/segundo. El cliente implementa delays automáticos.
- **Precios**: Los precios provienen de Scryfall y se actualizan diariamente. Pueden variar.
- **Almacenamiento**: Actualmente el mazo se guarda solo en memoria (sesión). Para persistencia, añadir base de datos.
- **Cartas Multicolor**: El algoritmo respeta la identidad de color del comandante.

## Mejoras Futuras

- [ ] Persistencia de mazos (base de datos)
- [ ] Exportar mazo a formatos populares (TappedOut, Moxfield)
- [ ] Análisis de curva de maná visual
- [ ] Comparación con mazos populares de EDHREC
- [ ] Autenticación de usuarios
- [ ] Compartir mazos vía URL
- [ ] Análisis de sinergias más profundo con ML
- [ ] Soporte para otros formatos (Modern, Standard)

## Recursos

- **Scryfall API**: https://scryfall.com/docs/api
- **EDHREC**: https://edhrec.com (inspiración)
- **CardMarket**: https://www.cardmarket.com/es/Magic (precios)
- **MTG Official Rules**: https://magic.wizards.com/en/rules

## Licencia

Este proyecto usa la API pública de Scryfall. Los datos de cartas son propiedad de Wizards of the Coast.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Autor

Desarrollado con ❤️ para la comunidad de Magic: The Gathering

---

**¡Disfruta construyendo mazos épicos de Commander!** 🎴✨
