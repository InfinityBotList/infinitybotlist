"""Populates submodules under the src folder as stated in components"""

from libstep import Stepper
from data.components import Component, Components
import os
import subprocess
import json

def run(s: Stepper, c: Components, args: dict[str, str]):
    # First loop over the src folder
    found_components = []
    for f in os.listdir("src"):
        found_comp = c.find(f)
        if not found_comp:
            # Delete the folder
            print(f"Deleting folder `{f}` [not in components.yaml]")
            subprocess.call(["git", "rm", "-rf", f"src/{f}"])
        else:
            # Add a step to update the git submodule
            for env in found_comp.envs:
                print(f"=> Updating submodule `{f}` [env={env}, branch={found_comp.env_branches[env]}]")
                subprocess.call(["git", "submodule", "update", "--remote", "--merge", f"src/{found_comp.dir}/{env}"])
            found_components.append(f)
    
    # Now loop over the components and add tasks to add components not found
    for name, component in c.components.items():
        if not component.dir in found_components:
            print(f"Adding component {name} to {component.dir}")
            for env in component.envs:
                branch = component.env_branches[env]
                print(f"=> [{name}] {env} [{branch}]")
                subprocess.call(["git", "submodule", "add", "-b", branch, "--force", component.repo, f"src/{component.dir}/{env}"])

    # Next, handle go.work/Cargo.work files to ensure easy development
    go_work_adds = []
    cargo_work_adds = []
    for f in os.listdir("src"):
        found_comp = c.find(f)

        if not found_comp:
            print(f"WARN: Component {f} not found in components.yaml. This should not happen after a populate.")
            continue

        for env in found_comp.envs:
            if env == "prod":
                continue # Disincentive direct coding on prod by removing it from the workspace

            if os.path.exists(f"src/{found_comp.dir}/{env}/go.mod"):
                go_work_adds.append(f"src/{found_comp.dir}/{env}")
            
            if os.path.exists(f"src/{found_comp.dir}/{env}/Cargo.toml"):
                cargo_work_adds.append([found_comp, env])
    
    if len(go_work_adds) > 0:
        print("Generating go.work files")
        subprocess.call(["rm", "-f", "go.work"])
        subprocess.call(["go", "work", "init"])

        for f in go_work_adds:
            print(f"Adding {f} to go.work")
            subprocess.call(["go", "work", "use", f])
    
    if len(cargo_work_adds) > 0:
        print("Generating Cargo.work files")
        subprocess.call(["rm", "-f", "Cargo.work"])
        base_file = "[workspace]\nmembers=" + json.dumps([f"{env}/{c.bin}" for c, env in cargo_work_adds])

        with open("Cargo.work", "w") as f:
            f.write(base_file)