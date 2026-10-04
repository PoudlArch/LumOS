#!/usr/bin/env bash
# Fonctions partagées par build.sh (ISO) et install.sh (Arch déjà installé).

LUMOS_DEPOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

info()   { printf '\e[38;2;211;166;37m✦\e[0m %s\n' "$*"; }
erreur() { printf '\e[31m✗ %s\e[0m\n' "$*" >&2; exit 1; }

# Lignes utiles d'un fichier de liste (sans commentaires ni lignes vides)
lignes() { sed -e 's/[[:space:]]*#.*//' -e '/^[[:space:]]*$/d' "$1"; }

# "8e1b1f" -> "142,27,31"
rvb() { printf '%d,%d,%d' "0x${1:0:2}" "0x${1:2:2}" "0x${1:4:2}"; }

# Un bloc [Colors:…] : section, fond, fond alterné, texte, décor, texte discret
_bloc_couleurs() {
    cat <<EOF
[Colors:$1]
BackgroundAlternate=$(rvb "$3")
BackgroundNormal=$(rvb "$2")
DecorationFocus=$(rvb "$5")
DecorationHover=$(rvb "$5")
ForegroundActive=$(rvb "$5")
ForegroundInactive=$(rvb "$6")
ForegroundLink=$(rvb "$5")
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=$(rvb "$4")
ForegroundPositive=39,174,96
ForegroundVisited=$(rvb "$6")

EOF
}

# Génère les jeux de couleurs Plasma (LumosGryffondor.colors, …) dans le dossier $1
lumos_couleurs() {
    local dest="$1" nom libelle accent sur_accent decor fond vue alterne bouton texte discret reste
    install -d -m 755 "$dest"
    while IFS='|' read -r nom libelle accent sur_accent decor fond vue alterne bouton texte discret reste; do
        {
            _bloc_couleurs Button "$bouton" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs Complementary "$fond" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs Header "$fond" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs 'Header][Inactive' "$fond" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs Selection "$accent" "$accent" "$sur_accent" "$decor" "$sur_accent"
            _bloc_couleurs Tooltip "$fond" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs View "$vue" "$alterne" "$texte" "$decor" "$discret"
            _bloc_couleurs Window "$fond" "$alterne" "$texte" "$decor" "$discret"
            cat <<EOF
[General]
ColorScheme=Lumos$libelle
Name=Lumos $libelle
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground=$(rvb "$fond")
activeBlend=$(rvb "$texte")
activeForeground=$(rvb "$texte")
inactiveBackground=$(rvb "$fond")
inactiveBlend=$(rvb "$discret")
inactiveForeground=$(rvb "$discret")
EOF
        } > "$dest/Lumos$libelle.colors"
        chmod 644 "$dest/Lumos$libelle.colors"
    done < <(lignes "$LUMOS_DEPOT/themes/maisons.conf")
}

# Convertit les fonds d'écran SVG en PNG dans le dossier $1
lumos_fonds() {
    local dest="$1" svg
    install -d -m 755 "$dest"
    for svg in "$LUMOS_DEPOT"/assets/fonds/*.svg; do
        rsvg-convert -w 2560 -h 1440 "$svg" -o "$dest/$(basename "${svg%.svg}").png"
        chmod 644 "$dest/$(basename "${svg%.svg}").png"
    done
}

# Pose le thème (rootfs/, couleurs, fonds, liens des sortilèges) sous la racine $1
lumos_superposer() {
    local racine="${1%/}" fichier rel mode sort
    while IFS= read -r -d '' fichier; do
        rel="${fichier#"$LUMOS_DEPOT/rootfs/"}"
        case "$rel" in usr/local/bin/*) mode=755 ;; *) mode=644 ;; esac
        install -D -m "$mode" "$fichier" "$racine/$rel"
    done < <(find "$LUMOS_DEPOT/rootfs" -type f -print0)
    for sort in $(bash "$LUMOS_DEPOT/rootfs/usr/local/bin/sortilege" --liste); do
        ln -sf sortilege "$racine/usr/local/bin/$sort"
    done
    lumos_couleurs "$racine/usr/share/color-schemes"
    lumos_fonds "$racine/usr/share/wallpapers/Lumos"
}
