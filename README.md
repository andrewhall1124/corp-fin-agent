# Corporate Finance Vertical AI Agent Repository

# Getting Started

## Virtual Environment Setup
The virtual environment will make it so that we have consistent package and Python versions across all of our devices running the repository.

### `uv` Installation (Package Manager)

MacOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Check installation
```bash
uv --version
```

If this returns an error you might need to add uv to your path. Run:

```bash
source $HOME/.local/bin/env
```
Restart your terminal for the changes to take effect.

### Sync Denpendencies
```bash
uv sync
```

### Activate Environment
MacOS/Linux
```bash
source .venv/bin/activate
```

Windows
```bash
.venv/Scripts/activate
```

That's it! You are all ready to go with the project!

## Running Streamlit
To run the streamlit app locally run:

```bash
uv run streamlit main
```

## Useful Commands

### Add a Dependency
```bash
uv add <package>
```

### Remove a Dependency
```bash
uv remove <package>
```
