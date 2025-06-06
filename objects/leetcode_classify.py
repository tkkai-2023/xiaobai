import json
from pathlib import Path
from objects.item import Item
import datetime
from colorama import init, Fore, Style


class LeetCodeClassify:
    def __init__(self, data_path: str = "data/classification.json"):
        self.data_path = Path(data_path)
        self._load_data()

    def _load_data(self) -> None:
        """从 JSON 文件加载数据到内存"""
        if not self.data_path.exists():
            self.data = {
                "category_to_problems": {},
                "problem_to_categories": {}
            }
            self._save_data()
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)

    def _save_data(self) -> None:
        """保存内存中的数据到 JSON 文件"""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_problem_to_category(self, problem_id: int, category: str) -> None:
        """将题号添加到分类（双向索引）"""
        problem_id_str = str(problem_id)
        
        # 更新 category_to_problems
        if category not in self.data["category_to_problems"]:
            self.data["category_to_problems"][category] = []
        if problem_id not in self.data["category_to_problems"][category]:
            self.data["category_to_problems"][category].append(problem_id)
        
        # 更新 problem_to_categories
        if problem_id_str not in self.data["problem_to_categories"]:
            self.data["problem_to_categories"][problem_id_str] = []
        if category not in self.data["problem_to_categories"][problem_id_str]:
            self.data["problem_to_categories"][problem_id_str].append(category)
        
        self._save_data()

    def get_related_problems(self, problem_id: int, category: str, exclude_self: bool = True) -> list[int]:
        """获取与题目关联的所有题目（跨分类）"""
        problem_id_list = self.data["category_to_problems"].get(category, [])
        
        related = set(problem_id_list)
        
        # if exclude_self and problem_id in related:
        #     related.remove(problem_id)
        
        return sorted(related)

    def get_categories_of_problem(self, problem_id: int) -> list[str]:
        """获取题目所属的所有分类"""
        return self.data["problem_to_categories"].get(str(problem_id), [])

    def delete_problem_from_category(self, problem_id: int, category: str) -> None:
        """从分类中移除题目（双向清理）"""
        # 清理 category_to_problems
        if category in self.data["category_to_problems"]:
            if problem_id in self.data["category_to_problems"][category]:
                self.data["category_to_problems"][category].remove(problem_id)
            # 如果分类为空则删除
            if not self.data["category_to_problems"][category]:
                del self.data["category_to_problems"][category]
        
        # 清理 problem_to_categories
        problem_id_str = str(problem_id)
        if problem_id_str in self.data["problem_to_categories"]:
            if category in self.data["problem_to_categories"][problem_id_str]:
                self.data["problem_to_categories"][problem_id_str].remove(category)
            # 如果题目无分类则删除
            if not self.data["problem_to_categories"][problem_id_str]:
                del self.data["problem_to_categories"][problem_id_str]
        
        self._save_data()

    def update_problem_categories(self, problem_id: int, new_categories: list[str]) -> None:
        """
        更新题目所属的分类（覆盖旧分类）
        
        参数:
            problem_id (int): 题目ID
            new_categories (list[str]): 新分类列表（去重后覆盖）
        """
        problem_id_str = str(problem_id)
        new_categories = list(set(new_categories))  # 去重

        # 1. 获取当前分类（拷贝避免遍历时修改问题）
        current_categories = self.data["problem_to_categories"].get(problem_id_str, []).copy()

        # 2. 从旧分类中移除题目
        for category in current_categories:
            if category in self.data["category_to_problems"]:
                # 确保题目存在于该分类的列表中
                if problem_id in self.data["category_to_problems"][category]:
                    self.data["category_to_problems"][category].remove(problem_id)
                    # 如果分类为空，删除该分类条目
                    if not self.data["category_to_problems"][category]:
                        del self.data["category_to_problems"][category]

        # 3. 更新到新分类
        if new_categories:
            # 更新反向索引（题目→分类）
            self.data["problem_to_categories"][problem_id_str] = new_categories
            # 更新正向索引（分类→题目）
            for category in new_categories:
                if category not in self.data["category_to_problems"]:
                    self.data["category_to_problems"][category] = []
                if problem_id not in self.data["category_to_problems"][category]:
                    self.data["category_to_problems"][category].append(problem_id)
        else:
            # 如果没有新分类，删除反向索引条目
            if problem_id_str in self.data["problem_to_categories"]:
                del self.data["problem_to_categories"][problem_id_str]

        # 4. 保存数据
        self._save_data()
    
    def calculate_tag_scores(self, items: list[Item]) -> dict[str, float]:
        """计算每个tag的得分（0-10）基于平均耗时和最近更新时间"""
        tag_scores = {}
        for tag, problem_ids in self.data["category_to_problems"].items():
            # 获取该tag下所有题目对象
            tag_items = [item for item in items if item.leetcode_id in problem_ids]
            if not tag_items:
                continue
            
            # 计算平均耗时（秒）
            avg_time = sum(item.time_cost_in_seconds() for item in tag_items) / len(tag_items)
            # 计算最旧更新时间（距离今天的天数）
            oldest_date = min(item.date for item in tag_items)
            days_old = (datetime.date.today() - oldest_date).days
            
            # 标准化到0-10分（耗时占比50%，时间占比50%）
            time_score = min(avg_time / 1800 * 10, 10)  # 假设30分钟为满分
            date_score = min(days_old / 30 * 10, 10)    # 假设30天未刷为满分
            total_score = (time_score + date_score) / 2
            tag_scores[tag] = round(total_score, 2)
        
        return tag_scores
    
    def calculate_tag_review_scores(self, items: list[Item]) -> dict[str, float]:
        """计算每个tag的复习得分（基于该分类下所有题目的平均复习得分）"""
        tag_scores = {}
        for tag, problem_ids in self.data["category_to_problems"].items():
            # 获取该tag下所有题目对象
            tag_items = [item for item in items if item.leetcode_id in problem_ids]
            if not tag_items:
                continue
            
            # 计算平均复习得分
            avg_score = sum(item.calculate_review_score() for item in tag_items) / len(tag_items)
            tag_scores[tag] = round(avg_score, 2)
        
        return tag_scores
    
    def print_items_table(self, items, title):
        """打印题目列表的表格视图"""
        init()
        
        if not items:
            print(Fore.YELLOW + f"没有{title}题目" + Style.RESET_ALL)
            return
        
        # 表头
        headers = ["题号", "日期", "难度", "耗时", "次数", "类型", "链接"]
        col_widths = [8, 10, 10, 10, 10, 10, 46]
        r_col_widths = [10, 12, 12, 12, 12, 12, 48]
        
        # 表格标题
        print("\n" + Fore.YELLOW + "=" * 100)
        print(f"{title:^100}")
        print("=" * 100 + Style.RESET_ALL)
        
        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
        
        # 打印数据行
        for item in items:
            # 准备数据
            data = [
                str(item.leetcode_id),
                item.date.strftime('%Y-%m-%d'),
                self._get_difficulty_symbol(item.difficulty),
                item.time_cost,
                str(item.times),
                item.tag[:10],
                item.leetcode_url
            ]
            
            # 打印行
            row = "│".join([d.center(w) for d, w in zip(data, r_col_widths)])
            print("│" + row + "│")
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")
        print(Fore.CYAN + f"共 {len(items)} 道题目" + Style.RESET_ALL)

    def print_recommended_problems(self, items):
        """打印推荐题目的精美表格"""
        # from colorama import init, Fore, Style
        init()
        
        if not items:
            print(Fore.YELLOW + "没有推荐题目" + Style.RESET_ALL)
            return
        
        # 表头
        headers = ["题号", "日期", "难度", "耗时", "次数", "类型", "推荐理由", "链接"]
        col_widths = [6, 10, 10, 10, 10, 10, 15, 35]
        r_col_widths = [8, 10, 12, 12, 12, 12, 12, 15, 35]

        # 表格标题
        print("\n" + Fore.YELLOW + "=" * 100)
        print(f"{'推荐题目':^100}")
        print("=" * 100 + Style.RESET_ALL)
        
        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
        
        # 打印数据行
        for item in items:
            # 生成推荐理由
            days_old = (datetime.date.today() - item.date).days
            if days_old > 30:
                reason = "长期未复习"
            elif item.time_cost_in_seconds() > 1200:  # 20分钟
                reason = "耗时过长"
            elif item.times == 1:
                reason = "首次练习"
            else:
                reason = "需要巩固"
            
            # 准备数据
            data = [
                str(item.leetcode_id),
                item.date.strftime('%Y-%m-%d'),
                self._get_difficulty_symbol(item.difficulty),
                item.time_cost,
                str(item.times),
                item.tag[:10],
                reason,
                item.leetcode_url[:33] + "..." if len(item.leetcode_url) > 33 else item.leetcode_url
            ]
            
            # 打印行
            row = "│".join([d.ljust(w) for d, w in zip(data, r_col_widths)])
            print("│" + row + "│")
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")

    def print_tag_scores_table(self, tag_scores, items):
        """打印分类分数表的精美表格"""
        # from colorama import init, Fore, Style
        init()
        
        if not tag_scores:
            print(Fore.YELLOW + "没有分类信息" + Style.RESET_ALL)
            return
        
        # 表头
        headers = ["分类", "平均耗时", "最旧题目日期", "题目数量", "综合得分", "状态"]
        col_widths = [20, 12, 14, 10, 10, 15]
        r_col_widths = [22, 16, 20, 14, 14, 17]

        
        # 表格标题
        print("\n" + Fore.YELLOW + "=" * 100)
        print(f"{'分类分数汇总':^85}")
        print("=" * 100 + Style.RESET_ALL)
        
        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths)])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in r_col_widths]) + "┤")
        
        # 按分数排序
        sorted_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 打印数据行
        for tag, score in sorted_tags:
            # 获取该分类的详细数据
            problem_ids = self.data["category_to_problems"][tag]
            tag_items = [item for item in items if item.leetcode_id in problem_ids]
            
            # 计算统计数据
            avg_time = sum(i.time_cost_in_seconds() for i in tag_items)/len(tag_items)
            oldest_date = min(i.date for i in tag_items).strftime("%Y-%m-%d")
            nums = f"{len(tag_items)}"
            
            # 格式转换
            avg_time_str = f"{int(avg_time//60)}:{int(avg_time%60):02d}"
            
            # 确定状态和颜色
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
                avg_time_str,
                oldest_date,
                nums,
                f"{score:.2f}",
                status
            ]
            
            # 打印行
            row = "│".join([d.center(w) for d, w in zip(data, r_col_widths)])
            print("│" + color + row + Style.RESET_ALL + "│")
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in r_col_widths]) + "┘")
        
        # 分数说明
        print(Fore.CYAN + "分数说明: " + 
            Fore.RED + ">6.0 (urgent 急需复习)  " + 
            Fore.YELLOW + "4.0-6.0 (suggest 建议复习)  " + 
            Fore.GREEN + "<4.0 (you're good 已掌握)" + 
            Style.RESET_ALL)

    def _get_difficulty_symbol(self, difficulty):
        """获取难度符号"""
        diff = difficulty.lower()
        if diff == "easy":
            return Fore.GREEN + "★" + Fore.RESET
        elif diff == "medium":
            return Fore.YELLOW + "★★" + Fore.RESET
        elif diff == "hard":
            return Fore.RED + "★★★" + Fore.RESET
        else:
            return difficulty
