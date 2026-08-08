#!/usr/bin/env bash
# 
# CAUTION: Tailored strictly for my ASUS Vivobook K6502VJ. 
# Will likely break things on other hardware. Inspect before running.
# STATUS: Untested / Active Test Phase. Use at your own risk.
# 
# install.sh - post-pacstrap bootstrap for this Arch/GNOME setup
#
# ASSUMES: base Arch install already done (pacstrap, bootloader, reboot
# complete). You are logged in as root on a bare TTY. Nothing else is
# configured yet - no sudo, no regular user, no NetworkManager.
#
# Run this as root:  ./install.sh

set -euo pipefail

NEW_USER="${1:-}"
if [[ -z "$NEW_USER" ]]; then
  read -rp "Username to create: " NEW_USER
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root (you're right after pacstrap, no sudo exists yet)."
  exit 1
fi

# --- 0. Confirm network connectivity before doing anything else ---
echo "==> Checking network connectivity..."
if ! ping -c 1 -W 3 archlinux.org &>/dev/null; then
  echo "No network connection detected."
  echo "Set up networking manually first, e.g.:"
  echo "  Wi-Fi: iwctl station wlan0 connect <SSID>"
  echo "  Ethernet: dhcpcd"
  exit 1
fi

# --- 1. Minimum packages needed before anything else can happen ---
# sudo: so we stop running everything as root after this
# base-devel + git: required to build anything from the AUR later
echo "==> Installing bootstrap essentials (sudo, base-devel, git, networkmanager)..."
pacman -Syu --needed --noconfirm sudo base-devel git networkmanager

# --- 2. Create the real user (AUR builds refuse to run as root) ---
if id "$NEW_USER" &>/dev/null; then
  echo "==> User $NEW_USER already exists, skipping creation."
else
  echo "==> Creating user $NEW_USER..."
  useradd -m -G wheel -s /bin/bash "$NEW_USER"
  passwd "$NEW_USER"
fi

# --- 3. Allow wheel group to use sudo ---
if ! grep -q '^%wheel ALL=(ALL:ALL) ALL' /etc/sudoers; then
  echo "==> Enabling sudo for the wheel group..."
  sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers
fi

# --- 4. Bring up NetworkManager for good, so networking survives reboot ---
systemctl enable --now NetworkManager.service

# --- Package lists ---
OFFICIAL_PKGS=(
  alsa-firmware alsa-utils fprintd gdm gnome-backgrounds gnome-color-manager
  gnome-console gnome-control-center gnome-disk-utility gnome-font-viewer
  gnome-keyring gnome-menus gnome-session gnome-settings-daemon gnome-shell
  gnome-software gnome-system-monitor gnome-text-editor grilo-plugins
  gst-thumbnailers gvfs linux linux-firmware mesa-utils nano nautilus
  nvidia-open nvidia-prime nvidia-settings nvidia-utils pavucontrol
  pipewire-alsa power-profiles-daemon rtkit sof-firmware sushi
  xdg-desktop-portal-gnome xdg-user-dirs-gtk zsh
)

AUR_PKGS=(
  envycontrol
  gnome-shell-extension-gpu-profile-selector-git
)

echo "==> Installing official repo packages..."
pacman -S --needed --noconfirm "${OFFICIAL_PKGS[@]}"

# --- 5. Everything AUR-related must run as the new user, not root ---
echo "==> Bootstrapping yay as $NEW_USER (makepkg refuses to run as root)..."
su - "$NEW_USER" -c '
  set -euo pipefail
  if ! command -v yay &>/dev/null; then
    tmpdir=$(mktemp -d)
    git clone https://aur.archlinux.org/yay-bin.git "$tmpdir/yay-bin"
    (cd "$tmpdir/yay-bin" && makepkg -si --noconfirm)
    rm -rf "$tmpdir"
  fi
'

echo "==> Installing AUR packages as $NEW_USER..."
su - "$NEW_USER" -c "yay -S --needed --noconfirm ${AUR_PKGS[*]}"

# --- 6. Enable core services ---
echo "==> Enabling services..."
systemctl enable gdm.service
systemctl enable power-profiles-daemon.service

echo "==> Done. Reboot, then log in as $NEW_USER."
