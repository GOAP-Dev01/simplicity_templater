# Repo Porting Automation Script

This Python script automates the process of cloning a template Git repository (referred to as the "example container") and transforming it into a new project repository. It performs path renaming, string replacements, configuration file renaming (e.g., for Simplicity Studio), and pushes the new repository to a remote GitLab location.

## Important
Clone using this command:
> `git clone --recurse-submodules <repo-url>`


## Features

* Clones a local Git repository (no remote dependency)
* Renames paths and strings inside the repo using `git-filter-repo`
* Renames Simplicity Studio project configuration files
* Cleans up Git cache
* Adds a remote and pushes the transformed project

## Requirements

* Python 3.x
* `git` installed and available in PATH
* [`git-filter-repo`](https://github.com/newren/git-filter-repo) installed and available in PATH

## Installation

Make sure you have `git` and `git-filter-repo` installed:

```bash
sudo apt install git
pip install git-filter-repo  # or follow the instructions on the official repo
```

## Usage

```bash
python3 port_project.py
```

You will be prompted to enter a new project name, and optionally any GitLab subgroups for the remote repository path.

### Optional Flags

* `--dry-run`: Simulate actions without making actual changes
* `--debug`: Print all internal shell commands

### Example

```bash
python3 port_project.py --debug
```

Sample prompt interaction:

```
Please provide the new project name: MyCoolProject
Add any subgroups needed, include / between subgroups. Leave empty if in top group:team-a/firmware
```

This will:

1. Clone `_example-sdk_2024121-EFR32ZG23_` into `mycoolproject/`
2. Rename all paths and strings in Git history:

   * `_example-sdk_2024121-EFR32ZG23_` → `mycoolproject`
   * `_EXAMPLE-SDK_2024121-EFR32ZG23_` → `MyCoolProject`
3. Rename all Simplicity Studio config files
4. Commit the changes
5. Push to `git@gitlab.com:goap/team-a/firmware/mycoolproject.git`

## File Structure

* `port_project.py`: The main script
* `replacements.txt`: Auto-generated file used for string replacements (deleted after use)

## Notes

* The script assumes you're cloning from a local repository (bare or non-bare).
* The script uses `--force-with-lease` when pushing, to ensure history rewriting doesn't cause issues with collaborators.
* It is interactive and designed to be run in a terminal.

## License

MIT License

---

Let me know if you want a versioned changelog or Docker wrapper.
