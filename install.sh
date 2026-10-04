#!/usr/bin/env bash
# Applique le thème Lumos OS (maisons, sortilèges, Choixpeau) à un Arch Linux déjà
# installé avec KDE Plasma, sans passer par l'ISO.
#
#   sudo ./install.sh                  installe
#   sudo ./install.sh --desinstaller   retire tout ce que le script a posé
set -euo pipefail
umask 022

ici="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/commun.sh
source "$ici/tools/commun.sh"

(( EUID == 0 )) || erreur "À lancer avec sudo : sudo ./install.sh"
command -v pacman >/dev/null || erreur "Ce script est prévu pour Arch Linux et ses dérivés."

ligne_rc='[ -r /usr/share/lumos/shellrc ] && . /usr/share/lumos/shellrc'
perso=""
if [[ -n ${SUDO_USER:-} && $SUDO_USER != root ]]; then
    perso="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
fi

if [[ ${1:-} == --desinstaller ]]; then
    for sort in $(bash "$ici/rootfs/usr/local/bin/sortilege" --liste); do
        [[ -L /usr/local/bin/$sort ]] && rm -f "/usr/local/bin/$sort"
    done
    while IFS= read -r -d '' fichier; do
        rm -f "/${fichier#"$ici/rootfs/"}"
    done < <(find "$ici/rootfs" -type f -print0)
    rm -rf /usr/share/lumos /usr/share/wallpapers/Lumos
    rm -f /usr/share/color-schemes/Lumos*.colors
    if [[ -n $perso ]]; then
        for rc in .bashrc .zshrc; do
            [[ -f $perso/$rc ]] && sed -i '\|/usr/share/lumos/shellrc|d' "$perso/$rc"
        done
    fi
    info "Finite Incantatem : le thème est retiré. Tes réglages Plasma actuels restent en place."
    exit 0
fi

info "Paquets nécessaires"
pacman -S --needed --noconfirm librsvg fastfetch kdialog

info "Pose du thème"
lumos_superposer /

if [[ -n $perso ]]; then
    for rc in .bashrc .zshrc; do
        [[ -f $perso/$rc ]] || continue
        grep -qF '/usr/share/lumos/shellrc' "$perso/$rc" || printf '\n%s\n' "$ligne_rc" >> "$perso/$rc"
    done
fi

info "C'est prêt. Le Choixpeau t'attend à la prochaine ouverture de session (ou lance « choixpeau » tout de suite)."
