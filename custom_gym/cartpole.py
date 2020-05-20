import gym
import math
from  gym import spaces, logger
from gym.utils import seeding
import numpy as np 
from custom_gym.models import Pole, Cart
from gym.envs.classic_control import rendering

class CustomCartPoleEnv(gym.Env):
    """
    Description:
        A pole is attached by an un-actuated joint to a cart, which moves along a frictionless track. The pendulum
        starts upright, and the goal is to prevent it from falling over by increasing and reducing the cart's velocity.
    Source:
        This environment corresponds to the version of the cart-pole problem described by Barto, Sutton, and Anderson
    Observation: 
        Type: Box(4)
        Num	Observation               Min             Max
        0	Cart Position             -100.0          100.0
        1	Cart Velocity             -Inf            Inf
        2	Pole 1 Angle              -180 deg        180 deg
        3	Pole 1 Velocity At Tip    -Inf            Inf
        
        
    Actions:
        Type: Discrete(2)
        Num	Action
        0	Push cart to the left
        1	Push cart to the right
        
        Note: The amount the velocity that is reduced or increased is not fixed; it depends on the angle the pole is
        pointing. This is because the center of gravity of the pole increases the amount of energy needed to move the
        cart underneath it
    Reward:
        
    Starting State:
        All observations are assigned a uniform random value
    Episode Termination: #to change
        Cart Position is more than 1000 (center of the cart reaches the edge of the display)
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, mode,render_mode='human'):
        self.cart = Cart(10)
        self.pole = Pole(1, 10, 10)
        self.gravity = 9.8
        self.time_step = 0.02
        self.force_mag = 400.0
        self.mode = mode
        self.render_mode = render_mode


        self.x_threshold = 100
        self.theta_threshold_radians = math.pi
        
        high = np.array([self.x_threshold * 2,
                         np.finfo(np.float32).max,
                         self.theta_threshold_radians * 2,
                         np.finfo(np.float32).max],
                        dtype=np.float32)

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(-high, high, dtype=np.float32)
        
        self.seed()
        self.viewer = None
        self.state = None
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action): # Execute one time step within the environment
        assert self.action_space.contains(action), "%r (%s) invalid"%(action, type(action))
        force = self.force_mag if action==1 else -self.force_mag
        self.steps += 1

        m1 = self.cart.mass
        m2 = self.pole.mass
        theta = -self.pole.theta
        l = self.pole.mass_center
        
        G = np.zeros(2)
        G[0] = -self.gravity * math.sin(theta)
        G[1] = force + m2 * l * self.pole.theta_dot * self.pole.theta_dot * math.sin(theta) 

        F = np.zeros((2,2))
        F[0,0] = math.cos(theta)
        F[0,1] = l
        F[1,0] = m1 + m2 
        F[1,1] = m2 * l * math.cos(theta)

        Finv = np.linalg.inv(F)
        
        T = Finv.dot(G)

        #print(T)

        self.cart.make_step(T[0], self.time_step)
        self.pole.make_step(T[1], self.time_step)

        #self.cart.print_info()
        #self.pole.print_info()
        
        out_of_bounds =  self.cart.x < -self.x_threshold or self.cart.x > self.x_threshold
        done = bool(out_of_bounds)

        if done:
            reward = -10.0
        else:
            r1 = self.cart.give_reward()
            r,v = self.pole.give_reward()
            reward = r+r1

        if self.render_mode != 'no' or self.mode:
            self.render(mode=self.render_mode)
        if self.mode == 0:
            self.state = (self.cart.x, self.cart.velocity,self.pole.theta,self.pole.theta_dot)
            return self.state, reward, done, {}
        else:
            return np.array(self.state), reward, done, {}



    def reset(self):  # Reset the state of the environment to an initial state
        self.cart.reset()
        self.pole.reset()
        self.steps = 0
        self.reward = 0
        if self.mode:
            self.render(mode='no')
        else:
            self.state = (self.cart.x, self.cart.velocity,self.pole.theta,self.pole.theta_dot)
        return np.array(self.state)

    

    def render(self, mode='human', close=False): # Render the environment to the screen
        screen_width = 1600
        screen_height = 1000

        world_width = self.x_threshold*2
        scale = screen_width/world_width
        carty = 180 # TOP OF CART
        polewidth = 6.0
        polelen1 = scale * self.pole.length
        cartwidth = 40.0
        cartheight = 15.0

        if self.viewer is None:
            
            self.viewer = rendering.Viewer(screen_width, screen_height)
            l,r,t,b = -cartwidth/2, cartwidth/2, cartheight/2, -cartheight/2
            axleoffset =cartheight/4.0
            cart = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            self.carttrans = rendering.Transform()
            cart.add_attr(self.carttrans)
            self.viewer.add_geom(cart)

            l,r,t,b = -polewidth/2,polewidth/2,polelen1-polewidth/2,-polewidth/2
            pole1 = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            pole1.set_color(.8,.6,.4)
            self.poletrans1 = rendering.Transform(translation=(0, axleoffset))
            pole1.add_attr(self.poletrans1)
            pole1.add_attr(self.carttrans)
            self.viewer.add_geom(pole1)

            self.axle = rendering.make_circle(polewidth/2)
            self.axle.add_attr(self.poletrans1)
            self.axle.add_attr(self.carttrans)
            self.axle.set_color(.5,.5,.8)
            self.viewer.add_geom(self.axle)
            self.track = rendering.Line((0,carty), (screen_width,carty))
            self.track.set_color(0,0,0)
            self.viewer.add_geom(self.track)

            self._pole_geom1 = pole1

        # Edit the pole polygon vertex

        cartx = self.cart.x * scale+screen_width/2.0 # MIDDLE OF CART
        self.carttrans.set_translation(cartx, carty)
        self.poletrans1.set_rotation(self.pole.theta)
        if self.mode:
            self.state=self.viewer.get_array()
        if mode != 'no':
            return self.viewer.render(return_rgb_array= (mode=='rgb_array'))