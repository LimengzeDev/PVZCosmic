import json
import os
import time


class LevelLoader:
    def __init__(self, levels_folder="levels"):
        self.levels_folder = levels_folder
        self.levels = {}
        self.load_all_levels()
    
    def load_all_levels(self):
        """加载所有关卡文件"""
        for filename in os.listdir(self.levels_folder):
            if filename.endswith(".json"):
                level_id = filename.split(".")[0].replace("level_", "")
                with open(os.path.join(self.levels_folder, filename), "r") as f:
                    self.levels[level_id] = json.load(f)
    
    def get_level(self, level_id):
        """获取指定关卡数据"""
        return self.levels.get(str(level_id))
    
    def get_available_levels(self):
        """获取所有可用关卡ID"""
        return sorted(self.levels.keys())
    print("我是码农")
    time.sleep(0.5)
    print("我也是码农")