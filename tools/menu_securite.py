#!/usr/bin/env python3
"""Génère le menu « outils de sécurité » de LumOS dans un système de fichiers cible.

Lit iso/outils.conf et écrit, sous la racine passée en argument :
  - usr/share/applications/lumos-<matiere>-<cmd>.desktop  (une entrée par outil)
  - usr/share/desktop-directories/lumos-<matiere>.directory + lumos-securite.directory
  - etc/xdg/menus/applications-merged/lumos-securite.menu (le dossier et ses sous-dossiers)

Les outils en terminal passent par /usr/local/bin/lumos-outil (ouvre Konsole).

    python tools/menu_securite.py <racine>
"""
import sys
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parent.parent


def lire_catalogue():
    matieres = {}        # clé -> {"libelle":…, "icone":…, "outils":[…]}
    for ligne in (RACINE_DEPOT / 'iso' / 'outils.conf').read_text(encoding='utf-8').splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith('#'):
            continue
        cle, libelle, icone, cmd, nom, desc, mode = (c.strip() for c in ligne.split('|'))
        m = matieres.setdefault(cle, {'libelle': libelle, 'icone': icone, 'outils': []})
        m['outils'].append({'cmd': cmd, 'nom': nom, 'desc': desc, 'mode': mode})
    return matieres


def ecrire(chemin: Path, contenu: str):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding='utf-8', newline='\n')


def main():
    if len(sys.argv) != 2:
        sys.exit('usage : menu_securite.py <racine>')
    racine = Path(sys.argv[1])
    matieres = lire_catalogue()

    applications = racine / 'usr/share/applications'
    directories = racine / 'usr/share/desktop-directories'
    menus = racine / 'etc/xdg/menus/applications-merged'

    # Dossier parent
    ecrire(directories / 'lumos-securite.directory',
           '[Desktop Entry]\nType=Directory\n'
           'Name=LumOS · Défense contre les Forces du Mal\nIcon=security-high\n')

    sous_menus = []
    n = 0
    for cle, m in matieres.items():
        ecrire(directories / f'lumos-{cle}.directory',
               f'[Desktop Entry]\nType=Directory\nName={m["libelle"]}\nIcon={m["icone"]}\n')
        for o in m['outils']:
            if o['mode'] == 'G':
                exec_line = o['cmd']
                terminal = 'false'
                icone = 'wireshark' if o['cmd'] == 'wireshark' else m['icone']
            else:
                exec_line = f'/usr/local/bin/lumos-outil {o["cmd"]} "{o["nom"]}"'
                terminal = 'false'
                icone = m['icone']
            ecrire(applications / f'lumos-{cle}-{o["cmd"]}.desktop',
                   '[Desktop Entry]\nVersion=1.4\nType=Application\n'
                   f'Name={o["nom"]}\nComment={o["desc"]}\n'
                   f'Exec={exec_line}\nIcon={icone}\nTerminal={terminal}\n'
                   f'Categories=Security;System;X-LumOS-{cle};\nKeywords=securite;audit;pentest;\n')
            n += 1
        sous_menus.append(
            f'    <Menu>\n'
            f'      <Name>LumOS {cle}</Name>\n'
            f'      <Directory>lumos-{cle}.directory</Directory>\n'
            f'      <Include><And><Category>X-LumOS-{cle}</Category></And></Include>\n'
            f'    </Menu>')

    ecrire(menus / 'lumos-securite.menu',
           '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<!DOCTYPE Menu PUBLIC "-//freedesktop//DTD Menu 1.0//EN" '
           '"http://www.freedesktop.org/standards/menu-spec/menu-1.0.dtd">\n'
           '<Menu>\n  <Name>Applications</Name>\n'
           '  <Menu>\n    <Name>LumOS Securite</Name>\n'
           '    <Directory>lumos-securite.directory</Directory>\n'
           + '\n'.join(sous_menus)
           + '\n  </Menu>\n</Menu>\n')

    print(f'Menu sécurité : {n} outils dans {len(matieres)} matières')


if __name__ == '__main__':
    main()
