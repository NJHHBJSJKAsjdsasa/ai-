from domain.services.cultivation_service import CultivationService
from domain.repositories.player_repository import PlayerRepository
from infrastructure.persistence.player_repository_impl import PlayerRepositoryImpl
from application.use_cases.cultivation_use_case import CultivationUseCase

class DependencyContainer:
    def __init__(self):
        # 初始化各个组件
        self.cultivation_service = CultivationService()
        self.player_repository = PlayerRepositoryImpl()
        
        # 初始化用例
        self.cultivation_use_case = CultivationUseCase(
            self.cultivation_service,
            self.player_repository
        )
    
    def get_cultivation_use_case(self):
        return self.cultivation_use_case
    
    def get_player_repository(self):
        return self.player_repository
    
    def get_cultivation_service(self):
        return self.cultivation_service
