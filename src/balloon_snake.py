from target import Target

import cv2
import copy
import math

def nothing(x):
    pass

class BalloonSnake:

    def __init__(self, target_data):
        self.target  = target_data
        self.first_dispersion = 5
        self.avgDist = 0
        self.alpha = 0.2
        self.beta  = 1
        self.gamma = 100

    def setup(self):
        cv2.namedWindow('Target')
        cv2.createTrackbar('Alpha','Target',2  ,100,nothing)
        cv2.createTrackbar('Beta' ,'Target',1  ,100,nothing)
        cv2.createTrackbar('Gamma','Target',100,100,nothing)

    def step(self):

        # Mark the thing ready if a single selection has been made as this is more a balloon snake
        if not self.target.ready and len(self.target.get_points()) > 0:
            self.target.mark_ready()
    
        if not self.target.ready:
            return 

        a = cv2.getTrackbarPos('Alpha','Target')
        b = cv2.getTrackbarPos('Beta', 'Target')
        g = cv2.getTrackbarPos('Gamma','Target')

        if a != 0:
            self.alpha = a / 100
        if b != 0:
            self.beta  = b
        if g != 0:
            self.gamma = g

        if len(self.target.get_points()) == 1:
            self.first_group()
            return

        height, width = self.target.sobel_image.shape

        idx = 0
        for point in self.target.get_points():
            
            # Calculate scope of the neighborhood
            start = [0,0]
            end   = [0,0]

            if point[0] - 3 > 0:
                start[0] = point[0] - 3

            if point[0] + 4 > width:
                end[0] = width
            else:
                end[0] = point[0] + 4
            
            if point[1] - 3 > 0:
                start[1] = point[1] - 3

            if point[1] + 4 > height:
                end[1] = height
            else:
                end[1] = point[1] + 4

            new_position = self.calculate_new_pos(idx, start, end)

            self.target.points[idx] = copy.deepcopy(new_position)

            idx = idx + 1

    # Get the first point and create the initial group to scan from
    def first_group(self):

        points = self.target.get_points()

        height, width = self.target.sobel_image.shape

        left_x  = points[0][0]
        right_x = points[0][0]
        upper_y = points[0][1]
        lower_y = points[0][1]
 
        if left_x >= self.first_dispersion:
            left_x = left_x - self.first_dispersion
        if right_x < (width - self.first_dispersion):
            right_x = right_x + self.first_dispersion
        if upper_y >= self.first_dispersion:
            upper_y = upper_y - self.first_dispersion
        if lower_y < (height  - self.first_dispersion):
            lower_y = lower_y + self.first_dispersion

        self.target.points = []
        self.target.points.append([left_x,  points[0][1]])
        self.target.points.append([left_x,  upper_y])
        self.target.points.append([points[0][0],  upper_y])
        self.target.points.append([right_x, upper_y])
        self.target.points.append([right_x, points[0][1]])
        self.target.points.append([right_x, lower_y])
        self.target.points.append([points[0][0],  lower_y])
        self.target.points.append([left_x,  lower_y])

    def updateAveragePointDistance(self):

        points = self.target.get_points()
        sum = 0.0
        for i in range(0, len(points)-1):
            sum = sum + math.sqrt(
                ((points[i][0] - points[i+1][0]) * (points[i][0] - points[i+1][0]) + 
                 (points[i][1] - points[i+1][1]) * (points[i][1] - points[i+1][1])))

        sum = sum + math.sqrt(
            ((points[len(points)-1][0] - points[0][0]) * (points[len(points)-1][0] - points[0][0]) + 
                (points[len(points)-1][1] - points[0][1]) * (points[len(points)-1][1] - points[0][1])))

        self.avgDist = sum / len(points)


    def calculate_new_pos(self, idx, start, end):

        cols = end[0] - start[0]
        rows = end[1] - start[1]

        points   = self.target.get_points()
        location = points[idx]

        flag = True 
        localMax = 0.00

        self.updateAveragePointDistance()

        ngmax = None 
        ngmin = None 

        for y in range(0, rows):
            for x in range(0, cols):
                cval = self.target.sobel_image[y + start[1], x + start[0]]
                if flag:
                    ngmax = cval
                    ngmin = cval 
                elif cval > ngmax:
                    ngmax = cval
                elif cval < ngmin:
                    ngmin = cval

        if ngmax == None or ngmax == 0:
            ngmax = 1
        if ngmin == None or ngmin == 0:
            ngmin = 1

        flag = True

        for y in range(0, rows):
            for x in range(0, cols):

                # E = ∫(α(s)Econt + β(s)Ecurv + γ(s)Eimage)ds

                parentX = x + start[0]
                parentY = y + start[1]

                # Econt
                # (δ- (x[i] - x[i-1]) + (y[i] - y[i-1]))^2
                # δ = avg dist between snake points

                prevPoint = [0,0]

                if idx == 0:
                    prevPoint = points[len(points)-1]
                else:
                    prevPoint = points[idx-1]

                # Econt 
                econt = (parentX - prevPoint[0]) + (parentY - prevPoint[1])
                econt = econt ** 2
                econt = self.avgDist - econt

                # Multiply by alpha value
                econt = econt * self.alpha

                # Ecurv
                # (x[i-1] - 2x[i] + x[i+1])^2 + (y[i-1] - 2y[i] + y[i+1])^2

                nextPoint = [0,0]
                if idx == len(points)-1:
                    nextPoint = points[0]
                else:
                    nextPoint = points[idx+1]

                ecurv = (prevPoint[0] - (parentX*2) + nextPoint[0]) ** 2
                ecurv = ecurv + (prevPoint[1] - (parentY*2) + nextPoint[1]) ** 2
                ecurv *= self.beta

                # Eimage
                # -||∇||
                eimg = self.target.sobel_image[parentY, parentX]
                eimg = eimg * self.gamma

                # Normalize

                econt = econt / ngmax
                ecurv = ecurv / ngmax 

                divisor = ngmax - ngmin 
                if divisor <= 0:
                    divisor = 1

                eimg = (eimg-ngmin) / divisor

                energy = econt + ecurv + eimg 

                if flag:
                    flag = False
                    localMax = energy
                    location = (parentX, parentY)
                elif energy > localMax:
                    localMax = energy
                    location = (parentX, parentY)

        return location
