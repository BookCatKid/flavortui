# FlavorTUI

FlavorTUI is a feature-rich terminal user interface (TUI) for Flavortown. With FlavorTUI, you can browse and create devlogs, manage your projects, explore the shop, and access other Flavortown features, all from an interactive terminal interface.

It is built using the `textual` library, which provides (imo) a great terminal UI experience. The TUI is of course written in Python 🥰. This is my first time creating a TUI so I hope its good :)

Your API key is stored securely using the `keyring` library, so you don't have to worry about it being exposed in your terminal history or config files.

<div>
  <img src="screenshots/kitchen.png" alt="Kitchen Screenshot" style="width:49%;">
  <img src="screenshots/with_sidebar.png" alt="Shop Screenshot" style="width:49%;">
</div>

## Usage

To run FlavorCLI, ensure that you have python installed. Start by installing the dependencies (I also recommend using a virtual environment):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Then to run it you can use:

```bash
python main.py
```

## API

Flavortown API docs can be found [here](https://flavortown.hackclub.com/api/v1/docs).
