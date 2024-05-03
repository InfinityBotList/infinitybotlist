#!/usr/bin/env python3
import subprocess
import typing
import sys
import pydantic
import tqdm
import contextlib

class Step(pydantic.BaseModel):
    """Name of the current step"""
    name: str
    """Function to call to execute the step"""
    func: typing.Callable

class DummyFile(object):
    file = None
    def __init__(self, rds: "Stepper", file):
        self.file = file
        self.rds = rds

    def write(self, x):
        # Avoid print() second call (useless \n)
        if len(x.rstrip()) > 0:
            self.rds.pbar.write(x, file=self.file)
    
    def flush(self):
        pass

    def fileno(self):
        return self.file.fileno()

class Stepper():
    repo_root: str
    state: dict[str, str]
    step: list[Step]
    pbar: tqdm.tqdm

    def __init__(
            self,
        ):
        self.repo_root = self.get_repo_root()
        self.state = {}
        self.pbar = None
        self.steps = []
    
    def get_input(self, str: str):
        """Get input from the user"""
        try:
            return input(str + ": ")
        except (KeyboardInterrupt, EOFError):
            print("Aborting due to KeyboardInterrupt or EOFError")
            sys.exit(1)
            

    def get_input_bool(self, str: str):
        """Get input from the user, but only allow y/n"""
        while True:
            inp = self.get_input(str + " (y/n)")
            if inp == "y":
                return True
            elif inp == "n":
                return False
            else:
                print("Invalid input, please enter y or n")
    
    def get_input_choice(self, str: str, choices: typing.List[str]):
        """Get input from the user, but only allow one of the choices"""
        while True:
            inp = self.get_input(str + " ({})".format(", ".join(choices)))
            if inp in choices:
                return inp
            else:
                print("Invalid input, please enter one of the choices")
    
    def get_input_int(self, str: str):
        """Get input from the user, but only allow integers"""
        while True:
            inp = self.get_input(str)
            try:
                return int(inp)
            except ValueError:
                print("Invalid input, please enter an integer")
    
    def get_repo_root(self):
        """Call git", "rev-parse", "--show-toplevel to get the root of the git repo"""
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode("utf-8").strip()

    @contextlib.contextmanager
    def _redirect(rds):
        save_stdout = sys.stdout
        sys.stdout = DummyFile(rds, sys.stdout)
        yield
        sys.stdout = save_stdout
    
    def exec(self, cmd: typing.List[str]):
        """Execute a command, redirecting stdout to tqdm.write and returning the output"""
        self.pbar.write(f"> `{' '.join(cmd)}`")
        with contextlib.redirect_stdout(DummyFile(self, sys.stdout)):
            return subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stdout)

    def main(self):
        self.repo_root = self.get_repo_root()

        print("libstep initialized")
        print("Repo root: {}".format(self.repo_root))
        
        self.pbar = tqdm.tqdm(total=100, file=sys.stdout)

        with self._redirect():
            for step in self.steps:
                self.pbar.update(round(100 / (len(self.steps) + 1)))
                self.pbar.set_description(step.name)
                step.func()
            
            self.pbar.update(round(100 / (len(self.steps) + 1)))

            self.pbar.close()
    
    def step(self, name: str):
        """Decorator for adding steps"""
        def decorator(func):
            self.steps.append(Step(name=name, func=func))
            return func
        return decorator