import pygetwindow as gw
import ctypes
import pyautogui
from pynput import keyboard
from pynput.keyboard import Listener
import win32api, win32con, win32gui
import time
import os
from dotenv import load_dotenv
load_dotenv()

sleep_default = 0.05
working = True
tecla_working=False
print('Activing')

altura = int(os.getenv('Height'))
largura = int(os.getenv('Width'))
repetir = int(os.getenv('Repeat'))

#keys
key_scroll = os.getenv('WScroll')
key_cleft = os.getenv('LClick')
key_cright = os.getenv('RClick')

BugBT = os.getenv('BugBT')
CancelBt = os.getenv('CancelBt')
RemoveBt = os.getenv('RemoveBt')
Pausescript = os.getenv('Pausescript')
Movemouse= os.getenv('Movemouse')
LegacyLClick = os.getenv('LegacyLClick')
MonitorIndex = int(os.getenv('MonitorIndex'))
MenorMonitorwidh = int(os.getenv('MenorMonitorwidh'))

MountGrid = os.getenv('MountGrid')
Linnhas = int(os.getenv('Linnhas'))
Collunas = int(os.getenv('Collunas'))
Exitscript = os.getenv('Exitscript')


cancelyes_x= int(os.getenv('cancelyes_x'))
cancelyes_y= int(os.getenv('cancelyes_y'))

delete_x = int(os.getenv('delete_x'))
delete_y = int(os.getenv('delete_y'))

titulo_janela = os.getenv('TitulodaJanela')

print(f"Repetir {repetir}")

def criar_grid_janelas(titulo_janela, monitor_index, grid_rows, grid_cols):
    # Obter a lista de janelas com o mesmo título
    janelas = []
    win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd) if win32gui.GetWindowText(hwnd) == titulo_janela and ctypes.windll.user32.IsWindowVisible(hwnd) != 0 else None, janelas)

    # Obter a informação do monitor desejado
    monitor_info = win32api.GetMonitorInfo(win32api.EnumDisplayMonitors()[monitor_index][0])
    monitor_rect = monitor_info['Monitor']
    trabalho_rect = monitor_info['Work']
    barra_tarefas_height = monitor_rect[3] - trabalho_rect[3]
    print(monitor_rect)
    #print(trabalho_rect)
    
    tela_widht = monitor_rect[0]#-5 #trabalho_rect[0]

    if MenorMonitorwidh > 0:
        tela_widht = MenorMonitorwidh

    # Calcular as dimensões de cada item do grid, descontando a altura da barra de tarefas
    item_width = tela_widht // grid_cols
    item_height = trabalho_rect[3] // grid_rows

    print(f"w{item_width} h{item_height}")

    # Posicionar as janelas no grid
    for i, hwnd in enumerate(janelas):
        row = i // grid_cols
        col = i % grid_cols

        left = tela_widht + col * item_width
        if len(janelas) > (grid_rows*grid_cols):
            row = i // (grid_cols*2)
            col = i % (grid_cols*2)
            left = col * item_width
            
            
        top = trabalho_rect[1] + row * item_height
        right = left + item_width
        bottom = top + item_height

        #print(f"left {left} top{top} w h")

        ctypes.windll.user32.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, right - left, bottom - top, win32con.SWP_SHOWWINDOW)
    
    ctypes.windll.user32.SetForegroundWindow(janelas[0])


def getwindowss():
    janelas = gw.getWindowsWithTitle(titulo_janela)
    #janelas = janelas[:10]
    return janelas

def change_var():
    global working
    if working:
        print('Disabled')
        working = False
    else:
        print('Activing')
        working = True

def win32left(x, y):
    #pyautogui.click(x,y)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def win32right(x, y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)

def win32scroll(x, y,direction=False):
    deslocamento = -900 if not direction else 900
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, deslocamento, 0)

def win32postClick(x,y,hwnd):
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x, y))
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(x, y))
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x, y))

def win32movemouse(x,y,hwnd):
    lparam = win32api.MAKELONG(x, y)
    ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_MOUSEMOVE, 0, lparam)

def win32postscroll(x,y,direction=False):
    HWHEEL = 0x01000
    WHEEL = 0x0800
    deslocamento = -120 if not direction else 120
    ctypes.windll.user32.SetCursorPos(x, y)
    ctypes.windll.user32.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, deslocamento, 0)
    #ctypes.windll.user32.mouse_event(WHEEL, None, None, deslocamento, None)

def getmousepos(janelas):
    x, y = win32api.GetCursorPos()
    rect = win32gui.GetClientRect(janelas[0]._hWnd)
    pt = ctypes.wintypes.POINT(x, y)
    ctypes.windll.user32.ScreenToClient(janelas[0]._hWnd, ctypes.byref(pt))
    x_rel = pt.x - rect[0]
    y_rel = pt.y - rect[1]

    return x_rel,y_rel

def getwindossize(janelas):
    rect = win32gui.GetClientRect(janelas[0]._hWnd)
    return rect[2],rect[3]

def leftCLickInative():
    global tecla_working
    mouse_position = pyautogui.position()
    janelas = getwindowss()
    janela_x, janela_y = janelas[0].left, janelas[0].top
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)

    posicao_rel_x,posicao_rel_y = getmousepos(janelas)
    
    print(f"Posição do mouse em relação à janela: ({posicao_rel_x}, {posicao_rel_y})")
    for janela in janelas:
        hwnd = janela._hWnd
        win32postClick(posicao_rel_x,posicao_rel_y,hwnd)
        time.sleep(0.01)

    #win32postClick(277,90,janelas[0]._hWnd)
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    win32api.SetCursorPos((mouse_position.x,mouse_position.y))
    tecla_working=False

def mopveMouse():
    global tecla_working
    janelas = getwindowss()
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)

    x_rel,y_rel = getmousepos(janelas)

    posicao_rel_x = x_rel
    posicao_rel_y =y_rel

    print(f"Posição do mouse em relação à janela: ({posicao_rel_x}, {posicao_rel_y})")

    for janela in janelas:
        hwnd = janela._hWnd
        ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(posicao_rel_x, posicao_rel_y))
        time.sleep(0.01)
    
    ctypes.windll.user32.SendMessageW(janelas[0]._hWnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(posicao_rel_x, posicao_rel_y))
    tecla_working=False

def exec_cleft():
    global tecla_working
    mouse_position = pyautogui.position()

    # Obtém as coordenadas X e Y
    x = mouse_position.x
    y = mouse_position.y
    print(f"Coordenadas do mouse: X={x}, Y={y}")
    
    for i in range(repetir):
        new_coord_x = x + (i * largura)
        print(new_coord_x, y)
        win32left(new_coord_x, y)
        # pyautogui.click(x = new_coord_x, y = y)

    for i in range(repetir):
        new_coord_x = x + (i * largura)
        print(new_coord_x, y + altura)
        win32left(new_coord_x, y + altura)
        # pyautogui.click(x = new_coord_x, y = y)

    time.sleep(sleep_default)
    win32api.SetCursorPos((x,y))
    tecla_working=False
    
def exec_cright():
    global tecla_working
    mouse_position = pyautogui.position()

    # Obtém as coordenadas X e Y
    x = mouse_position.x
    y = mouse_position.y
    print(f"Coordenadas do mouse: X={x}, Y={y}")

    for i in range(repetir):
        new_coord_x = x + (i * largura)
        print(new_coord_x, y)
        win32right(new_coord_x, y)

    for i in range(repetir):
        new_coord_x = x + (i * largura)
        print(new_coord_x, y + altura)
        win32right(new_coord_x, y + altura)

    time.sleep(sleep_default)
    win32api.SetCursorPos((x,y))
    tecla_working=False

def new_scrol():
     global tecla_working
     mouse_position = pyautogui.position()
     janelas = getwindowss()
     ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
     
     x_rel,y_rel = getmousepos(janelas)
     
     for janela in janelas:
        hwnd = janela._hWnd
        rect = win32gui.GetWindowRect(hwnd)
        left = rect[0] + x_rel+int(16/2)
        top = rect[1] + y_rel #+int(8/2)
        #win32postscroll(left,top)
        win32scroll(left,top)
        time.sleep(0.01)

     time.sleep(0.08)
     ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
     win32api.SetCursorPos((mouse_position.x,mouse_position.y))
     tecla_working=False

def exec_scroll():
    global tecla_working
    mouse_position = pyautogui.position()
    x = mouse_position.x
    y = mouse_position.y

    sleep_time = 0.1

    for i in range(repetir):
        new_coord_x = x + (i * largura)
        print('Uscroll:', new_coord_x, y)
        win32scroll(new_coord_x, y)
        time.sleep(sleep_time)

    for i in range(repetir):
        new_coord_x = x + (i * altura)
        print('Dscroll at:', new_coord_x, y + altura)
        win32scroll(new_coord_x, y + altura)
        time.sleep(sleep_time)

    time.sleep(sleep_default)
    win32api.SetCursorPos((x,y))
    tecla_working=False

def cancelButton():
    global tecla_working
    mouse_position = pyautogui.position()
    janelas = getwindowss()
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    click_x,click_y=getwindossize(janelas)
    click_x=int(click_x/2)
    click_y=click_y-24
    
    for janela in janelas:
        hwnd = janela._hWnd
        win32postClick(click_x,click_y,hwnd)
        time.sleep(0.01)

    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    win32api.SetCursorPos((mouse_position.x,mouse_position.y))
    tecla_working=False

def makeaBUg():
    global tecla_working
    mouse_position = pyautogui.position()
    janelas = getwindowss()
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)

    posicao_rel_x,posicao_rel_y = getmousepos(janelas)

    cancel_rel_x=int(janelas[0].width/2)
    cancel_rel_y=janelas[0].height-24

    print(f"click_x{posicao_rel_x} click_y{posicao_rel_y}")
    print(f"cancel_x{cancel_rel_x} cancel_y{cancel_rel_y}")

    for janela in janelas:
        hwnd = janela._hWnd
        win32postClick(posicao_rel_x,posicao_rel_y,hwnd)
        time.sleep(0.08)
        win32postClick(cancel_rel_x,cancel_rel_y,hwnd)

    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    win32api.SetCursorPos((mouse_position.x,mouse_position.y))
    tecla_working=False
 

def deleteAction():
    global tecla_working
    mouse_position = pyautogui.position()
    originalX = 203
    originalY = 368

    originalWidth = 513
    originalHeight = 524

    janelas =getwindowss()
    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    janela_x, janela_y, janela_w, janela_h = janelas[0].left, janelas[0].top, janelas[0].width,  janelas[0].height
    print(f"janela w{janela_w} janela h{janela_h}")
    delete_click_x=int(janela_w/2)+13
    delete_click_y=janela_h-28

    print(f"delete x{delete_click_x} delete y{delete_click_y}")

    adjustedX = int((janela_w / originalWidth * originalX))
    adjustedY = int((janela_h / originalHeight * originalY))

    if cancelyes_x > 0:
         adjustedX=cancelyes_x
    
    if cancelyes_y > 0:
         adjustedX=cancelyes_y

    if delete_x > 0:
       delete_click_x = delete_x

    if delete_y > 0:
         delete_click_y=delete_y

    print(f"yes x{adjustedX} yes y{adjustedY}")

    for janela in janelas:
        hwnd = janela._hWnd
        win32postClick(delete_click_x,delete_click_y,hwnd)
        time.sleep(0.08)
        win32postClick(adjustedX,adjustedY,hwnd)

    ctypes.windll.user32.SetForegroundWindow(janelas[0]._hWnd)
    win32api.SetCursorPos((mouse_position.x,mouse_position.y))
    tecla_working=False


def on_release(key):
    global tecla_working
    print('{0} released'.format(
        key))
    
    if not hasattr(key, "char"):
         return
    
    if key.char == Pausescript:
        print('Change Varz')
        change_var()
    
    if key.char == Exitscript:
        print('Exit')
        return False

    if not working:
        return
    
    if tecla_working:
         print("Ocupado")
         return
    
    if key.char == key_cleft:
            print('Left')
            tecla_working=True
            leftCLickInative()
            #exec_cleft()

    if key.char == LegacyLClick:
            print('Left')
            tecla_working=True
            exec_cleft()

    if key.char == Movemouse:
            print('Move Mouse')
            tecla_working=True
            mopveMouse()
    
    
    if key.char == key_cright:
            print('Right')
            tecla_working=True
            exec_cright()

    if key.char == key_scroll:
            print('Scroll')
            tecla_working=True
            #exec_scroll()
            new_scrol()

    if key.char == CancelBt:
            print('CC')
            tecla_working=True
            cancelButton()

    if key.char == RemoveBt:
            print('XX')
            tecla_working=True
            deleteAction() 

    if key.char == BugBT:
            print('BB')
            tecla_working=True
            makeaBUg() 

    if key.char == MountGrid:
         criar_grid_janelas(titulo_janela,MonitorIndex,Linnhas,Collunas)
         
list = keyboard.Listener(on_release=on_release);
list.start()
list.join()

"""# Exemplo de uso: grid
titulo_janela = "Exemplo de Título"  # Título das janelas desejadas
monitor_index = 1  # Índice do segundo monitor (começando em 0)
grid_rows = 5  # Número de linhas do grid
grid_cols = 2  # Número de colunas do grid

criar_grid_janelas(titulo_janela, monitor_index, grid_rows, grid_cols)


---
barra_tarefas_height = monitor_rect[3] - trabalho_rect[3]  # Altura da barra de tarefas

    # Calcular as dimensões de cada item do grid, descontando a altura da barra de tarefas
    item_width = trabalho_rect[2] // grid_cols
    item_height = (trabalho_rect[3] - barra_tarefas_height) // grid_rows
"""