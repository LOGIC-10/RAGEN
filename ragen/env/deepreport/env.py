
from ragen.env import BaseLanguageBasedEnv
import gym

class DeepReportEnv(BaseLanguageBasedEnv, gym.Env):
    def __init__(self):
        super().__init__()
        # TODO: 初始化你的DeepReport环境
        
    def step(self, action):
        """执行动作并获取reward"""
        # TODO: 实现与你的环境交互的逻辑
        # 返回observation, reward, done, info
        # reward应该从你的环境中获取
        pass
        
    def reset(self):
        # TODO: 实现环境重置逻辑
        pass
        
    def render(self):
        # TODO: 实现环境状态的可视化
        pass

    @staticmethod 
    def parse_update_info_to_obs(update_info, action_is_valid):
        # TODO: 将环境信息转换为observation字符串
        pass