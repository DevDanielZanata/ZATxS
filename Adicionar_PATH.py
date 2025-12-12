import os
import sys
import platform
import subprocess
from pathlib import Path


class PathInstaller:
    def __init__(self, executable_name="ZATxS"):
        self.executable_name = executable_name
        self.system = platform.system()
        self.script_dir = Path(__file__).parent.absolute()

    def is_admin(self):
        try:
            if self.system == "Windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except:
            return False

    def add_to_path_windows(self):
        try:
            exe_path = str(self.script_dir)

            result = subprocess.run(
                ['reg', 'query', 'HKCU\\Environment', '/v', 'PATH'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                current_path = ""
                for line in result.stdout.split('\n'):
                    if 'PATH' in line and 'REG_' in line:
                        parts = line.split('REG_EXPAND_SZ', 1)
                        if len(parts) > 1:
                            current_path = parts[1].strip()
                        else:
                            parts = line.split('REG_SZ', 1)
                            if len(parts) > 1:
                                current_path = parts[1].strip()

                if exe_path.lower() in current_path.lower():
                    print(f"✓ '{exe_path}' is already in PATH")
                    return True


                new_path = f"{current_path};{exe_path}" if current_path else exe_path

                subprocess.run(
                    ['setx', 'PATH', new_path],
                    check=True,
                    capture_output=True
                )

                print(f"✓ Successfully added '{exe_path}' to PATH")
                print("\n⚠ IMPORTANT: You need to restart your terminal/CMD for changes to take effect")
                return True
            else:
           
                subprocess.run(
                    ['setx', 'PATH', exe_path],
                    check=True,
                    capture_output=True
                )
                print(f"✓ Successfully created PATH and added '{exe_path}'")
                print("\n⚠ IMPORTANT: You need to restart your terminal/CMD for changes to take effect")
                return True

        except subprocess.CalledProcessError as e:
            print(f"✗ Error modifying PATH: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False

    def add_to_path_unix(self):
        try:
            exe_path = str(self.script_dir)
            home = Path.home()

            shell_profiles = [
                home / '.bashrc',
                home / '.bash_profile',
                home / '.zshrc',
                home / '.profile'
            ]

            profile_file = None
            for profile in shell_profiles:
                if profile.exists():
                    profile_file = profile
                    break

            if profile_file is None:
                profile_file = home / '.bashrc'

            export_line = f'export PATH="$PATH:{exe_path}"'

            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    content = f.read()
                    if exe_path in content:
                        print(f"✓ '{exe_path}' is already in PATH ({profile_file.name})")
                        return True

            with open(profile_file, 'a') as f:
                f.write(f'\n# Added by ZATxS installer\n')
                f.write(f'{export_line}\n')

            print(f"✓ Successfully added '{exe_path}' to PATH")
            print(f"  Modified file: {profile_file}")
            print(f"\n⚠ IMPORTANT: Run 'source {profile_file}' or restart your terminal")

            return True

        except Exception as e:
            print(f"✗ Error modifying PATH: {e}")
            return False

    def create_executable_wrapper(self):
        if self.system == "Windows":
            exe_file = self.script_dir / f"{self.executable_name}.exe"
            bat_file = self.script_dir / f"{self.executable_name}.bat"
            py_file = self.script_dir / f"{self.executable_name}.py"

            if not exe_file.exists() and py_file.exists():
                with open(bat_file, 'w') as f:
                    f.write(f'@echo off\n')
                    f.write(f'python "{py_file}" %*\n')
                print(f"✓ Created batch wrapper: {bat_file.name}")
        else:
            py_file = self.script_dir / f"{self.executable_name}.py"
            if py_file.exists():
                os.chmod(py_file, 0o755)
                print(f"✓ Made executable: {py_file.name}")

    def install(self):
        print("=" * 70)
        print(f"ZATxS PATH INSTALLER")
        print("=" * 70)
        print(f"\nExecutable: {self.executable_name}")
        print(f"Location: {self.script_dir}")
        print(f"System: {self.system}")
        print()

        self.create_executable_wrapper()

        if self.system == "Windows":
            success = self.add_to_path_windows()
        elif self.system in ["Linux", "Darwin"]:
            success = self.add_to_path_unix()
        else:
            print(f"✗ Unsupported operating system: {self.system}")
            return False

        if success:
            print("\n" + "=" * 70)
            print("INSTALLATION COMPLETED")
            print("=" * 70)
            print(f"\nYou can now use '{self.executable_name}' from anywhere in the terminal")
            print("\nTest it by running:")
            print(f"  {self.executable_name} --help")
            print()

        return success

    def uninstall(self):
        print("=" * 70)
        print(f"ZATxS PATH UNINSTALLER")
        print("=" * 70)

        exe_path = str(self.script_dir)

        if self.system == "Windows":
            try:
                # Get current PATH
                result = subprocess.run(
                    ['reg', 'query', 'HKCU\\Environment', '/v', 'PATH'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    current_path = ""
                    for line in result.stdout.split('\n'):
                        if 'PATH' in line and 'REG_' in line:
                            parts = line.split('REG_EXPAND_SZ', 1)
                            if len(parts) > 1:
                                current_path = parts[1].strip()
                            else:
                                parts = line.split('REG_SZ', 1)
                                if len(parts) > 1:
                                    current_path = parts[1].strip()

                    paths = [p.strip() for p in current_path.split(';') if p.strip()]
                    new_paths = [p for p in paths if p.lower() != exe_path.lower()]

                    if len(new_paths) < len(paths):
                        new_path = ';'.join(new_paths)
                        subprocess.run(['setx', 'PATH', new_path], check=True)
                        print(f"✓ Removed '{exe_path}' from PATH")
                        print("\n⚠ Restart your terminal for changes to take effect")
                    else:
                        print(f"✓ '{exe_path}' was not in PATH")

            except Exception as e:
                print(f"✗ Error: {e}")

        else:
            # Unix/Linux
            home = Path.home()
            shell_profiles = [
                home / '.bashrc',
                home / '.bash_profile',
                home / '.zshrc',
                home / '.profile'
            ]

            for profile in shell_profiles:
                if profile.exists():
                    with open(profile, 'r') as f:
                        lines = f.readlines()

                    new_lines = [line for line in lines if exe_path not in line]

                    if len(new_lines) < len(lines):
                        with open(profile, 'w') as f:
                            f.writelines(new_lines)
                        print(f"✓ Removed from {profile.name}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--uninstall":
        installer = PathInstaller("ZATxS")
        installer.uninstall()
    else:
        installer = PathInstaller("ZATxS")
        installer.install()

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()