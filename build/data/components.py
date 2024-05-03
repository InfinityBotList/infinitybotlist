import pydantic
from ruamel.yaml import YAML
from typing import TypeVar, Generic, Any

T = TypeVar("T", bound=Any)

class Differs(pydantic.BaseModel, Generic[T]):
    """A class that represents a difference between two values"""
    staging: T 
    """The old value"""
    prod: T
    """The new value"""

class Component(pydantic.BaseModel):
    repo: str
    """The repository name of the component"""

    description: str
    """A brief description of the component"""

    dir: str
    """The directory of the component"""

    bin: str | None = None
    """The binary name of the component"""

    envs: list[str] | None = ["staging"]
    """The environments in which the component can be deployed in"""

    env_file: str | None = None
    """The environment file for the component. Only useful for components with staging/prod envs"""

    systemd_service: Differs[str] | None = None
    """The systemd service file for the component"""

    build: Differs[list[str]]
    """The build commands for the component"""

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