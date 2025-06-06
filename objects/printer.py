from colorama import init, Fore, Back, Style
import datetime
import math
# from const import HEADER_TO_WIDTHS, HEADER_TO_ROW_WIDTHS
import const.const as const

class ColorPrinter:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ColorPrinter, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            init()  # 初始化colorama
            self._initialized = True
    
    def get_difficulty_symbol(self, difficulty):
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
    
    def print_menu(self, title, options):
        """打印菜单"""
        print("\n" + Back.BLUE + Fore.WHITE + f" {title} ".center(80, "=") + Style.RESET_ALL)
        for i, option in enumerate(options, 1):
            print(Fore.CYAN + f"{i}. {option}" + Style.RESET_ALL)
        print("=" * 80)
    
    def print_table(self, items, headers, title="", show_count=False, color_fn=None):
        """通用表格打印方法"""
        if not items:
            print(Fore.YELLOW + f"没有{title}数据" + Style.RESET_ALL)
            return
        
        # 表格标题
        if title:
            print("\n" + Fore.YELLOW + "=" * 100)
            print(f"{title:^100}")
            print("=" * 100 + Style.RESET_ALL)
        
        # 确定列宽
        col_widths = [[const.HEADER_TO_WIDTHS[h] for h in headers],
                      [const.HEADER_TO_ROW_WIDTHS[h] for h in headers]]

        # 打印表头
        header_line = "│".join([h.center(w) for h, w in zip(headers, col_widths[0])])
        print("│" + header_line + "│")
        print("├" + "┼".join(["─" * w for w in col_widths[1]]) + "┤")
        
        # 打印数据行
        for item in items:
            # 准备数据
            if isinstance(item, dict):
                data = [str(item.get(h, ""))[:w] for h, w in zip(headers, col_widths)]
            else:
                # 假设是Item对象
                data = [
                    str(item.leetcode_id),
                    item.date.strftime('%Y-%m-%d'),
                    self.get_difficulty_symbol(item.difficulty),
                    item.time_cost,
                    str(item.times),
                    item.tag[:10],
                    item.leetcode_url
                ]
            
            # 应用颜色函数（如果有）
            row_color = color_fn(item) if color_fn else ""
            
            # 打印行
            row = "│".join([d.ljust(w) for d, w in zip(data, col_widths[1])])
            print("│" + row_color + row + (Style.RESET_ALL if row_color else "") + "│")
        
        # 表格底部
        print("└" + "┴".join(["─" * w for w in col_widths[1]]) + "┘")
        
        # 显示总数（如果需要）
        if show_count:
            print(Fore.CYAN + f"共 {len(items)} 条记录" + Style.RESET_ALL)
    
    def print_items(self, items, title="题目列表"):
        """打印题目列表"""
        headers = ["题号", "日期", "难度", "耗时", "次数", "类型", "链接"]
        self.print_table(items, headers, title, show_count=True)
    