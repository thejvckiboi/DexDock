# Welcome to DexDock X64! Here you can view and alter the code that makes DexDock run.

import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import winreg

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "DexDock"


class DexDock:

    def __init__(self, root):
        self.root = root
        self.root.title("DexDock v1.0.1")
        self.root.geometry("420x570")
        self.root.resizable(False, False)

        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.base_dir, "config.json")
        self.config = self.load_config()

        try:
            icon_path = os.path.join(self.base_dir, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass

        padding = {"padx": 15, "pady": 4}

        # Resolution Text Input
        ttk.Label(root, text="Display Resolution:").pack(anchor="w", **padding)
        self.res_var = tk.StringVar(value=self.config.get("resolution", "1920x1080"))
        res_entry = ttk.Entry(root, textvariable=self.res_var)
        res_entry.pack(fill="x", padx=15, pady=2)

        # DPI Text Input
        ttk.Label(root, text="Display DPI:").pack(anchor="w", **padding)
        self.dpi_var = tk.StringVar(value=self.config.get("dpi", "160"))
        dpi_entry = ttk.Entry(root, textvariable=self.dpi_var)
        dpi_entry.pack(fill="x", padx=15, pady=2)

        # Refresh Rate selection
        ttk.Label(root, text="Refresh Rate (FPS):").pack(anchor="w", **padding)
        self.fps_var = tk.StringVar(value=self.config.get("fps", "60"))
        fps_dropdown = ttk.Combobox(
            root,
            textvariable=self.fps_var,
            values=["60", "90", "120", "144"],
            state="readonly",
        )
        fps_dropdown.pack(fill="x", padx=15, pady=2)

        # Codec selection
        ttk.Label(root, text="Video Codec:").pack(anchor="w", **padding)
        self.codec_var = tk.StringVar(value=self.config.get("codec", "h265"))
        codec_dropdown = ttk.Combobox(
            root,
            textvariable=self.codec_var,
            values=["h264", "h265", "av1"],
            state="readonly",
        )
        codec_dropdown.pack(fill="x", padx=15, pady=2)

        # Bitrate selection
        ttk.Label(root, text="Video Bitrate:").pack(anchor="w", **padding)
        self.bitrate_var = tk.StringVar(value=self.config.get("bitrate", "8M"))
        bitrate_dropdown = ttk.Combobox(
            root,
            textvariable=self.bitrate_var,
            values=["4M", "8M", "16M", "24M", "32M"],
            state="readonly",
        )
        bitrate_dropdown.pack(fill="x", padx=15, pady=2)

        # Fullscreen Checkbox
        self.fullscreen_var = tk.BooleanVar(
            value=self.config.get("fullscreen", True)
        )
        fullscreen_chk = ttk.Checkbutton(
            root,
            text="Launch in Fullscreen [Press FN + F11 to exit]",
            variable=self.fullscreen_var,
        )
        fullscreen_chk.pack(anchor="w", padx=15, pady=5)

        # Run at Startup Checkbox
        self.startup_var = tk.BooleanVar(value=self.check_startup_status())
        startup_chk = ttk.Checkbutton(
            root,
            text="Run DexDock when Windows starts",
            variable=self.startup_var,
            command=self.toggle_startup,
        )
        startup_chk.pack(anchor="w", padx=15, pady=2)

        # Action Buttons Frame 1 (Shortcuts)
        shortcut_frame = ttk.Frame(root)
        shortcut_frame.pack(fill="x", padx=15, pady=6)

        desktop_btn = ttk.Button(
            shortcut_frame,
            text="Create Desktop Shortcut",
            command=self.create_desktop_shortcut,
        )
        desktop_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        startmenu_btn = ttk.Button(
            shortcut_frame,
            text="Add to Start Menu & Search",
            command=self.create_start_menu_shortcut,
        )
        startmenu_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Action Button Frame 2 (Launch)
        launch_frame = ttk.Frame(root)
        launch_frame.pack(fill="x", padx=15, pady=4)

        launch_btn = ttk.Button(
            launch_frame, text="Launch DexDock", command=self.launch_scrcpy
        )
        launch_btn.pack(expand=True, fill="x")

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        config_data = {
            "resolution": self.res_var.get().strip(),
            "dpi": self.dpi_var.get().strip(),
            "fps": self.fps_var.get(),
            "codec": self.codec_var.get(),
            "bitrate": self.bitrate_var.get(),
            "fullscreen": self.fullscreen_var.get(),
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        except Exception:
            pass

    def check_startup_status(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def toggle_startup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_WRITE
            )
            if self.startup_var.get():
                app_path = (
                    f'"{sys.executable}"'
                    if getattr(sys, "frozen", False)
                    else f'"{sys.executable}" "{os.path.abspath(__file__)}"'
                )
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror(
                "Registry Error", f"Could not update startup settings:\n{e}"
            )
            self.startup_var.set(not self.startup_var.get())

    def create_desktop_shortcut(self):
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "DexDock.lnk")
            target = (
                sys.executable
                if getattr(sys, "frozen", False)
                else os.path.abspath(__file__)
            )
            icon_path = os.path.join(self.base_dir, "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = target

            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{target}"
            $Shortcut.WorkingDirectory = "{self.base_dir}"
            $Shortcut.IconLocation = "{icon_path},0"
            $Shortcut.Save()
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True
            )
            if result.returncode == 0:
                messagebox.showinfo(
                    "Success", "Desktop shortcut created successfully!"
                )
            else:
                messagebox.showerror("Error", f"Failed to create shortcut:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def create_start_menu_shortcut(self):
        try:
            appdata = os.path.expandvars(r"%AppData%")
            start_menu_programs = os.path.join(
                appdata, r"Microsoft\Windows\Start Menu\Programs"
            )
            os.makedirs(start_menu_programs, exist_ok=True)
            shortcut_path = os.path.join(start_menu_programs, "DexDock.lnk")

            target = (
                sys.executable
                if getattr(sys, "frozen", False)
                else os.path.abspath(__file__)
            )
            icon_path = os.path.join(self.base_dir, "icon.ico")
            if not os.path.exists(icon_path):
                icon_path = target

            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{target}"
            $Shortcut.WorkingDirectory = "{self.base_dir}"
            $Shortcut.IconLocation = "{icon_path},0"
            $Shortcut.Save()
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True
            )
            if result.returncode == 0:
                messagebox.showinfo(
                    "Success", "DexDock has been added to your Start Menu & Search!"
                )
            else:
                messagebox.showerror(
                    "Error", f"Failed to add to Start Menu:\n{result.stderr}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def launch_scrcpy(self):
        self.save_config()

        resolution = self.res_var.get().strip()
        dpi = self.dpi_var.get().strip()
        fps = self.fps_var.get()
        codec = self.codec_var.get()
        bitrate = self.bitrate_var.get()

        display_arg = f"{resolution}/{dpi}"
        scrcpy_path = os.path.join(self.base_dir, "scrcpy.exe")

        cmd = [
            scrcpy_path,
            f"--new-display={display_arg}",
            f"--video-codec={codec}",
            f"--max-fps={fps}",
            f"--video-bit-rate={bitrate}",  # Fixed from --video-bitrate
            "--mouse=sdk",
            "--keyboard=uhid",
        ]

        if self.fullscreen_var.get():
            cmd.append("--fullscreen")

        try:
            creationflags = 0x08000000  # CREATE_NO_WINDOW
            subprocess.Popen(cmd, cwd=self.base_dir, creationflags=creationflags)
        except FileNotFoundError:
            messagebox.showerror(
                "Error",
                f"Could not find scrcpy.exe at:\n{scrcpy_path}\n\nMake sure it is"
                " sitting in this exact folder.",
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = DexDock(root)
    root.mainloop()
