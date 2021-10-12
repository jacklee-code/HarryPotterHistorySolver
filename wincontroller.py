import mss
import win32gui, win32ui, win32api, win32con
import numpy

def drawRectOnScreen(startpos, endpos, rgb = (255, 0, 0)):
    hwnd = win32gui.GetDesktopWindow();
    hPen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(rgb[0], rgb[1], rgb[2]))
    win32gui.InvalidateRect(hwnd, None, True)
    win32gui.UpdateWindow(hwnd)
    win32gui.RedrawWindow(hwnd, None, None,
                          win32con.RDW_FRAME | win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW | win32con.RDW_ALLCHILDREN)

    hwndDC = win32gui.GetDC(hwnd)

    win32gui.SelectObject(hwndDC, hPen)
    hbrush = win32gui.GetStockObject(win32con.NULL_BRUSH)
    prebrush = win32gui.SelectObject(hwndDC, hbrush)
    win32gui.Rectangle(hwndDC, startpos[0], startpos[1], endpos[0], endpos[1])
    win32gui.SaveDC(hwndDC);
    win32gui.SelectObject(hwndDC, prebrush)
    win32gui.ReleaseDC(hwnd, hwndDC)

def backgroundScreenshot(windowname):
    hWnd = win32gui.FindWindow(None, windowname)
    left, top, right, bot = win32gui.GetWindowRect(hWnd)
    width = right - left
    height = bot - top
    hWndDC = win32gui.GetWindowDC(hWnd)
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    img = numpy.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)
    return img

def screenCapture(x1y1x2y2):
    with mss.mss() as sct:
        # Part of the screen to capture
        monitor = {"top": x1y1x2y2[1], "left": x1y1x2y2[0],
                   "width": x1y1x2y2[2]-x1y1x2y2[0], "height": x1y1x2y2[3]-x1y1x2y2[1]}
        img = numpy.array(sct.grab(monitor))
        return img

def clickLeftButton(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
