import datetime
import math

class Item:
    def __init__(self, leetcode_id: int, meta: dict):
        self.leetcode_id = leetcode_id  # 题目ID作为独立属性
        self.meta = meta  # 其他属性统一存入meta字典

        
        # 确保meta包含必要字段的默认值（可选）
        self.meta.setdefault("date", datetime.date.today())
        self.meta.setdefault("difficulty", "Unknown")
        self.meta.setdefault("time_cost", "0:00")
        self.meta.setdefault("times", 0)

    def __repr__(self):
        return (
            f"题目: \n"
            f"  leetcode_id={self.leetcode_id}\n"
            f"  leetcode_url={self.meta['leetcode_url']}\n"
            f"  date={self.meta['date']}\n"
            f"  difficulty={self.meta['difficulty']}\n"
            f"  time_cost={self.meta['time_cost']}\n"
            f"  times={self.meta['times']}\n"
            f"  tag={self.meta['tag']}"
        )
    
    def to_dict(self) -> dict:
        """序列化为字典（包含日期格式化）"""
        return {
            "leetcode_id": self.leetcode_id,
            "meta": {
                # 日期序列化为ISO字符串
                "date": self.meta["date"].isoformat(),
                "difficulty": self.meta["difficulty"],
                "time_cost": self.meta["time_cost"],
                "times": self.meta["times"],
                "tag": self.meta["tag"],
                "leetcode_url": self.meta["leetcode_url"],
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        """从字典反序列化"""
        meta = data["meta"].copy()
        # 日期反序列化为date对象
        meta["date"] = datetime.datetime.strptime(
            meta["date"], "%Y-%m-%d"
        ).date()
        return cls(
            leetcode_id=data["leetcode_id"],
            meta=meta
        )

    def time_cost_in_seconds(self) -> int:
        """将 time_cost 转换为秒数"""
        try:
            parts = self.meta["time_cost"].split(":")
            if len(parts) == 1:  # 仅分钟格式（如"5"表示5分钟）
                return int(parts[0]) * 60
            elif len(parts) == 2:  # 分:秒格式
                return int(parts[0]) * 60 + int(parts[1])
            else:
                raise ValueError("Invalid time format")
        except (ValueError, AttributeError):
            return 0
    def calculate_review_score(self) -> float:
        """计算复习分数（基于遗忘曲线、难度、耗时）"""
        # 艾宾浩斯遗忘曲线参数（复习间隔天数）
        ebbinghaus_intervals = [1, 2, 4, 7, 15]
        
        # 难度权重（难度越大，分数越高）
        difficulty_weights = {"easy": 1, "medium": 1.5, "hard": 2}
        
        # 计算距今天数
        days_since_last = (datetime.datetime.now().date() - self.date).days
        
        # 获取最近复习间隔（基于复习次数）
        interval_index = min(self.times - 1, len(ebbinghaus_intervals) - 1)
        ideal_interval = ebbinghaus_intervals[interval_index] if interval_index >= 0 else 0
        
        # 计算遗忘惩罚因子（超过理想间隔越多，分数越高）
        forget_factor = max(1, math.log(max(1, days_since_last - ideal_interval) + 1))
        
        # 计算耗时因子（耗时越长，分数越高）
        time_factor = min(5, self.time_cost_in_seconds() / 60)  # 每分钟增加1分
        
        # 计算难度因子
        diff_factor = difficulty_weights.get(self.difficulty.lower(), 1)
        
        # 综合评分 = 遗忘因子 * 难度因子 + 耗时因子
        return round(forget_factor * diff_factor + time_factor, 2)
    
    # 可选：通过属性快速访问常用字段（保持旧代码兼容性）
    @property
    def date(self) -> datetime.date:
        return self.meta["date"]

    @property
    def difficulty(self) -> str:
        return self.meta["difficulty"]

    @property
    def time_cost(self) -> str:
        return self.meta["time_cost"]

    @property
    def times(self) -> int:
        return self.meta["times"]
    
    @property
    def tag(self) -> str:
        return self.meta["tag"]
    @property
    def leetcode_url(self) -> str:
        return self.meta["leetcode_url"]