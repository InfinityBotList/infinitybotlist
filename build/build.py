#!/usr/bin/env python3
from data.components import Components
from libstep import Stepper

components = Components.load()
stepper = Stepper()

@stepper.step("Test")
def test():
    print("Testing")

stepper.main()