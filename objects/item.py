import datetime

class Item:
    def __init__(self, leetcode_id: int, meta: dict, leetcode_url: str):
        self.leetcode_id = leetcode_id  # 题目ID作为独立属性
        self.meta = meta  # 其他属性统一存入meta字典
        self.leetcode_url = leetcode_url
        
        # 确保meta包含必要字段的默认值（可选）
        self.meta.setdefault("date", datetime.date.today())
        self.meta.setdefault("difficulty", "Unknown")
        self.meta.setdefault("time_cost", "0:00")
        self.meta.setdefault("times", 0)

    def __repr__(self):
        return (
            f"题目: \n"
            f"  leetcode_id={self.leetcode_id}\n"
            f"  leetcode_url={self.leetcode_url}\n"
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
            "leetcode_url": self.leetcode_url,
            "meta": {
                # 日期序列化为ISO字符串
                "date": self.meta["date"].isoformat(),
                "difficulty": self.meta["difficulty"],
                "time_cost": self.meta["time_cost"],
                "times": self.meta["times"],
                "tag": self.meta["tag"]
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