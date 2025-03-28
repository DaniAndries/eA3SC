import ctypes
from ctypes import wintypes
import sys
import time
import webbrowser
import os
import config

# Asegurarse de que los tipos necesarios están definidos
if not hasattr(wintypes, "LRESULT"):
    wintypes.LRESULT = ctypes.c_longlong
if not hasattr(wintypes, "HCURSOR"):
    wintypes.HCURSOR = ctypes.c_void_p

# Constantes de Windows
WM_USER, WM_DESTROY, WM_COMMAND = 0x0400, 0x0002, 0x0111
WM_TRAYICON, WM_RBUTTONUP, WM_LBUTTONDBLCLK = WM_USER + 20, 0x0205, 0x0203
NIM_ADD, NIM_DELETE = 0x00000000, 0x00000002
NIF_MESSAGE, NIF_ICON, NIF_TIP, NIF_INFO = 0x00000001, 0x00000002, 0x00000004, 0x00000010
ID_TRAY_APP_ICON, ID_OPTION_1, ID_OPTION_2, ID_OPTION_3 = 5000, 5001, 5002, 5003

# Acceso a las DLLs de Windows
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
shell32 = ctypes.windll.shell32

# Definición de la estructura NOTIFYICONDATA
class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uID", wintypes.UINT),
        ("uFlags", wintypes.UINT),
        ("uCallbackMessage", wintypes.UINT),
        ("hIcon", wintypes.HICON),
        ("szTip", wintypes.WCHAR * 128),
        ("dwState", wintypes.DWORD),
        ("dwStateMask", wintypes.DWORD),
        ("szInfo", wintypes.WCHAR * 256),
        ("uVersion", wintypes.UINT),
        ("szInfoTitle", wintypes.WCHAR * 64),
        ("dwInfoFlags", wintypes.DWORD),
        ("guidItem", ctypes.c_char * 16),
        ("hBalloonIcon", wintypes.HICON),
    ]

# Definición de la estructura WNDCLASS
class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

# Funciones asociadas al menú
def option_1():
    webbrowser.open(config.CONFIG_PARSER['POPUP_MENU']['INFORMATION_URL'])

def option_2():
    webbrowser.open(config.CONFIG_PARSER['POPUP_MENU']['CONFIGURATION_URL'])

def option_3(hWnd):
    user32.PostMessageW(hWnd, WM_DESTROY, 0, 0)

# Obtener la posición del cursor
def get_cursor_pos():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def show_context_menu(hWnd):
    x, y = get_cursor_pos()
    hMenu = user32.CreatePopupMenu()
    user32.AppendMenuW(hMenu, 0x0, ID_OPTION_1, config.CONFIG_PARSER['POPUP_MENU']['OPTION_1'])
    user32.AppendMenuW(hMenu, 0x0, ID_OPTION_2, config.CONFIG_PARSER['POPUP_MENU']['OPTION_2'])
    user32.AppendMenuW(hMenu, 0x0, ID_OPTION_3, config.CONFIG_PARSER['POPUP_MENU']['OPTION_3'])
    user32.SetForegroundWindow(hWnd)
    cmd = user32.TrackPopupMenu(hMenu, 0x0100, x, y, 0, hWnd, None)
    if cmd == ID_OPTION_1:
        option_1()
    elif cmd == ID_OPTION_2:
        option_2()
    elif cmd == ID_OPTION_3:
        option_3(hWnd)
    user32.DestroyMenu(hMenu)

# Definición de la función de ventana (Window Procedure)
def wnd_proc(hWnd, msg, wParam, lParam):
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    elif msg == WM_TRAYICON:
        if lParam == WM_RBUTTONUP:
            show_context_menu(hWnd)
        elif lParam == WM_LBUTTONDBLCLK:
            option_1()
        return 0
    elif msg == WM_COMMAND:
        id_command = wParam & 0xFFFF
        if id_command == ID_OPTION_1:
            option_1()
        elif id_command == ID_OPTION_2:
            option_2()
        elif id_command == ID_OPTION_3:
            option_3(hWnd)
        return 0
    return user32.DefWindowProcW(hWnd, msg, wParam, wintypes.LPARAM(lParam))

WndProc = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)(wnd_proc)

# Función para cargar un icono desde un archivo
def load_icon_from_file(icon_path):
    if not os.path.exists(icon_path):
        print(f"Error: No se encontró el archivo de icono en: {icon_path}")
        return None
    return user32.LoadImageW(None, icon_path, 1, 0, 0, 0x00000010 | 0x00000040)

# Registrar y crear la ventana
class_name = "eA3SC_App"
window_proc = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)(wnd_proc)
instance = kernel32.GetModuleHandleW(None)
wc = WNDCLASS()
wc.lpfnWndProc = window_proc
wc.hInstance = instance
wc.lpszClassName = class_name

if not user32.RegisterClassW(ctypes.byref(wc)):
    print("Error al registrar la clase de ventana")
    sys.exit(1)

hWnd = user32.CreateWindowExW(0, class_name, "eA3SC", 0, 0, 0, 0, 0, None, None, instance, None)

png_path = os.path.realpath(config.CONFIG_PARSER['POPUP_MENU']['ICO_PATH'])
hIcon = load_icon_from_file(png_path) or user32.LoadIconW(None, wintypes.LPCWSTR(32512))

def notification(title, text):
    nid = NOTIFYICONDATA()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
    nid.hWnd = hWnd
    nid.uID = ID_TRAY_APP_ICON
    nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP | NIF_INFO
    nid.uCallbackMessage = WM_TRAYICON
    nid.hIcon = hIcon
    nid.szTip = config.CONFIG_PARSER['POPUP_MENU']['APP_NAME']
    nid.szInfoTitle = title
    nid.szInfo = text
    nid.dwInfoFlags = 0x00000001
    
    # Mostrar la notificación
    shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

    # Esperar antes de eliminar la notificación
    time.sleep(5)

    # Eliminar la notificación después de mostrarse
    shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

# Función principal
def popup():
    hInstance = kernel32.GetModuleHandleW(None)
    wndclass = WNDCLASS()
    wndclass.style = 0
    wndclass.lpfnWndProc = WndProc
    wndclass.cbClsExtra = 0
    wndclass.cbWndExtra = 0
    wndclass.hInstance = hInstance
    wndclass.hIcon = user32.LoadIconW(None, wintypes.LPCWSTR(32512))
    wndclass.hCursor = user32.LoadCursorW(None, wintypes.LPCWSTR(32512))
    wndclass.hbrBackground = 5
    wndclass.lpszMenuName = None
    wndclass.lpszClassName = "TrayIconDemo"

    if not user32.RegisterClassW(ctypes.byref(wndclass)):
        print("Error al registrar la clase de ventana")
        sys.exit(1)

    hWnd = user32.CreateWindowExW(0, wndclass.lpszClassName, "Tray Icon Demo", 0, 0, 0, 0, 0, None, None, hInstance, None)
    if not hWnd:
        print("Error al crear la ventana")
        sys.exit(1)

    nid = NOTIFYICONDATA()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATA)
    nid.hWnd = hWnd
    nid.uID = ID_TRAY_APP_ICON
    nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP | NIF_INFO
    nid.uCallbackMessage = WM_TRAYICON
    nid.hIcon = hIcon
    nid.szTip = config.CONFIG_PARSER['POPUP_MENU']['APP_NAME']
    nid.szInfoTitle = config.CONFIG_PARSER['SERVICE_NOTIFICATION']['POPUP_TITLE']
    nid.szInfo = config.CONFIG_PARSER['SERVICE_NOTIFICATION']['POPUP_TEXT']
    nid.dwInfoFlags = 0x00000001

    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
        print("Error al agregar el icono a la bandeja")
        sys.exit(1)

    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))

    shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
    user32.DestroyWindow(hWnd)