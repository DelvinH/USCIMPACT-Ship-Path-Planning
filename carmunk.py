import random
import math
import numpy as np

import pygame as pg
from pygame.color import THECOLORS

from line_intersection import intersectLines

import pymunk
from pymunk.vec2d import Vec2d
from pymunk.pygame_util import DrawOptions as draw

np.random.seed(1)
random.seed(1)

clock = pg.time.Clock()
vec = pg.math.Vector2

step_to_sec = 2
ROT = 0.25    # unit: degree/second
v0 = 7.7167   # unit: m/s
ratio = 8.73  # unit: m/pixel


class GameState:
    def __init__(self, env_size, path_g, path_op, start_dir):
        # PyGame init
        pg.init()
        self.screen = pg.display.set_mode(env_size) # env_size = (width, height)
        self.screen.set_alpha(None)

        # Path Planning OP and Goal
        self.path_x_g, self.path_y_g = path_g[0], path_g[1]  # Goal of path
        self.path_x_0, self.path_y_0, = path_op[0], path_op[1]  # OP of path
        self.path_r_0 = math.radians(start_dir)  # Start direction of path

        # **FUNCTION TO DEFINE TS PATH**
        self.target_center_pos = 500, 250
        self.target_goal_pos = 50, 250
        self.target_rot_deg = 180

        # Status
        self.crashed = False
        self.future_collision = False
        self.course_reached = True

        # Physics
        self.space = pymunk.Space()
        self.space.gravity = pymunk.Vec2d(0., 0.)

        # Create own ship.
        self.create_own_ship(self.path_x_0, self.path_y_0, self.path_r_0)
        own_ship_vertices = self.get_vertices_list(self.path_x_0, self.path_y_0, self.path_r_0)
        pg.draw.polygon(self.screen, THECOLORS['green'], own_ship_vertices)

        # Record steps.
        self.num_steps = 0

        target_ship_vertices = self.get_vertices_list(x_ts_0, y_ts_0, rot_ts)
        pg.draw.polygon(self.screen, THECOLORS['red'], target_ship_vertices)


    def create_dynamic_obs(self, ts_op, path):
        # Create body and position
        self.obs_body = pymunk.Body(pymunk.inf, pymunk.inf)
        self.obs_body.position = (ts_op[0], ts_op[1])

        # Vertices


        # Path


        # Old code
        self.obs_shape = pymunk.Circle(self.obs_body, 5)
        self.obs_shape = pymunk.Circle(self.obs_body, 5, (5,5))
        self.obs_shape.color = THECOLORS["red"]
        self.obs_shape.elasticity = 1.0
        self.obs_body.angle = 2.09 + 2*random.random()
        direction = Vec2d(1, 0).rotated(self.obs_body.angle)
        self.obs_body.apply_impulse(direction)
        self.space.add(self.obs_body, self.obs_shape)

    def get_random(self):
        r = 200 + 150 * random.random()
        theta = math.pi*random.random()
        return r, theta

    def create_goal(self):
        #inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.goal_body = pymunk.Body(pymunk.inf, pymunk.inf)
        self.goal_body.position = width*(0.1+0.8*random.random()), height*0.85
        xg, yg = (200, -200) # or (200,200)?
        size = 30
        self.points = [(xg-size, yg-size), (xg-size, yg+size), (xg+size,yg+size), (xg+size, yg-size)]
        #self.goal_shape = pymunk.Poly(self.goal_body, self.points)
        self.goal_shape = pymunk.Circle(self.goal_body, 5)
        self.goal_shape.color = THECOLORS["orange"]
        self.goal_shape.elasticity = 1.0
        self.goal_shape.angle = 0.5
        direction = Vec2d(1, 0).rotated(self.goal_body.angle)
        self.space.add(self.goal_body, self.goal_shape)

    def create_own_ship(self, x, y, r):
        inertia = pymunk.moment_for_circle(1, 0, 14, (0, 0))
        self.car_body = pymunk.Body(1, inertia)
        self.car_body.position = x, y
        self.car_shape = pymunk.Circle(self.car_body, 5)
        self.car_shape.color = THECOLORS["green"]
        self.car_shape.elasticity = 1.0
        self.car_body.angle = r
        driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        self.car_body.apply_impulse_at_local_point(driving_direction)#self.car_body.apply_impulse(driving_direction) --- apply_impulse is depreciated; could be world_point instead of local
        self.space.add(self.car_body, self.car_shape)

    def frame_step(self, course_goal):
        if course_goal == 'base':
            theta = math.radians(self.own_rot_deg)
            x_0, y_0 = self.own_center_pos
            yg_local = -(self.x_g - x_0) * math.sin(theta) + (self.y_g - y_0) * math.cos(theta)
            xg_local = (self.x_g - x_0) * math.cos(theta) + (self.y_g - y_0) * math.sin(theta)
            angle_to_goal_deg = math.degrees(math.atan2(yg_local, xg_local))
            course_adjusted = self.own_rot_deg + angle_to_goal_deg
            # print('ajusted course for base: ', course_adjusted)
        else:
            course_adjusted = course_goal - 90
        x_os, y_os = self.own_center_pos
        if abs(self.own_rot_deg - course_adjusted) >= 0.51:
            self.course_reached = False
            if self.own_rot_deg > course_adjusted:
                self.own_rot_deg -= ROT * step_to_sec
            else:
                self.own_rot_deg += ROT * step_to_sec
        else:

            self.course_reached = True
        # print('------')
        # print('own rot = ', self.own_rot_deg, 'course goal = ', course_adjusted)
        # print('reached? ', self.course_reached)
        # print('------')
        x_os_new = x_os + v0 * step_to_sec * math.cos(math.radians(self.own_rot_deg)) / ratio
        y_os_new = y_os + v0 * step_to_sec * math.sin(math.radians(self.own_rot_deg)) / ratio
        self.own_center_pos = (x_os_new, y_os_new)
        # self.move_cat()
        # x0, y0 = self.car_body.position

        # driving_direction = Vec2d(1, 0).rotated(self.car_body.angle)
        # self.car_body.velocity = 100 * driving_direction

        # Update the screen and stuff.
        self.screen.fill(THECOLORS["black"])

        x_0, y_0 = self.own_center_pos
        rot = math.radians(self.own_rot_deg)

        # print('own ship pos: ', self.own_center_pos, 'rot: ', self.own_rot_deg)


        direction = vec(self.target_goal_pos) - vec(self.target_center_pos)
        target_rot_radians = math.atan2(direction.y, direction.x)

        self.target_center_pos += vec(v0 * step_to_sec / ratio, 0).rotate(math.degrees(target_rot_radians))


        # calculate if future collision possible
        pt1 = self.own_center_pos
        pt2 = pt1 + vec(500, 0).rotate(self.own_rot_deg)

        pt3 = self.target_center_pos
        pt4 = self.target_goal_pos
        result = intersectLines(pt1, pt2, pt3, pt4)
        if result[3] < 0 or result[4] < 0:
            self.future_collision = False
        else:
            self.future_collision = True
        # print(self.future_collision)

        # draw ships
        x_ts, y_ts = self.target_center_pos

        own_ship_vertices = self.get_vertices_list(x_0, y_0, rot)
        target_ship_vertices = self.get_vertices_list(x_ts, y_ts, target_rot_radians)

        pg.draw.polygon(self.screen, THECOLORS['red'], target_ship_vertices)
        pg.draw.polygon(self.screen, THECOLORS['green'], own_ship_vertices)
        #print(own_ship_vertices)
        pg.draw.line(self.screen, THECOLORS['orange'], (x_0,y_0),(self.x_g,self.y_g))
        pg.draw.line(self.screen, THECOLORS['orange'], (x_0, y_0), (self.x_g, self.y_g))

        ## get local coordinates of target ship in the own-ship coordinate system
        theta = math.radians(self.own_rot_deg)
        y_local = -(x_ts - x_0) * math.sin(theta) + (y_ts - y_0) * math.cos(theta)
        x_local = (x_ts - x_0) * math.cos(theta) + (y_ts - y_0) * math.sin(theta)
        local_angle_deg = math.degrees(math.atan2(y_local, x_local))

        pg.draw.line(self.screen, THECOLORS['blue'], (x_0, y_0), (50 * math.cos(math.radians(course_adjusted)) + x_0, 50 *  math.sin(math.radians(course_adjusted)) + y_0))
        # local_angle_deg is within (-180, 180]
        valid_actions = []
        if local_angle_deg >= -70 and local_angle_deg <= 70:
            temp_idx = int((local_angle_deg + 70) / 5)
            # print('local angle is ', local_angle_deg, '----index =', temp_inx)
            if self.future_collision:
                if local_angle_deg <= 0:
                    for course in range(0, temp_idx+1):
                        valid_actions.append(course)
                else:
                    for course in range(temp_idx, 29):
                        valid_actions.append(course)
            else:
                for course in range(0, 29):
                    valid_actions.append(course)
        else:
            for course in range(0, 29):
                valid_actions.append(course)

        # print('valid actions are: ', valid_actions)

        #draw(self.screen, self.space)
        self.space.step(1./10)
        if draw_screen:
            pg.display.flip()
        clock.tick()


        distance = (vec(self.own_center_pos) - vec(self.target_center_pos)).length()
        # print(distance)
        # Set the reward.
        if distance < 100:
            reward = -100
        elif self.future_collision:
            reward = -0.5

        else:
            yg_local = -(self.x_g - x_0) * math.sin(theta) + (self.y_g - y_0) * math.cos(theta)
            xg_local = (self.x_g - x_0) * math.cos(theta) + (self.y_g - y_0) * math.sin(theta)
            distance_to_goal = vec(xg_local, yg_local).length()
            # print(distance_to_goal)
            if distance_to_goal <= 200: # 200
                reward = 100
            else:
                reward = -0.3
        # else:
        #     if self.course_reached:
        #         theta = math.radians(self.own_rot_deg)

        #         yg_local = -(self.x_g - x_0) * math.sin(theta) + (self.y_g - y_0) * math.cos(theta)
        #         xg_local = (self.x_g - x_0) * math.cos(theta) + (self.y_g - y_0) * math.sin(theta)
        #         angle_to_goal_deg = abs(math.degrees(math.atan2(yg_local, xg_local)))
        #         distance_to_goal = vec(xg_local, yg_local).length()

        #         if angle_to_goal_deg <= 40:
        #             if distance_to_goal <= 460:
        #                 punishment = 0
        #             elif distance_to_goal >= 560:
        #                 punishment = 1
        #             else:
        #                 punishment = (distance_to_goal - 460) / 100
        #             reward = 100 - 30 * punishment - angle_to_goal_deg / 2
        #             print('distance punishment = ', punishment, 'angle to goal = ', angle_to_goal_deg)
        #         else:
        #             reward = 0
        #     else:
        #         reward = 0
        # print(reward)
        self.num_steps += 1
        # print(reward)
        return reward, self.screen, valid_actions, self.course_reached, self.future_collision

    def get_vertices_list(self, x_0, y_0, rot):
        L1 = 20
        L2 = 10
        x_1 = x_0 - L1 * math.cos(rot) / 2 - L2 * math.sin(rot) / 2
        y_1 = y_0 - L1 * math.sin(rot) / 2 + L2 * math.cos(rot) / 2
        x_2 = x_0 + L1 * math.cos(rot) / 2 - L2 * math.sin(rot) / 2
        y_2 = y_0 + L1 * math.sin(rot) / 2 + L2 * math.cos(rot) / 2
        x_3 = x_0 + L1 * math.cos(rot) / 2 + L2 * math.sin(rot) / 2
        y_3 = y_0 + L1 * math.sin(rot) / 2 - L2 * math.cos(rot) / 2
        x_4 = x_0 - L1 * math.cos(rot) / 2 + L2 * math.sin(rot) / 2
        y_4 = y_0 - L1 * math.sin(rot) / 2 - L2 * math.cos(rot) / 2
        x_5 = x_0 + L1 * math.cos(rot)
        y_5 = y_0 + L1 * math.sin(rot)

        vertices_list = [(x_1, y_1), (x_2, y_2), (x_5, y_5), (x_3, y_3), (x_4, y_4)]
        return vertices_list

    def move_target_ships(self):
        x_cat, y_cat = self.cat_body.position
        x_obs, y_obs = self.obs_body.position
        new_a_cat = self.test_boundary(x_cat, y_cat, self.cat_body.angle)
        new_a_obs = self.test_boundary(x_obs, y_obs, self.obs_body.angle)
        speed = 20
        self.cat_body.angle = new_a_cat
        self.obs_body.angle = new_a_obs
        direction_cat = Vec2d(1, 0).rotated(self.cat_body.angle)
        direction_obs = Vec2d(1, 0).rotated(self.obs_body.angle)
        self.cat_body.velocity = speed * direction_cat
        self.obs_body.velocity = speed * direction_obs

    def car_is_crashed(self, readings):
        if readings[0] == 1 or readings[1] == 1 or readings[2] == 1:
            return True
        else:
            return False

    def test_boundary(self, x, y, angle):
        sz = 70
        if x < sz:
            if y < sz:
                return 0.52 + (1.05-0.52)*random.random()
            elif y > height - sz:
                return 5.23 + 0.53*random.random()
            else: return -1 + 2 * random.random()
        elif x > width - sz:
            if y < sz:
                return 2.09 + 0.52*random.random()
            elif y > height - sz:
                return 3.66 + 0.52*random.random()
            else: return 2.09+(4.17-2.09)*random.random()
        elif y < sz:
            return 0.52 + (2.61 - 0.52)*random.random()
        elif y > height - sz - 70:
            return 3.66 + (5.75 - 3.66) * random.random()
        else: return angle


    def recover_from_crash(self, driving_direction):
        """
        We hit something, so recover.
        """
        while self.crashed:
            # Go backwards.
            self.space.remove(self.car_body, self.car_shape)
            #self.space.remove(self.goal_body, self.goal_shape)
            self.space.remove(self.cat_body, self.cat_shape)
            self.create_car(width/2, 100, 1.57)
            #self.create_goal()
            self.create_cat()
            self.space.remove(self.obs_body, self.obs_shape)
            self.create_obs()
            self.crashed = False

    def sum_readings(self, readings):
        """Sum the number of non-zero readings."""
        tot = 0
        for i in readings:
            tot += i
        return tot


    def get_track_or_not(self, reading):
        color = 0   #black

        if reading == THECOLORS['black']:
            color = 0
        elif reading == THECOLORS['red'] or reading == THECOLORS['blue']:
            color = 1   #red
        else: color = 2   #orange

        return color


if __name__ == "__main__":
    game_state = GameState()
    while True:
        game_state.frame_step((random.randint(0, 2)))
