from domain.entities.player import Player
from domain.value_objects.cultivation_realm import CultivationRealm
from typing import Optional, List

class CultivationService:
    """修炼服务"""
    def __init__(self):
        pass
    
    def calculate_cultivation_progress(self, player: Player, time_spent: int) -> int:
        """计算修炼进度并返回获得的经验值"""
        return player.cultivate(time_spent)
    
    def check_breakthrough(self, player: Player) -> bool:
        """检查是否可以突破"""
        return player.can_breakthrough()
    
    def perform_breakthrough(self, player: Player) -> bool:
        """执行突破"""
        return player.breakthrough()
    
    def get_cultivation_status(self, player: Player) -> dict:
        """获取修炼状态"""
        return {
            "current_realm": player.cultivation_realm.name,
            "current_exp": player.current_exp_value,
            "required_exp": player.cultivation_realm.required_exp,
            "progress": player.get_cultivation_progress(),
            "next_realm": player.cultivation_realm.next_realm.name if player.cultivation_realm.next_realm else None
        }
    
    def create_realm_hierarchy(self) -> List[CultivationRealm]:
        """创建修炼境界层次结构"""
        # 先创建最高境界
        soul_transformation = CultivationRealm(
            name="化神期",
            level=5,
            description="元婴成长为元神，能够感悟天地法则",
            required_exp=100000,
            lifespan_bonus=1000,
            spiritual_power_bonus=1000
        )
        
        # 创建元婴期，设置下一个境界为化神期
        nascent_soul = CultivationRealm(
            name="元婴期",
            level=4,
            description="金丹破碎，形成元婴，拥有元婴出窍的能力",
            required_exp=50000,
            lifespan_bonus=500,
            spiritual_power_bonus=500,
            next_realm=soul_transformation
        )
        
        # 创建金丹期，设置下一个境界为元婴期
        golden_core = CultivationRealm(
            name="金丹期",
            level=3,
            description="将灵气凝聚成金丹，寿命大幅增加",
            required_exp=10000,
            lifespan_bonus=200,
            spiritual_power_bonus=100,
            next_realm=nascent_soul
        )
        
        # 创建筑基期，设置下一个境界为金丹期
        foundation_establishment = CultivationRealm(
            name="筑基期",
            level=2,
            description="打下修炼基础，灵气在体内形成循环",
            required_exp=5000,
            lifespan_bonus=100,
            spiritual_power_bonus=50,
            next_realm=golden_core
        )
        
        # 创建练气期，设置下一个境界为筑基期
        qi_refining = CultivationRealm(
            name="练气期",
            level=1,
            description="修炼的基础阶段，开始吸收天地灵气",
            required_exp=1000,
            lifespan_bonus=50,
            spiritual_power_bonus=10,
            next_realm=foundation_establishment
        )
        
        return [qi_refining, foundation_establishment, golden_core, nascent_soul, soul_transformation]
