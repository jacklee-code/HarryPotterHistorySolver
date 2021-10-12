import pygame
import win32api
import win32con
import win32gui

class Overlay:
    def __init__(self, attachWindowName):
        # Initialize overlay
        self.attachedWindowName = attachWindowName
        self.isOverlayRunning = True
        pygame.init()
        pygame.font.init()
        self.__font = 'chinese_font.ttf'
        self.OverlayScreen = pygame.display.set_mode((self.__getGameWindow(self.attachedWindowName)[2],
                                                      self.__getGameWindow(self.attachedWindowName)[3]),
                                                     pygame.NOFRAME)
        self.__fuchsia = (255, 0, 128)  # Transparency color

        # Set window transparency color
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.__fuchsia), 0, win32con.LWA_COLORKEY)

    def UpdateOverlayPart1(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.isOverlayRunning = False

        # Track Game
        self.__trackGameWindow(self.attachedWindowName)  # Make sure overlay follows the game
        self.OverlayScreen.fill(self.__fuchsia)

    def DrawText(self, text, textSize, positionXY, rgb, bold = True):
        # PYGAME TEXT UPDATES:
        overlayFont = pygame.font.Font(self.__font, textSize)
        overlayFont.bold = bold
        gameText = overlayFont.render(text, False, rgb)
        self.OverlayScreen.blit(gameText, positionXY)

    def DrawRectangle(self, bbox, thickness, rgb):
        pygame.draw.rect(self.OverlayScreen, rgb, pygame.Rect(bbox[0], bbox[1], bbox[2], bbox[3]), thickness)

    def UpdateOverlayPart2(self):
        pygame.display.update()

    def __getGameWindow(self, windowname):
        hwnd = win32gui.FindWindow(None, windowname)
        windowrect = win32gui.GetWindowRect(hwnd)
        x = windowrect[0] - 5  # -5 so it lines up perfectly
        y = windowrect[1]
        width = windowrect[2] - x
        height = windowrect[3] - y
        return x, y, width, height

    def __trackGameWindow(self, windowname):
        win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], -1,
                              self.__getGameWindow(windowname)[0],
                              self.__getGameWindow(windowname)[1], 0, 0, 0x0001)



