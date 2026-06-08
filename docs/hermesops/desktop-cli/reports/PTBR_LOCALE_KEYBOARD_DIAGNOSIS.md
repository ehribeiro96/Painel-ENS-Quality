# PT-BR Locale and Keyboard Diagnosis

## What was observed

- The local shell reports `LANG=pt_BR.UTF-8`.
- `locale` still shows `LC_ALL=C.UTF-8` in this host session.
- `localectl status` could not return full information in this environment.
- `setxkbmap -query` cannot open the X display here, so Xwayland/WSLg keyboard state is not fully observable from this host.
- `locale -a` does include `pt_BR.utf8`.

## Diagnosis

- The PT-BR locale is available, but the host still has WSL/X11 limitations that keep keyboard verification incomplete.
- `setxkbmap` failure here is consistent with Xwayland/WSLg limitations and does not prove a Hermes bug.
- The fix path remains two-layered:
  - WSL locale must be set manually to `pt_BR.UTF-8`.
  - Windows keyboard must be set to `Português (Brasil) ABNT2`.

## Evidence

- `reports/hermes_desktop_mod/evidence/locale_keyboard_current.txt`
- `hermesops desktop keyboard status`
- `hermesops desktop locale status`

