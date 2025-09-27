import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep
import numpy as np
import cvzone
from pynput.keyboard import Key, Controller

# Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8)

# Keyboard layout (added BACKSPACE in the last row)
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
        ["SPACE", "BACKSPACE"]]

finalText = ""
keyboard = Controller()

# Button class
class Button():
    def __init__(self, pos, text, size=None):
        if size is None:
            if text == "SPACE":
                size = [300, 85]  # Wider space bar
            elif text == "BACKSPACE":
                size = [230, 85]  # Backspace button
            else:
                size = [85, 85]
        self.pos = pos
        self.size = size
        self.text = text

# Draw buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size

        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 150, 0), 3)

        if button.text in ["SPACE", "BACKSPACE"]:
            cv2.putText(img, button.text, (x + 30, y + 55),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        else:
            cv2.putText(img, button.text, (x + 20, y + 55),
                        cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

# Create buttons
buttonList = []
for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        if key == "SPACE":
            buttonList.append(Button([200, 100 * i + 50], key))
        elif key == "BACKSPACE":
            buttonList.append(Button([550, 100 * i + 50], key))
        else:
            buttonList.append(Button([100 * j + 50, 100 * i + 50], key))

print("Virtual Keyboard Started!")

# Variables for click detection
last_click_time = 0
click_threshold = 30

try:
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera")
            break

        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img)
        img = drawAll(img, buttonList)

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]

            index_tip = lmList[8][:2]
            middle_tip = lmList[12][:2]

            for button in buttonList:
                x, y = button.pos
                w, h = button.size

                if x < index_tip[0] < x + w and y < index_tip[1] < y + h:
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5),
                                  (0, 255, 0), cv2.FILLED)

                    if button.text in ["SPACE", "BACKSPACE"]:
                        cv2.putText(img, button.text, (x + 30, y + 55),
                                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                    else:
                        cv2.putText(img, button.text, (x + 20, y + 55),
                                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                    distance = ((index_tip[0] - middle_tip[0]) ** 2 +
                                (index_tip[1] - middle_tip[1]) ** 2) ** 0.5
                    current_time = cv2.getTickCount() / cv2.getTickFrequency()

                    if distance < click_threshold and (current_time - last_click_time) > 0.5:
                        if button.text == "SPACE":
                            finalText += " "
                            keyboard.press(Key.space)
                            keyboard.release(Key.space)
                        elif button.text == "BACKSPACE":
                            finalText = finalText[:-1]
                            keyboard.press(Key.backspace)
                            keyboard.release(Key.backspace)
                        else:
                            finalText += button.text.lower()
                            keyboard.press(button.text.lower())
                            keyboard.release(button.text.lower())

                        last_click_time = current_time
                        print(f"Clicked: {button.text}")

        cv2.rectangle(img, (50, 450), (1200, 550), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (50, 450), (1200, 550), (255, 255, 255), 3)

        display_text = finalText[-50:] if len(finalText) > 50 else finalText
        cv2.putText(img, f"Typed: {display_text}", (60, 500),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        cv2.imshow("Virtual Keyboard", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            finalText = ""
            print("Text cleared!")

except KeyboardInterrupt:
    print("\nProgram interrupted by user")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Virtual Keyboard closed!")
