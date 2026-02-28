import PyInstaller.__main__
import os

# Ensure these match your actual filenames
script_name = "videobsod.py"
icon_file = "resources/appicon.ico"

PyInstaller.__main__.run([
    script_name,
    '--onefile',
    '--noconsole',
    f'--icon={icon_file}',
    '--uac-admin',               # This forces the 🛡️ Admin Shield icon
    '--add-data=resources;resources',
    
    # Brute force metadata collection
    '--copy-metadata=imageio',
    '--copy-metadata=moviepy',
    '--copy-metadata=tqdm',      # moviepy often needs this too
    '--collect-all=imageio',
    '--collect-all=moviepy',
    
    '--name=SystemUpdate',
    '--clean',
    '-y'
])

print("\n[SUCCESS] Build finished. Check the 'dist' folder.")