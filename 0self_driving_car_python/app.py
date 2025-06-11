import numpy as np
import math
import pygame

screen=pygame.display.set_mode((1200,800))
clock=pygame.time.Clock()

class Car:
    def __init__(self):
        self.x=60   #change start positions if needed
        self.y=650
        self.width=20
        self.height=40
        self.alive=True
        self.fitness=0
        self.sensor_angles=[-85,-65,-45,-25,0,25,45,65,85]
        self.sensor_length=40
        self.speed=0
        self.angle=0
        self.brain=np.random.uniform(-1,1,(len(self.sensor_angles),3))
    
    def update(self,track):
        if self.alive is False:
            return
        sensors=self.get_sensor_data(track)
        output=np.dot(sensors,self.brain)
        action=np.argmax(output)

        if action==0:
            self.angle-=5
        elif action==1:
            self.angle+=5
        self.speed=3

        self.x+=math.cos(math.radians(self.angle))*self.speed
        self.y+=math.sin(math.radians(self.angle))*self.speed

        if self.check_collision(track):
            self.alive=False
        else:
            self.fitness+=1
    
    def get_sensor_data(self,track):
        data=[]
        for angle in self.sensor_angles:
            sensor_x=int(self.x+self.sensor_length*math.cos(math.radians(self.angle+angle)))
            sensor_y=int(self.y+self.sensor_length*math.sin(math.radians(self.angle+angle)))

            if 0<=sensor_x<track.get_width() and 0<=sensor_y<track.get_height():
                data.append(1 if track.get_at((sensor_x,sensor_y))[:3]==(0,0,0) else 0)
            else:
                data.append(0)
        return data
    
    def check_collision(self,track):
        if 0<=int(self.x)<track.get_width() and 0<=int(self.y)<track.get_height():
            return track.get_at((int(self.x),int(self.y)))[:3]==(0,0,0)
        return True

    def mutation(self):
        mutation=np.random.uniform(-100,100,self.brain.shape)
        self.brain+=mutation
    
    def draw(self,screen):
        #if self.alive==False:
        #    return
        
        car_rect=pygame.Rect(self.x-self.width//2,
                             self.y-self.height//2,
                             self.width,
                             self.height)
        
        pygame.draw.rect(screen,"blue",car_rect)

        for angle in self.sensor_angles:
            sensor_x=int(self.x+self.sensor_length*math.cos(math.radians(self.angle+angle)))
            sensor_y=int(self.y+self.sensor_length*math.sin(math.radians(self.angle+angle)))

            pygame.draw.line(screen,"red",(int(self.x),int(self.y)),(sensor_x,sensor_y),3)
    
class Population:
    def __init__(self):
        self.cars=[Car() for _ in range(100)]
        self.generation=0

    def update(self,track):
        for car in self.cars:
            car.update(track)

    def evolve(self):
        self.cars.sort(key=lambda c:c.fitness, reverse=True)
        print(f"generation : {self.generation} best_fitness : {self.cars[0].fitness}")
        elite=self.cars[:99]
        new_cars=[]

        for _ in range(100):
            new_car=Car()
            parent=np.random.choice(elite)
            new_car.brain=np.copy(parent.brain)
            new_car.mutation()
            new_cars.append(new_car)
        
        self.cars=new_cars
        self.generation+=1

track=pygame.image.load("track.png")
track=pygame.transform.scale(track,(1200,800))

population=Population()

running=True
while running is True:
    screen.blit(track,(0,0))

    population.update(track)

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    
    if all(car.alive==False for car in population.cars):
        population.evolve()

    for car in population.cars:
        if car.alive is True:
            car.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()