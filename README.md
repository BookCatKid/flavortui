# FlavorTUI

[![PyPI - Version](https://img.shields.io/pypi/v/flavortui.svg)](https://pypi.org/project/flavortui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/flavortui.svg)](https://pypi.org/project/flavortui)

- [FlavorTUI](#flavortui)
  - [Demo](#demo)
  - [Description](#description)
  - [Performance (PLEASE READ)](#performance-please-read)
  - [Storage Locations](#storage-locations)
  - [Screenshots](#screenshots)
  - [Installation](#installation)
  - [Local Development](#local-development)
  - [API](#api)
  - [License](#license)


## Demo

If you want a demo video dispalying _almost_ all of the features, you can watch this:

https://github.com/user-attachments/assets/22f0fe11-7338-4f3a-81ef-6a218db126e5

## Description

FlavorTUI is a terminal user interface (TUI) for Flavortown. With FlavorTUI, you can view your stats, browse your projects and devlogs, explore the shop, and discover other users' projects, all from an interactive terminal interface.

It is built using the `textual` library, which provides (imo) a great terminal UI experience. The TUI is of course written in Python 🥰. This is my first time creating a TUI so I hope its good :) Depending on your terminal, the ui might look different. It all depends on how well your terminal supports different things.

Your API key is stored "securely" using the `keyring` library, so you don't have to worry about it being exposed in your terminal history or config files.

## Performance (PLEASE READ)

**Image lag**:
Depending on your terminal, performance might be *very* bad. I suggest switching image rendering modes until you find one that works. Worst case you can disable images entirely.

**Buggy UI**: If your UI looks buggy (text is in the wrong spot, images are jittery), please try changing your image rendering mode. Bad terminals (such as the **Windows Terminal**) will most likely **break stuff really badly**

I **highly recommend** using a terminal that supports all of these modern rendering things. From the very minimal selection that I have tested, I suggest:

- Kitty (the best!)
- WezTerm
- iTerm
- Alacritty

Kitty (in my opinion) is the best. It has great performance and support for everything. The others, you might want to change the image rendering settings.

Please avoid reporting UI issues if you're using a terminal with limited or inconsistent graphics support, as these issues are often caused by the terminal itself rather than the app.

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
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/shop.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/shop-item.png" width="100%"></td>
    </tr>
    <tr>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/kitchen.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/explore.png" width="100%"></td>
    </tr>
    <tr>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/explore-devlogs.png" width="100%"></td>
      <td><img src="https://raw.githubusercontent.com/BookCatKid/flavortui/main/screenshots/explore-users.png" width="100%"></td>
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

or, to install the latest from GitHub:

```bash
pip install git+https://github.com/bookcatkid/flavortui
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
