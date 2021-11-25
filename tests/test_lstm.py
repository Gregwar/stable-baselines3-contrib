import numpy as np
from gym import spaces
from gym.envs.classic_control import CartPoleEnv
from gym.wrappers.time_limit import TimeLimit

from sb3_contrib import RecurrentPPO


class CartPoleNoVelEnv(CartPoleEnv):
    """Variant of CartPoleEnv with velocity information removed. This task requires memory to solve."""

    def __init__(self):
        super().__init__()
        high = np.array(
            [
                self.x_threshold * 2,
                self.theta_threshold_radians * 2,
            ]
        )
        self.observation_space = spaces.Box(-high, high, dtype=np.float32)

    @staticmethod
    def _pos_obs(full_obs):
        xpos, _xvel, thetapos, _thetavel = full_obs
        return xpos, thetapos

    def reset(self):
        full_obs = super().reset()
        return CartPoleNoVelEnv._pos_obs(full_obs)

    def step(self, action):
        full_obs, rew, done, info = super().step(action)
        return CartPoleNoVelEnv._pos_obs(full_obs), rew, done, info


def test_ppo_lstm():
    from stable_baselines3.common.env_util import make_vec_env

    # env = make_vec_env("CartPole-v1", n_envs=8)

    def make_env():
        env = CartPoleNoVelEnv()
        env = TimeLimit(env, max_episode_steps=500)
        return env

    env = make_vec_env(make_env, n_envs=8)

    model = RecurrentPPO(
        "MlpLstmPolicy",
        env,
        n_steps=32,
        learning_rate=0.0007,
        verbose=1,
        batch_size=256,
        seed=0,
        n_epochs=10,
        # max_grad_norm=1,
        gae_lambda=0.98,
        policy_kwargs=dict(net_arch=[dict(vf=[64])], ortho_init=False),
        # policy_kwargs=dict(net_arch=[dict(pi=[64], vf=[64])])
        # create_eval_env=True,
    )

    # model.learn(total_timesteps=500, eval_freq=250)
    # model.learn(total_timesteps=1_000_000)
    model.learn(total_timesteps=100)
