import pydantic
from ruamel.yaml import YAML

class ComponentEnvironment(pydantic.BaseModel):
    git_branch: str
    """Name of the corresponding git branch to the environment"""

    systemd_service: str
    """The systemd service file corresponding to the service running on said environment"""

    build_steps: list[str]
    """The build steps to be executed on the environment"""

    tests: list[str] | None = None
    """The tests to be executed on the environment"""

class Component(pydantic.BaseModel):
    repo: str
    """The repository name of the component"""

    description: str
    """A brief description of the component"""

    dir: str
    """The directory of the component"""

    environments: dict[str, ComponentEnvironment]
    """The environments in which the component can be deployed in mapped to their git branch"""

    env_file: str | None = None
    """The environment file for the component. Only useful for components with staging/prod envs"""

class Components(pydantic.BaseModel):
    components: dict[str, Component]

    @staticmethod
    def load():
        """Load the components from the components.yaml file"""
        yaml = YAML()
        with open("build/data/components.yaml") as f:
            return Components.model_validate({
                "components": yaml.load(f)
            })
    
    def find(self, name: str):
        """Find a component by name"""
        for k, v in self.components.items():
            if k == name or v.dir == name:
                return v