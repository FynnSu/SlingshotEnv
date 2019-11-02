import gym
from gym import error, spaces, utils
from gym.utils import seeding

####################
import random
import math



#################
FRAME_WIDTH = 20.0
FRAME_HEIGHT = 10.0
ROCKET_SPAWN_BOUNDARY_X = 0.1
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
MAX_INIT_SPEED = 1.0/ (2 * MAX_STEPS)
MAX_INIT_ANGLE = math.pi / 6
SPEED_FACTOR = 20 # Km/s
ROCKET_ACC = 0.02 # km/s^2
ROCKET_ROT_ANGLE = math.pi / 6

FUEL_COST = -1
TURN_COST = -0.1

STEP_DURATION = 3600 # Seconds
GRAVITY_CONSTANT = 6.674 * 10 **-20 # km^3 / (kg s^2)
DISTANCE_FACTOR =  SPEED_FACTOR / MAX_INIT_SPEED * STEP_DURATION

class SlingshotEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
      """ 
      Define program state.
      All positions are relative to frame i.e. [0,1] X [0,1] where (0,0) indicates top 
      left corner and (1,1) indicates bottom right corner
      """

      self.target_x = random.uniform(TARGET_SPAWN_BOUNDARY_X, 1)
      self.target_y = random.uniform(0,1)
      self.planet_x = random.uniform(PLANET_SPAWN_BOUNDARY_X_LEFT, PLANET_SPAWN_BOUNDARY_X_RIGHT)
      self.planet_y = random.uniform(PLANET_SPAWN_BOUNDARY_Y_BOT, PLANET_SPAWN_BOUNDARY_Y_TOP)
      self.planet_m = random.uniform(PLANET_MIN_MASS, PLANET_MAX_MASS)
      self.rocket_x = random.uniform(0, ROCKET_SPAWN_BOUNDARY_X)
      self.rocket_y = random.uniform(ROCKET_SPAWN_BOUNDARY_Y_BOT, ROCKET_SPAWN_BOUNDARY_Y_TOP)
      speed = random.uniform(0, MAX_INIT_SPEED)
      self.rocket_angle = random.uniform(-MAX_INIT_ANGLE, MAX_INIT_ANGLE)
      self.rocket_vel_x = speed * math.cos(self.rocket_angle)
      self.rocket_vel_y = speed * math.sin(self.rocket_angle)
      self.min_distance = math.sqrt((self.target_x - self.rocket_x)**2 + (self.target_y - self.target_y)**2) 
      self.time_step = 0




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
    self.updatePosition(action)
    done = self.isDone()
    reward = self.calculate_reward(action, done)
    distance = math.sqrt((self.target_x - self.rocket_x)**2 + (self.target_y - self.target_y)**2) 
    if distance < self.min_distance:
      self.min_distance = distance
    
    return (self.getObs(), reward, done, dict())




  def updatePosition(self, action):
    delta_x = (self.planet_x - self.rocket_x)
    delta_y = (self.planet_y - self.rocket_y)
    r_p = math.sqrt(delta_x**2 + delta_y**2) * DISTANCE_FACTOR
    a_of_g = 0 #GRAVITY_CONSTANT * self.planet_m / (r_p**2) # km / s^2
    a_of_g_x = a_of_g * delta_x / r_p
    a_of_g_y = a_of_g * delta_y / r_p
    a_of_t = ROCKET_ACC * action[0]
    final_angle = self.rocket_angle + ROCKET_ROT_ANGLE * action[1]
    half_angle = (self.rocket_angle + final_angle) / 2
    a_of_t_x = a_of_t * math.cos(half_angle)
    a_of_t_y = a_of_t * math.sin(half_angle)

    a_x = (a_of_g_x + a_of_t_x)
    a_y = (a_of_g_y + a_of_t_y)


    self.rocket_x = (self.rocket_x * DISTANCE_FACTOR + self.rocket_vel_x * SPEED_FACTOR * STEP_DURATION + 1/2 * a_x * STEP_DURATION ** 2) / DISTANCE_FACTOR
    self.rocket_y = (self.rocket_y * DISTANCE_FACTOR + self.rocket_vel_y * SPEED_FACTOR * STEP_DURATION + 1/2 * a_y * STEP_DURATION ** 2) / DISTANCE_FACTOR
    self.rocket_vel_x = self.rocket_vel_x + a_x * STEP_DURATION / SPEED_FACTOR
    self.rocket_vel_y = self.rocket_vel_y + a_y * STEP_DURATION / SPEED_FACTOR
    self.rocket_angle = final_angle

  def getObs(self):
    return (self.rocket_x, self.rocket_y, self.rocket_vel_x, 
    self.rocket_vel_y, self.planet_x, self.planet_y, self.planet_m,
    self.target_x, self.target_y)

  def isDone(self):
    if self.rocket_x > 1 or self.rocket_x < 0:
      return True
    elif self.rocket_y > 1 or self.rocket_y < 0:
      return True
    elif self.time_step > MAX_STEPS:
      return True
    else:
      return False

  def calculate_reward(self, actions, done):
    reward = actions[0] * FUEL_COST + actions[1] * TURN_COST

    if done:
      reward += 200/(1+100*self.min_distance) - 2
    return reward





  def reset(self):
    self.__init__()
    return self.getObs()


  def render(self, mode='human'):
    pass

  def close(self):
    pass


env = SlingshotEnv()
