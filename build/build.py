#!/usr/bin/env python3
from data.components import Components
from libstep import Stepper
import os
import sys
from importlib import import_module 
from types import ModuleType

components = Components.load()
stepper = Stepper()

supported_actions: dict[str, ModuleType] = {}
for action in os.listdir("build/actions"):
    if action.endswith(".py"):
        module = import_module(f"actions.{action[:-3]}")
        supported_actions[action[:-3]] = module

def show_supported_actions():
    print("Supported Actions:")
    for action in supported_actions.keys():
        runnable = supported_actions[action].__dict__.get('run') is not None
        print(f"  - {action}: {supported_actions[action].__doc__} (runnable: {runnable})")

if len(supported_actions) == 0:
    print("No supported actions found.")
    exit(1)

if len(sys.argv) < 2:
    print("Usage: ./build.py <action>")
    show_supported_actions()
    exit(1)

action = sys.argv[1]

if action not in supported_actions.keys():
    print(f"ERROR: Action {action} not supported.")
    show_supported_actions()
    exit(1)

args = {}

if len(sys.argv) > 2:
    for arg in sys.argv[2:]:
        split = arg.split("=", maxsplit=2)
        if len(split) != 2:
            split = [split[0], ""]
        
        args[split[0]] = split[1]

runnable = supported_actions[action].__dict__.get('run') is not None
if not runnable:
    print(f"ERROR: Action {action} does not have a run function.")
    show_supported_actions()
    exit(1)

supported_actions[action].run(stepper, components, args)