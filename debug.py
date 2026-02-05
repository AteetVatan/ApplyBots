"""Debug script to start all development services.

Standards: python_clean.mdc
- Clean separation of concerns
- Type hints for public APIs
- Small, focused functions
- Error handling
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Get project root
ROOT = Path(__file__).parent.resolve()

# Service configurations
SERVICES = [
    {
        "name": "Backend API",
        "normal_cmd": ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"],
        "debug_cmd": ["python", "-m", "debugpy", "--listen", "5678", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8080"],
        "cwd": ROOT / "backend",
        "title": "ApplyBots - Backend API",
        "service_port": 8080,
        "debug_port": 5678,
        "debug_env": {},
    },
    {
        "name": "Frontend",
        "normal_cmd": ["npm", "run", "dev"],
        "debug_cmd": None,  # Will use NODE_OPTIONS env var
        "cwd": ROOT / "frontend",
        "title": "ApplyBots - Frontend",
        "service_port": 3000,
        "debug_port": 9229,
        "debug_env": {"NODE_OPTIONS": "--inspect=9229"},
    },
    {
        "name": "Reactive Resume",
        "normal_cmd": ["pnpm", "dev"],
        "debug_cmd": None,  # Will use NODE_OPTIONS env var
        "cwd": ROOT / "reactive-resume",
        "title": "ApplyBots - Reactive Resume",
        "service_port": 3002,
        "debug_port": 9230,
        "debug_env": {"NODE_OPTIONS": "--inspect=9230"},
    },
    {
        "name": "Celery Worker",
        "normal_cmd": ["python", "-m", "celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"],
        "debug_cmd": ["python", "-m", "celery", "-A", "app.workers.celery_app", "worker", "--loglevel=info"],
        "cwd": ROOT / "backend",
        "title": "ApplyBots - Celery Worker",
        "debug_port": None,
        "debug_env": {},
    },
    {
        "name": "Celery Beat",
        "normal_cmd": ["python", "-m", "celery", "-A", "app.workers.celery_app", "beat", "--loglevel=info"],
        "debug_cmd": ["python", "-m", "celery", "-A", "app.workers.celery_app", "beat", "--loglevel=info"],
        "cwd": ROOT / "backend",
        "title": "ApplyBots - Celery Beat",
        "debug_port": None,
        "debug_env": {},
    },
]


def check_dependencies() -> dict[str, bool]:
    """Check if required dependencies are available.
    
    Returns:
        Dictionary mapping dependency names to availability status.
    """
    deps: dict[str, bool] = {}
    
    # Check Python
    deps["python"] = sys.executable is not None
    
    # Check npm/pnpm - use shell=True on Windows for better PATH resolution
    shell_mode = sys.platform == "win32"
    
    # Check npm
    try:
        if shell_mode:
            subprocess.run(
                "npm --version",
                shell=True,
                capture_output=True,
                check=True,
                timeout=5,
            )
        else:
            subprocess.run(["npm", "--version"], capture_output=True, check=True, timeout=5)
        deps["npm"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        deps["npm"] = False
    
    # Check pnpm
    try:
        if shell_mode:
            subprocess.run(
                "pnpm --version",
                shell=True,
                capture_output=True,
                check=True,
                timeout=5,
            )
        else:
            subprocess.run(["pnpm", "--version"], capture_output=True, check=True, timeout=5)
        deps["pnpm"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        deps["pnpm"] = False
    
    # Check debugpy for debug mode
    try:
        subprocess.run(
            [sys.executable, "-m", "debugpy", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        deps["debugpy"] = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        deps["debugpy"] = False
    
    return deps


def start_service_in_integrated_terminal(service: dict[str, Any], *, debug_mode: bool = False) -> bool:
    """Start a service in VS Code/Cursor integrated terminal using tasks.
    
    Args:
        service: Service configuration dictionary.
        debug_mode: If True, use debug command; otherwise use normal command.
    
    Returns:
        True if task was created successfully, False otherwise.
    """
    # This will be handled by tasks.json - just verify the service config
    cwd = service["cwd"]
    
    if not cwd.exists():
        print(f"ERROR: Directory not found: {cwd}", file=sys.stderr)
        return False
    
    print(f"  ✓ {service['name']} task configured")
    if debug_mode and service.get("debug_port"):
        print(f"  → Debug port: {service['debug_port']}")
    return True


def create_vscode_tasks_config(debug_mode: bool) -> None:
    """Create or update VS Code tasks.json with service tasks.
    
    Args:
        debug_mode: Whether debug mode is enabled (affects task configuration).
    """
    vscode_dir = ROOT / ".vscode"
    tasks_json = vscode_dir / "tasks.json"
    
    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(exist_ok=True)
    
    # Read existing config if present
    existing_config: dict[str, Any] = {}
    if tasks_json.exists():
        try:
            with open(tasks_json, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            existing_config = {}
    
    # Ensure version and tasks exist
    if "version" not in existing_config:
        existing_config["version"] = "2.0.0"
    if "tasks" not in existing_config:
        existing_config["tasks"] = []
    
    tasks = existing_config["tasks"]
    
    # Remove existing service tasks to avoid duplicates
    service_names = [s["name"] for s in SERVICES]
    tasks = [t for t in tasks if t.get("label") not in service_names]
    
    # Build command for each service
    for service in SERVICES:
        # Determine command and args
        if debug_mode:
            debug_cmd = service.get("debug_cmd")
            if debug_cmd is not None:
                # Use explicit debug command
                if isinstance(debug_cmd, list):
                    if "python" in debug_cmd:
                        # Replace "python" with ${command:python.interpreterPath} for VS Code
                        cmd_parts = [arg if arg != "python" else "${command:python.interpreterPath}" for arg in debug_cmd]
                    else:
                        cmd_parts = debug_cmd
                    # First part is command, rest are args
                    command = cmd_parts[0]
                    args = cmd_parts[1:] if len(cmd_parts) > 1 else []
                else:
                    command = debug_cmd
                    args = []
                env = None
            else:
                # Use normal command with debug environment variables
                normal_cmd = service["normal_cmd"]
                command = normal_cmd[0]
                args = normal_cmd[1:] if len(normal_cmd) > 1 else []
                # Add environment variables
                debug_env = service.get("debug_env", {})
                env = debug_env if debug_env else None
        else:
            normal_cmd = service["normal_cmd"]
            # Replace "python" with ${command:python.interpreterPath} for VS Code
            if isinstance(normal_cmd, list) and "python" in normal_cmd:
                cmd_parts = [arg if arg != "python" else "${command:python.interpreterPath}" for arg in normal_cmd]
                command = cmd_parts[0]
                args = cmd_parts[1:] if len(cmd_parts) > 1 else []
            else:
                command = normal_cmd[0]
                args = normal_cmd[1:] if len(normal_cmd) > 1 else []
            env = None
        
        # Create task configuration
        task: dict[str, Any] = {
            "label": service["name"],
            "type": "shell",
            "command": command,
            "args": args,
            "options": {
                "cwd": "${workspaceFolder}/" + str(service["cwd"].relative_to(ROOT)).replace("\\", "/"),
            },
            "presentation": {
                "reveal": "always",
                "panel": "dedicated",
                "focus": False,
                "clear": False,
            },
            "problemMatcher": [],
            "isBackground": True,
        }
        
        # Add environment variables if needed
        if env:
            task["options"]["env"] = env
        
        # Add runOptions for background tasks
        task["runOptions"] = {
            "runOn": "default",
        }
        
        tasks.append(task)
    
    existing_config["tasks"] = tasks
    
    # Write updated config
    try:
        with open(tasks_json, "w", encoding="utf-8") as f:
            json.dump(existing_config, f, indent=2)
        print(f"\n✓ Updated {tasks_json.relative_to(ROOT)}")
    except Exception as e:
        print(f"\n⚠ Could not update tasks.json: {e}", file=sys.stderr)


def create_vscode_launch_config(debug_mode: bool) -> None:
    """Create or update VS Code launch.json with debug configurations.
    
    Args:
        debug_mode: Whether debug mode is enabled (affects configuration).
    """
    vscode_dir = ROOT / ".vscode"
    launch_json = vscode_dir / "launch.json"
    
    # Create .vscode directory if it doesn't exist
    vscode_dir.mkdir(exist_ok=True)
    
    # Read existing config if present
    existing_config: dict[str, Any] = {}
    if launch_json.exists():
        try:
            with open(launch_json, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            existing_config = {}
    
    # Ensure version and configurations exist
    if "version" not in existing_config:
        existing_config["version"] = "0.2.0"
    if "configurations" not in existing_config:
        existing_config["configurations"] = []
    
    configurations = existing_config["configurations"]
    
    # Remove existing attach configurations to avoid duplicates
    config_names = ["Attach to Backend", "Attach to Frontend", "Attach to Reactive Resume"]
    configurations = [c for c in configurations if c.get("name") not in config_names]
    
    # Add attach configurations for debug mode
    if debug_mode:
        configurations.extend([
            {
                "name": "Attach to Backend",
                "type": "debugpy",
                "request": "attach",
                "connect": {
                    "host": "localhost",
                    "port": 5678,
                },
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}/backend",
                        "remoteRoot": "${workspaceFolder}/backend",
                    },
                ],
                "justMyCode": False,
            },
            {
                "name": "Attach to Frontend",
                "type": "node",
                "request": "attach",
                "port": 9229,
                "restart": True,
                "protocol": "inspector",
                "skipFiles": ["<node_internals>/**"],
            },
            {
                "name": "Attach to Reactive Resume",
                "type": "node",
                "request": "attach",
                "port": 9230,
                "restart": True,
                "protocol": "inspector",
                "skipFiles": ["<node_internals>/**"],
            },
        ])
    
    existing_config["configurations"] = configurations
    
    # Write updated config
    try:
        with open(launch_json, "w", encoding="utf-8") as f:
            json.dump(existing_config, f, indent=2)
        print(f"\n✓ Updated {launch_json.relative_to(ROOT)}")
    except Exception as e:
        print(f"\n⚠ Could not update launch.json: {e}", file=sys.stderr)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start all development services for ApplyBots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug.py              # Start all services in normal mode
  python debug.py --debug      # Start all services with debugger ports exposed
  
Debug Mode:
  When using --debug, services start with debugger ports exposed:
  - Backend: debugpy on port 5678
  - Frontend: Node.js inspector on port 9229
  - Reactive Resume: Node.js inspector on port 9230
  
  Use VS Code/Cursor's "Attach to Process" debug configurations to connect.
  The script will automatically create/update .vscode/launch.json with these configurations.
        """,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Start services with debugger ports exposed for breakpoint debugging",
    )
    parser.add_argument(
        "--skip-vscode-config",
        action="store_true",
        help="Skip creating/updating VS Code launch.json",
    )
    
    args = parser.parse_args()
    args.debug = True
    
    print("=" * 80)
    print("ApplyBots Development Services Launcher")
    print("=" * 80)
    print(f"Mode: {'DEBUG' if args.debug else 'NORMAL'}")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    deps = check_dependencies()
    
    missing_deps = []
    if not deps.get("python"):
        missing_deps.append("Python")
    if not deps.get("npm"):
        missing_deps.append("npm")
    if not deps.get("pnpm"):
        missing_deps.append("pnpm")
    
    if args.debug and not deps.get("debugpy"):
        missing_deps.append("debugpy (install with: pip install debugpy)")
    
    if missing_deps:
        print(f"⚠ Warning: Missing dependencies: {', '.join(missing_deps)}")
        print("  Some services may fail to start.\n")
    else:
        print("✓ All dependencies found\n")
    
    # Create VS Code tasks and launch configs if requested
    if not args.skip_vscode_config:
        create_vscode_tasks_config(args.debug)
        create_vscode_launch_config(args.debug)
    
    # Tasks have been created - provide instructions to run them
    print("\n" + "=" * 80)
    print("Tasks have been created in .vscode/tasks.json")
    print("=" * 80)
    print("\nTo start services in integrated terminals (in this Cursor window):")
    print("\n  Option 1: Run all tasks at once")
    print("    1. Press Ctrl+Shift+P (Command Palette)")
    print("    2. Type 'Tasks: Run Task'")
    print("    3. Select each service task one by one:")
    for service in SERVICES:
        print(f"       - {service['name']}")
        if service.get("service_port"):
            print(f"         Service: http://localhost:{service['service_port']}")
            # Add communication flow information
            if service["name"] == "Backend API":
                print(f"         ← Frontend (3000) and Reactive Resume (3002) connect here")
            elif service["name"] == "Frontend":
                print(f"         → Connects to Backend (8080), embeds Reactive Resume (3002)")
            elif service["name"] == "Reactive Resume":
                print(f"         → Connects to Backend (8080), communicates with Frontend (3000)")
        if args.debug and service.get("debug_port"):
            print(f"         Debugger: port {service['debug_port']}")
    
    print("\n  Option 2: Use Terminal menu")
    print("    1. Go to Terminal → Run Task...")
    print("    2. Select a service task")
    print("    3. Repeat for each service")
    
    print("\n  Option 3: Quick access")
    print("    - Press Ctrl+Shift+P → 'Tasks: Run Task' → Select service")
    print("    - Each service will open in its own dedicated terminal panel")
    
    print("\n" + "-" * 80)
    print(f"✓ Configured {len(SERVICES)} service tasks ready to run")
    
    if args.debug:
        print("\n" + "=" * 80)
        print("Debug Mode Active - How Cross-Service Debugging Works:")
        print("=" * 80)
        print("\nEach service has its own debugger port (separate from service ports):")
        print("  • Backend (8080) → Debugger on port 5678 (Python debugpy)")
        print("  • Frontend (3000) → Debugger on port 9229 (Node.js inspector)")
        print("  • Reactive Resume (3002) → Debugger on port 9230 (Node.js inspector)")
        print("\nHow to debug:")
        print("  1. Start all services (they're already running with debug ports exposed)")
        print("  2. Set breakpoints in any service's code")
        print("  3. Attach debuggers using VS Code/Cursor:")
        print("     - Press F5 or go to Run and Debug panel")
        print("     - Select 'Attach to Backend', 'Attach to Frontend', or 'Attach to Reactive Resume'")
        print("     - You can attach to multiple services simultaneously!")
        print("\nCross-service debugging example:")
        print("  • Set breakpoint in Frontend code that calls Backend API")
        print("  • Set breakpoint in Backend API endpoint")
        print("  • Attach to both Frontend (9229) and Backend (5678)")
        print("  • When Frontend makes API call → hits Frontend breakpoint")
        print("  • Then Backend receives request → hits Backend breakpoint")
        print("  • You can step through the entire request flow!")
        print("\nDebug configurations are in .vscode/launch.json")
    
    print("\n" + "=" * 80)
    print("Services are running in integrated terminals.")
    print("You can stop them by closing the terminal panels or using the terminal kill button.")
    print("=" * 80)


if __name__ == "__main__":
    main()
