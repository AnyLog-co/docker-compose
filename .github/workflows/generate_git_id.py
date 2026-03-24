import os
import subprocess
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(__file__).split(".github", 1)[0], "setup.cfg")

def get_git_commit_id():
    try:
        # Get the latest commit hash from Git
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        commit_id = result.stdout.strip()
        return commit_id
    except subprocess.CalledProcessError as e:
        print(f"Error getting Git commit ID: {e}")
        return None


def get_git_info():
    try:
        commit = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, check=True
        ).stdout.strip()

        return commit, branch

    except subprocess.CalledProcessError as e:
        print(f"Error getting Git info: {e}")
        return None, None

def update_version(new_version):
    lines = []

    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if line.strip().startswith("version"):
                line = f"version = {new_version}\n"
            lines.append(line)

    with open(CONFIG_FILE, "w") as f:
        f.writelines(lines)

def update_git_id_file():
    commit_id, branch = get_git_info()
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')


    last_six_digits = f"{commit_id[:6]}" if commit_id else "Missig Git ID"
    version_id = f"{branch} - {last_six_digits} [{formatted_now}]"
    update_version(version_id)




if __name__ == "__main__":
    update_git_id_file()