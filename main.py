import os
import random
import sys
import threading
import time
import keyboard
import easyocr as ocr
import win32gui
import wincontroller
from overlay import Overlay

#You can configure the question area and answer area location depend on your game resolution
# X1, Y1, X2, Y2 (Top Left Corner -> Right Bottom Corner)
QUESTION_BOX = (216, 649, 1316, 744)
ANSWER_A_BOX = (146, 814, 523, 904)
ANSWER_B_BOX = (1078, 814, 1449, 904)
ANSWER_C_BOX = (146, 953, 523, 1046)
ANSWER_D_BOX = (1078, 953, 1449, 1046)
ANSWERS_BOOK_FILENAME = 'Answers.csv'
CLICK_ONLY_IF_COMPLETELY_CORRECT = True
DEBUG_MODE = True

ANSWER_BOXES = (ANSWER_A_BOX, ANSWER_B_BOX, ANSWER_C_BOX, ANSWER_D_BOX)

SpammerIndex = 0

GAME_WINDOW_NAME = '哈利波特：魔法覺醒'
QUESTION_DIALOG_PROCESS = 'MagicOfHistoryDialog.exe'
NO_ANSWER_IS_FOUND = '找不到答案'
PUNCTUATION = ' ・!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､　、〃〈〉《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏﹑﹔·！？｡。'


ScanMode = False
ScanResult = None

QandA = {}
reader = None

_tempStatus = ScanMode

COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)

def Coord2BBox(x1y1x2y2):
    return (x1y1x2y2[0], x1y1x2y2[1], x1y1x2y2[2]-x1y1x2y2[0], x1y1x2y2[3]-x1y1x2y2[1])

def SpamAnswer():
    global SpammerIndex
    global ScanMode

    while ScanMode:
        wincontroller.clickLeftButton(ANSWER_BOXES[SpammerIndex][2], ANSWER_BOXES[SpammerIndex][3])
        time.sleep(0.04)

def CallDialog():
    global ScanMode
    # get question and answer
    question = ''.join(GetTextListInArea(QUESTION_BOX))
    answers = ';'.join([''.join(GetTextListInArea(pos)) for pos in ANSWER_BOXES])
    # call .exe
    os.system(f'{QUESTION_DIALOG_PROCESS} \"{question}\" \"{answers}\"')
    ScanMode = _tempStatus



def isAllSubstringsFindInKey(dict, sortedStringList):
    matched_key = ''
    for key in dict.keys():
        if sortedStringList[0] in key:
            matched_key = key

    if matched_key == '':
        return False

    #check all string matched key
    for str in sortedStringList:
        if not str in matched_key:
            if DEBUG_MODE:
                print(f'sentence \'{sortedStringList}\' is unmatched with key {matched_key} at location {str}')
            return False
    return True

def ConvertCsv2Dict(csv_filename):
    dict = {}
    with open(csv_filename, mode='r', encoding='UTF-8') as fr:
        for line in fr:
            pair = line.split(';')
            pure_key, pure_value = RemoveAllPuncation(pair[0]), RemoveAllPuncation(pair[1]).replace('\n', '')
            if len(pure_key) < 0:
                continue
            if pure_key in dict.keys():
                pure_key += str(random.random())
            dict[pure_key] = pure_value
    return dict


def RemoveAllPuncation(str):
    return str.translate(str.maketrans('', '', PUNCTUATION))


def GetCorrectAnswer(question):
    """
    return None if answer is not found\n
    return [true, list] if more than 1 answer\n
    return [false, string] if only 1 answer\n
    :return: bool, Any
    """
    if len(question) == 0:
        return None
    answers = []
    for key in QandA.keys():
        if question in key:
            answers.append(QandA[key])

    if len(answers) == 0:
        return None
    elif len(answers) == 1:
        return [False, answers[0]]
    else:
        return [True, answers]

def GetTextListInArea(x1y1x2y2):
    img = wincontroller.screenCapture(x1y1x2y2)
    textList = reader.readtext(img)
    return [textBlock[1].translate(str.maketrans('', '', PUNCTUATION)) for textBlock in textList]

def ScanQuestion():
    global ScanMode
    global ScanResult
    global QandA
    global SpammerIndex
    while ScanMode:
        completelyCorrect = False
        answerFound = False
        questionsNoPuncList = GetTextListInArea(QUESTION_BOX)
        correctAnswerList = GetCorrectAnswer(''.join(questionsNoPuncList))
        if (correctAnswerList is None):
            if len(questionsNoPuncList) > 0:
                sortedQuestionStringList = sorted(questionsNoPuncList, key=len, reverse=True)
                if CLICK_ONLY_IF_COMPLETELY_CORRECT:
                    completelyCorrect = isAllSubstringsFindInKey(QandA, sortedQuestionStringList)
                for questionBlock in sortedQuestionStringList:
                    correctAnswerList = GetCorrectAnswer(questionBlock)
                    if correctAnswerList is not None:
                        break
                if correctAnswerList is None:
                    correctAnswerList = NO_ANSWER_IS_FOUND
        else:
            completelyCorrect = True

        if DEBUG_MODE:
            print(f'question list {questionsNoPuncList}')
            print(f'answer list : {correctAnswerList}')
            print(f'completely pass? : {completelyCorrect}')

        if correctAnswerList is not None and correctAnswerList != NO_ANSWER_IS_FOUND:
            #Check four answer box
            for index in range(0, len(ANSWER_BOXES)):
                selectOption = ''.join(GetTextListInArea(ANSWER_BOXES[index]))
                if DEBUG_MODE:
                    print(f'ScanResult : {correctAnswerList[1]}')
                    print(f'selectOption : {selectOption}')

                answer = ''
                #if it is string
                if not correctAnswerList[0]:
                    if correctAnswerList[1].find(selectOption) > -1:
                        SpammerIndex = index
                        answerFound = True
                        ScanResult = selectOption
                else:
                    for ans in correctAnswerList[1]:
                        if ans.find(selectOption) > -1:
                            SpammerIndex = index
                            answerFound = True
                            answer = selectOption
                            break
                if answerFound:
                    if correctAnswerList[0]:
                        ScanResult = correctAnswerList[1]
                        ScanResult.insert(0, answer)
                    break
        #Click if spam mode is off
        if CLICK_ONLY_IF_COMPLETELY_CORRECT and completelyCorrect and answerFound:
            wincontroller.clickLeftButton(ANSWER_BOXES[SpammerIndex][2], ANSWER_BOXES[SpammerIndex][3])

def main():
    global QandA
    global ScanMode
    global reader
    global ScanResult
    global _tempStatus

    print('Welcome to use Auto Answering Tool for Harry Potter : Magic Awakened.\n')
    print('Press F2 to auto answer question and spamming a random answer.')
    print('Press F3 to add new question and answer to database.')
    print('Press F4 to close the script.')


    # Initialize OCR
    print('Initialzing OCR System ......... ', end='')
    reader = ocr.Reader(['ch_tra'], gpu=True)
    print('Finished')

    #Initialize Answers Databases
    print(f'Loading data from CSV file {ANSWERS_BOOK_FILENAME} ......... ', end='')
    # excel = pd.ExcelFile('Answers.xlsx')
    # tempQandA = excel.parse(excel.sheet_names[0]).set_index('Question')['Answer'].to_dict()

    # I decided to use csv now. May change to database later
    QandA = ConvertCsv2Dict(ANSWERS_BOOK_FILENAME)
    print('Finished')


    #Check whether Harry Potter is launched
    print('Checking whether the game is already open ......... ', end='')
    hWnd = 0
    while hWnd == 0:
        hWnd = win32gui.FindWindow(None, GAME_WINDOW_NAME)
        time.sleep(0.1)
    print('Finished')

    # Initialize overlay
    print('Creating Overlay ......... ', end='')
    overlay = Overlay(GAME_WINDOW_NAME)
    print('Finished')
    print('Auto Solver is completely loaded. Please do not close this window.')

    # Test Area

    was_pressed = False
    while overlay.isOverlayRunning:

        overlay.UpdateOverlayPart1()

        overlay.DrawText(f'Scan Question  (F2)', 30, (15, 20), COLOR_GREEN if ScanMode else COLOR_RED)
        overlay.DrawText(f'Add New Question (F3)', 30, (15, 60), COLOR_RED)
        overlay.DrawText(f'Close the program  (F4)', 30, (15, 100), COLOR_RED)

        if ScanResult != None:
            overlay.DrawText(f'Answer is {ScanResult}', 30, (15, 140), COLOR_RED)

        if ScanMode:
            overlay.DrawText(f'Scanning...', 30, (400, 20), COLOR_GREEN)
            #draw scan box
            overlay.DrawRectangle(Coord2BBox(QUESTION_BOX), 3, COLOR_RED)
            for index in range(0, len(ANSWER_BOXES)):
                if (index == SpammerIndex):
                    overlay.DrawRectangle(Coord2BBox(ANSWER_BOXES[index]), 3, (0, 255, 0))
                    continue
                overlay.DrawRectangle(Coord2BBox(ANSWER_BOXES[index]), 3, COLOR_RED)


        overlay.UpdateOverlayPart2()

        if keyboard.is_pressed('f2'):
            if not was_pressed:
                was_pressed = True
                ScanMode = not ScanMode
                ScanResult = NO_ANSWER_IS_FOUND
                #Start Scann Thread
                if ScanMode:
                    scanThread = threading.Thread(target=ScanQuestion)
                    scanThread.start()
                    if not CLICK_ONLY_IF_COMPLETELY_CORRECT:
                        spamThread = threading.Thread(target=SpamAnswer)
                        spamThread.start()
        elif keyboard.is_pressed('f3'):
            if not was_pressed:
                was_pressed = True
                _tempStatus = ScanMode
                ScanMode = False
                windowThread = threading.Thread(target=CallDialog)
                windowThread.start()
        elif keyboard.is_pressed('f4'):
            ScanMode = False
            sys.exit()
        else:
            was_pressed = False

if __name__ == '__main__':
    main()