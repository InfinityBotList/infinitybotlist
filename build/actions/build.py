"""Build all components"""

from libstep import Stepper
from data.components import ComponentEnvironment, Components, Component
import subprocess

def run(s: Stepper, c: Components, args: dict[str, str]):
    components: dict[str, Component] = {}

    components_str = args.get("components")

    if not components_str:
        components = c.components
    else:
        component_strlist = components_str.split(",")

        for component_str in component_strlist:
            component_str = component_str.strip()
            if component_str not in c.components:
                print(f"ERROR: Component {component_str} not found.")
                exit(1)

            components[component_str] = c.components[component_str]

    for component_name, component in components.items():
        environment = args.get(f"{component_name}.env")
        envs: dict[str, ComponentEnvironment] = []

        if environment:
            if environment not in component.environments:
                print(f"ERROR: Environment {environment} not found for component {component_name}")
                exit(1)

            envs = {environment: component.environments[environment]}
        else:
            envs = component.environments

        for env_name, env in envs.items():
            print(f"=> {component_name} [env={env_name}]")

            for build_step in env.build_steps:
                print(f"  - {build_step}")
                # Call the build step using subprocess.call
                ret = subprocess.call(build_step, shell=True, cwd=f"src/{component.dir}/{env_name}")

                if ret != 0:
                    print(f"ERROR: Build step failed with code {ret}")
                    exit(1)