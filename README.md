<p align="center"><img src="assets/logo.svg" width="150" alt="Lumos OS"></p>

# Lumos OS

Une distribution Linux à l'ambiance d'école de sorcellerie, basée sur **Arch Linux** et le bureau **KDE Plasma**.
Au premier démarrage, le Choixpeau te pose trois questions et t'envoie dans une maison ; le bureau prend alors ses couleurs. Dans le terminal, on installe un paquet avec `accio`, on met à jour avec `reparo`, on éteint avec `mefait-accompli`.

![Les quatre maisons](assets/apercu.png)

> Projet de fan, non officiel, sans but commercial et sans lien avec Warner Bros. ni J.K. Rowling. Il ne contient aucun logo, police ou illustration officiels : tous les dessins sont originaux.

## Ce qu'il y a dedans

- **Une ISO live** : elle démarre sur un bureau Plasma en français, compte `sorcier` sans mot de passe, avec les outils d'installation d'Arch (`archinstall`).
- **Quatre maisons** (Gryffondor, Serpentard, Serdaigle, Poufsouffle) : chacune a son jeu de couleurs, son fond d'écran et sa couleur d'invite dans le terminal. Le thème clair « Parchemin » s'allume avec `lumos`.
- **Le Choixpeau** : `choixpeau` relance la cérémonie, `choixpeau --choisir` laisse choisir, `maison serdaigle` change directement.
- **Le grimoire** : les commandes du quotidien sous forme d'incantations.

| Sortilège | Effet |
| --- | --- |
| `accio <paquet>` | installe un paquet |
| `evanesco <paquet>` | désinstalle un paquet |
| `reparo` | met tout le système à jour |
| `revelio <mot>` | cherche un paquet |
| `alohomora <commande>` | exécute en administrateur |
| `lumos` / `nox` | thème clair / thème sombre de la maison |
| `geminio <source> <copie>` | duplique |
| `wingardium-leviosa <source> <destination>` | déplace |
| `reducto <dossier>` / `engorgio <archive>` | compresse / décompresse |
| `stupefix` / `enervatum <processus>` | fige / réveille un processus |
| `finite-incantatem <processus>` | arrête un processus proprement |
| `avada-kedavra <processus>` | tue un processus |
| `hominum-revelio` | montre qui est connecté |
| `portus [dossier]` | change de dossier |
| `obliviate` | efface l'écran et l'historique |
| `mefait-accompli` | éteint l'ordinateur |
| `grimoire` | affiche la liste |

## Obtenir l'ISO

**Avec GitHub** (rien à installer) : onglet *Actions* › *ISO* › *Run workflow*. Au bout d'une demi-heure environ, l'ISO est téléchargeable dans les artefacts de l'exécution. Pousser une étiquette `v0.1` construit l'ISO et la joint à la version.

**Sur une machine Arch Linux** :

```bash
sudo pacman -S --needed archiso librsvg ttf-liberation
sudo ./build.sh
```

L'ISO arrive dans `out/`. Pour l'essayer : VirtualBox ou VMware (4 Go de mémoire, EFI ou BIOS), ou une clé USB écrite avec Ventoy, Rufus ou `dd`.

## Mettre le thème sur un Arch déjà installé

Sur un Arch Linux avec KDE Plasma, sans passer par l'ISO :

```bash
sudo ./install.sh
```

Le Choixpeau se présente à la prochaine ouverture de session. `sudo ./install.sh --desinstaller` retire tout.

## Organisation du dépôt

| Dossier | Rôle |
| --- | --- |
| `themes/maisons.conf` | la palette : source unique des couleurs et des fonds d'écran |
| `rootfs/` | les fichiers du thème, posés tels quels dans le système (ISO et `install.sh`) |
| `iso/` | ce qui ne concerne que l'ISO : paquets ajoutés ou retirés, session live |
| `assets/` | logo, écran de démarrage, fonds d'écran (SVG) |
| `tools/` | fonctions communes et générateur des fonds d'écran |
| `build.sh` | construit l'ISO à partir du profil officiel `releng` d'archiso |
| `install.sh` | applique le thème à un système existant |

Changer une couleur : modifier `themes/maisons.conf`, puis `python tools/dessiner_fonds.py` pour redessiner les fonds. Ajouter un sortilège : une ligne dans le tableau et un cas dans `rootfs/usr/local/bin/sortilege`.

## État et suite

Version de départ : l'ISO n'a pas encore été construite ni démarrée, la première construction dira ce qu'il reste à ajuster.

À venir : installateur graphique (Calamares) pour que le système installé garde le thème, écran de connexion et animation de démarrage aux couleurs des maisons, sons, icônes, dépôt de paquets.

## Licence

Code et illustrations sous licence MIT (voir `LICENSE`). Arch Linux et KDE sont des marques de leurs détenteurs respectifs ; les noms tirés de l'univers de Harry Potter appartiennent à leurs ayants droit.
