"""List all components and their info"""

from libstep import Stepper
from data.components import Components

def run(s: Stepper, c: Components, args: dict[str, str]):
    for name, component in c.components.items():
        print(f"\n=======================")
        print(f"Name: {name}")
        print(f"Description: {component.description}")
        print(f"Directory: {component.dir}")

        for name, env in component.environments.items():
            print(f"\n[{name}]")
            print(f"Git Branch: {env.git_branch}")
            print(f"Systemd Service: {env.systemd_service}")
            print(f"Build Steps: {env.build_steps}")
            print(f"Tests: {env.tests}" if env.tests else "No tests available for this service+environment pair")