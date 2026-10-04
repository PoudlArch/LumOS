#!/usr/bin/env bash
# Construit l'ISO live de LumOS.
# À lancer en root sur Arch Linux (ou dans un conteneur archlinux privilégié) avec
# les paquets archiso, librsvg et ttf-liberation installés.
#
# Le profil part du profil officiel « releng » d'archiso, copié au moment de la
# construction : on suit ainsi ses évolutions sans en recopier les fichiers ici.
# LumOS ajoute le dépôt BlackArch (outils d'audit de sécurité) : build.sh installe
# son trousseau de clés sur la machine de construction et l'inscrit dans le profil.
set -euo pipefail
umask 022

ici="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tools/commun.sh
source "$ici/tools/commun.sh"

base=/usr/share/archiso/configs/releng
travail="${LUMOS_TRAVAIL:-/var/tmp/lumos-build}"
sortie="${LUMOS_SORTIE:-$ici/out}"

(( EUID == 0 )) || erreur "build.sh doit être lancé en root."
for outil in mkarchiso rsvg-convert; do
    command -v "$outil" >/dev/null || erreur "Outil manquant : $outil (pacman -S archiso librsvg ttf-liberation)"
done
[[ -d $base ]] || erreur "Profil releng introuvable : $base"

info "Préparation du profil dans $travail"
rm -rf "$travail"
mkdir -p "$travail" "$sortie"
profil="$travail/profil"
cp -a "$base" "$profil"
racine="$profil/airootfs"

info "Dépôt BlackArch (outils de sécurité)"
# pacstrap vérifie les signatures avec le trousseau de la machine de construction :
# on y installe donc blackarch-keyring avant d'inscrire le dépôt dans le profil.
if ! pacman-key -l blackarch &>/dev/null && ! pacman -Qq blackarch-keyring &>/dev/null; then
    tmpkr="$travail/blackarch-keyring.pkg.tar.zst"
    curl -fL "https://blackarch.org/keyring/blackarch-keyring.pkg.tar.zst" -o "$tmpkr"
    pacman -U --noconfirm --needed "$tmpkr"
fi
pacman-key --populate blackarch
# Dépôt côté machine de construction (pour pacstrap) et côté profil (pour l'ISO).
blackarch_repo=$'\n[blackarch]\nServer = https://mirror.rackspace.com/blackarch/blackarch/os/$arch\nSigLevel = Required DatabaseOptional\n'
grep -q '^\[blackarch\]' /etc/pacman.conf || printf '%s' "$blackarch_repo" >> /etc/pacman.conf
grep -q '^\[blackarch\]' "$profil/pacman.conf" || printf '%s' "$blackarch_repo" >> "$profil/pacman.conf"
pacman -Sy

info "Liste des paquets"
{
    grep -vxFf <(lignes "$ici/iso/packages.remove") "$profil/packages.x86_64" || true
    lignes "$ici/iso/packages.extra"
    lignes "$ici/iso/packages.security"
} | sort -u > "$travail/paquets"
mv "$travail/paquets" "$profil/packages.x86_64"

info "Thème et fichiers de la session live"
lumos_superposer "$racine"
cp -a "$ici/iso/airootfs/." "$racine/"

info "Services"
unites="$racine/etc/systemd/system"
# Plasma pilote le réseau avec NetworkManager : on retire systemd-networkd et iwd de releng.
rm -f "$unites"/multi-user.target.wants/{systemd-networkd,iwd}.service \
      "$unites"/sockets.target.wants/systemd-networkd.socket \
      "$unites"/network-online.target.wants/systemd-networkd-wait-online.service \
      "$unites"/dbus-org.freedesktop.network1.service
mkdir -p "$unites/multi-user.target.wants"
ln -sf /usr/lib/systemd/system/NetworkManager.service "$unites/multi-user.target.wants/NetworkManager.service"
ln -sf /usr/lib/systemd/system/sddm.service "$unites/display-manager.service"
ln -sf /etc/systemd/system/lumos-live.service "$unites/multi-user.target.wants/lumos-live.service"
ln -sf /usr/share/zoneinfo/Europe/Paris "$racine/etc/localtime"

info "Identité de l'ISO et menus de démarrage"
cat >> "$profil/profiledef.sh" <<'EOF'

# --- LumOS ---
iso_name="lumos"
iso_label="LUMOS_$(date --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m)"
iso_publisher="LumOS"
iso_application="LumOS, session live d'audit de sécurité"
file_permissions+=(["/etc/sudoers.d/10-lumos-live"]="0:0:440")
EOF
# mkarchiso copie airootfs sans conserver les droits : on déclare les exécutables.
for fichier in "$racine"/usr/local/bin/*; do
    [[ -L $fichier ]] && continue
    printf 'file_permissions+=(["/usr/local/bin/%s"]="0:0:755")\n' "$(basename "$fichier")"
done >> "$profil/profiledef.sh"

{ grep -rlZ 'Arch Linux' "$profil"/{syslinux,grub,efiboot} 2>/dev/null || true; } | xargs -0 -r sed -i \
    -e 's/Arch Linux install medium/LumOS/g' \
    -e 's/^MENU TITLE Arch Linux/MENU TITLE LumOS/' \
    -e 's/It allows you to install Arch Linux or perform system maintenance/Session live Plasma d'\''audit de sécurité, avec les outils d'\''installation d'\''Arch Linux/'
sed -i 's/^\(MENU COLOR title .*\)#9033ccff/\1#ffd3a625/' "$profil/syslinux/archiso_head.cfg" || true
rsvg-convert -w 640 -h 480 "$ici/assets/splash.svg" -o "$profil/syslinux/splash.png"

info "Construction de l'ISO (compter 20 à 40 minutes)"
mkarchiso -v -w "$travail/work" -o "$sortie" "$profil"

( cd "$sortie" && for iso in lumos-*.iso; do sha256sum "$iso" > "$iso.sha256"; done )
rm -rf "$travail"
info "ISO prête dans $sortie"
ls -lh "$sortie"
