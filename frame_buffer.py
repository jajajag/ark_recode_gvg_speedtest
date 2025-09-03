# -*- coding:  utf-8 -*-
import sys
import win32gui, win32con, win32api
import time


class FrameBuffer(object): 
    def __init__(self,
            class_name='Qt5156QWindowIcon',
            title_name='MuMu模拟器12',
            # Using left bottom corner as default
            pause_coord=(0.05, 0.95),
            unpause_coord=(0.05, 0.9),
            is_pcr=True):
        # Init coordinates
        self.pause_coord = pause_coord
        self.unpause_coord = unpause_coord
        self.is_pcr = is_pcr
        # Default delay
        self.delay = 20
        # Find handle of current window and children windows
        self.hwnd = []
        self.hwnd.append(win32gui.FindWindow(class_name, title_name))
        #self.hwnd.append(win32gui.GetWindow(hwnd, win32con.GW_CHILD))
        def children(hwnd, lparam):
            self.hwnd.append(hwnd)
        win32gui.EnumChildWindows(self.hwnd[0], children, None)
        # Set the program to forground
        #win32gui.SetForegroundWindow(hwnd)

    def click(self):
        # Use the first child window
        hwnd = self.hwnd[1]
        # Calculat the size of the window
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bottom - top
        # Click to unpause
        x1, y1 = int(self.unpause_coord[0] * width + left), \
                int(self.unpause_coord[1] * height + top)
        # Click to pause
        x2, y2 = int(self.pause_coord[0] * width + left), \
                int(self.pause_coord[1] * height + top)
        l_param_1 = win32api.MAKELONG(x1, y1)
        l_param_2 = win32api.MAKELONG(x2, y2)
        # Activate the bluestacks
        win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE,
                             win32con.WA_CLICKACTIVE, 0)
        # Move mouse to (0, 0) globally
        win32api.mouse_event(
                win32con.MOUSEEVENTF_ABSOLUTE | win32con.MOUSEEVENTF_MOVE, 0, 0)
        # 1. Freeze to pause
        if self.is_pcr:
            win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param_1)
            win32api.Sleep(500)
            win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param_1)
        # 2. Pause to unpause
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param_1)
        win32api.Sleep(100)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param_1)
        # Add 20ms to skip 1-2 frames
        win32api.Sleep(self.delay)
        # 3. Unpause to pause
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, l_param_2)
        if self.is_pcr:
            win32api.Sleep(200)
        else:
            win32api.Sleep(10)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, l_param_2)

    def run(self, is_pcr=True): 
        delay = input('延迟(默认20ms)：')
        self.delay = int(delay) if delay.isdigit() else self.delay
        # Run the main function
        while True: 
            input()
            self.click()


if __name__ == '__main__': 
    if len(sys.argv) > 1:
        # Ark Re:Code
        fb = FrameBuffer(pause_coord=(0.04, 0.13), unpause_coord=(0.04, 0.13), is_pcr=False)
    else:
        # PCR
        fb = FrameBuffer(pause_coord=(0.05, 0.95), unpause_coord=(0.05, 0.9), is_pcr=True)
    fb.run()
