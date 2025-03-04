# xiaobai
leetcode helper

## 背景：
- 想设计一个刷题的反馈机器，根据每天积累的题目信息来计划安排当天需要刷的题目

## 目标：

- 需要将每道题都刷到懂，在**3分钟**只内能相处具体思路并在**10分钟**内能完成编程

## 详细设计：

- 将每个题目根据日期，题目号，难易程度来存储（后续也许会更多标签）
- user每次执行代码后，程序会根据存储的题目列表来进行计算，反馈给用户题目来练习
- 第一版需要根据日期号来执行，根据时间和难易度来排序，并返回对应的题目列表
- 第二版需要家里题目类型的考虑，需要有关联性
- 需求：

| 需求 | 完成日期 |
| --- | --- |
| 题目与题目之间需关联性 | 2.26 |
|  |  |

### 题目列表设计

难易由小到大排列，1-3，数值越大越难

| 日期 | 题目号 | 难易 | 耗时 | 刷题次数 | 标签 |
| --- | --- | --- | --- | --- | --- |
| 2025-2-21 | xxx | 2 | 1:34 | 1 |  |
| 2025-1-31 | xx | 1 | 5:34 | 2 |  |
| 2025-2-5 | xxx | 3 | 30:24 | 1 |  |

### 题目关联性设计

题目与题目之间根据最明显的特征进行关联，要是每天刷题数量允许，一天可安排所有关联的题目

例如：1、2、3、4都是关于双指针的题目，只要其中任何一个按排序安排到当天题目列表中，只要题目数量允许，直接安排