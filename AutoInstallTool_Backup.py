import os
import shutil
import subprocess
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
import winsound
import sys
import ctypes
import json
import time

# Ghi đè CTkFont để sử dụng Segoe UI mặc định giúp dịu mắt hơn
_orig_CTkFont = ctk.CTkFont
def soft_font(*args, **kwargs):
    if "family" not in kwargs:
        kwargs["family"] = "Segoe UI"
    return _orig_CTkFont(*args, **kwargs)
ctk.CTkFont = soft_font

# --- Tự động yêu cầu quyền Admin ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# --- Chỉ cho phép chạy 1 instance duy nhất ---
MUTEX_NAME = "Global\\AutoInstallTool_Mutex_PhamSu"

def check_single_instance():
    global mutex_handle
    kernel32 = ctypes.windll.kernel32
    mutex_handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
    
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        kernel32.CloseHandle(mutex_handle)
        return False
    return True

if not check_single_instance():
    from tkinter import messagebox
    messagebox.showwarning("Thông báo", "Ứng dụng đang chạy!\nVui lòng tắt ứng dụng trước khi khởi chạy lại.")
    sys.exit()

# --- Thiết lập giao diện CustomTkinter ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# --- Hàm đọc cấu hình ---
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("apps", [])
    except Exception as e:
        print(f"Lỗi đọc file config.json: {e}")
        return []


# --- Tạo cửa sổ chính ---
root = ctk.CTk()
root.title("Auto install app by Phạm Sự")
root.geometry("900x650")
root.resizable(False, False)

apps = load_config()

# ==============================================================================
# LAYOUT CHÍNH: SIDEBAR, HEADER, CONTENT AREA (MAIN & LOG)
# ==============================================================================

# --- 1. Sidebar ---
sidebar_frame = ctk.CTkFrame(root, width=220, corner_radius=0)
sidebar_frame.pack(side="left", fill="both")
sidebar_frame.pack_propagate(False)

header_label = ctk.CTkLabel(sidebar_frame, text="AUTO INSTALL TOOL", font=ctk.CTkFont(size=18, weight="bold"))
header_label.pack(padx=20, pady=(25, 20), anchor="w")

# --- 2. Container cho phần còn lại bên phải ---
right_container = ctk.CTkFrame(root, fg_color="transparent")
right_container.pack(side="right", fill="both", expand=True)

# --- 3. Header ---
header_frame = ctk.CTkFrame(right_container, height=65, corner_radius=0)
header_frame.pack(side="top", fill="x")

appearance_mode_menu = ctk.CTkOptionMenu(
    header_frame, values=["System", "Dark", "Light"], command=lambda mode: ctk.set_appearance_mode(mode)
)
appearance_mode_menu.pack(side="right", padx=20, pady=18)

# --- 4. Content Area dưới Header ---
content_area = ctk.CTkFrame(right_container, fg_color="transparent")
content_area.pack(side="top", fill="both", expand=True)

# --- 5. Main Section (Chứa các Tab) ---
main_frame = ctk.CTkFrame(content_area, fg_color="transparent")
main_frame.pack(fill="both", expand=True)

# Các Tab nội dung inside main_frame
install_tab = ctk.CTkFrame(main_frame, fg_color="transparent")
edit_tab = ctk.CTkFrame(main_frame, fg_color="transparent")
info_tab = ctk.CTkFrame(main_frame, fg_color="transparent")


# --- Hàm log thread-safe ---
def log(msg):
    root.after(0, lambda: _log(msg))


def _log(msg):
    log_text.configure(state="normal")
    timestamp = time.strftime("[%H:%M:%S] ")
    
    if msg.startswith("SUMMARY:"):
        parts = msg.replace("SUMMARY:", "").split("/")
        success = int(parts[0])
        total = int(parts[1])
        
        log_text._textbox.insert("end", timestamp)
        log_text._textbox.insert("end", "Đã hoàn thành cài đặt ", "green_text")
        if success < total:
            log_text._textbox.insert("end", str(success), "red_text")
        else:
            log_text._textbox.insert("end", str(success), "green_text")
        log_text._textbox.insert("end", f"/{total} ứng dụng.\n", "green_text")
        
        log_text.configure(state="disabled")
        log_text.see("end")
        return
        
    tag = None
    if msg.startswith("[SUCCESS]"):
        tag = "success"
    elif msg.startswith("[ERROR]"):
        tag = "error"
    elif msg == "Trình cài đặt đã đóng...":
        tag = "end"
        
    if tag:
        log_text._textbox.insert("end", timestamp + msg + "\n", tag)
    else:
        log_text._textbox.insert("end", timestamp + msg + "\n")
        
    log_text.configure(state="disabled")
    log_text.see("end")


def clear_log():
    log_text.configure(state="normal")
    log_text.delete("1.0", "end")
    log_text.configure(state="disabled")


# ==============================================================================
# NỘI DUNG TAB: CÀI ĐẶT APP (install_tab)
# ==============================================================================
top_frame = ctk.CTkFrame(install_tab, fg_color="transparent")
top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(10, 5))

title_label = ctk.CTkLabel(top_frame, text="Chọn ứng dụng cần cài đặt", font=ctk.CTkFont(size=16, weight="bold"))
title_label.pack(anchor="w", padx=10, pady=(5, 5))

frame = ctk.CTkScrollableFrame(top_frame)
frame.pack(fill="both", expand=True, padx=5, pady=5)

bottom_frame = ctk.CTkFrame(install_tab, fg_color="transparent")
bottom_frame.pack(side="bottom", fill="both", expand=True, padx=20, pady=(5, 10))

checkbox_grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
checkbox_grid_frame.pack(fill="both", padx=10, pady=5, expand=True)


def toggle_chip(var, btn):
    new_state = not var.get()
    var.set(new_state)
    if new_state:
        btn.configure(fg_color="#2ecc71", hover_color="#27ae60")
    else:
        btn.configure(fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"))
    update_select_all_btn()


vars = []


def load_app_list():
    global apps, vars
    for widget in checkbox_grid_frame.winfo_children():
        widget.destroy()
        
    apps = load_config()
    vars = []
    columns = 3

    for i, app in enumerate(apps):
        name = app.get("name", "Unknown")
        exe = app.get("exe", "")
        var = ctk.BooleanVar(value=False)

        btn = ctk.CTkButton(
            checkbox_grid_frame,
            text=name,
            corner_radius=8,
            height=40,
            fg_color=("gray75", "gray30"),
            hover_color=("gray65", "gray40"),
            text_color=("black", "white"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn.configure(command=lambda v=var, b=btn: toggle_chip(v, b))
        
        r = i // columns
        c = i % columns
        btn.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        checkbox_grid_frame.grid_columnconfigure(c, weight=1)
        
        vars.append((var, exe, name, btn))
        
    update_select_all_btn()


btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
btn_frame.pack(fill="x", padx=5, pady=5)


def update_select_all_btn():
    all_selected = all(var.get() for var, _, _, _ in vars) if vars else False
    if all_selected:
        btn_select_all.configure(
            text="Bỏ chọn tất cả", 
            command=deselect_all, 
            fg_color="#e74c3c", 
            hover_color="#c0392b"
        )
    else:
        btn_select_all.configure(
            text="Chọn tất cả", 
            command=select_all, 
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        )


def select_all():
    for var, _, _, btn in vars:
        var.set(True)
        btn.configure(fg_color="#2ecc71", hover_color="#27ae60")
    update_select_all_btn()


def deselect_all():
    for var, _, _, btn in vars:
        var.set(False)
        btn.configure(fg_color=("gray75", "gray30"), hover_color=("gray65", "gray40"))
    update_select_all_btn()


btn_select_all = ctk.CTkButton(
    btn_frame, 
    text="Chọn tất cả", 
    command=select_all,
    height=40,
    font=ctk.CTkFont(size=14, weight="bold")
)
btn_select_all.pack(side="left", padx=(5, 10))


def install_apps():
    btn_install.configure(state="disabled")
    checked = [(exe, name) for var, exe, name, btn in vars if var.get()]
    total = len(checked)
    if total == 0:
        messagebox.showwarning("Thông báo", "Vui lòng chọn ít nhất một ứng dụng để cài!")
        btn_install.configure(state="normal")
        return

    progress.set(0)
    clear_log()

    def run_install():
        time.sleep(0.1)
        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        success = 0

        for i, (exe, name) in enumerate(checked, start=1):
            log(f"[INSTALL] Đang cài: {name} ...")
            exe_path = os.path.join(base_path, "installers", exe)

            if not os.path.exists(exe_path):
                log(f"[ERROR] Không tìm thấy file: {exe}")
                continue

            try:
                exe_lower = exe.lower()
                name_lower = name.lower()

                if "unikey" in exe_lower:
                    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                    dest_path = os.path.join(desktop, exe)
                    if not os.path.exists(dest_path):
                        shutil.copy2(exe_path, desktop)
                        log("[SUCCESS] UniKey đã được sao chép ra Desktop.")
                        success += 1
                    else:
                        log("[INFO] UniKey đã tồn tại trên Desktop, bỏ qua.")

                elif "foxit" in exe_lower:
                    log("[INFO] Đang cài Foxit PDF Reader ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/quiet"], check=False)
                    if result.returncode == 0:
                        log(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                elif "office 2019" in name_lower:
                    setup_exe = exe_path
                    if os.path.exists(setup_exe):
                        log("[INFO] Đang cài đặt Office 2019...")
                        result = subprocess.run([setup_exe], check=False)
                        if result.returncode == 0:
                            log(f"[SUCCESS] Xử lý xong: {name}")
                            success += 1
                        else:
                            log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")
                    else:
                        log("[ERROR] Không tìm thấy Office2019ProPlus.exe.")

                elif "office 365" in name_lower:
                    setup_exe = exe_path
                    config_xml = os.path.join(base_path, "installers", "configuration-Office365-x64.xml")
                    if os.path.exists(setup_exe) and os.path.exists(config_xml):
                        log("[INFO] Đang cài đặt Office 365 tự động bằng ODT...")
                        result = subprocess.run([setup_exe, "/configure", config_xml], check=False)
                        if result.returncode == 0:
                            log(f"[SUCCESS] Xử lý xong: {name}")
                            success += 1
                        else:
                            log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")
                    else:
                        log("[ERROR] Không tìm thấy setup.exe hoặc configuration.xml của ODT.")

                elif "winrar" in exe_lower:
                    log("[INFO] Đang cài đặt WinRAR ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/S"], check=False)
                    if result.returncode == 0:
                        log(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                elif "zalo" in exe_lower:
                    log("[INFO] Đang cài đặt Zalo ở chế độ im lặng...")
                    result = subprocess.run([exe_path, "/quiet", "/S"], check=False)
                    if result.returncode == 0:
                        log(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

                else:
                    log(f"[INFO] Đang cài đặt {name} ở chế độ im lặng...")
                    try:
                        result = subprocess.run([exe_path, "/silent", "/verysilent"], check=False)
                    except:
                        result = subprocess.run([exe_path], check=False)

                    if result.returncode == 0:
                        log(f"[SUCCESS] Xử lý xong: {name}")
                        success += 1
                    else:
                        log(f"[ERROR] Cài đặt {name} thất bại (Mã lỗi: {result.returncode})")

            except Exception as e:
                log(f"[ERROR] Lỗi khi cài {name}: {e}")

            progress_value = i / total
            root.after(0, lambda val=progress_value: progress.set(val))

        winsound.MessageBeep()
        log(f"SUMMARY:{success}/{total}")
        log("Trình cài đặt đã đóng...")
        root.after(0, lambda: btn_install.configure(state="normal"))

    threading.Thread(target=run_install).start()


btn_install = ctk.CTkButton(
    btn_frame, 
    text="Cài đặt", 
    command=install_apps, 
    fg_color="#2ecc71", 
    hover_color="#27ae60",
    height=40,
    font=ctk.CTkFont(size=14, weight="bold")
)
btn_install.pack(side="left", padx=10)

# Thanh tiến trình
progress = ctk.CTkProgressBar(bottom_frame, orientation="horizontal")
progress.pack(fill="x", padx=10, pady=10)
progress.set(0)

# Khung log
log_frame = ctk.CTkFrame(bottom_frame)
log_frame.pack(fill="both", padx=5, pady=(5, 10), expand=True)

log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
log_header.pack(fill="x", padx=10, pady=(10, 5))

title_log = ctk.CTkLabel(log_header, text="Nhật ký hoạt động (Log)", font=ctk.CTkFont(size=14, weight="bold"))
title_log.pack(side="left", anchor="w")

btn_clear = ctk.CTkButton(
    log_header,
    text="Xóa Log",
    width=80,
    height=24,
    command=clear_log,
    fg_color="transparent",
    border_width=1,
    text_color=("gray10", "#DCE4EE"),
)
btn_clear.pack(side="right", anchor="e")

log_text = ctk.CTkTextbox(log_frame, state="disabled", font=ctk.CTkFont(family="Consolas", size=13))
log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

log_text._textbox.tag_config("success", background="#27ae60", foreground="white")
log_text._textbox.tag_config("error", background="#c0392b", foreground="white")
log_text._textbox.tag_config("end", foreground="#27ae60")
log_text._textbox.tag_config("green_text", foreground="#27ae60")
log_text._textbox.tag_config("red_text", foreground="#c0392b")


# ==============================================================================
# NỘI DUNG TAB: CHỈNH SỬA (edit_tab)
# ==============================================================================
edit_top_frame = ctk.CTkFrame(edit_tab, fg_color="transparent")
edit_top_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(10, 5))

edit_title_label = ctk.CTkLabel(edit_top_frame, text="Quản lý & Chỉnh sửa ứng dụng", font=ctk.CTkFont(size=16, weight="bold"))
edit_title_label.pack(anchor="w", padx=10, pady=(5, 5))

edit_scroll_frame = ctk.CTkScrollableFrame(edit_top_frame)
edit_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

edit_bottom_frame = ctk.CTkFrame(edit_tab, fg_color="transparent")
edit_bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(5, 10))

btn_edit_frame = ctk.CTkFrame(edit_bottom_frame, fg_color="transparent")
btn_edit_frame.pack(fill="x", padx=5, pady=5)

edit_vars = []


def load_edit_app_list():
    global edit_vars
    for widget in edit_scroll_frame.winfo_children():
        widget.destroy()
        
    edit_vars = []
    current_apps = load_config()

    for i, app in enumerate(current_apps):
        name = app.get("name", "Unknown")
        exe = app.get("exe", "")
        var = ctk.BooleanVar(value=False)

        row_frame = ctk.CTkFrame(edit_scroll_frame, height=60)
        row_frame.pack_propagate(False)
        row_frame.pack(fill="x", padx=15, pady=8)

        original_bg = row_frame.cget("fg_color")

        cb = ctk.CTkCheckBox(row_frame, text="", variable=var, width=24)
        cb.pack(side="left", padx=15)

        name_lbl = ctk.CTkLabel(
            row_frame, 
            text=name, 
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_lbl.pack(side="left", fill="x", expand=True, padx=10)

        # Toggle checkbox when clicking row or name label
        row_frame.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))
        name_lbl.bind("<Button-1>", lambda e, v=var: v.set(not v.get()))

        is_hovering = [False]

        def update_row_color(rf, v, nl, is_hover=False):
            if is_hover:
                rf.configure(cursor="hand2")
                nl.configure(cursor="hand2")
            else:
                rf.configure(cursor="")
                nl.configure(cursor="")

            if v.get():
                nl.configure(text_color="white")
                if is_hover:
                    rf.configure(fg_color=("#2980b9", "#1f618d"))
                else:
                    rf.configure(fg_color=("#3498db", "#2980b9"))
            else:
                nl.configure(text_color=("black", "white"))
                if is_hover:
                    rf.configure(fg_color=("gray85", "gray25"))
                else:
                    rf.configure(fg_color=original_bg)

        def handle_enter(e, r=row_frame, v=var, n=name_lbl):
            is_hovering[0] = True
            update_row_color(r, v, n, True)
            
        def handle_leave(e, r=row_frame, v=var, n=name_lbl):
            is_hovering[0] = False
            update_row_color(r, v, n, False)

        row_frame.bind("<Enter>", handle_enter)
        row_frame.bind("<Leave>", handle_leave)
        name_lbl.bind("<Enter>", handle_enter)
        name_lbl.bind("<Leave>", handle_leave)
        cb.bind("<Enter>", handle_enter)
        cb.bind("<Leave>", handle_leave)

        # Trace state changes
        var.trace_add("write", lambda *args, r=row_frame, v=var, n=name_lbl: update_row_color(r, v, n, is_hovering[0]))

        btn_edit_item = ctk.CTkButton(
            row_frame,
            text="Chỉnh sửa",
            width=100,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=lambda idx=i, n=name, e=exe: open_edit_overlay(idx, n, e)
        )
        btn_edit_item.pack(side="right", padx=10)

        edit_vars.append((var, app))


def open_edit_overlay(idx=None, old_name="", old_exe=""):
    overlay = ctk.CTkFrame(main_frame, fg_color=("gray20", "gray10"))
    overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    center_frame = ctk.CTkFrame(
        overlay, 
        fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"], 
        corner_radius=12, 
        border_width=2, 
        border_color="#3498db"
    )
    center_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.45)

    title_text = "Thêm mới ứng dụng" if idx is None else "Chỉnh sửa ứng dụng"
    lbl = ctk.CTkLabel(center_frame, text=title_text, font=ctk.CTkFont(size=16, weight="bold"))
    lbl.pack(pady=(15, 5))

    entry_rename = ctk.CTkEntry(center_frame, font=ctk.CTkFont(size=15), height=40, placeholder_text="Tên ứng dụng")
    if idx is not None:
        entry_rename.insert(0, old_name)
    entry_rename.pack(fill="x", padx=30, pady=10)
    entry_rename.focus()
    if idx is not None:
        entry_rename.select_range(0, "end")

    file_layout = ctk.CTkFrame(center_frame, fg_color="transparent")
    file_layout.pack(fill="x", padx=30, pady=10)

    exe_text = f"File: {old_exe}" if old_exe else "File: Chưa chọn file"
    exe_label = ctk.CTkLabel(
        file_layout, 
        text=exe_text, 
        font=ctk.CTkFont(size=13),
        anchor="w"
    )
    exe_label.pack(side="left", fill="x", expand=True, padx=(0, 10))

    selected_file_path = [None]

    def pick_file():
        f_path = filedialog.askopenfilename(
            title="Chọn file cài đặt",
            filetypes=[("Executable Files", "*.exe *.msi"), ("All Files", "*.*")]
        )
        if f_path:
            selected_file_path[0] = f_path
            exe_label.configure(text=f"File mới: {os.path.basename(f_path)}")

    btn_change_file = ctk.CTkButton(
        file_layout, 
        text="Thay đổi" if idx is not None else "Chọn file", 
        width=100, 
        height=35,
        command=pick_file,
        fg_color="#3498db",
        hover_color="#2980b9"
    )
    btn_change_file.pack(side="right")

    btn_action_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
    btn_action_frame.pack(fill="x", padx=30, pady=(20, 10))

    def on_confirm():
        new_name = entry_rename.get().strip()
        if not new_name:
            messagebox.showwarning("Cảnh báo", "Tên không được để trống!")
            return

        if idx is None and not selected_file_path[0]:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file cài đặt!")
            return

        base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        config_path = os.path.join(base_path, "config.json")
        installers_dir = os.path.join(base_path, "installers")
        os.makedirs(installers_dir, exist_ok=True)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if idx is not None:
                data["apps"][idx]["name"] = new_name

                if selected_file_path[0]:
                    file_path = selected_file_path[0]
                    filename = os.path.basename(file_path)
                    dest_path = os.path.join(installers_dir, filename)

                    old_file_name = data["apps"][idx].get("exe")
                    if old_file_name and old_file_name != filename:
                        old_file_full = os.path.join(installers_dir, old_file_name)
                        if os.path.exists(old_file_full):
                            try:
                                os.remove(old_file_full)
                            except:
                                pass

                    if not os.path.exists(dest_path):
                        shutil.copy2(file_path, dest_path)

                    data["apps"][idx]["exe"] = filename

                log(f"[INFO] Đã cập nhật ứng dụng: {new_name}")
            else:
                file_path = selected_file_path[0]
                filename = os.path.basename(file_path)
                dest_path = os.path.join(installers_dir, filename)

                if not os.path.exists(dest_path):
                    shutil.copy2(file_path, dest_path)

                new_app = {
                    "name": new_name,
                    "exe": filename,
                    "type": "Install"
                }
                data["apps"].append(new_app)
                log(f"[INFO] Đã thêm ứng dụng mới: {new_name}")

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            load_app_list()
            load_edit_app_list()
        except Exception as e:
            log(f"[ERROR] Không thể lưu thay đổi: {e}")

        overlay.destroy()

    def on_cancel():
        overlay.destroy()

    btn_confirm = ctk.CTkButton(
        btn_action_frame, 
        text="Xác nhận", 
        fg_color="#2ecc71", 
        hover_color="#27ae60",
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        command=on_confirm
    )
    btn_confirm.pack(side="left", padx=(0, 10), expand=True, fill="x")

    btn_cancel = ctk.CTkButton(
        btn_action_frame, 
        text="Quay lại", 
        fg_color="#e74c3c", 
        hover_color="#c0392b",
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        command=on_cancel
    )
    btn_cancel.pack(side="right", padx=(10, 0), expand=True, fill="x")





def delete_apps_from_edit():
    checked_to_del = [app.get("name") for var, app in edit_vars if var.get()]
    if not checked_to_del:
        messagebox.showwarning("Thông báo", "Vui lòng chọn ít nhất một ứng dụng để xóa!")
        return

    confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(checked_to_del)} ứng dụng khỏi danh sách?")
    if not confirm:
        return

    base_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    config_path = os.path.join(base_path, "config.json")
    installers_dir = os.path.join(base_path, "installers")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data.get("apps", []):
            if item.get("name") in checked_to_del:
                exe_name = item.get("exe")
                if exe_name:
                    file_to_del = os.path.join(installers_dir, exe_name)
                    if os.path.exists(file_to_del):
                        try:
                            os.remove(file_to_del)
                        except:
                            pass

        data["apps"] = [item for item in data.get("apps", []) if item.get("name") not in checked_to_del]

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        log(f"[INFO] Đã xóa thành công {len(checked_to_del)} ứng dụng.")
        load_edit_app_list()
        load_app_list()
    except Exception as e:
         messagebox.showerror("Lỗi", f"Không thể thực hiện xóa: {e}")


btn_add_app = ctk.CTkButton(
    btn_edit_frame,
    text="➕ Thêm mới",
    fg_color="#2ecc71",
    hover_color="#27ae60",
    height=40,
    font=ctk.CTkFont(size=14, weight="bold"),
    command=lambda: open_edit_overlay()
)
btn_add_app.pack(side="left", padx=(5, 10))

btn_del_app = ctk.CTkButton(
    btn_edit_frame,
    text="🗑️ Xóa",
    fg_color="#e74c3c",
    hover_color="#c0392b",
    height=40,
    font=ctk.CTkFont(size=14, weight="bold"),
    command=delete_apps_from_edit
)
btn_del_app.pack(side="left", padx=10)


# ==============================================================================
# NỘI DUNG TAB: GIỚI THIỆU (info_tab)
# ==============================================================================
info_card = ctk.CTkFrame(info_tab)
info_card.pack(fill="both", padx=40, pady=40, expand=True)

info_title = ctk.CTkLabel(info_card, text="VỀ ỨNG DỤNG", font=ctk.CTkFont(size=22, weight="bold"))
info_title.pack(pady=(30, 20))

about_text = """
Công cụ tự động cài đặt ứng dụng hàng loạt (Auto Install Tool).

• Phiên bản: 2.0 (CustomTkinter Edition)
• Tính năng: Cài đặt im lặng, không cần bấm Next.
• Cấu hình: Dễ dàng tùy chỉnh qua file config.json.
• Tác giả: Phạm Sự

Cảm ơn bạn đã sử dụng sản phẩm!
"""
info_desc = ctk.CTkLabel(info_card, text=about_text, font=ctk.CTkFont(size=15), justify="left")
info_desc.pack(padx=30, pady=10, anchor="w")


def show_tab(tab_name):
    if tab_name == "install":
        info_tab.pack_forget()
        edit_tab.pack_forget()
        install_tab.pack(fill="both", expand=True)
        btn_install_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        btn_edit_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        btn_info_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
    elif tab_name == "edit":
        install_tab.pack_forget()
        info_tab.pack_forget()
        edit_tab.pack(fill="both", expand=True)
        btn_edit_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        btn_install_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        btn_info_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        load_edit_app_list()
    elif tab_name == "info":
        install_tab.pack_forget()
        edit_tab.pack_forget()
        info_tab.pack(fill="both", expand=True)
        btn_info_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], text_color=("white", "white"))
        btn_install_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))
        btn_edit_tab.configure(fg_color="transparent", text_color=("gray10", "gray90"))


btn_install_tab = ctk.CTkButton(
    sidebar_frame, 
    text="📦 Cài đặt App", 
    command=lambda: show_tab("install"),
    height=45,
    font=ctk.CTkFont(size=15, weight="bold")
)
btn_install_tab.pack(padx=10, pady=8, fill="x")

btn_edit_tab = ctk.CTkButton(
    sidebar_frame, 
    text="✏️ Chỉnh sửa", 
    command=lambda: show_tab("edit"),
    height=45,
    font=ctk.CTkFont(size=15, weight="bold")
)
btn_edit_tab.pack(padx=10, pady=8, fill="x")

btn_info_tab = ctk.CTkButton(
    sidebar_frame, 
    text="ℹ️ Giới thiệu", 
    command=lambda: show_tab("info"),
    height=45,
    font=ctk.CTkFont(size=15, weight="bold")
)
btn_info_tab.pack(padx=10, pady=8, fill="x")

# Mặc định tab install

# Mặc định tab install
show_tab("install")
load_app_list()

log("[INFO] Đã tải danh sách ứng dụng từ config.json thành công.")

root.mainloop()
