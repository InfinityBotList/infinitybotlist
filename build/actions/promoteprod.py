"""Promotes a staging build to production"""

from libstep import Stepper
from data.components import Components
import subprocess
import secrets
from .populate import run as populate_run

"""
	rm -rf ../prod2
	cd .. && cp -rf staging prod2
	echo "prod" > ../prod2/config/current-env
	cd ../prod2 && make && rm -rf ../prod && mv -vf ../prod2 ../prod && sudo systemctl restart popplio-prod
	cd ../prod && make ts

	# Git push to "current-prod" branch
	cd ../prod && git branch current-prod && git add -v . && git commit -m "Promote staging to prod" && git push -u origin HEAD:current-prod --force
"""

def run(s: Stepper, c: Components, args: dict[str, str]):
    project = args.get("component")

    if not project:
        print("ERROR: component required.")
        exit(1)

    found_comp = c.find(project)

    if not found_comp:
        print(f"ERROR: Component {project} not found.")
        exit(1)

    proj_root = f"src/{found_comp.dir}"

    print(f"Pushing current staging to git")
    subprocess.call(["git", "add", "-v", "."], cwd=f"{proj_root}/staging")
    subprocess.call(["git", "commit", "-m", "Push staging pre-promotion"], cwd=f"{proj_root}/staging")
    subprocess.call(["git", "push", "origin", "--force"], cwd=f"{proj_root}/staging")

    print(f"Removing folder '{proj_root}/prod2' and making temp submodule")
    subprocess.call(["git", "rm", "-rf", f"{proj_root}/prod2"])
    subprocess.call(["rm", "-rf", f"{proj_root}/prod2"])

    tempid = secrets.token_hex(8)
    subprocess.call(["git", "submodule", "add", "-b", found_comp.env_branches["staging"], "--name", tempid, found_comp.repo, f"{proj_root}/prod2"])


    if found_comp.env_file:
        print(f"Setting current environment to 'prod'")
        with open(f"{proj_root}/prod2/{found_comp.env_file}", "w") as f:
            f.write("prod")

    # Try fixing some stuff
    print("Adding current-env (and other) changes to prod")
    subprocess.call(["git", "push", "origin", "--delete", "current-prod"], cwd=f"{proj_root}/prod2")
    subprocess.call(["git", "add", "-v", "."], cwd=f"{proj_root}/prod2")
    subprocess.call(["git", "commit", "-m", "Promote staging to prod"], cwd=f"{proj_root}/prod2")
    subprocess.call(["git", "push", "-u", "origin", "HEAD:current-prod", "--force"], cwd=f"{proj_root}/prod2")

    print(f"Building '{proj_root}/prod2'")
    for cmd in found_comp.build.prod:
        subprocess.call(cmd.split(" "), cwd=f"{proj_root}/prod2")

    print(f"Removing 'prod' and 'prod2'")
    subprocess.call(["git", "rm", "--cached", "-f", f"{proj_root}/prod2"])
    subprocess.call(["git", "rm", "-rf", f"{proj_root}/prod2"])
    subprocess.call(["rm", "-rf", f"{proj_root}/prod"])
    subprocess.call(["rm", "-rf", f"{proj_root}/prod2"])

    # Hacky solution, remove temp submodule from .gitmodules manually
    with open(f"{s.get_repo_root()}/.gitmodules", "r") as f:
        lines = f.readlines()

    with open(f"{s.get_repo_root()}/.gitmodules", "w") as f:
        for line in lines:
            if tempid not in line:
                f.write(line)
            else:
                break
            

    print(f"Running populate")
    populate_run(s, c, {})
