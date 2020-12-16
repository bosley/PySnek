# A basic snake using : E = ∫(αEcont + βEcurv + γEimage)ds

from target import Target

import copy
import math

class BasicSnake:

    def __init__(self, target_data):
        self.target  = target_data
        self.avgDist = 0
        self.alpha = 0.2
        self.beta  = 1
        self.gamma = 100

    def step(self):

        if not self.target.ready:
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

            print(new_position)

            self.target.points[idx] = copy.deepcopy(new_position)

            idx = idx + 1

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
        localMin = 1000.00

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

        print("Rows: ", rows, " . Cols: ", cols)

        for y in range(0, rows):
            for x in range(0, cols):

                print("MOOT")

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

                print("Energy   :", energy)
                print("localMin :", localMin)

                if flag:
                    flag = False
                    localMin = energy
                    location = (parentX, parentY)
                elif energy < localMin:
                    localMin = energy
                    location = (parentX, parentY)

        return location