# KiCad Discord Presence

KiCad Discord Rich Presence client for Windows. It runs silently in the background and updates Discord activity while KiCad is open.

## Requirements

- Windows
- Discord desktop app running
- Discord Activity Privacy enabled for activity sharing

## Install

1. Go to **Releases**.
2. Download `KiCadDiscordPresence-Setup.exe`.
3. Run the installer.

The app installs to `%LOCALAPPDATA%\KiCadPresence` and auto-starts at logon for the current user.

## Uninstall

- Use Windows **Apps & Features**, or
- Run the uninstaller from `%LOCALAPPDATA%\KiCadPresence`.

Uninstall removes app files and the autostart entry.

## Troubleshooting

- If VS Code activity overrides KiCad status, disable VS Code in Discord **Registered Games**.
- If Discord activity is not shown, verify Discord **Activity Privacy** settings are enabled.
