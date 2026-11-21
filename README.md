# KatMods

Catálogo de mods de Minecraft (Fabric, MC 26.2) hechos por **Oliver**.

- **Minecraft Plus** v0.6.1
- **Titans Mod** v2.0.0

Abre `index.html` o visita la página en GitHub Pages.

## API

API JSON gratuita y sin clave: https://kikerayo.github.io/KatMods/api.html

- `GET /api/mods.json` — todos los mods
- `GET /api/mods/{id}.json` — detalle de un mod (`mcplus`, `titanes`)
- `GET /api/mods/{id}/contenido.json` — bloques, ítems y entidades

Para regenerarla después de cambiar un `.jar`: `python generar_api.py`
