import gym
from gym import error, spaces, utils
from gym.utils import seeding

####################
import random
import math
import pyglet
from pyglet.gl import *
import time
from pyglet_test import MyWindow
from newpyglet import main
####################
FRAME_WIDTH = 1000
FRAME_HEIGHT = 800
# ROCKET_SPAWN_BOUNDARY_X = 0.1
ROCKET_SPAWN_BOUNDARY_Y_TOP = 0.8
ROCKET_SPAWN_BOUNDARY_Y_BOT = 0.2
TARGET_SPAWN_BOUNDARY_X = 0.9
PLANET_SPAWN_BOUNDARY_X_LEFT = 0.35
PLANET_SPAWN_BOUNDARY_X_RIGHT = 0.75
PLANET_SPAWN_BOUNDARY_Y_TOP = 0.8
PLANET_SPAWN_BOUNDARY_Y_BOT = 0.2
PLANET_MAX_MASS = 10**25
PLANET_MIN_MASS = 10**23

MAX_STEPS = 200
MAX_INIT_SPEED = 1.0/(2 * MAX_STEPS)
MAX_INIT_ANGLE = math.pi / 6
SPEED_FACTOR = 20  # Km/s
ROCKET_ACC = 1e-7  # km/s^2
ROCKET_ROT_ANGLE = math.pi / 6

NO_TOUCHING_ZONE_RADIUS = 0.05

FUEL_COST = -1
TURN_COST = -0.1

STEP_DURATION = 3600  # Seconds / tick
GRAVITY_CONSTANT = 6.674 * 10 ** (-19)  # km^3 / (kg s^2)
DISTANCE_FACTOR = SPEED_FACTOR * STEP_DURATION


class SlingshotEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
      """ 
      Define program state.
      All positions are relative to frame i.e. [0,1] X [0,1] where (0,0) indicates top 
      left corner and (1,1) indicates bottom right corner
      """
      self.reset()
      self.x = main(FRAME_WIDTH, FRAME_HEIGHT)
      self.positions = []

  def step(self, action):
    """
    Parameters
    ------------
    action :
    [forward_thrust, turn_angle] #forward_thrust in [0,1] turn_angle in [-1,1]

    Returns
    ------------
    (observations, reward, done, info)
    observations (tuple) :
        (rocket_x, rocket_y, rocket_vel_x, rocket_vel_y
        planet_x, planet_y, planet_m, target_x, target_y)

    reward (float) :
        r = time_penalty + fuel_penalty
        if done : score
    
    done (bool) :
        True if env is completed
    
    info (dict) :
        debugging data (gravity and stuff)

    """
    self.update_position(action)
    done = self.is_done()
    reward = self.calculate_reward(action, done)
    distance = math.sqrt((self.target_x - self.rocket_x)**2 + (self.target_y - self.rocket_y)**2) 
    if distance < self.min_distance:
      self.min_distance = distance
    
    return self.get_obs(), reward, done, dict()

  def update_position(self, action):
    delta_x = (self.planet_x - self.rocket_x)
    delta_y = (self.planet_y - self.rocket_y)
    r_p = math.sqrt(delta_x**2 + delta_y**2) * DISTANCE_FACTOR
    a_of_g = GRAVITY_CONSTANT * self.planet_m / (r_p**2) # km / s^2
    a_of_g_x = a_of_g * delta_x / r_p
    a_of_g_y = a_of_g * delta_y / r_p
    a_of_t = ROCKET_ACC * action[0]
    final_angle = self.rocket_angle + ROCKET_ROT_ANGLE * action[1]
    half_angle = (self.rocket_angle + final_angle) / 2
    a_of_t_x = a_of_t * math.cos(half_angle)
    a_of_t_y = a_of_t * math.sin(half_angle)

    a_x = (a_of_g_x + a_of_t_x)
    a_y = (a_of_g_y + a_of_t_y)

    self.rocket_x = (self.rocket_x * DISTANCE_FACTOR + self.rocket_vel_x * SPEED_FACTOR * STEP_DURATION + 1/2 * a_x *
                     STEP_DURATION ** 2) / DISTANCE_FACTOR
    self.rocket_y = (self.rocket_y * DISTANCE_FACTOR + self.rocket_vel_y * SPEED_FACTOR * STEP_DURATION + 1/2 * a_y *
                     STEP_DURATION ** 2) / DISTANCE_FACTOR
    self.rocket_vel_x = self.rocket_vel_x + a_x * STEP_DURATION / SPEED_FACTOR
    self.rocket_vel_y = self.rocket_vel_y + a_y * STEP_DURATION / SPEED_FACTOR
    self.rocket_angle = final_angle
    self.acc_x = a_x
    self.acc_y = a_y

  def get_obs(self):
    return (self.rocket_x, self.rocket_y, self.rocket_vel_x, 
            self.rocket_vel_y, self.planet_x, self.planet_y, self.planet_m,
            self.target_x, self.target_y)

  def is_done(self):
    radius_planet = math.sqrt((self.rocket_x - self.planet_x) ** 2 + (self.rocket_y - self.planet_y)**2)
    if self.rocket_x > 1 or self.rocket_x < 0:
      return True
    elif self.rocket_y > 1 or self.rocket_y < 0:
      return True
    elif self.time_step > MAX_STEPS:
      return True
    elif radius_planet < NO_TOUCHING_ZONE_RADIUS:
      print("Entered No touching zone")
      return True
    else:
      return False

  def calculate_reward(self, actions, done):
    reward = abs(actions[0]) * FUEL_COST + abs(actions[1]) * TURN_COST

    if done:
      reward += 200/(1+100*self.min_distance) - 2
    return reward

  def reset(self):
    self.target_x = random.uniform(TARGET_SPAWN_BOUNDARY_X, 1)
    self.target_y = random.uniform(0, 1)
    self.planet_x = random.uniform(PLANET_SPAWN_BOUNDARY_X_LEFT, PLANET_SPAWN_BOUNDARY_X_RIGHT)
    self.planet_y = random.uniform(PLANET_SPAWN_BOUNDARY_Y_BOT, PLANET_SPAWN_BOUNDARY_Y_TOP)
    self.planet_m = random.uniform(PLANET_MIN_MASS, PLANET_MAX_MASS)
    self.rocket_x = 0.0
    self.rocket_y = random.uniform(ROCKET_SPAWN_BOUNDARY_Y_BOT, ROCKET_SPAWN_BOUNDARY_Y_TOP)
    speed = random.uniform(0, MAX_INIT_SPEED)
    self.rocket_angle = random.uniform(-MAX_INIT_ANGLE, MAX_INIT_ANGLE)
    self.rocket_vel_x = speed * math.cos(self.rocket_angle)
    self.rocket_vel_y = speed * math.sin(self.rocket_angle)
    self.min_distance = math.sqrt((self.target_x - self.rocket_x) ** 2 + (self.target_y - self.target_y) ** 2)
    self.time_step = 0
    return self.get_obs()

  def render(self, mode='human'):
    self.positions.append(int(self.rocket_x*FRAME_WIDTH))
    self.positions.append(int(self.rocket_y*FRAME_HEIGHT))
    self.x.render(self.positions[-2], self.positions[-1], self.rocket_angle, self.planet_x * FRAME_WIDTH,
                  self.planet_y * FRAME_HEIGHT, self.target_x * FRAME_WIDTH, self.target_y * FRAME_HEIGHT,
                  self.positions, 1)
    event = self.x.dispatch_events()

  def close(self):
    pass


if __name__ == '__main__':
  env = SlingshotEnv()
  state = env.reset()
  positions = []
  print(state)
  print(env.rocket_angle)

  for i in range(10000):
    positions.append(int(state[0] * FRAME_WIDTH))
    positions.append(int(state[1] * FRAME_HEIGHT))
    if env.rocket_angle > math.pi/2:
      state, reward, done, _ = env.step((0.5, -0.1))
    elif env.rocket_angle < math.pi/2:
      state, reward, done, _ = env.step((1, 0.1))
    else:
      state, reward, done, _ = env.step((1, 0))

    env.render()
    if done:
      print("Iter", i)
      print("Vel: ", env.rocket_vel_x, env.rocket_vel_y)
      print("Acc: ", env.acc_x, env.acc_y)
      break


