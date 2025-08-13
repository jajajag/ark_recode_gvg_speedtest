import asyncio
import numpy as np

# 行动条输入为100.5时，说明跑到行动条底
def compute_speed(
        allies: list[tuple[str, float, float, float]],
        enemies: list[tuple[str, float, float]],
        N_sample: int = int(1e6)):
    '''
    allies: list of tuples (name, start_gauge, end_gauge, speed)
    enemy: tuple (name, start_gauge, end_gauge)
    '''
    ally_start_gauge, ally_end_gauge = [], []
    enemy_start_gauge, enemy_end_gauge = [], []

    for i in range(len(allies)):
        # 我方乱速范围
        ally_start_gauge_lower = max(allies[i][1] - 0.5, 0)
        ally_start_gauge_upper = min(allies[i][1] + 0.5, 5)
        ally_end_gauge_lower = min(allies[i][2] - 0.5, 100)
        ally_end_gauge_upper = min(allies[i][2] + 0.5, 100)
        # Sample我方行动条
        ally_start_gauge.append(np.random.uniform(
            ally_start_gauge_lower, ally_start_gauge_upper, N_sample))
        ally_end_gauge.append(np.random.uniform(
            ally_end_gauge_lower, ally_end_gauge_upper, N_sample))

    # Sample敌方行动条
    for i in range(len(enemies)):
        # 敌方乱速范围
        enemy_start_gauge_lower = max(enemies[i][1] - 0.5, 0)
        enemy_start_gauge_upper = min(enemies[i][1] + 0.5, 5)
        enemy_end_gauge_lower = min(enemies[i][2] - 0.5, 100)
        enemy_end_gauge_upper = min(enemies[i][2] + 0.5, 100)
        # Sample敌方行动条
        enemy_start_gauge.append(np.random.uniform(
            enemy_start_gauge_lower, enemy_start_gauge_upper, N_sample))
        enemy_end_gauge.append(np.random.uniform(
            enemy_end_gauge_lower, enemy_end_gauge_upper, N_sample))

    enemy_info = []
    for i in range(len(enemies)):
        # 敌方速度范围
        enemy_min_speed, enemy_max_speed = 0, float('inf')
        enemy_speed_cat = []

        for j in range(len(allies)):
            # 计算敌方速度，存入对应位置
            enemy_speed = (enemy_end_gauge[i] - enemy_start_gauge[i]) \
                    / (ally_end_gauge[j] - ally_start_gauge[j]) * allies[j][3]
            # 计算敌方的速度上下界（改用Monte Carlo）
            #min_speed = ally_speed * (enemy_end_lower - enemy_start_upper) \
            #        / (ally_end_upper - ally_start_lower)
            #max_speed = ally_speed * (enemy_end_upper - enemy_start_lower) \
            #        / (ally_end_lower - ally_start_upper)
            enemy_min_speed = max(enemy_min_speed, np.min(enemy_speed))
            enemy_max_speed = min(enemy_max_speed, np.max(enemy_speed))
            enemy_speed_cat.append(enemy_speed)

        # 过滤不可能的速度
        enemy_speed_cat = np.concatenate(enemy_speed_cat)
        enemy_speed_cat = enemy_speed_cat[np.where(
            (enemy_speed_cat <= enemy_max_speed) \
            & (enemy_speed_cat >= enemy_min_speed))]

        # 计算MC均值和中位数
        mean = np.mean(enemy_speed_cat)
        med = np.median(enemy_speed_cat)
        # 计算我方稳定超车的速度
        ally_min_speed = enemy_max_speed / 0.95
        
        enemy_info.append((enemies[i][0], enemy_min_speed, enemy_max_speed,
                           mean, med, ally_min_speed))

    return enemy_info

async def compute_speed_async(*args, **kwargs):
    return await asyncio.to_thread(compute_speed, *args, **kwargs)

ally_1 = ('水马', 1, 56, 135)
ally_2 = ('水琴', 1, 70, 170)
ally_3 = ('水拳', 4, 58, 131)
enemy_1 = ('朱茵', 1, 101)
enemy_2 = ('盖儿', 1, 84)
print(compute_speed([ally_1, ally_2, ally_3], [enemy_1, enemy_2], N_sample=10**6))
