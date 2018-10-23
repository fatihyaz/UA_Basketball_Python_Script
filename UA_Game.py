import os
import pygame
from math import tan, radians, degrees, copysign
from pygame.math import Vector2
import serial  
import codecs
import binascii
import string
import time
import numpy as np
from scipy import linalg
import statistics
# serial port settings
ser = serial.Serial()
ser.baudrate = 115200
#print("*********************")
ser.port = "COM5"
#print("*********************")

# trackers info
Trackers = np.array([
    [0,0]
])
# anchors info (Sıralama degismemeli!!!)
Anchors = np.array([
    [335,455],      # B1
    [784,388],      # B2
    [337,85],       # B3
    [661,166]       # BF

])
anch1 = 0 
anch2 = 1
anch3 = 2
anch4 = 3

# distances info
Distances = np.array([0, 0, 0])
# standart deviation
xcoord_list = []
ycoord_list = []

ser.open()


class Basket:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x, y)
        self.last_position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 20
        self.brake_deceleration = 10
        self.free_deceleration = 2
        
        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if not (self.last_position.x == self.position.x):
            self.position.x = self.last_position.x + 0.01

        if not (self.last_position.y == self.position.y):
            self.position.y = self.last_position.y + 0.01


        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.angle += degrees(angular_velocity) * dt


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Basket tutorial")
        width = 900
        height = 580
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
 
        self.ticks = 120
        self.exit = False

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "basketball_1.png")
        image_path1 = os.path.join(current_dir, "oyunalani.png")
        
        basket_image = pygame.image.load(image_path)
        map_image = pygame.image.load(image_path1)
        basket = Basket(0, 0)
        ppu = 32

        dt = self.clock.get_time() / 1000


        
        while not self.exit:
            
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            #UA
            
            packet_sending = ""
            data = ser.readline()
            
            packet_sending += str(data,'utf-8')
            
            #print(packet_sending)
            if 'radio_rx' in packet_sending:
                ua = []
                ua = packet_sending.split('C1')
                ua_message =("C1"+ua[1])
                #print("Time : ",time.strftime('%T'))        
                #print("\nPacket : ",ua_message)
                device_adress       = ua_message[6:12]
                tracker_ua_adress   = ua_message[18:24]
                
                anchor1_adress ="------"
                anchor1_cm     ="------"
                anchor2_adress ="------"
                anchor2_cm     ="------"
                anchor3_adress ="------"
                anchor3_cm     ="------"
                anchor4_adress ="------"
                anchor4_cm     ="------"
                #print("packet len : ",len(ua_message))
                if len(ua_message) > 32:
                    anchor1_adress      = ua_message[24:30]
                    if (all(c in string.hexdigits for c in ua_message[30:34] )):
                        anchor1_cm        = int(ua_message[30:34],16)
                if len(ua_message) > 42:
                    anchor2_adress      = ua_message[34:40]
                    if (all(c in string.hexdigits for c in ua_message[40:44] )):
                        anchor2_cm        = int(ua_message[40:44],16)
                if len(ua_message) > 52:
                    anchor3_adress      = ua_message[44:50]
                    if (all(c in string.hexdigits for c in ua_message[50:54] )):
                        anchor3_cm        = int(ua_message[50:54],16)
                if len(ua_message) > 62:
                    anchor4_adress      = ua_message[54:60]
                    if (all(c in string.hexdigits for c in ua_message[60:64] )):
                        anchor4_cm        = int(ua_message[60:64],16)

            # [A][xy] = [b]
            # ...............................................
                if len(ua_message) > 62:
                    # parameters
                    d1 = anchor1_cm
                    d2 = anchor2_cm
                    d3 = anchor3_cm
                    d4 = anchor4_cm
                    '''
                    d1 = 300
                    d2 = 300
                    d3 = 400
                    d4 = 100
                    '''
                    #if(d1 == 0 or d2 == 0 or d3 == 0 or d4 == 0): 
                        #continue
                    dt = self.clock.get_time() / 1000
                    x1 = Anchors[(anch1)][0]
                    y1 = Anchors[(anch1)][1]

                    x2 = Anchors[(anch2)][0]
                    y2 = Anchors[(anch2)][1]

                    x3 = Anchors[(anch3)][0]
                    y3 = Anchors[(anch3)][1]

                    x4 = Anchors[(anch4)][0]
                    y4 = Anchors[(anch4)][1]

                    # ...............................................
                    # calculate
                    Q1 = d1**2 - x1**2 - y1**2 - d4**2 + x4**2 + y4**2
                    Q2 = d2**2 - x2**2 - y2**2 - d4**2 + x4**2 + y4**2
                    Q3 = d3**2 - x3**2 - y3**2 - d4**2 + x4**2 + y4**2
                    
                    b = [Q1, Q2, Q3]
                    
                    a = np.array([[(x1-x4),(y1-y4)],
                                 [(x2-x4),(y2-y4)],
                                 [(x3-x4),(y3-y4)]]
                                 )
                    
                    A = np.dot(-2,a)
                    #print("---------------------------")
                    A_trans =   A.transpose()
                    #print("A Transpose Value :   \n",A_trans)
                    
                    result1= np.dot(A_trans,A)
                    #print("A Transpose * A  : \n",result1)

                    invmatrix = linalg.inv(result1)
                    #print("Inv Matrix: \n",invmatrix)

                    result2 = np.dot(invmatrix,A_trans)
                    #print("Inv Matrix * A Tranpose : \n",result2)

                    result3= np.dot(result2,b)
                    #print("Final Result : \n",result3)
                    

                    #print("****************************")
                    Trackers = result3
                    #print("Tracker Position: \n",Trackers)
                    x_coordinates = float(Trackers[0])/32
                    y_coordinates = float(Trackers[1])/32

                    
                    #print(str(x_coordinates) + "," + str(y_coordinates))
                    basket.acceleration = 5
                    basket.velocity.x = 20
                    
                    #*********filters for smooth*********#
                    xcoord_list.append(x_coordinates)
                    ycoord_list.append(y_coordinates)

                    xcoord_last5 = xcoord_list[-5:]
                    ycoord_last5 = ycoord_list[-5:]


                    last_x  = xcoord_last5[len(xcoord_last5)-1]
                    last2_x = xcoord_last5[len(xcoord_last5)-2]
                    
                    last_y  = ycoord_last5[len(ycoord_last5)-1]
                    last2_y = ycoord_last5[len(ycoord_last5)-2]

                    dif_x = last_x-last2_x
                    dif_y = last_y-last2_y
                
                    
                    pstdev_x = statistics.pstdev(xcoord_last5)
                    pstdev_y = statistics.pstdev(ycoord_last5)


                    ave_x = sum(xcoord_last5)/len(xcoord_last5)
                    ave_y = sum(ycoord_last5)/len(ycoord_last5)
                    #print("dif X : ",dif_x)
                    #print("dif Y : ",dif_y)
                    print(dt)
                    #print("X : ",str(pstdev_x) + "  Y : ",str(pstdev_y))
                    #if pstdev_x <0.6 and pstdev_y <0.75:
                        #continue
                    if dif_x <0.25 and dif_y <0.35:
                        continue
                    #basket.position = Vector2(x_coordinates,y_coordinates)
                    basket.last_position = Vector2(ave_x, ave_y)
                    
                    # Logic
                    basket.update(dt)

            # Drawing
            self.screen.fill((0, 0, 0))
            map_image = pygame.transform.scale(map_image, (900, 580))
            rotated = pygame.transform.rotate(basket_image, basket.angle)
            rotated1 = pygame.transform.rotate(map_image,0)
            
            rect  = rotated.get_rect()
            rect1 = rotated1.get_rect()
            
            self.screen.blit(rotated1, (0, 0))
            
            self.screen.blit(rotated,  basket.position * ppu - (rect.width / 2, rect.height / 2))
            
            pygame.display.flip()


            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
