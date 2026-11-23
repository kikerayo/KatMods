"""Genera la API estática de KatMods en la carpeta api/.

Uso:  python generar_api.py
Lee los .jar de descargas/ (fabric.mod.json y el idioma es_es) y escribe los JSON.
Para añadir un mod: pon su .jar en descargas/ y añade una entrada en MODS.
"""
import hashlib
import json
import zipfile
from pathlib import Path
from urllib.parse import quote

BASE = "https://kikerayo.github.io/KatMods"
RAIZ = Path(__file__).parent
API = RAIZ / "api"

MODS = {
    "mcplus": {
        "nombre": "Minecraft Plus",
        "jar": "mcplus-0.6.1.jar",
        "version": "0.6.1",
        "categorias": ["aventura", "tecnologia", "jefes"],
        "resumen": "El mod universal: añade de todo a Minecraft, desde el End y el espacio hasta tecnología, armas, comida, gatos y desafíos.",
        "novedades": [
            "End Update: Cristal del Vacío, armadura y herramientas del Vacío",
            "Space Update: cohetes, traje espacial y planetas",
            "Update 3: armas, tecnología, Lord Ender y GOD",
            "Mega Expansión: 5 reinos, dimensiones de bolsillo, Wither Storm, consola con robot y más",
        ],
    },
    "titanes": {
        "nombre": "Titans Mod",
        "subtitulo": "Titanes: La Furia de Kat",
        "jar": "titanes-2.0.0.jar",
        "version": "2.0.0",
        "categorias": ["aventura", "jefes"],
        "resumen": "Jefes titánicos gigantes, el Titán Kat cósmico como jefe final y nuevas armaduras y herramientas legendarias.",
        "novedades": [
            "Titanes: Gorgoth, Osario, la Tejedora Abismal y el Rey Ceniza",
            "Jefe final: Titán Kat, la Gata Cósmica",
            "Pepinus: Gato Pepino, Gato Pepinus y Pepinus Dios",
            "Equipo: sets de Titanita y Cósmico, Bastón Láser Kat",
        ],
    },
    "oliversupreme": {
        "nombre": "Oliver Supreme",
        "subtitulo": "Cheat menu",
        "jar": "oliversupreme-3.0.0+26.2.jar",
        "version": "3.0.0",
        "icono": "icon.svg",
        "categorias": ["cheats"],
        "resumen": "Cheat menu de Oliver con 59 módulos en 4 categorías (Combat, Movement, Render y Player). Se abre con Shift derecho.",
        "advertencia": "Esto es un cheat menu. Usarlo en servidores multijugador puede hacer que te baneen. Oliver no se hace responsable de los baneos ni de ninguna consecuencia por usar este mod.",
        "novedades": [
            "Combat: KillAura, TriggerBot, AimAssist, Criticals, AutoTotem, Velocity, Reach",
            "Movement: Fly, Speed, BunnyHop, NoFall, Spider, Jesus, Step, ElytraFly",
            "Render: ESP, Fullbright, Radar, InfoHUD, ArmorHUD, TargetHUD, Zoom",
            "Player: Scaffold, Nuker, ChestStealer, AutoTool, AutoEat, AutoFish, AntiAFK",
        ],
    },
    "devorador": {
        "nombre": "Oliver's Devorador",
        "jar": "devorador-1.0.0.jar",
        "version": "1.0.0",
        "categorias": ["jefes"],
        "resumen": "Un wither corrompido y gigante que arranca el terreno con rayos tractores morados, se come lo que levanta y crece en 4 fases. Se invoca con una T de obsidiana llorosa y 3 cráneos de esqueleto wither.",
        "novedades": [
            "Ritual: T de obsidiana llorosa + 3 cráneos de esqueleto wither",
            "Rayos tractores que arrancan bloques y jalan mobs y jugadores",
            "4 fases: Brote, Hambriento, Colosal y Supremo (unos 30 bloques de alto)",
            "Punto débil: al digerir recibe el triple de daño",
        ],
    },
    "iblock": {
        "nombre": "iBlock",
        "subtitulo": "Teléfono, Laptop y Tele",
        "jar": "iblock-1.0.0.jar",
        "version": "1.0.0",
        "categorias": ["tecnologia"],
        "resumen": "Un iPhone dentro de Minecraft con TikTok, Instagram, Facebook, App Store, Siri y Minecraft dentro de Minecraft, internet de verdad en el teléfono y la laptop, más una tele con canales.",
        "novedades": [
            "iBlock 26 Pro Max: TikTok, Instagram, Facebook, App Store, Cámara y Ajustes",
            "Siri cambia el mundo de verdad: día/noche, lluvia, rayos, diamantes, comida y más",
            "Internet real en el teléfono y la laptop: páginas, links, imágenes y búsquedas",
            "Laptop con escritorio y ventanas, Tele con 11 canales y control remoto, y Minecraft 2D jugable",
        ],
    },
}


def escribir(ruta, datos):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def contenido(jar, modid):
    """Bloques, ítems y entidades con su nombre en español, sacados del idioma del mod."""
    try:
        lang = json.loads(jar.read(f"assets/{modid}/lang/es_es.json").decode("utf-8"))
    except KeyError:
        return {"bloques": [], "items": [], "entidades": []}
    archivos = set(jar.namelist())
    grupos = {"block": "bloques", "item": "items", "entity": "entidades"}
    salida = {v: [] for v in grupos.values()}
    # Cheat menus: cada tecla "key.<modid>.<modulo>" es un módulo.
    modulos = [n for k, n in lang.items()
               if k.startswith(f"key.{modid}.") and not k.endswith((".menu", ".main"))]
    if modulos:
        salida["modulos"] = sorted(modulos, key=str.lower)
    for clave, nombre in sorted(lang.items()):
        partes = clave.split(".")
        if len(partes) != 3 or partes[0] not in grupos or partes[1] != modid:
            continue
        tipo, _, id_ = partes
        entrada = {"id": f"{modid}:{id_}", "nombre": nombre}
        textura = f"assets/{modid}/textures/{tipo}/{id_}.png"
        if textura in archivos:
            entrada["textura"] = f"{BASE}/img/{modid}/{id_}.png" if (RAIZ / "img" / modid / f"{id_}.png").exists() else None
        salida[grupos[tipo]].append(entrada)
    for lista in salida.values():
        for e in lista:
            if not isinstance(e, dict):
                continue
            if e.get("textura") is None:
                e.pop("textura", None)
    return salida


def main():
    resumenes = []
    for modid, info in MODS.items():
        ruta_jar = RAIZ / "descargas" / info["jar"]
        datos_jar = ruta_jar.read_bytes()
        with zipfile.ZipFile(ruta_jar) as jar:
            meta = json.loads(jar.read("fabric.mod.json").decode("utf-8"))
            cont = contenido(jar, modid)

        resumen = {
            "id": modid,
            "nombre": info["nombre"],
            "version": info["version"],
            "autor": "Oliver",
            "categorias": info["categorias"],
            "resumen": info["resumen"],
            **({"advertencia": info["advertencia"]} if "advertencia" in info else {}),
            "icono": f"{BASE}/img/{modid}/{info.get('icono', 'icon.png')}",
            "descarga": f"{BASE}/descargas/{quote(info['jar'])}",
            "detalle": f"{BASE}/api/mods/{modid}.json",
        }
        resumenes.append(resumen)

        detalle = {
            **{k: v for k, v in resumen.items() if k != "detalle"},
            **({"subtitulo": info["subtitulo"]} if "subtitulo" in info else {}),
            "descripcion": meta.get("description", ""),
            "loader": "fabric",
            "lado": meta.get("environment", "*"),
            "requisitos": meta.get("depends", {}),
            "sugiere": list(meta.get("suggests", {}).keys()),
            "licencia": meta.get("license"),
            "novedades": info["novedades"],
            "totales": {k: len(v) for k, v in cont.items()},
            "archivo": {
                "nombre": info["jar"],
                "url": f"{BASE}/descargas/{quote(info['jar'])}",
                "bytes": len(datos_jar),
                "sha256": hashlib.sha256(datos_jar).hexdigest(),
            },
            "contenido": f"{BASE}/api/mods/{modid}/contenido.json",
        }
        escribir(API / "mods" / f"{modid}.json", detalle)
        escribir(API / "mods" / modid / "contenido.json", {"mod": modid, **cont})

    escribir(API / "mods.json", {"total": len(resumenes), "mods": resumenes})
    escribir(API / "index.json", {
        "nombre": "KatMods API",
        "version": "1",
        "autor": "Oliver",
        "docs": f"{BASE}/api.html",
        "endpoints": {
            "mods": f"{BASE}/api/mods.json",
            "mod": f"{BASE}/api/mods/{{id}}.json",
            "contenido": f"{BASE}/api/mods/{{id}}/contenido.json",
        },
    })
    print("API generada:", ", ".join(MODS))


if __name__ == "__main__":
    main()
