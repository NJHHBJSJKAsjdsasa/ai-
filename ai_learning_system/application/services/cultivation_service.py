from domain.services.cultivation_service import CultivationService
from domain.repositories.player_repository import PlayerRepository
from application.commands.cultivation_commands import CultivateCommand, AttemptBreakthroughCommand
from application.queries.cultivation_queries import GetCultivationStatusQuery
from application.handlers.cultivation_command_handler import CultivationCommandHandler
from application.handlers.cultivation_query_handler import CultivationQueryHandler

class CultivationService:
    """修炼应用服务"""
    def __init__(self, cultivation_service: CultivationService, player_repository: PlayerRepository):
        self.command_handler = CultivationCommandHandler(cultivation_service, player_repository)
        self.query_handler = CultivationQueryHandler(cultivation_service, player_repository)
    
    def cultivate(self, player_id: str, time_spent: int) -> dict:
        """执行修炼"""
        command = CultivateCommand(player_id=player_id, time_spent=time_spent)
        return self.command_handler.handle_cultivate(command)
    
    def attempt_breakthrough(self, player_id: str) -> dict:
        """尝试突破"""
        command = AttemptBreakthroughCommand(player_id=player_id)
        return self.command_handler.handle_attempt_breakthrough(command)
    
    def get_cultivation_status(self, player_id: str) -> dict:
        """获取修炼状态"""
        query = GetCultivationStatusQuery(player_id=player_id)
        return self.query_handler.handle_get_cultivation_status(query)
