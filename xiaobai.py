import json
import datetime
import random
import os
from objects.item import Item
from objects.leetcode_classify import LeetCodeClassify
from colorama import init, Fore, Back, Style

from objects.printer import ColorPrinter

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
        "tag": tag,
        "leetcode_url": leetcode_url
    }
    new_item = Item(leetcode_id, new_meta) 
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
        leetcode_url = input(f"请输入leetcode题号对应的url(当前url: {item_to_update.leetcode_url}):")
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
        
        if leetcode_url:
            new_meta["leetcode_url"] = leetcode_url

        if difficulty:
            new_meta["difficulty"] = difficulty
        if time_cost:
            new_meta["time_cost"] = time_cost
        new_meta["times"] += 1
        if tag:
            new_meta["tag"] = tag
            leetcode_classifier.update_problem_categories(leetcode_id, [tag])
        item_to_update.meta = new_meta
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

    if len(l) > 0:
        for i in l:
            print(f"{i}\t")
    else:
        for i in sorted_items[:random_number]:
            print(f"{i.leetcode_id}\t")

# 添加题目得分计算函数
def calculate_problem_score(item: Item) -> float:
    """计算单个题目的推荐得分（0-10）"""
    time_score = min(item.time_cost_in_seconds() / 1800 * 5, 5)  # 耗时占5分
    days_old = (datetime.date.today() - item.date).days
    date_score = min(days_old / 30 * 5, 5)  # 旧时间占5分
    return round(time_score + date_score, 2)

# 替换原有的get_item_sorted_by_date_and_time_cost函数
def get_recommended_problems(items: list[Item], leetcode_classifier: LeetCodeClassify):
    # 计算所有标签得分
    tag_scores = leetcode_classifier.calculate_tag_scores(items)
    
    if not tag_scores:
        print("暂无分类信息，随机推荐:")
        random_items = random.sample(items, min(3, len(items)))
        for item in random_items:
            print(f"题目ID：{item.leetcode_id}")
        return
    
    # 找到最高分标签
    max_score = max(tag_scores.values())
    max_tags = [tag for tag, score in tag_scores.items() if score == max_score]
    selected_tag = random.choice(max_tags)  # 如果有多个，随机选一个
    
    # 获取该标签下所有题目并计算单个题目得分
    problem_ids = leetcode_classifier.data["category_to_problems"][selected_tag]
    tag_items = [item for item in items if item.leetcode_id in problem_ids]
    sorted_items = sorted(tag_items, key=lambda x: calculate_problem_score(x), reverse=True)
    
    # 推荐前3题或全部
    print(f"推荐类型：{selected_tag}（得分：{tag_scores[selected_tag]}/10）")
    for item in sorted_items[:3]:
        print(f"题目ID：{item.leetcode_id}（得分：{calculate_problem_score(item)}）(链接：{item.leetcode_url})")

# 修改后的当天题目显示函数
def get_today_questions(items):
    sorted_items = [x for x in items if x.date == datetime.datetime.now().date()]
    print(f"今天已经刷的题有{len(sorted_items)}道:")
    for i in sorted_items:
        print(f"|题目|\t |日期|\t\t|难度|\t |耗时|\t |次数|\t |类型|\t\t |链接|\t \n"
            f" {i.leetcode_id}\t  {i.meta['date']}\t {i.meta['difficulty']}\t  {i.meta['time_cost']}\t  {i.meta['times']}\t   {i.meta['tag']}\t  {i.meta['leetcode_url']}")

def review_problems(items, leetcode_classifier):
    """复习题目 - 支持按题目或类型排序"""
    
    # 标题装饰
    print("\n" + Back.BLUE + Fore.WHITE + " 复习模式 ".center(80, "=") + Style.RESET_ALL)
    print(Fore.CYAN + "1. 按题目复习（基于遗忘曲线评分）")
    print("2. 按类型复习（基于分类评分）" + Style.RESET_ALL)
    mode = input("\n请选择复习模式 (1/2): ")
    
    if mode == '1':
        # 按题目复习
        sorted_items = sorted(
            items, 
            key=lambda item: item.calculate_review_score(), 
            reverse=True
        )
        
        # 表格标题
        print("\n" + Fore.YELLOW + "=" * 110)
        title = "复习优先级排序（分数越高越需要复习）"
        print(f"{title:^110}")
        print("=" * 110 + Style.RESET_ALL)
        
        # 表头
        headers = ["题号", "日期", "难度", "耗时", "次数", "类型", "分数", "状态", "链接"]
        col_widths = [8, 12, 8, 8, 8, 16, 8, 10, 40]
        r_col_widths = [10, 14, 10, 10, 10, 18, 10, 12, 42]
        
        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
        
        # 打印数据行
        for item in sorted_items[:20]:  # 显示前20个
            score = item.calculate_review_score()
            # 根据分数设置状态和颜色
            if score > 6:
                status = "urgent"
                color = Fore.RED
            elif score > 4:
                status = "suggest"
                color = Fore.YELLOW
            else:
                status = "you're good"
                color = Fore.GREEN
            
            # 准备数据
            data = [
                str(item.leetcode_id),
                item.date.strftime('%m-%d'),
                _get_difficulty_symbol(item.difficulty),
                item.time_cost,
                str(item.times),
                item.tag[:10],
                f"{score:.2f}",
                status,
                item.leetcode_url
            ]
            
            # 打印行
            row = "│".join([d.center(w) for d, w in zip(data, r_col_widths)])
            print("│" + color + row + Style.RESET_ALL)
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")
        
        # 分数说明
        print(Fore.CYAN + "\n分数说明: " + 
              Fore.RED + ">6.0 (urgent 急需复习)  " + 
              Fore.YELLOW + "4.0-6.0 (suggest 建议复习)  " + 
              Fore.GREEN + "<4.0 (you're good 已掌握)" + 
              Style.RESET_ALL)
        print(Fore.CYAN + "目标: 所有题目耗时 ≤10分钟" + Style.RESET_ALL)
    
    elif mode == '2':
        # 按类型复习
        tag_scores = leetcode_classifier.calculate_tag_review_scores(items)
        if not tag_scores:
            print(Fore.RED + "暂无分类信息" + Style.RESET_ALL)
            return
        
        # 按分数排序
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 类型表格
        print("\n" + Fore.YELLOW + "=" * 60)
        title = "类型复习优先级（分数越高越需要复习）"
        print(f"{title:^60}")
        print("=" * 60 + Style.RESET_ALL)
        
        # 表头
        headers = ["类型", "平均分数", "题目数", "状态"]
        col_widths = [20, 10, 10, 20]
        r_col_widths = [22, 14, 12, 22]
        
        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
        
        # 打印数据行
        for tag, score in sorted_tags:
            count = len(leetcode_classifier.data["category_to_problems"].get(tag, []))
            # 根据分数设置状态和颜色
            if score > 6:
                status = "urgent"
                color = Fore.RED
            elif score > 4:
                status = "suggest"
                color = Fore.YELLOW
            else:
                status = "you're good"
                color = Fore.GREEN
            
            # 准备数据
            data = [
                tag[:18],
                f"{score:.2f}",
                str(count),
                status
            ]
            
            # 打印行
            row = "│".join([d.center(w) for d, w in zip(data, r_col_widths)])
            print("│" + color + row + Style.RESET_ALL + "│")
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")
        
        # 让用户选择具体类型查看题目
        selected_tag = input("\n输入要查看的类型（直接回车返回）: ")
        if selected_tag:
            problem_ids = leetcode_classifier.data["category_to_problems"].get(selected_tag, [])
            tag_items = [item for item in items if item.leetcode_id in problem_ids]
            
            if not tag_items:
                print(Fore.RED + f"类型 '{selected_tag}' 下无题目" + Style.RESET_ALL)
                return
            
            # 按分数排序该类型下的题目
            sorted_items = sorted(
                tag_items, 
                key=lambda item: item.calculate_review_score(), 
                reverse=True
            )
            
            # 题目详情表格
            print("\n" + Fore.YELLOW + "=" * 100)
            title = f"类型【{selected_tag}】下的题目（按复习优先级排序）"
            print(f"{title:^100}")
            print("=" * 100 + Style.RESET_ALL)
            
            # 表头
            headers = ["题号", "日期", "难度", "耗时", "次数", "分数", "状态", "链接"]
            col_widths = [8, 10, 10, 10, 10, 10, 10, 46]
            r_col_widths = [10, 12, 12, 12, 12, 12, 12, 48]
            
            # 打印表头
            header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
            print("│" + header_line + "│")
            print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
            
            # 打印数据行
            for item in sorted_items:
                score = item.calculate_review_score()
                # 根据分数设置状态和颜色
                if score > 6:
                    status = "urgent"
                    color = Fore.RED
                elif score > 4:
                    status = "suggest"
                    color = Fore.YELLOW
                else:
                    status = "you're good"
                    color = Fore.GREEN
                
                # 准备数据
                data = [
                    str(item.leetcode_id),
                    item.date.strftime('%m-%d'),
                    _get_difficulty_symbol(item.difficulty),
                    item.time_cost,
                    str(item.times),
                    f"{score:.2f}",
                    status,
                    item.leetcode_url[:44] + "..." if len(item.leetcode_url) > 44 else item.leetcode_url
                ]
                
                # 打印行
                row = "│".join([d.center(w) for d, w in zip(data, r_col_widths)])
                print("│" + color + row + Style.RESET_ALL )
            
            # 表格底部
            print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")

def _get_difficulty_symbol(difficulty):
    """获取难度符号"""
    from colorama import Fore
    diff = difficulty.lower()
    if diff == "easy":
        return Fore.GREEN + "★" + Fore.RESET
    elif diff == "medium":
        return Fore.YELLOW + "★★" + Fore.RESET
    elif diff == "hard":
        return Fore.RED + "★★★" + Fore.RESET
    else:
        return difficulty
    
    
# 主程序入口
def main():
    filename = './data/leetcode_list.json'
    folder_path = './data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    items = load_items_from_json(filename)
    leetcode_classifier = LeetCodeClassify()

    # 创建全局单例实例
    printer = ColorPrinter()
    
    while True:
        print("\n" + "="*50)
        print(Fore.BLUE + " LeetCode 刷题管理系统 ".center(50, "=") + Style.RESET_ALL)
        print(Fore.CYAN + "1. 添加新题")
        print("2. 更新已刷的题")
        print("3. 查看所有题信息")
        print("4. 复习题目")
        print("5. 显示分类分数表")
        print("6. 查看今日刷题记录")
        print("7. 结束")
        print("="*50 + Style.RESET_ALL)
        
        choice = input("请选择操作：")
        
        if choice == '1':
            add_new_item(items, leetcode_classifier)
            save_items_to_json(items, filename)
        elif choice == '2':
            update_item_by_id(items, leetcode_classifier)
            save_items_to_json(items, filename)
        elif choice == '3':
            # 功能3：查看所有题信息
            printer.print_items(items, "所有题目")
        elif choice == '4':
            # 功能4：复习题目
            review_problems(items, leetcode_classifier)
        elif choice == '5':
            # 功能5：显示分类分数表
            tag_scores = leetcode_classifier.calculate_tag_scores(items)
            # printer.print_tag_scores(tag_scores, items, leetcode_classifier)
            leetcode_classifier.print_tag_scores_table(tag_scores, items)
        elif choice == '6':
            # 功能6：查看今日刷题记录
            today = datetime.date.today()
            today_items = [item for item in items if item.date == today]
            leetcode_classifier.print_items_table(today_items, "今日刷题记录")
        elif choice == '7':
            print("byebye...")
            break
        else:
            print("无效的选择，请重新输入。")

# 执行主程序
if __name__ == "__main__":
    main()