# handlers/player_handler.py
from astrbot.api.event import AstrMessageEvent
from ..data import data_manager
from ..game import xiuxian_logic
from ..config_manager import config
from ..data.models import Player

__all__ = ["PlayerHandler"]

class PlayerHandler:
    def __init__(self, plugin):
        self.plugin = plugin

    async def handle_start_xiuxian(self, event: AstrMessageEvent):
        user_id = event.get_sender_id()
        if await data_manager.get_player_by_id(user_id):
            yield event.plain_result("道友，你已踏入仙途，无需重复此举。")
            return

        new_player = xiuxian_logic.generate_new_player_stats(user_id)
        await data_manager.create_player(new_player)
        reply_msg = (
            f"恭喜道友 {event.get_sender_name()} 踏上仙途！\n"
            f"初始灵根：【{new_player.spiritual_root}】\n"
            f"启动资金：【{new_player.gold}】灵石\n"
            f"发送「{config.CMD_PLAYER_INFO}」查看状态，「{config.CMD_CHECK_IN}」领取福利！"
        )
        yield event.plain_result(reply_msg)

    async def handle_player_info(self, event: AstrMessageEvent, player: Player):
        sect_info = f"宗门：{player.sect_name if player.sect_name else '逍遥散人'}"
        reply_msg = (
            f"--- 道友 {event.get_sender_name()} 的信息 ---\n"
            f"境界：{player.level}\n"
            f"灵根：{player.spiritual_root}\n"
            f"修为：{player.experience}\n"
            f"灵石：{player.gold}\n"
            f"{sect_info}\n"
            f"状态：{player.state}\n"
            "--- 战斗属性 ---\n"
            f"生命: {player.hp}/{player.max_hp}\n"
            f"攻击: {player.attack}\n"
            f"防御: {player.defense}\n"
            f"暴击: {player.crit_chance:.1%}\n"
            f"爆伤: {player.crit_damage:.0%}\n"
            f"闪避: {player.dodge_chance:.1%}\n"
            f"--------------------------"
        )
        yield event.plain_result(reply_msg)

    async def handle_check_in(self, event: AstrMessageEvent, player: Player):
        success, msg, updated_player = xiuxian_logic.handle_check_in(player)
        if success:
            await data_manager.update_player(updated_player)
        yield event.plain_result(msg)

    async def handle_start_cultivation(self, event: AstrMessageEvent, player: Player):
        success, msg, updated_player = xiuxian_logic.handle_start_cultivation(player)
        if success:
            await data_manager.update_player(updated_player)
        yield event.plain_result(msg)

    async def handle_end_cultivation(self, event: AstrMessageEvent, player: Player):
        success, msg, updated_player = xiuxian_logic.handle_end_cultivation(player)
        if success:
            await data_manager.update_player(updated_player)
        yield event.plain_result(msg)

    async def handle_breakthrough(self, event: AstrMessageEvent, player: Player):
        if player.state != "空闲":
            yield event.plain_result(f"道友当前正在「{player.state}」中，无法尝试突破。")
            return
        success, msg, updated_player = xiuxian_logic.handle_breakthrough(player)
        await data_manager.update_player(updated_player)
        yield event.plain_result(msg)
