import os
import shutil
import subprocess
import argparse

# Constants
example_container = '_example-sdk_2024123-EFR32ZG23_'
example_name = '_EXAMPLE-SDK_2024123-EFR32ZG23_'
replacement_instructions_file = 'replacements.txt'

# Global flags
DRY_RUN = False
DEBUG = False


def run_command(command, check=True):
    if DEBUG or DRY_RUN:
        print(f"[command] {command}")
    if not DRY_RUN:
        subprocess.run(command, shell=True, check=check)


def run_command_output(command):
    if DEBUG or DRY_RUN:
        print(f"[command] {command}")
    if DRY_RUN:
        return "dry-run-placeholder"
    return subprocess.check_output(command, shell=True, text=True).strip()


def clone_repo(new_container):
    run_command(f'git clone --no-local {example_container} {new_container}')
    if not DRY_RUN:
        os.chdir(new_container)


def cache_cleanup():
    run_command('git reflog expire --expire=now --all')
    run_command('git gc --prune=now --aggressive')


def replace_paths(old_path, new_path):
    run_command(f'git filter-repo --path-rename {old_path}:{new_path}')
    cache_cleanup()


def replace_text(new_container, new_name):
    if DEBUG:
        print(f"[write file] {replacement_instructions_file}")
    if not DRY_RUN:
        with open(replacement_instructions_file, 'w') as file:
            content = f'{example_container}==>{new_container}\n{example_name}==>{new_name}\n'
            file.write(content)

    run_command(f'git filter-repo --replace-text {replacement_instructions_file}')
    cache_cleanup()

    if not DRY_RUN:
        os.remove(replacement_instructions_file)


def fix_simplicity_config_files(old_name, new_container, new_name):
    extensions = ["pintool", "slcp", "slpb", "slps"]
    for ext in extensions:
        old_file = f"./{new_container}/{old_name}.{ext}"
        new_file = f"./{new_container}/{new_name}.{ext}"
        if os.path.exists(old_file):
            print(f"Renamed: {old_file} → {new_file}")
            if not DRY_RUN:
                shutil.move(old_file, new_file)
        else:
            print(f"Skipped: {old_file} does not exist.")

    run_command('git add .')
    run_command('git commit -m "Porting from example container, changing the Simplicity Studio config files"')


def verify_changes():
    run_command('git log -p')
    input('Press enter for next check.')
    run_command('git ls-tree -r HEAD --name-only')
    input('Press enter for next check.')
    run_command(f'git grep -i "{example_container}"')
    input('Press enter for next check.')


def push_to_remote():
    repo_name = run_command_output("git rev-parse --show-toplevel | xargs basename")
    branch_name = run_command_output("git rev-parse --abbrev-ref HEAD")
    subgroups = input('Add any subgroups needed, include / between subgroups. Leave empty if in top group:').strip()
    if subgroups and not subgroups.endswith('/'):
        subgroups += '/'
    remote_url = f"git@gitlab.allterco.net:shellytech_slo/{subgroups}{repo_name}.git"
    remote_name = "origin"

    remotes = run_command_output("git remote").splitlines()
    if remote_name not in remotes:
        print(f"Adding remote '{remote_name}' → {remote_url}")
        if not DRY_RUN:
            subprocess.run(["git", "remote", "add", remote_name, remote_url], check=True)

    print(f"Pushing branch '{branch_name}' to remote '{remote_name}'")
    if not DRY_RUN:
        subprocess.run(["git", "push", "--force-with-lease", "--set-upstream", remote_name, branch_name], check=True)


def main():
    global DRY_RUN, DEBUG

    parser = argparse.ArgumentParser(description="Clone and transform a project repo.")
    parser.add_argument('--dry-run', action='store_true', help="Simulate actions without making changes")
    parser.add_argument('--debug', action='store_true', help="Print all executed commands")
    args = parser.parse_args()

    DRY_RUN = args.dry_run
    DEBUG = args.debug

    new_project_name = input("Please provide the new project name: ").strip()
    new_project_container = new_project_name.lower()

    clone_repo(new_project_container)

    replace_paths(f'{example_container}/', f'{new_project_container}/')
    replace_paths(f'{example_name}/', f'{new_project_name}/')

    replace_text(new_project_container, new_project_name)
    
    fix_simplicity_config_files(example_name, new_project_container, new_project_name)

    if False:
        verify_changes()

    push_to_remote()

    if not DRY_RUN:
        os.chdir('..')


if __name__ == '__main__':
    if not shutil.which("git"):
        raise EnvironmentError("Git is not installed or not found in PATH.")
    if not shutil.which("git-filter-repo"):
        raise EnvironmentError("git-filter-repo is not installed or not found in PATH.")
    
    main()
