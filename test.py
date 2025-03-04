import datetime, json
from objects.item import Item

def convert_legacy_item(legacy_data: dict) -> Item:
    """将旧版数据结构转换为新版带 meta 的 Item 对象"""
    # 1. 提取 leetcode_id 并构建 meta 字典
    leetcode_id = legacy_data["leetcode_id"]
    meta = {
        "date": datetime.datetime.strptime(legacy_data["date"], "%Y-%m-%d").date(),
        "difficulty": legacy_data["difficulty"],
        "time_cost": legacy_data["time_cost"],
        "times": legacy_data["times"]
    }
    
    # 2. 创建新 Item 对象
    return Item(
        leetcode_id=leetcode_id,
        meta=meta
    )

# 从JSON文件读取数据并转换为Item对象列表
def load_items_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data
    
# 测试示例 -------------------------------------------------
legacy_data_list = load_items_from_json('./data/leetcode_list.json')
res = []
for i in legacy_data_list:
    new_item = convert_legacy_item(i)
    print(json.dumps(new_item.to_dict(), indent=2)+',')
