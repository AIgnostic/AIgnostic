#!/usr/bin/env python3

# aignostic.py
import argparse
import subprocess
import sys

def run_docker_compose():
    try:
        subprocess.run(['docker', 'compose', '-f', 'docker-compose.local.yml', 'up'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Docker Compose: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(prog='aignostic', description='Aignostic CLI Tool')
    subparsers = parser.add_subparsers(dest='command', required=True)

    run_parser = subparsers.add_parser('run', help='Run the application using Docker Compose')
    run_parser.set_defaults(func=run_docker_compose)

    args = parser.parse_args()
    args.func()

if __name__ == '__main__':
    main()
