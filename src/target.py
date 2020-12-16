import cv2

def get_sobel(image):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    x = cv2.Sobel(gray, cv2.CV_16S, 1,0, ksize=3, scale=1)
    y = cv2.Sobel(gray, cv2.CV_16S, 0,1, ksize=3, scale=1)
    absx= cv2.convertScaleAbs(x)
    absy = cv2.convertScaleAbs(y)
    return cv2.addWeighted(absx, 0.5, absy, 0.5,0)

class Target:
    def __init__(self):
        self.points = []
        self.image  = None 
        self.sobel_image = None
        self.ready  = False

    def update_image(self, img):
        self.image = img
        self.sobel_image = get_sobel(img)

    def mark_ready(self):
        if self.ready:
            return

        print("Marked Ready")
        self.ready = True

    def get_image(self):
        return self.image

    def get_points(self):
        return self.points 

    def mouse_click(self, event, x, y, flags, param):

        if self.ready:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append([x,y])

    def show(self, show_points=True, show_lines=True):

        if self.image is None :
            print("No image")
            return 

        if show_points:

            # Draw points
            for p in self.points:
                self.image = cv2.circle(self.image, (p[0], p[1]), 1, (0,0,255), 10)

        if show_lines and len(self.points) > 1:

            # Draw lines
            for x in range(0, len(self.points)-1):
                self.image = cv2.line(self.image, (self.points[x][0], self.points[x][1]), (self.points[x+1][0], self.points[x+1][1]), (0,255,0), 5) 

            # Show last line
            self.image = cv2.line(self.image, (self.points[0][0], self.points[0][1]), (self.points[len(self.points)-1][0],self.points[len(self.points)-1][1]), (0,255,0), 5) 

        cv2.imshow('Target', self.image)

        cv2.setMouseCallback('Target', self.mouse_click) 

