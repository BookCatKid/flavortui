# FlavorTUI

[![PyPI - Version](https://img.shields.io/pypi/v/flavortui.svg)](https://pypi.org/project/flavortui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flavortui.svg)](https://pypi.org/project/flavortui)

- [FlavorTUI](#flavortui)
  - [Demo](#demo)
  - [Description](#description)
  - [Storage Locations](#storage-locations)
  - [Screenshots](#screenshots)
  - [Installation](#installation)
  - [Local Development](#local-development)
  - [API](#api)
  - [License](#license)


## Demo

If you want a demo video dispalying _almost_ all of the features, you can watch this:

<video width="400" controls>
  <source src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/demo.mov" type="video/mov">
  [Click here to watch it](https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/demo.mov)
</video>

## Description

FlavorTUI is a terminal user interface (TUI) for Flavortown. With FlavorTUI, you can view your stats, browse your projects and devlogs, explore the shop, and discover other users' projects, all from an interactive terminal interface.

It is built using the `textual` library, which provides (imo) a great terminal UI experience. The TUI is of course written in Python 🥰. This is my first time creating a TUI so I hope its good :) Depending on your terminal, the ui might look different. It all depends on how well your terminal supports different things.

Your API key is stored "securely" using the `keyring` library, so you don't have to worry about it being exposed in your terminal history or config files.

## Storage Locations

FlavorTUI stores data in three places:

- API key: system keychain/keyring (via `keyring`)
- Settings JSON: user config directory (via `platformdirs.user_config_dir("flavortui")`)
- API/image cache: user cache directory (via `platformdirs.user_cache_dir("flavortui")`)

Typical paths:

To easily find where your data is stored, you can simply go to the bottom of the settings menu and click on the associated buttons!

- macOS:
  - Settings: `~/Library/Application Support/flavortui/settings.json`
  - Cache: `~/Library/Caches/flavortui/`
- Windows:
  - Settings: `%LOCALAPPDATA%\\flavortui\\settings.json`
  - Cache: `%LOCALAPPDATA%\\flavortui\\Cache\\`
- Linux:
  - Settings: `~/.config/flavortui/settings.json` (or `$XDG_CONFIG_HOME/flavortui/settings.json`)
  - Cache: `~/.cache/flavortui/` (or `$XDG_CACHE_HOME/flavortui/`)

## Screenshots

<div align="center">
  <table>
    <tr>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/kitchen.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/projects.png" width="100%"></td>
    </tr>
    <tr>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/kitchen.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/explore.png" width="100%"></td>
    </tr>
    <tr>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/settings.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/with-sidebar.png" width="100%"></td>
    </tr>
  </table>
</div>

## Installation

```bash
pip install flavortui
```

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

Run with either:

```bash
flavortui
```

or:

```bash
python -m flavortui
```

## API

Flavortown API docs can be found [here](https://flavortown.hackclub.com/api/v1/docs).

## License

`flavortui` is distributed under the terms of the MIT license.
