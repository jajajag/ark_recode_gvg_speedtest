from hoshino import Service, priv
from hoshino.typing import CQEvent
from .speed import compute_speed_async

sv_name = '团战测速'
sv_help = (
    '星陨计划团战测速（没输入速度的为敌方）\n'
    '每行格式：角色 乱速 终点行动条 [速度]\n'
    '示例：\n'
    '团战测速\n'
    '我方A 0 80 180\n'
    '我方B 5 90 165\n'
    '敌人A 0 100\n'
    '敌人B 0 95\n'
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

    return allies, enemies

@sv.on_prefix('团战测速')
async def speed_test(bot, ev: CQEvent):
    # Extract plain text after 团战测速
    raw = ev.message.extract_plain_text()
    # Output instructions if no text is provided
    if not raw.strip():
        await bot.finish(ev, sv_help, at_sender=True)
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
                f'- {enemy}：敌速区间[{enemy_min:.1f}, {enemy_max:.1f}]，'
                f'均值{mean:.1f}，中位数{med:.1f}，稳定超车速度{ally_min:.1f}'
            )
        msg = '\n'.join(lines)
        await bot.send(ev, msg, at_sender=True)
    except Exception as e:
        await bot.send(ev, f'计算错误，请检查输入数值是否正确', at_sender=True)
