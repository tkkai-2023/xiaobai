import json
import datetime
import random
import os
from objects.item import Item
from objects.leetcode_classify import LeetCodeClassify

# 将Item对象列表保存到JSON文件
def save_items_to_json(items, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=4)

# 从JSON文件读取数据并转换为Item对象列表
def load_items_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Item.from_dict(item) for item in data]

# 添加新Item到列表
def add_new_item(items, leetcode_classifier):
    date_str = input("请输入日期（格式 YYYY-MM-DD):")
    leetcode_id = int(input("请输入leetcode题号:"))
    leetcode_url = input("请输入leetcode题号对应的url:")
    difficulty = input("请输入难易度(1-easy, 2-medium, 3-hard):")
    time_cost = input("请输入刷题耗时(min:sec):")
    tag = input("请输入题目tag类型(贪心/双指针/二叉树...):")
    # times = input("请输入已刷次数:")

    # 创建新Item对象并添加到列表
    if date_str:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        date = datetime.datetime.now().date()
    new_meta = {
        "date": date,
        "difficulty": difficulty,
        "time_cost": time_cost,
        "times": 1, # 自动设置times = 1
        "tag": tag
    }
    new_item = Item(leetcode_id, new_meta, leetcode_url =leetcode_url) 
    items.append(new_item)
    leetcode_classifier.add_problem_to_category(leetcode_id, tag)
    print(f"新条目已添加:{new_item}")

# 根据题号更新Item信息
def update_item_by_id(items, leetcode_classifier):
    leetcode_id = int(input("请输入要更新的题号："))
    
    # 查找是否存在该题号的Item
    item_to_update = next((item for item in items if item.leetcode_id == leetcode_id), None)
    
    if item_to_update:
        print(f"找到题目: {item_to_update}")
        date_str = input(f"请输入新的日期（当前日期: {item_to_update.date}，格式 YYYY-MM-DD, 不输入默认更新成今日):")
        difficulty = input(f"请输入新的难易度(1-easy, 2-medium, 3-hard) 当前难易度:{item_to_update.difficulty}):")
        time_cost = input(f"请输入刷题耗时(min:sec) 当前耗时: {item_to_update.time_cost}):")
        tag = input(f"请输入题目tag类型(贪心/双指针/二叉树...) 当前tag类型: {item_to_update.tag}):")
        new_meta = item_to_update.meta
        
        # 更新Item信息
        if date_str:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            new_meta["date"] = date
        else:
            date = datetime.datetime.now().date()
            new_meta["date"] = date

        if difficulty:
            new_meta["difficulty"] = difficulty
        if time_cost:
            new_meta["time_cost"] = time_cost
        new_meta["times"] += 1
        new_meta["tag"] = tag

        item_to_update.meta = new_meta
        leetcode_classifier.update_problem_categories(leetcode_id, [tag])
        print(f"对应题号信息已更新: {item_to_update}")
    else:
        print("未找到对应的题号。")

# 按时间成本和日期排序并返回第一个Item
def get_item_sorted_by_date_and_time_cost(items, leetcode_classifier):
    # 按日期排序，再按时间成本排序    
    # Select a random number between 1 and 4
    random_number = random.randint(2, 5)
    sorted_items = sorted(items, key=lambda item: (item.times, item.date, item.time_cost_in_seconds()))
    # print(sorted_items[0].tag, sorted_items[0].leetcode_id)
    l = leetcode_classifier.get_related_problems(sorted_items[0].leetcode_id, sorted_items[0].tag)
    print(f"今天要刷的题有:")
    # print(len(l))

    if len(l) > 0:
        for i in l:
            print(f"{i}\t")
    else:
        for i in sorted_items[:random_number]:
            print(f"{i.leetcode_id}\t")

# 获取当天所刷的所有题目
def get_today_questions(items):
    sorted_items = [x for x in items if x.date == datetime.datetime.now().date()]
    print(f"今天已经刷的题有{len(sorted_items)}道:")
    for i in sorted_items:
        print(f"|题目|\t |日期|\t\t|难度|\t |耗时|\t |次数|\t |类型|\t |链接|\t \n"
            f" {i.leetcode_id}\t  {i.meta['date']}\t {i.meta['difficulty']}\t  {i.meta['time_cost']}\t  {i.meta['times']}\t   {i.meta['tag']}\t  {i.leetcode_url}")

# 主程序入口
def main():
    filename = './data/leetcode_list.json'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    items = load_items_from_json(filename)
    leetcode_classifier = LeetCodeClassify()
    
    while True:
        print("\n1. 添加新题")
        print("2. 更新已刷的题")
        print("3. 查看所有题信息")
        print("4. 今天刷哪些题呀？")
        print("5. 看看今天刷了哪些题了？")
        print("6. 结束")

        
        choice = input("请选择操作：")
        
        if choice == '1':
            add_new_item(items, leetcode_classifier)
            save_items_to_json(items, filename)
        elif choice == '2':
            update_item_by_id(items, leetcode_classifier)
            save_items_to_json(items, filename)
        elif choice == '3':
            for item in items:
                print(item)
        elif choice == '4':
            get_item_sorted_by_date_and_time_cost(items, leetcode_classifier)
            break
        elif choice == '5':
            get_today_questions(items)
            break
        elif choice == '6':
            print("byebye...")
            break
        else:
            print("无效的选择，请重新输入。")

# 执行主程序
if __name__ == "__main__":
    main()