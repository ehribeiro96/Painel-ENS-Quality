# Hermes Desktop PT-BR Keyboard Flow

This document captures the safe, manual prerequisites for the PT-BR Hermes Desktop launcher.

## Manual prerequisites

Run these in WSL Ubuntu before testing the desktop wrapper:

```bash
sudo apt update
sudo apt install -y locales keyboard-configuration xkb-data x11-xkb-utils

sudo locale-gen pt_BR.UTF-8
sudo update-locale LANG=pt_BR.UTF-8
```

## Validation

```bash
echo "$LANG"
locale
locale -a | grep -i pt_BR
localectl status
setxkbmap -query 2>/dev/null || true
```

## Windows keyboard setting

Use Windows 11:

```text
Configurações → Hora e idioma → Idioma e região → Português (Brasil) → Teclado → Português (Brasil ABNT2)
```

## Restart WSL

After changing Windows keyboard or locale settings, restart WSL:

```powershell
wsl --shutdown
```

## Notes

- `setxkbmap` can fail against Xwayland/WSLg. That does not prove a Hermes bug.
- Correct Windows + WSL locale first, then test Electron/Hermes.
- The PT-BR launcher wrapper prints locale and XKB metadata before launching Hermes Desktop.
