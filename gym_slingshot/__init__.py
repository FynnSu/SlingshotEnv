from gym.envs.registration import register

register(
    id='slingshot-v0',
    entry_point='gym_slingshot.envs:SlingshotEnv',
)
register(
    id='slingshot-extrahard-v0',
    entry_point='gym_slingshot.envs:SlingshotExtraHardEnv',
)