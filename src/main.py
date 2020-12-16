
import cv2
import copy
import argparse
from os import path

import target
import basic_snake

image_target = target.Target()

algo_basic_snake = basic_snake.BasicSnake(image_target)

def info():
    print("Click to start adding the base points to the image")
    print("Once the initial point(s) have been added, press 'space'")
    print("to kick start the algorithm")

def execute(image):

    image_target.update_image(image)

    image_target.show()

    # The basic snake algo - Modify alpha, beta, and gamma to change properties of the snake
    algo_basic_snake.step()

    key = cv2.waitKey(1)

    if key == 27: 
        return False

    elif key == 32:
        image_target.mark_ready()

    return True

def camera(camera_number):
    info()
    cam = cv2.VideoCapture(camera_number)

    process = True
    while process:
        _, img = cam.read()
        process = execute(img)
    cv2.destroyAllWindows()

def image_file(file):
    info()
    base_image = cv2.imread(file, 1)

    process = True
    while process:
        input_image = copy.deepcopy(base_image)
        process = execute(input_image)
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--camera", help="Use camera",
                        action="store_true")

    parser.add_argument("-f", "--file", help="Use a static file",
                        action="store_true")

    parser.add_argument("-s", "--source", help="Source")

    args = parser.parse_args()

    if args.camera and args.file:
        print("Please select either 'camera' OR 'file' but not both")
        exit(1)

    if args.camera:
        camera_number = -1
        try:
            camera_number = int(args.source)
        except ValueError:
            print("Camera source must be of type 'int', you gave type \"", type(args.source), "\"")
            exit(1)

        camera(camera_number)
        exit(0)

    if args.file:

        if not path.exists(args.source):
            print("Given file path does not exist")
            exit(1)

        image_file(args.source)
        exit(0)

    print("No input given, please use -h to see options")

if __name__ == '__main__':
    main()