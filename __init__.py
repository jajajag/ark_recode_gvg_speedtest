from hoshino import Service, priv
from hoshino.typing import CQEvent
from .speed import compute_speed_async, overtake_prob

sv_name = '团战测速'
sv_help = (
    '[团战测速] 星陨计划团战测速，示例：\n'
    '团战测速\n'
    '水马 1 56 135\n'
    '水琴 1 70 170\n'
    '水拳 4 58 131\n'
    '朱茵 1 101\n'
    '盖儿 1 84\n'
    '（没输入速度的为敌方，101表示到达终点）\n'
    '[超车] 计算角色A超车角色B的概率，示例：\n'
    '超车 245 240'
).strip()

sv = Service(name=sv_name, use_priv=priv.NORMAL, manage_priv=priv.ADMIN,
             visible=True, enable_on_default=True, bundle='娱乐', help_=sv_help)

def _parse_tokens(text: str):
    # Initialization
    tokens = text.strip().split()
    allies, enemies, character = [], [], []
    pos = 0

    for token in tokens:
        # Character name, or action gauges
        if pos < 3:
            if pos == 0: character.append(token)
            else: character.append(int(token))
            pos += 1
        else:
            # Speed
            if token.isdigit():
                character.append(int(token))
                allies.append(tuple(character))
                character = []
                pos = 0
            # Next character's name
            else:
                enemies.append(tuple(character))
                character = [token]
                pos = 1
    # Put the last charactor into enmies if it has three elements
    if character: enemies.append(tuple(character))

    # Change the action gauge to 100 if not a single >100 value is specified
    end_gauge = [x[2] for x in allies + enemies]
    if not any(v > 100 for v in end_gauge) and end_gauge.count(100) == 1:
        for lst in (allies, enemies):
            for i, item in enumerate(lst):
                if item[2] == 100:
                    lst[i] = item[:2] + (101,) + item[3:]

    return allies, enemies

@sv.on_prefix('团战测速')
async def speed_test(bot, ev: CQEvent):
    # Extract plain text after 团战测速
    raw = ev.message.extract_plain_text()
    # Output instructions if no text is provided
    if not raw.strip():
        await bot.finish(ev, '\n' + sv_help, at_sender=True)
    # Parse the input tokens
    try:
        allies, enemies = _parse_tokens(raw)
    except Exception as e:
        await bot.finish(ev, 
            f'输入错误，请检查输入，或发团战测速查看详细用法', at_sender=True)
    # Compute the speeds of enemies
    try:
        ret = await compute_speed_async(allies=allies, enemies=enemies, 
                                        N_sample=int(1e6))

        lines = []
        for (enemy, enemy_min, enemy_max, mean, med, ally_min) in ret:
            lines.append(
                f'\n- {enemy}：速度区间[{enemy_min:.1f}, {enemy_max:.1f}]，'
                f'MC均值{mean:.1f}，中位数{med:.1f}，稳定超车速度{ally_min:.1f}'
            )
        msg = ''.join(lines)
        await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, f'计算错误，请检查输入数值是否正确', at_sender=True)

#@sv.on_rex(r'^超车\s*(\d+)\s+(\d+)$')
@sv.on_rex(r'^超车\s*(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)$')
async def overtake(bot, ev: CQEvent):
    # Match input numbers
    match = ev['match']
    v1 = float(match.group(1))
    v2 = float(match.group(2))
    try:
        # Calculate the overtaking probability
        prob = overtake_prob(v1, v2)
        percent = round(prob * 100, 1)
        await bot.send(ev,
            f'\n角色A超车角色B的概率为{percent}%', at_sender=True)
    except Exception as e:
        await bot.send(ev, f'计算错误，请检查输入数值是否正确', at_sender=True)
