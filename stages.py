from dataclasses import dataclass
from typing import List, Dict
from enum import Enum
import random

class StageType(Enum):
    NORMAL = "normal"
    BOSS = "boss"

@dataclass
class StageConfig:
    stage_id: int
    name: str
    stage_type: StageType
    enemy_spawn_delay: int
    max_enemies: int
    difficulty_level: str
    enemy_types_weights: Dict[str, float]
    duration: int  # in seconds, 0 for infinite
    boss_text: str = ""

class StageManager:
    def __init__(self):
        self.current_stage = 0
        self.stage_time = 0
        self.stages = self.create_stages()
    
    def create_stages(self) -> List[StageConfig]:
        return [
            # Stage 1: Tutorial
            StageConfig(
                stage_id=1,
                name="街の郊外",
                stage_type=StageType.NORMAL,
                enemy_spawn_delay=180,  # 3 seconds
                max_enemies=3,
                difficulty_level="easy",
                enemy_types_weights={"zombie": 0.8, "runner": 0.2, "shooter": 0.0},
                duration=60  # 1 minute
            ),
            
            # Stage 2: City Streets
            StageConfig(
                stage_id=2,
                name="街の中心部",
                stage_type=StageType.NORMAL,
                enemy_spawn_delay=120,  # 2 seconds
                max_enemies=4,
                difficulty_level="medium",
                enemy_types_weights={"zombie": 0.5, "runner": 0.3, "shooter": 0.2},
                duration=90  # 1.5 minutes
            ),
            
            # Stage 3: Boss Fight
            StageConfig(
                stage_id=3,
                name="ボス戦: メガゾンビ",
                stage_type=StageType.BOSS,
                enemy_spawn_delay=300,  # 5 seconds
                max_enemies=2,
                difficulty_level="hard",
                enemy_types_weights={"zombie": 0.3, "runner": 0.4, "shooter": 0.3},
                duration=0,  # Infinite until boss is defeated
                boss_text="MEGABOSS"
            ),
            
            # Stage 4: Industrial Zone
            StageConfig(
                stage_id=4,
                name="工業地帯",
                stage_type=StageType.NORMAL,
                enemy_spawn_delay=90,  # 1.5 seconds
                max_enemies=5,
                difficulty_level="hard",
                enemy_types_weights={"zombie": 0.3, "runner": 0.4, "shooter": 0.3},
                duration=120  # 2 minutes
            ),
            
            # Stage 5: Final Boss
            StageConfig(
                stage_id=5,
                name="最終ボス: キングゾンビ",
                stage_type=StageType.BOSS,
                enemy_spawn_delay=240,  # 4 seconds
                max_enemies=3,
                difficulty_level="hard",
                enemy_types_weights={"zombie": 0.2, "runner": 0.3, "shooter": 0.5},
                duration=0,  # Infinite until boss is defeated
                boss_text="FINALKING"
            )
        ]
    
    def get_current_stage(self) -> StageConfig:
        if self.current_stage < len(self.stages):
            return self.stages[self.current_stage]
        else:
            # Generate endless stages
            return self.generate_endless_stage()
    
    def generate_endless_stage(self) -> StageConfig:
        stage_num = self.current_stage + 1
        return StageConfig(
            stage_id=stage_num,
            name=f"エンドレス ステージ {stage_num - len(self.stages) + 1}",
            stage_type=StageType.NORMAL,
            enemy_spawn_delay=max(60, 150 - stage_num * 5),
            max_enemies=min(8, 3 + stage_num // 3),
            difficulty_level="hard" if stage_num > 10 else "medium",
            enemy_types_weights={"zombie": 0.2, "runner": 0.4, "shooter": 0.4},
            duration=90 + stage_num * 10
        )
    
    def next_stage(self):
        self.current_stage += 1
        self.stage_time = 0
    
    def update(self, dt: float):
        self.stage_time += dt
    
    def is_stage_complete(self, enemies_count: int) -> bool:
        current = self.get_current_stage()
        
        if current.stage_type == StageType.BOSS:
            # Boss stages complete when no enemies left
            return enemies_count == 0
        else:
            # Normal stages complete when time is up
            return current.duration > 0 and self.stage_time >= current.duration
    
    def get_stage_progress(self) -> float:
        current = self.get_current_stage()
        if current.duration == 0:
            return 0.0  # Boss stages don't have time progress
        return min(1.0, self.stage_time / current.duration)

# Japanese word lists for different difficulties
JAPANESE_WORDS = {
    "easy": [
        "ねこ", "いぬ", "はしる", "とぶ", "あるく", "ひ", "みず", "たいよう", "つき", "ほし",
        "あか", "あお", "みどり", "しろ", "くろ", "おおきい", "ちいさい", "あつい", "つめたい", "たのしい"
    ],
    "medium": [
        "コンピューター", "キーボード", "マウス", "タイピング", "ゲーム", "ゾンビ", "こうげき", "まもる", "ぶき", "たたかい",
        "がっこう", "しごと", "でんしゃ", "じどうしゃ", "りょこう", "おんがく", "えいが", "ほん", "しんぶん", "テレビ"
    ],
    "hard": [
        "プログラミング", "かいはつ", "アルゴリズム", "インターフェース", "アーキテクチャ", "さいてきか", "デバッグ", "じっそう",
        "データベース", "ネットワーク", "セキュリティ", "クラウド", "じんこうちのう", "きかいがくしゅう", "ブロックチェーン"
    ]
}