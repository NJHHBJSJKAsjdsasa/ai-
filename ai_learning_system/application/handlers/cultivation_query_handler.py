from domain.services.cultivation_service import CultivationService
from domain.repositories.player_repository import PlayerRepository
from application.queries.cultivation_queries import GetCultivationStatusQuery

class CultivationQueryHandler:
    """修炼查询处理程序"""
    def __init__(self, cultivation_service: CultivationService, player_repository: PlayerRepository):
        self.cultivation_service = cultivation_service
        self.player_repository = player_repository
    
    def handle_get_cultivation_status(self, query: GetCultivationStatusQuery) -> dict:
        """处理获取修炼状态查询"""
        player = self.player_repository.find_by_id(query.player_id)
        if not player:
            return None
        
        return self.cultivation_service.get_cultivation_status(player)
