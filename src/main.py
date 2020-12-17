
import cv2
import copy
import argparse
from os import path

import target
import basic_snake
import balloon_snake

image_target = target.Target()


algorithms = {
    'basic_snake': basic_snake.BasicSnake(image_target),
    'balloon_snake': balloon_snake.BalloonSnake(image_target)
}


algorithm_selection = 'basic_snake'

def info():
    print("Click to start adding the base points to the image")
    print("Once the initial point(s) have been added, press 'space'")
    print("to kick start the algorithm")
    print("To reset the algorithm press 'r'")

def execute(image):

    image_target.update_image(image)

    image_target.show()

    algorithms[algorithm_selection].step()

    key = cv2.waitKey(1)

    if key == 27: 
        return False

    if key == 114 and image_target.ready:
        image_target.reset()

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
    global algorithm_selection

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--camera", help="Use camera",
                        action="store_true")

    parser.add_argument("-f", "--file", help="Use a static file",
                        action="store_true")

    parser.add_argument("-s", "--source", help="Source")

    parser.add_argument("-a", "--algorithm", help="Select an algorithm (basic_snake, balloon_snake)")

    args = parser.parse_args()


    if args.algorithm == "basic_snake":
        print("Basic snake selected")
    elif args.algorithm == "balloon_snake":
        algorithm_selection = "balloon_snake"
        print("Balloon snake selected")
    else:
        print("Unknown algorithm selection given - Using 'basic_snake'")
        algorithm_selection = "basic_snake"

    if args.camera and args.file:
        print("Please select either 'camera' OR 'file' but not both")
        exit(1)

    algorithms[algorithm_selection].setup()

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