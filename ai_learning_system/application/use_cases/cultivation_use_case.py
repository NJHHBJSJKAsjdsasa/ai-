from application.services.cultivation_service import CultivationService

class CultivationUseCase:
    """修炼用例"""
    def __init__(self, cultivation_service: CultivationService):
        self.cultivation_service = cultivation_service
    
    def execute(self, player_id: str, time_spent: int) -> dict:
        """执行修炼"""
        return self.cultivation_service.cultivate(player_id, time_spent)
    
    def get_cultivation_status(self, player_id: str) -> dict:
        """获取修炼状态"""
        return self.cultivation_service.get_cultivation_status(player_id)
    
    def attempt_breakthrough(self, player_id: str) -> dict:
        """尝试突破"""
        return self.cultivation_service.attempt_breakthrough(player_id)
