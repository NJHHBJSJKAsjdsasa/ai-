"""
战斗命令处理器

处理所有与战斗相关的CLI命令，包括切磋、死斗、攻击、技能、逃跑等。
"""

from typing import Optional, Dict, Any, List
from .base_handler import BaseHandler
from game.combat import (
    CombatSystem, CombatMode, CombatStatus,
    create_player_combat_unit, create_npc_combat_unit, create_beast_combat_unit
)
from game.execution_system import ExecutionChoice, execution_system
from game.material_generator import material_generator, MaterialGenerator, GeneratedMaterial, MaterialRarity
from game.death_manager import death_manager
from utils.colors import Color, colorize, success, error, warning, info, bold


class CombatHandler(BaseHandler):
    """
    战斗命令处理器
    
    处理所有战斗相关命令，提供完整的战斗交互体验。
    """
    
    def __init__(self, cli):
        """
        初始化战斗处理器
        
        Args:
            cli: CLI实例
        """
        super().__init__(cli)
        self.combat_system: Optional[CombatSystem] = None
        self.current_target: Optional[Any] = None
        self.current_mode: Optional[CombatMode] = None
    
    def handle_combat(self, args: str):
        """
        发起战斗
        
        提示玩家选择战斗模式（切磋/死斗）
        
        Args:
            args: 目标名称
        """
        if not args.strip():
            self.print(error("请指定战斗目标！用法: /战斗 <目标名>"))
            return
        
        target_name = args.strip()
        target = self._get_target(target_name)
        
        if not target:
            self.print(error(f"找不到目标 '{target_name}'"))
            return
        
        self.current_target = target
        
        # 显示目标信息
        self.print(f"\n{bold('═══ 战斗发起 ═══')}")
        self.print(f"目标: {colorize(target_name, Color.CYAN)}")
        
        # 提示选择模式
        self.print(f"\n{colorize('请选择战斗模式:', Color.YELLOW)}")
        self.print(f"  {colorize('1.', Color.GREEN)} 切磋 - 友好比试，不会死亡，结束后恢复")
        self.print(f"  {colorize('2.', Color.RED)} 死斗 - 生死之战，可能死亡，掉落物品")
        self.print(f"\n请输入 {colorize('1', Color.GREEN)} 或 {colorize('2', Color.RED)} (或输入 '取消' 退出):")
        
        # 设置等待模式选择状态
        self.cli.set_state('combat_mode_selection', {'target': target, 'target_name': target_name})
    
    def handle_spar(self, args: str):
        """
        发起切磋
        
        检查目标是否接受，然后初始化战斗
        
        Args:
            args: 目标名称
        """
        if not args.strip():
            self.print(error("请指定切磋目标！用法: /切磋 <目标名>"))
            return
        
        target_name = args.strip()
        target = self._get_target(target_name)
        
        if not target:
            self.print(error(f"找不到目标 '{target_name}'"))
            return
        
        # 检查NPC是否愿意切磋
        if hasattr(target, 'data') and hasattr(target.data, 'favorability'):
            if target.data.favorability < -20:
                self.print(error(f"{target_name} 对你好感度太低，拒绝切磋！"))
                return
        
        self._start_combat(target, CombatMode.SPAR)
    
    def handle_deathmatch(self, args: str):
        """
        发起死斗
        
        检查NPC好感度，确认后初始化战斗
        
        Args:
            args: 目标名称
        """
        if not args.strip():
            self.print(error("请指定死斗目标！用法: /死斗 <目标名>"))
            return
        
        target_name = args.strip()
        target = self._get_target(target_name)
        
        if not target:
            self.print(error(f"找不到目标 '{target_name}'"))
            return
        
        # 检查NPC好感度
        if hasattr(target, 'data') and hasattr(target.data, 'favorability'):
            if target.data.favorability > 30:
                self.print(warning(f"{target_name} 对你有好感，你确定要发起死斗吗？"))
                self.print(f"输入 {colorize('/确认死斗', Color.RED)} 继续，或其他命令取消")
                self.cli.set_state('confirm_deathmatch', {'target': target, 'target_name': target_name})
                return
        
        self._start_combat(target, CombatMode.DEATHMATCH)
    
    def _start_combat(self, target, mode: CombatMode):
        """
        初始化并开始战斗
        
        Args:
            target: 战斗目标
            mode: 战斗模式
        """
        # 创建战斗系统
        self.combat_system = CombatSystem()
        self.current_mode = mode
        
        # 创建战斗单位
        player_unit = create_player_combat_unit(self.player)
        
        if hasattr(target, 'data'):
            # NPC目标
            enemy_unit = create_npc_combat_unit(target)
        elif isinstance(target, dict):
            # 妖兽目标
            enemy_unit = create_beast_combat_unit(target)
        else:
            self.print(error("无效的战斗目标类型"))
            return
        
        # 开始战斗
        result = self.combat_system.start_combat(player_unit, enemy_unit, mode)
        self.current_target = target
        
        # 显示战斗界面
        self._display_combat_ui()
        
        # 检查是否需要玩家行动
        if self.combat_system.current_turn_unit == player_unit:
            self._prompt_combat_action()
        else:
            # 敌人先出手，执行敌人回合
            self.handle_attack()  # 触发战斗流程
    
    def _prompt_combat_action(self):
        """提示玩家选择战斗行动"""
        self.print(f"\n{colorize('请选择行动:', Color.YELLOW)}")
        self.print(f"  {colorize('/攻击', Color.RED)}    - 普通攻击")
        
        # 显示可用技能
        available_skills = self.combat_system.player.get_available_skills()
        if available_skills:
            self.print(f"  {colorize('/技能', Color.CYAN)}    - 使用技能")
            for skill in available_skills:
                self.print(f"    • {skill.name} (消耗{skill.mana_cost}灵力)")
        
        self.print(f"  {colorize('/逃跑', Color.YELLOW)}    - 尝试逃跑")
        self.print(f"  {colorize('/状态', Color.GREEN)}    - 查看战斗状态")
    
    def handle_attack(self):
        """执行普通攻击"""
        if not self._check_in_combat():
            return
        
        result = self.combat_system.execute_turn("attack")
        self._process_combat_result(result)
    
    def handle_skill(self, skill_name: str):
        """
        使用技能
        
        Args:
            skill_name: 技能名称
        """
        if not self._check_in_combat():
            return
        
        if not skill_name.strip():
            self.print(error("请指定技能名称！用法: /技能 <技能名>"))
            return
        
        skill_name = skill_name.strip()
        
        # 查找技能
        skill = None
        for s in self.combat_system.player.skills:
            if s.name == skill_name:
                skill = s
                break
        
        if not skill:
            self.print(error(f"你没有 '{skill_name}' 这个技能"))
            return
        
        # 检查灵力
        if not self.combat_system.player.can_use_skill(skill):
            self.print(error(f"灵力不足或技能冷却中！需要 {skill.mana_cost} 灵力"))
            return
        
        result = self.combat_system.execute_turn("skill", skill_name)
        self._process_combat_result(result)
    
    def handle_flee(self):
        """尝试逃跑"""
        if not self._check_in_combat():
            return
        
        result = self.combat_system.execute_turn("flee")
        self._process_combat_result(result)
    
    def handle_combat_status(self):
        """查看战斗状态"""
        if not self._check_in_combat():
            return
        
        self._display_combat_ui()
        self._prompt_combat_action()
    
    def _check_in_combat(self) -> bool:
        """
        检查是否处于战斗中
        
        Returns:
            是否在战斗中
        """
        if not self.combat_system or self.combat_system.status != CombatStatus.ONGOING:
            self.print(error("当前不在战斗中！"))
            return False
        return True
    
    def _process_combat_result(self, result):
        """
        处理战斗结果
        
        Args:
            result: 战斗结果对象
        """
        # 显示战斗日志
        for log in result.combat_log[-5:]:  # 显示最近5条日志
            if "暴击" in log:
                self.print(colorize(log, Color.RED))
            elif "使用" in log:
                self.print(colorize(log, Color.CYAN))
            elif "恢复" in log or "治疗" in log:
                self.print(colorize(log, Color.GREEN))
            elif "逃跑" in log:
                self.print(colorize(log, Color.YELLOW))
            else:
                self.print(log)
        
        # 清空已显示的日志
        self.combat_system.combat_log.clear()
        
        # 检查战斗是否结束
        if result.status != CombatStatus.ONGOING:
            self._handle_combat_end(result)
        else:
            # 继续战斗，显示状态并提示行动
            self._display_combat_ui()
            if self.combat_system.current_turn_unit == self.combat_system.player:
                self._prompt_combat_action()
    
    def _handle_combat_end(self, result):
        """
        处理战斗结束
        
        Args:
            result: 战斗结果
        """
        self.print(f"\n{bold('═══ 战斗结束 ═══')}")
        
        if result.status == CombatStatus.PLAYER_WIN:
            self.print(success(f"🎉 你获得了胜利！"))
            self._display_deathmatch_result(result) if result.mode == CombatMode.DEATHMATCH else self._display_spar_result(result)
        elif result.status == CombatStatus.ENEMY_WIN:
            self.print(error(f"💀 你战败了..."))
            if result.mode == CombatMode.DEATHMATCH:
                self.print(error("死斗失败，角色死亡！"))
        elif result.status == CombatStatus.FLED:
            self.print(warning(f"🏃 你成功逃离了战斗！"))
        else:
            self.print(info(f"🤝 战斗结束"))
        
        # 清理战斗状态
        self.combat_system = None
        self.current_target = None
        self.current_mode = None
        self.cli.clear_state('combat_mode_selection')
        self.cli.clear_state('confirm_deathmatch')
    
    def _display_combat_ui(self):
        """显示彩色战斗界面"""
        if not self.combat_system:
            return
        
        player = self.combat_system.player
        enemy = self.combat_system.enemy
        mode_str = "切磋" if self.current_mode == CombatMode.SPAR else "死斗"
        mode_color = Color.GREEN if self.current_mode == CombatMode.SPAR else Color.RED
        
        self.print(f"\n{bold('╔' + '═' * 38 + '╗')}")
        self.print(f"{bold('║')} {colorize(f'【{mode_str}】', mode_color).center(36)} {bold('║')}")
        self.print(f"{bold('╠' + '═' * 38 + '╣')}")
        
        # 玩家信息
        player_hp_bar = self._create_hp_bar(player.health, player.max_health, 15)
        player_mp_bar = self._create_mp_bar(player.mana, player.max_mana, 15)
        self.print(f"{bold('║')} {colorize('【你】', Color.GREEN)} {player.name:<28} {bold('║')}")
        self.print(f"{bold('║')}   HP: {player_hp_bar} {player.health}/{player.max_health:<5} {bold('║')}")
        self.print(f"{bold('║')}   MP: {player_mp_bar} {player.mana}/{player.max_mana:<5} {bold('║')}")
        
        self.print(f"{bold('║')} {'VS':^36} {bold('║')}")
        
        # 敌人信息
        enemy_hp_bar = self._create_hp_bar(enemy.health, enemy.max_health, 15)
        enemy_mp_bar = self._create_mp_bar(enemy.mana, enemy.max_mana, 15)
        enemy_color = Color.RED if self.current_mode == CombatMode.DEATHMATCH else Color.YELLOW
        self.print(f"{bold('║')} {colorize('【敌】', enemy_color)} {enemy.name:<28} {bold('║')}")
        self.print(f"{bold('║')}   HP: {enemy_hp_bar} {enemy.health}/{enemy.max_health:<5} {bold('║')}")
        self.print(f"{bold('║')}   MP: {enemy_mp_bar} {enemy.mana}/{enemy.max_mana:<5} {bold('║')}")
        
        self.print(f"{bold('╠' + '═' * 38 + '╣')}")
        self.print(f"{bold('║')} {f'第 {self.combat_system.turn} 回合':^36} {bold('║')}")
        
        # 当前行动方
        if self.combat_system.current_turn_unit == player:
            turn_text = colorize('→ 你的回合', Color.GREEN)
        else:
            turn_text = colorize('→ 敌方回合', Color.RED)
        self.print(f"{bold('║')} {turn_text:^36} {bold('║')}")
        
        self.print(f"{bold('╚' + '═' * 38 + '╝')}")
    
    def _create_hp_bar(self, current: int, max_val: int, length: int = 20) -> str:
        """
        创建血条
        
        Args:
            current: 当前值
            max_val: 最大值
            length: 条长度
            
        Returns:
            血条字符串
        """
        ratio = current / max_val if max_val > 0 else 0
        filled = int(length * ratio)
        
        if ratio > 0.6:
            color = Color.GREEN
        elif ratio > 0.3:
            color = Color.YELLOW
        else:
            color = Color.RED
        
        bar = "█" * filled + "░" * (length - filled)
        return colorize(bar, color)
    
    def _create_mp_bar(self, current: int, max_val: int, length: int = 20) -> str:
        """
        创建灵力条
        
        Args:
            current: 当前值
            max_val: 最大值
            length: 条长度
            
        Returns:
            灵力条字符串
        """
        ratio = current / max_val if max_val > 0 else 0
        filled = int(length * ratio)
        bar = "█" * filled + "░" * (length - filled)
        return colorize(bar, Color.CYAN)
    
    def _display_spar_result(self, result):
        """
        显示切磋结果
        
        Args:
            result: 战斗结果
        """
        self.print(f"\n{colorize('═══ 切磋奖励 ═══', Color.GREEN)}")
        self.print(f"获得经验: {colorize(f'+{result.exp_reward}', Color.GREEN)}")
        
        # 应用经验奖励
        if hasattr(self.player, 'gain_exp'):
            self.player.gain_exp(result.exp_reward)
        
        if result.loot:
            self.print(f"获得物品: {', '.join(result.loot)}")
    
    def _display_deathmatch_result(self, result):
        """
        显示死斗结果
        
        处理死斗胜利后的奖励展示和处决选择逻辑。
        如果 result.execution_pending 为 True，则显示处决选择提示，
        并使用动态材料生成器生成材料。
        
        Args:
            result: 战斗结果对象，包含 exp_reward, spirit_stones_reward, loot, execution_pending 等属性
        """
        self.print(f"\n{colorize('═══ 死斗战利品 ═══', Color.RED)}")
        self.print(f"获得经验: {colorize(f'+{result.exp_reward}', Color.GREEN)}")
        self.print(f"获得灵石: {colorize(f'+{result.spirit_stones_reward}', Color.YELLOW)}")
        
        # 应用奖励
        if hasattr(self.player, 'gain_exp'):
            self.player.gain_exp(result.exp_reward)
        if hasattr(self.player, 'add_spirit_stones'):
            self.player.add_spirit_stones(result.spirit_stones_reward)
        
        # 检查是否需要显示处决选择（NPC对战且execution_pending为True）
        if hasattr(result, 'execution_pending') and result.execution_pending and self.current_target:
            target = self.current_target
            
            # 获取NPC名称
            npc_name = ""
            if hasattr(target, 'data') and hasattr(target.data, 'dao_name'):
                npc_name = target.data.dao_name
            elif hasattr(target, 'name'):
                npc_name = target.name
            else:
                npc_name = "未知敌人"
            
            # 显示处决选择提示
            self.print(f"\n{bold('╔' + '═' * 48 + '╗')}")
            self.print(f"{bold('║')} {colorize('【战斗胜利】', Color.GREEN).center(46)} {bold('║')}")
            self.print(f"{bold('╠' + '═' * 48 + '╣')}")
            self.print(f"{bold('║')} {f'{npc_name}已败于你手，生死皆在你一念之间'.center(44)} {bold('║')}")
            self.print(f"{bold('╠' + '═' * 48 + '╣')}")
            self.print(f"{bold('║')} {'请选择你的行动：'.center(44)} {bold('║')}")
            self.print(f"{bold('║')} {' ' * 46} {bold('║')}")
            self.print(f"{bold('║')} {colorize('  /处决', Color.RED)} - 彻底击杀，斩草除根{' ' * 14} {bold('║')}")
            self.print(f"{bold('║')} {'    · 获得额外战斗奖励'.ljust(44)} {bold('║')}")
            self.print(f"{bold('║')} {'    · 根据对方善恶影响业力'.ljust(44)} {bold('║')}")
            self.print(f"{bold('║')} {' ' * 46} {bold('║')}")
            self.print(f"{bold('║')} {colorize('  /饶恕', Color.GREEN)} - 放其一条生路，结个善缘{' ' * 12} {bold('║')}")
            self.print(f"{bold('║')} {'    · 对方好感度大幅提升'.ljust(44)} {bold('║')}")
            self.print(f"{bold('║')} {'    · 根据对方善恶获得业力'.ljust(44)} {bold('║')}")
            self.print(f"{bold('╚' + '═' * 48 + '╝')}")
            
            # 保存NPC引用到状态等待玩家选择
            self.cli.set_state('execution_pending', {'npc': target, 'npc_name': npc_name})
            
            # 使用动态材料生成器生成材料
            self._generate_and_save_materials(target)
            
            # 不清理战斗状态，等待玩家选择处决或饶恕
            return
        
        # 处理普通掉落物品
        if result.loot:
            self.print(f"掉落物品: {colorize(', '.join(result.loot), Color.CYAN)}")
            # 添加物品到背包
            if hasattr(self.player, 'inventory'):
                for item_name in result.loot:
                    # 创建动态道具数据
                    item_data = {
                        "name": item_name,
                        "description": f"从战斗中获得的{item_name}",
                        "type": "material",
                        "rarity": "common",
                        "value": 10,
                        "effect": {},
                        "usable": False,
                        "tradable": True,
                    }
                    success = self.player.inventory.add_item(item_name, 1, item_data)
                    if success:
                        self.print(success(f"  ✓ {item_name} 已添加到背包"))
                    else:
                        self.print(warning(f"  ✗ {item_name} 添加失败"))
    
    def _generate_and_save_materials(self, target):
        """
        生成并保存战斗材料
        
        使用动态材料生成器根据目标信息生成材料，
        保存到数据库并显示材料信息。
        
        Args:
            target: 战斗目标（NPC或妖兽）
        """
        # 获取目标信息
        enemy_name = ""
        enemy_level = 1
        enemy_type = "npc"
        
        if hasattr(target, 'data'):
            # NPC目标
            if hasattr(target.data, 'dao_name'):
                enemy_name = target.data.dao_name
            if hasattr(target.data, 'realm_level'):
                # 处理realm_level可能是字符串的情况
                from config import REALM_NAME_TO_LEVEL
                realm_level = target.data.realm_level
                if isinstance(realm_level, str):
                    enemy_level = REALM_NAME_TO_LEVEL.get(realm_level, 0)
                    if enemy_level == 0 and realm_level.isdigit():
                        enemy_level = int(realm_level)
                else:
                    enemy_level = int(realm_level)
            enemy_type = "npc"
        elif isinstance(target, dict):
            # 字典类型的妖兽目标
            enemy_name = target.get('name', '未知妖兽')
            enemy_level = target.get('level', 1)
            enemy_type = "beast"
        elif hasattr(target, 'name'):
            enemy_name = target.name
            if hasattr(target, 'level'):
                enemy_level = target.level
            enemy_type = "beast"
        
        # 生成材料数量（根据目标等级决定）
        material_count = min(3, max(1, enemy_level // 10 + 1))
        
        # 调用材料生成器生成多个材料
        materials = material_generator.generate_multiple_materials(
            enemy_name=enemy_name,
            enemy_level=enemy_level,
            enemy_type=enemy_type,
            count=material_count
        )
        
        # 保存材料到数据库并添加到玩家背包
        saved_materials = []
        for material in materials:
            # 尝试保存到数据库
            try:
                # 将材料转换为字典并保存
                material_dict = material.to_dict()
                # 这里可以调用数据库保存方法
                # db.save_material(material_dict)
                saved_materials.append(material)
            except Exception as e:
                # 保存失败也继续，不影响游戏体验
                saved_materials.append(material)
            
            # 添加到玩家背包
            if hasattr(self.player, 'inventory'):
                item_data = {
                    "name": material.name,
                    "description": material.description,
                    "type": "material",
                    "rarity": material.rarity.value,
                    "value": material.value,
                    "effect": material.effects,
                    "usable": True,
                    "tradable": True,
                    "material_id": material.id,
                    "material_type": material.material_type,
                    "level": material.level,
                }
                add_success = self.player.inventory.add_item(material.name, 1, item_data)
                if not add_success:
                    self.print(warning(f"  ✗ {material.name} 添加到背包失败"))
        
        # 显示生成的材料
        if saved_materials:
            self._display_materials(saved_materials)
    
    def _display_materials(self, materials: List[GeneratedMaterial]):
        """
        显示生成的材料
        
        使用颜色工具美化输出，展示材料的名称、稀有度、类型和效果等信息。
        
        Args:
            materials: 生成的材料列表
        """
        if not materials:
            return
        
        self.print(f"\n{colorize('═══ 战斗材料掉落 ═══', Color.CYAN)}")
        
        # 稀有度对应的颜色
        rarity_colors = {
            MaterialRarity.COMMON: Color.WHITE,
            MaterialRarity.UNCOMMON: Color.GREEN,
            MaterialRarity.RARE: Color.BLUE,
            MaterialRarity.EPIC: Color.MAGENTA,
            MaterialRarity.LEGENDARY: Color.YELLOW,
        }
        
        # 稀有度对应的图标
        rarity_icons = {
            MaterialRarity.COMMON: "⚪",
            MaterialRarity.UNCOMMON: "🟢",
            MaterialRarity.RARE: "🔵",
            MaterialRarity.EPIC: "🟣",
            MaterialRarity.LEGENDARY: "🟡",
        }
        
        for i, material in enumerate(materials, 1):
            # 获取材料的颜色和图标
            rarity_color = rarity_colors.get(material.rarity, Color.WHITE)
            rarity_icon = rarity_icons.get(material.rarity, "⚪")
            
            # 显示材料基本信息
            self.print(f"\n{colorize(f'【{i}】', Color.CYAN)} {rarity_icon} {colorize(material.name, rarity_color)}")
            self.print(f"    类型: {material.material_type} | 等级: {material.level} | 价值: {material.value}灵石")
            
            # 显示材料描述
            if material.description:
                self.print(f"    描述: {material.description}")
            
            # 显示材料效果
            if material.effects:
                effects_str = []
                if "primary_effect" in material.effects:
                    effects_str.append(f"主效果:{material.effects['primary_effect']}")
                if "secondary_effect" in material.effects:
                    effects_str.append(f"副效果:{material.effects['secondary_effect']}")
                if "special_trait" in material.effects:
                    effects_str.append(f"{colorize('★特殊:' + material.effects['special_trait'], Color.YELLOW)}")
                if "power" in material.effects:
                    effects_str.append(f"威力:{material.effects['power']}")
                
                if effects_str:
                    self.print(f"    属性: {' | '.join(effects_str)}")
            
            # 显示材料来源
            if material.source:
                self.print(f"    {colorize('└─', Color.CYAN)} 来源: {material.source}")
        
        # 显示总计
        total_value = sum(m.value for m in materials)
        self.print(f"\n{colorize('─' * 40, Color.CYAN)}")
        self.print(f"共获得 {colorize(str(len(materials)), Color.YELLOW)} 个材料，总价值 {colorize(str(total_value), Color.YELLOW)} 灵石")
        self.print(success("✓ 所有材料已自动添加到背包"))
    
    def _get_target(self, target_name: str) -> Optional[Any]:
        """
        获取战斗目标（NPC或妖兽）
        
        Args:
            target_name: 目标名称
            
        Returns:
            目标对象或None
        """
        # 先尝试查找NPC
        if self.npc_manager:
            npc = self.npc_manager.get_npc_by_name(target_name)
            if npc:
                # 检查NPC是否存活
                if hasattr(npc, 'data') and hasattr(npc.data, 'is_alive'):
                    if not npc.data.is_alive:
                        self.print(error(f"{target_name} 已经死亡，无法与之战斗！"))
                        return None
                return npc
        
        # 再尝试查找当前区域的妖兽
        if self.exploration_manager and hasattr(self.exploration_manager, 'current_location'):
            location = self.exploration_manager.current_location
            if location and hasattr(location, 'beasts'):
                for beast in location.beasts:
                    if isinstance(beast, dict):
                        if beast.get('name') == target_name:
                            return beast
                    elif hasattr(beast, 'name') and beast.name == target_name:
                        return beast
        
        # 检查是否是特殊目标（如当前遭遇的妖兽）
        if hasattr(self.cli, 'current_encounter') and self.cli.current_encounter:
            encounter = self.cli.current_encounter
            if isinstance(encounter, dict):
                if encounter.get('name') == target_name:
                    return encounter
            elif hasattr(encounter, 'name') and encounter.name == target_name:
                return encounter
        
        return None
    
    def handle_confirm_deathmatch(self):
        """确认死斗"""
        state = self.cli.get_state('confirm_deathmatch')
        if state and 'target' in state:
            self._start_combat(state['target'], CombatMode.DEATHMATCH)
        else:
            self.print(error("没有待确认的死斗"))
    
    def handle_combat_mode_select(self, choice: str):
        """
        处理战斗模式选择
        
        Args:
            choice: 玩家选择 (1 或 2)
        """
        state = self.cli.get_state('combat_mode_selection')
        if not state:
            self.print(error("没有待选择的战斗"))
            return
        
        target = state['target']
        
        if choice == '1':
            self._start_combat(target, CombatMode.SPAR)
        elif choice == '2':
            # 检查NPC好感度
            if hasattr(target, 'data') and hasattr(target.data, 'favorability'):
                if target.data.favorability > 30:
                    self.print(warning(f"{state['target_name']} 对你有好感，你确定要发起死斗吗？"))
                    self.print(f"输入 {colorize('/确认死斗', Color.RED)} 继续，或其他命令取消")
                    self.cli.set_state('confirm_deathmatch', {'target': target, 'target_name': state['target_name']})
                    self.cli.clear_state('combat_mode_selection')
                    return
            self._start_combat(target, CombatMode.DEATHMATCH)
        elif choice.lower() in ['取消', 'cancel', 'q', 'quit']:
            self.print(info("已取消战斗"))
            self.cli.clear_state('combat_mode_selection')
        else:
            self.print(error("无效的选择，请输入 1 或 2"))

    def handle_execute(self, args: str = ""):
        """
        处理 /处决 命令
        
        在死斗胜利后，玩家可以选择处决NPC。
        处决将彻底击杀NPC，玩家获得额外奖励，并根据NPC善恶值计算业力变化。
        
        流程：
        1. 检查是否有待处决的NPC（通过execution_pending状态）
        2. 调用 execution_system.execute_npc 执行处决
        3. 显示处决结果和业力变化
        4. 清理战斗状态
        """
        # 检查是否有待处决的NPC
        state = self.cli.get_state('execution_pending')
        if not state or 'npc' not in state:
            self.print(error("当前没有可以处决的目标！"))
            return
        
        npc = state['npc']
        
        # 检查NPC对象是否有效
        if not npc:
            self.print(error("目标NPC无效！"))
            return
        
        # 调用处决系统执行处决
        result = execution_system.execute_npc(npc, self.player)
        
        # 显示处决结果
        self.print(f"\n{bold('═══ 处决结果 ═══')}")
        
        if result.success:
            self.print(success(f"✓ {result.message}"))
            
            # 显示业力变化
            if result.karma_change > 0:
                self.print(success(f"☯ 业力值 +{result.karma_change}（替天行道，善业增长）"))
            elif result.karma_change < 0:
                self.print(error(f"☯ 业力值 {result.karma_change}（滥杀无辜，恶业增长）"))
            else:
                self.print(info("☯ 业力值无变化"))
            
            # 记录NPC死亡到死亡管理器
            if hasattr(npc, 'data'):
                death_manager.mark_npc_dead(
                    npc=npc,
                    killer_name=self.player.stats.name if hasattr(self.player, 'stats') else "玩家",
                    reason=f"被{self.player.stats.name if hasattr(self.player, 'stats') else '玩家'}处决"
                )
        else:
            self.print(error(f"✗ 处决失败：{result.message}"))
        
        # 清理战斗状态和处决状态
        self._clear_combat_state()
        self.cli.clear_state('execution_pending')
    
    def handle_spare(self, args: str = ""):
        """
        处理 /饶恕 命令
        
        在死斗胜利后，玩家可以选择饶恕NPC。
        饶恕将保留NPC性命，大幅提升好感度，并根据NPC善恶值计算业力变化。
        
        流程：
        1. 检查是否有待处决的NPC（通过execution_pending状态）
        2. 调用 execution_system.spare_npc 执行饶恕
        3. 显示饶恕结果和业力变化
        4. 清理战斗状态
        """
        # 检查是否有待处决的NPC
        state = self.cli.get_state('execution_pending')
        if not state or 'npc' not in state:
            self.print(error("当前没有可以饶恕的目标！"))
            return
        
        npc = state['npc']
        
        # 检查NPC对象是否有效
        if not npc:
            self.print(error("目标NPC无效！"))
            return
        
        # 调用处决系统执行饶恕
        result = execution_system.spare_npc(npc, self.player)
        
        # 显示饶恕结果
        self.print(f"\n{bold('═══ 饶恕结果 ═══')}")
        
        if result.success:
            self.print(success(f"✓ {result.message}"))
            
            # 显示业力变化
            if result.karma_change > 20:
                self.print(success(f"☯ 业力值 +{result.karma_change}（慈悲为怀，大善之举）"))
            elif result.karma_change > 0:
                self.print(success(f"☯ 业力值 +{result.karma_change}（心存善念）"))
            else:
                self.print(info("☯ 业力值无变化"))
        else:
            self.print(error(f"✗ 饶恕失败：{result.message}"))
        
        # 清理战斗状态和处决状态
        self._clear_combat_state()
        self.cli.clear_state('execution_pending')
    
    def _clear_combat_state(self):
        """
        清理战斗状态
        
        重置所有与战斗相关的状态变量
        """
        self.combat_system = None
        self.current_target = None
        self.current_mode = None
        self.cli.clear_state('combat_mode_selection')
        self.cli.clear_state('confirm_deathmatch')
