from domain.repositories.player_repository import PlayerRepository
from domain.entities.player import Player
import json
import os

class PlayerRepositoryImpl(PlayerRepository):
    def __init__(self, save_dir='saves'):
        self.save_dir = save_dir
        os.makedirs(self.save_dir, exist_ok=True)
    
    def save(self, player):
        file_path = os.path.join(self.save_dir, f'player_{player.id}.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                'id': player.id,
                'name': player.name,
                'cultivation_realm': player.cultivation_realm,
                'level': player.level,
                'attributes': player.attributes,
                'inventory': player.inventory,
                'techniques': player.techniques,
                'friends': player.friends,
                'enemies': player.enemies
            }, f, ensure_ascii=False, indent=2)
    
    def find_by_id(self, player_id):
        file_path = os.path.join(self.save_dir, f'player_{player_id}.json')
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Player(
                data['id'],
                data['name'],
                data['cultivation_realm'],
                data['level'],
                data['attributes']
            )
    
    def update(self, player):
        self.save(player)
    
    def delete(self, player_id):
        file_path = os.path.join(self.save_dir, f'player_{player_id}.json')
        if os.path.exists(file_path):
            os.remove(file_path)
