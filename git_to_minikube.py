import os
import subprocess
import argparse
import platform

def run_cmd(cmd, cwd=None):
    """Run a shell command and print output (UTF-8 safe)"""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        check=True,
        text=True,
        capture_output=True,
        cwd=cwd,
        encoding="utf-8",   # <-- force UTF-8 decoding
        errors="replace"    # <-- replace any undecodable chars safely
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

def configure_minikube_docker_env():
    """Configure Docker to use Minikube depending on OS"""
    system = platform.system()
    print("\n>>> Configuring Docker to use Minikube's daemon...")

    if system == "Windows":
        # Use cmd style output for easier parsing
        result = subprocess.run(
            ["minikube", "-p", "minikube", "docker-env", "--shell", "cmd"],
            text=True, capture_output=True, check=True
        )

        for line in result.stdout.splitlines():
            if line.startswith("SET "):  # e.g. "SET DOCKER_HOST=tcp://..."
                key, val = line[4:].split("=", 1)
                os.environ[key] = val
                print(f"Set {key}={val}")

    else:  # Linux/macOS
        result = subprocess.run(
            ["minikube", "-p", "minikube", "docker-env", "--shell", "bash"],
            text=True, capture_output=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("export "):  # e.g. "export DOCKER_HOST=tcp://..."
                key, val = line[7:].split("=", 1)
                os.environ[key] = val
                print(f"Set {key}={val}")

def main(repo, image, deploy_file, service_file=None):
    # Step 1: Clone repo
    repo_name = repo.split("/")[-1].replace(".git", "")
    if not os.path.exists(repo_name):
        run_cmd(f"git clone {repo}")
    else:
        print(f"Repo {repo_name} already exists, pulling latest changes...")
        run_cmd("git pull", cwd=repo_name)

    # Step 2: Configure docker to use Minikube
    configure_minikube_docker_env()

    # Step 3: Build docker image inside repo dir
    run_cmd(f"docker build -t {image} .", cwd=repo_name)

    # Step 4: Deploy to Kubernetes
    run_cmd(f"kubectl apply -f {deploy_file}")

    if service_file:
        run_cmd(f"kubectl apply -f {service_file}")
    else:
        print("\n>>> Skipping Service deployment (no service file provided).")

    # Step 5: Show status
    run_cmd("kubectl get pods")
    run_cmd("kubectl get svc")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy Python app from Git to Minikube")
    parser.add_argument("--repo", required=True, help="Git repo URL")
    parser.add_argument("--image", required=True, help="Docker image name (e.g., my-app:1.0)")
    parser.add_argument("--deploy-file", required=True, help="Path to deployment.yaml")
    parser.add_argument("--service-file", required=False, help="Path to service.yaml (optional)")  # <-- not required
    args = parser.parse_args()

    main(args.repo, args.image, args.deploy_file, args.service_file)
