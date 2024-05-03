"""List all components and their info"""

from libstep import Stepper
from data.components import Components

def run(s: Stepper, c: Components, args: dict[str, str]):
    for name, component in c.components.items():
        print(f"\n=======================")
        print(f"Name: {name}")
        print(f"Description: {component.description}")
        print(f"Directory: {component.dir}")
        print(f"Binary: {component.bin}")
        print(f"Environments: {component.envs}")
        print(f"Environment File: {component.env_file}")
        print(f"Systemd Service: {component.systemd_service}")
        print(f"Build: {component.build}")
        print(f"Supports Prod: {component.supports_prod}")
