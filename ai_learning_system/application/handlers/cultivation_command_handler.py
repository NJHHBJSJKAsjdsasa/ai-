from domain.entities.player import Player
from domain.services.cultivation_service import CultivationService
from domain.repositories.player_repository import PlayerRepository
from application.commands.cultivation_commands import CultivateCommand, AttemptBreakthroughCommand

class CultivationCommandHandler:
    """修炼命令处理程序"""
    def __init__(self, cultivation_service: CultivationService, player_repository: PlayerRepository):
        self.cultivation_service = cultivation_service
        self.player_repository = player_repository
    
    def handle_cultivate(self, command: CultivateCommand) -> dict:
        """处理修炼命令"""
        # 获取玩家
        player = self.player_repository.find_by_id(command.player_id)
        if not player:
            return None
        
        # 计算修炼进度
        gained_exp = self.cultivation_service.calculate_cultivation_progress(player, command.time_spent)
        
        # 检查突破
        breakthrough_result = False
        if self.cultivation_service.check_breakthrough(player):
            breakthrough_result = self.cultivation_service.perform_breakthrough(player)
        
        # 保存玩家状态
        self.player_repository.update(player)
        
        # 获取修炼状态
        cultivation_status = self.cultivation_service.get_cultivation_status(player)
        
        # 返回详细信息
        return {
            "player": player,
            "gained_exp": gained_exp,
            "breakthrough": breakthrough_result,
            "cultivation_status": cultivation_status
        }
    
    def handle_attempt_breakthrough(self, command: AttemptBreakthroughCommand) -> dict:
        """处理尝试突破命令"""
        player = self.player_repository.find_by_id(command.player_id)
        if not player:
            return None
        
        breakthrough_result = self.cultivation_service.perform_breakthrough(player)
        
        # 保存玩家状态
        self.player_repository.update(player)
        
        return {
            "player": player,
            "breakthrough": breakthrough_result,
            "cultivation_status": self.cultivation_service.get_cultivation_status(player)
        }
