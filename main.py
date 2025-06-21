#!/usr/bin/env python3

import pygame
import sys
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
from sounds import SoundManager
from stages import StageManager, JAPANESE_WORDS
from graphics import GraphicsManager, FontManager
from romaji_input import TypingInputHandler

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_RED = (139, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# 改善された色パレット（視認性重視）
BRIGHT_GREEN = (50, 255, 50)      # 完了した文字用
BRIGHT_YELLOW = (255, 255, 100)   # 入力中の文字用  
BRIGHT_WHITE = (255, 255, 255)    # 待機中の文字用
LIGHT_BLUE = (150, 200, 255)      # ヒント文字用
DARK_GRAY = (80, 80, 80)          # 未入力文字用
ORANGE = (255, 165, 0)            # 強調用
BRIGHT_RED = (255, 50, 50)        # エラー用

class GameState(Enum):
    TITLE = "title"
    GAME = "game"
    RESULT = "result"
    SETTINGS = "settings"

class EnemyType(Enum):
    ZOMBIE = "zombie"
    RUNNER = "runner" 
    SHOOTER = "shooter"
    BOSS = "boss"

@dataclass
class Enemy:
    x: float
    y: float
    enemy_type: EnemyType
    text: str
    hp: int
    max_hp: int
    speed: float
    attack_power: int
    typed_chars: int = 0
    color: Tuple[int, int, int] = RED
    
    def is_defeated(self) -> bool:
        return self.typed_chars >= len(self.text)
    
    def get_remaining_text(self) -> str:
        return self.text[self.typed_chars:]
    
    def get_typed_text(self) -> str:
        return self.text[:self.typed_chars]


@dataclass(frozen=True)
class EnemyProfile:
    hp: int
    speed: float
    attack_power: int
    color: Tuple[int, int, int]


ENEMY_PROFILES: Dict[EnemyType, EnemyProfile] = {
    EnemyType.ZOMBIE: EnemyProfile(1, 1.0, 10, (139, 69, 19)),
    EnemyType.RUNNER: EnemyProfile(1, 2.0, 5, (255, 165, 0)),
    EnemyType.SHOOTER: EnemyProfile(2, 0.5, 15, (128, 0, 128)),
}

class TypingGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("タイピング・オブ・ザ・デッド風ゲーム")
        self.clock = pygame.time.Clock()
        
        self.sound_manager = SoundManager()
        self.stage_manager = StageManager()
        self.graphics_manager = GraphicsManager()
        self.font_manager = FontManager()
        
        # BGM設定
        if self.sound_manager.enabled:
            self.sound_manager.set_sound_volume('bgm', 0.3)  # BGMの音量を下げる
        
        self.bgm_playing = False
        
        self.state = GameState.TITLE
        
        self.score = 0
        self.combo = 0
        self.player_hp = 100
        self.max_hp = 100
        
        self.enemies: List[Enemy] = []
        self.current_target: Optional[Enemy] = None
        self.current_input = ""
        self.typing_handler = TypingInputHandler()
        
        self.enemy_spawn_timer = 0
        
        self.word_lists = {
            "easy": ["cat", "dog", "run", "jump", "walk", "fire", "water", "sun", "moon", "star"],
            "medium": ["computer", "keyboard", "mouse", "typing", "game", "zombie", "attack", "defend", "weapon", "battle"],
            "hard": ["programming", "development", "algorithm", "interface", "architecture", "optimization", "debugging", "implementation"]
        }
        
        self.japanese_mode = True  # Enable Japanese mode with romaji input
        self.running = True
        self.error_flash_timer = 0  # エラー時の視覚フィードバック用
        
    def get_random_word(self) -> str:
        current_stage = self.stage_manager.get_current_stage()
        if self.japanese_mode:
            return random.choice(JAPANESE_WORDS[current_stage.difficulty_level])
        else:
            return random.choice(self.word_lists[current_stage.difficulty_level])
    
    def spawn_enemy(self):
        current_stage = self.stage_manager.get_current_stage()
        
        # Choose enemy type based on stage weights
        weights = current_stage.enemy_types_weights
        enemy_type_names = list(weights.keys())
        enemy_weights = list(weights.values())
        
        chosen_type_name = random.choices(enemy_type_names, weights=enemy_weights)[0]
        enemy_type = EnemyType(chosen_type_name)
        
        x = random.randint(50, SCREEN_WIDTH - 150)
        y = random.randint(50, SCREEN_HEIGHT // 2)
        
        text = self.get_random_word()

        profile = ENEMY_PROFILES.get(enemy_type)
        enemy = Enemy(
            x,
            y,
            enemy_type,
            text,
            profile.hp,
            profile.hp,
            profile.speed,
            profile.attack_power,
            color=profile.color,
        )
        self.enemies.append(enemy)
    
    def handle_typing_input(self, char: str):
        print(f"Handling input: '{char}'")
        
        if self.japanese_mode:
            self.handle_japanese_input(char)
        else:
            self.handle_english_input(char)
    
    def handle_japanese_input(self, char: str):
        """日本語（ローマ字入力）の処理"""
        if not self.current_target:
            # 新しいターゲットを探す
            for enemy in self.enemies:
                # 新しいハンドラーでテスト
                test_handler = TypingInputHandler()
                test_handler.set_target_text(enemy.text)
                result = test_handler.process_input(char)
                if result['success']:
                    self.current_target = enemy
                    self.typing_handler.set_target_text(enemy.text)
                    self.typing_handler.process_input(char)  # 実際の入力を処理
                    print(f"Target selected: {enemy.text}")
                    break
        
        elif self.current_target:  # ターゲットが既に選択されている場合
            result = self.typing_handler.process_input(char)
            
            if result['success']:
                self.sound_manager.play_sound('type')
                self.current_input = self.typing_handler.get_current_input_display()
                print(f"Good input! Next expected: {result.get('expected_next', 'None')}")
                
                if result['char_completed']:
                    self.current_target.typed_chars += 1
                    print(f"Character completed! Progress: {self.current_target.typed_chars}/{len(self.current_target.text)}")
                    
                    if result['word_completed']:
                        print(f"Word completed!")
                        self.defeat_enemy(self.current_target)
                        self.current_target = None
                        self.current_input = ""
                        # ハンドラーもリセット
                        self.typing_handler = TypingInputHandler()
            else:
                expected_chars = result.get('expected_next', [])
                expected_str = '/'.join(expected_chars) if expected_chars else '?'
                print(f"Wrong input! Expected: {expected_str}")
                # ミスした場合は現在の文字の入力をリセット（単語は保持）
                self.typing_handler.reset_current_char_input()
                self.combo = 0
                self.sound_manager.play_sound('error')
                
                # 視覚的フィードバック用にエラーフラグを設定
                self.error_flash_timer = 30  # 30フレーム（0.5秒）間赤く点滅
    
    def handle_english_input(self, char: str):
        """英語入力の処理"""
        if not self.current_target:
            for enemy in self.enemies:
                remaining_text = enemy.get_remaining_text()
                if remaining_text and remaining_text[0].lower() == char.lower():
                    self.current_target = enemy
                    print(f"Target selected: {remaining_text}")
                    break
        
        if self.current_target:
            remaining = self.current_target.get_remaining_text()
            if remaining and remaining[0].lower() == char.lower():
                self.current_target.typed_chars += 1
                self.current_input += char
                self.sound_manager.play_sound('type')
                print(f"Correct! Progress: {self.current_target.typed_chars}/{len(self.current_target.text)}")
                
                if self.current_target.is_defeated():
                    print(f"Enemy defeated!")
                    self.defeat_enemy(self.current_target)
                    self.current_target = None
                    self.current_input = ""
            else:
                print(f"Wrong character!")
                self.combo = 0
                self.sound_manager.play_sound('error')
    
    def defeat_enemy(self, enemy: Enemy):
        if enemy in self.enemies:
            points = len(enemy.text) * 10 * (self.combo + 1)
            self.score += points
            self.combo += 1
            self.enemies.remove(enemy)
            self.sound_manager.play_sound('defeat')
    
    def update_enemies(self):
        remaining = []
        for enemy in self.enemies:
            enemy.y += enemy.speed
            if enemy.y > SCREEN_HEIGHT - 100:
                self.player_hp -= enemy.attack_power
                if enemy == self.current_target:
                    self.current_target = None
                    self.current_input = ""
                self.combo = 0
                self.sound_manager.play_sound('damage')
            else:
                remaining.append(enemy)
        self.enemies = remaining
    
    def draw_title_screen(self):
        # Draw background
        bg = self.graphics_manager.get_image('background')
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay for better text readability
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = self.font_manager.get_font('large', self.japanese_mode)
        title_text = title_font.render("タイピング・オブ・ザ・デッド", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = self.font_manager.get_font('medium', False)
        subtitle_text = subtitle_font.render("TYPING OF THE DEAD", True, GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Menu buttons with graphics
        button_img = self.graphics_manager.get_image('button')
        
        # Start button
        start_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)
        self.screen.blit(button_img, start_button_rect)
        start_font = self.font_manager.get_font('medium', False)
        start_text = start_font.render("SPACE: Start", True, WHITE)
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        self.screen.blit(start_text, start_text_rect)
        
        # Settings button
        settings_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
        settings_button_img = pygame.transform.scale(button_img, (200, 40))
        self.screen.blit(settings_button_img, (settings_button_rect.x, settings_button_rect.y + 5))
        settings_font = self.font_manager.get_font('small', False)
        settings_text = settings_font.render("S: Settings", True, LIGHT_GRAY)
        settings_text_rect = settings_text.get_rect(center=(settings_button_rect.centerx, settings_button_rect.centery + 5))
        self.screen.blit(settings_text, settings_text_rect)
        
        # Quit instruction
        quit_font = self.font_manager.get_font('small', False)
        quit_text = quit_font.render("ESC: Quit", True, GRAY)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 520))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_game_screen(self):
        # Draw background
        bg = self.graphics_manager.get_image('background')
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay for gameplay area
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(64)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw enemies (with animation)
        animation_frame = int(pygame.time.get_ticks() / 150) % 10  # アニメーション速度調整
        font_large = self.font_manager.get_font('large', self.japanese_mode)
        font_xlarge = self.font_manager.get_font('xlarge', self.japanese_mode)

        for enemy in self.enemies:
            sprite_name = enemy.enemy_type.value
            
            enemy.animation_frame = animation_frame
            
            # アニメーションまたは静的スプライトを取得
            animation_name = f"{sprite_name}_walk"
            if animation_name in self.graphics_manager.animations:
                enemy_sprite = self.graphics_manager.get_animation_frame(animation_name, animation_frame)
            else:
                enemy_sprite = self.graphics_manager.get_image(sprite_name)
            
            # Highlight current target
            if enemy == self.current_target:
                # Yellow glow effect
                glow_surf = pygame.Surface((enemy_sprite.get_width() + 10, enemy_sprite.get_height() + 10))
                glow_surf.set_alpha(128)
                glow_surf.fill(YELLOW)
                self.screen.blit(glow_surf, (enemy.x - enemy_sprite.get_width()//2 - 5, enemy.y - enemy_sprite.get_height()//2 - 5))
            
            # Draw enemy sprite
            sprite_rect = enemy_sprite.get_rect(center=(int(enemy.x), int(enemy.y)))
            self.screen.blit(enemy_sprite, sprite_rect)
            
            # Adaptive text box sizing based on content
            if enemy == self.current_target:
                # Calculate required width based on text length
                test_font = font_xlarge
                text_width = test_font.size(enemy.text)[0] if enemy.text else 100
                textbox_width = max(350, text_width + 100)  # 余裕を持たせる
                textbox_height = 120  # より高く
            else:
                test_font = font_large
                text_width = test_font.size(enemy.text)[0] if enemy.text else 100
                textbox_width = max(250, text_width + 60)
                textbox_height = 60
            
            # 画面内に収まるように位置調整（改善版）
            textbox_x = max(textbox_width//2 + 10, min(SCREEN_WIDTH - textbox_width//2 - 10, enemy.x))
            textbox_y = max(textbox_height + 30, min(enemy.y - 30, SCREEN_HEIGHT // 2))
            
            # テキストボックス描画
            textbox_img = self.graphics_manager.get_image('textbox')
            textbox_scaled = pygame.transform.scale(textbox_img, (textbox_width, textbox_height))
            textbox_rect = pygame.Rect(textbox_x - textbox_width//2, textbox_y - textbox_height, textbox_width, textbox_height)
            self.screen.blit(textbox_scaled, textbox_rect)
            
            # 改善されたテキスト表示
            self.draw_enemy_text_with_progress(enemy, textbox_rect, textbox_width)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw stage info
        self.draw_stage_info()
    
    def draw_enemy_text_with_progress(self, enemy: Enemy, textbox_rect: pygame.Rect, textbox_width: int):
        """敵のテキストを進行状況付きで描画"""
        # テキストボックスの実際の位置を使用
        textbox_x = textbox_rect.centerx
        textbox_y = textbox_rect.centery
        textbox_height = textbox_rect.height

        font_large = self.font_manager.get_font('large', self.japanese_mode)
        font_xlarge = self.font_manager.get_font('xlarge', self.japanese_mode)
        small_font = self.font_manager.get_font('medium', False)
        
        if enemy != self.current_target:
            # 非ターゲットの敵は通常表示（大きなフォント）
            typed_text = enemy.get_typed_text()
            remaining_text = enemy.get_remaining_text()
            
            text_font = font_large  # より大きく
            
            text_x = textbox_x - textbox_width//2 + 15
            text_y = textbox_y - textbox_height//2 + 15
            
            if typed_text:
                typed_surface = text_font.render(typed_text, True, BRIGHT_GREEN)
                self.screen.blit(typed_surface, (text_x, text_y))
            
            if remaining_text:
                remaining_surface = text_font.render(remaining_text, True, BRIGHT_WHITE)
                typed_width = text_font.size(typed_text)[0] if typed_text else 0
                self.screen.blit(remaining_surface, (text_x + typed_width, text_y))
        else:
            # ターゲットの敵は詳細表示（大幅改善）
            progress_info = self.typing_handler.get_progress_info()
            typed_text = enemy.get_typed_text()
            remaining_text = enemy.get_remaining_text()
            current_romaji = progress_info['current_romaji']
            expected_next = progress_info['expected_next']
            current_target_char = progress_info['current_target_char']
            
            # より大きなフォント
            text_font = font_xlarge
            
            # メインテキスト行
            text_x = textbox_x - textbox_width//2 + 15
            text_y = textbox_y - 65
            x_current = text_x
            
            # 完了した文字（明るい緑）
            if typed_text:
                typed_surface = text_font.render(typed_text, True, BRIGHT_GREEN)
                # 影効果追加
                shadow_surface = text_font.render(typed_text, True, BLACK)
                self.screen.blit(shadow_surface, (x_current + 2, text_y + 2))
                self.screen.blit(typed_surface, (x_current, text_y))
                x_current += text_font.size(typed_text)[0]
            
            # 現在入力中の文字（強調表示）
            if current_target_char:
                if self.error_flash_timer > 0 and self.error_flash_timer % 6 < 3:
                    color = BRIGHT_RED  # エラー時の点滅効果
                else:
                    color = BRIGHT_YELLOW if current_romaji else BRIGHT_WHITE
                
                char_surface = text_font.render(current_target_char, True, color)
                char_rect = char_surface.get_rect()
                char_rect.topleft = (x_current, text_y)
                
                # 強調背景
                bg_rect = pygame.Rect(char_rect.x - 5, char_rect.y - 5, char_rect.width + 10, char_rect.height + 10)
                pygame.draw.rect(self.screen, (50, 50, 100), bg_rect, border_radius=5)
                pygame.draw.rect(self.screen, color, bg_rect, width=3, border_radius=5)
                
                # 影効果
                shadow_surface = text_font.render(current_target_char, True, BLACK)
                self.screen.blit(shadow_surface, (x_current + 2, text_y + 2))
                self.screen.blit(char_surface, char_rect)
                
                # アンダーライン（太く）
                pygame.draw.line(self.screen, color, 
                               (char_rect.left, char_rect.bottom + 3), 
                               (char_rect.right, char_rect.bottom + 3), 4)
                
                # カーソル点滅効果
                if not current_romaji and pygame.time.get_ticks() % 1000 < 500:
                    pygame.draw.line(self.screen, BRIGHT_WHITE, 
                                   (char_rect.left - 3, char_rect.top), 
                                   (char_rect.left - 3, char_rect.bottom), 4)
                
                x_current += char_rect.width + 5
            
            # 残りの文字（見やすいグレー）
            if len(remaining_text) > (1 if current_target_char else 0):
                remaining_display = remaining_text[1:] if current_target_char else remaining_text
                remaining_surface = text_font.render(remaining_display, True, DARK_GRAY)
                # 薄い影効果
                shadow_surface = text_font.render(remaining_display, True, BLACK)
                self.screen.blit(shadow_surface, (x_current + 1, text_y + 1))
                self.screen.blit(remaining_surface, (x_current, text_y))
            
            # 入力状況表示（下の行、改善）
            sub_y = textbox_y - 25
            if current_romaji:
                # 現在の入力（強調）
                romaji_text = f"入力中: {current_romaji}"
                romaji_surface = small_font.render(romaji_text, True, BRIGHT_YELLOW)
                romaji_bg = pygame.Rect(text_x - 5, sub_y - 5, romaji_surface.get_width() + 10, romaji_surface.get_height() + 10)
                pygame.draw.rect(self.screen, (40, 40, 0), romaji_bg, border_radius=3)
                self.screen.blit(romaji_surface, (text_x, sub_y))
                
                # 期待される次の文字
                if expected_next:
                    expected_text = f"次: {'/'.join(expected_next)}"
                    expected_surface = small_font.render(expected_text, True, LIGHT_BLUE)
                    expected_x = text_x + romaji_surface.get_width() + 15
                    self.screen.blit(expected_surface, (expected_x, sub_y))
            elif current_target_char:
                # 入力待ち状態（ヒント表示）
                target_patterns = self.typing_handler.converter.get_possible_romaji_patterns(current_target_char)
                if target_patterns:
                    hint_text = f"入力可能: {'/'.join(target_patterns)}"
                    hint_surface = small_font.render(hint_text, True, LIGHT_BLUE)
                    hint_bg = pygame.Rect(text_x - 5, sub_y - 5, hint_surface.get_width() + 10, hint_surface.get_height() + 10)
                    pygame.draw.rect(self.screen, (0, 20, 40), hint_bg, border_radius=3)
                    self.screen.blit(hint_surface, (text_x, sub_y))
    
    def draw_hud(self):
        # Score (LARGER)
        score_font = self.font_manager.get_font('large', self.japanese_mode)  # Changed to large and use japanese mode
        score_label = "スコア: " if self.japanese_mode else "Score: "
        score_text = score_font.render(f"{score_label}{self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Combo with glow effect (LARGER)
        combo_font = self.font_manager.get_font('large', self.japanese_mode)  # Changed to large and use japanese mode
        combo_label = "コンボ: " if self.japanese_mode else "Combo: "
        combo_text = combo_font.render(f"{combo_label}{self.combo}", True, YELLOW)
        
        # Add glow effect for high combos
        if self.combo > 5:
            glow_text = combo_font.render(f"{combo_label}{self.combo}", True, WHITE)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                self.screen.blit(glow_text, (10 + dx, 70 + dy))  # Adjusted position
        
        self.screen.blit(combo_text, (10, 70))  # Adjusted position
        
        # Graphical HP Bar
        hp_bar_bg_img = self.graphics_manager.get_image('hp_bar_bg')
        self.screen.blit(hp_bar_bg_img, (10, SCREEN_HEIGHT - 50))
        
        # HP bar fill
        hp_percentage = self.player_hp / self.max_hp
        hp_bar_img = self.graphics_manager.get_image('hp_bar')
        hp_width = int(hp_bar_img.get_width() * hp_percentage)
        
        if hp_width > 0:
            hp_bar_cropped = pygame.Surface((hp_width, hp_bar_img.get_height()))
            hp_bar_cropped.blit(hp_bar_img, (0, 0))
            self.screen.blit(hp_bar_cropped, (12, SCREEN_HEIGHT - 48))
        
        # HP text (LARGER)
        hp_font = self.font_manager.get_font('medium', self.japanese_mode)  # Changed to medium and use japanese mode
        hp_label = "HP: " if not self.japanese_mode else "HP: "  # HP is commonly used in Japanese games
        hp_text = hp_font.render(f"{hp_label}{self.player_hp}/{self.max_hp}", True, WHITE)
        self.screen.blit(hp_text, (10, SCREEN_HEIGHT - 90))  # Adjusted position
        
        # Current input with background (LARGER) - 改善された表示
        if self.current_target and self.typing_handler:
            progress_info = self.typing_handler.get_progress_info()
            current_romaji = progress_info['current_romaji']
            expected_next = progress_info['expected_next']
            
            input_font = self.font_manager.get_font('large', self.japanese_mode)
            small_font = self.font_manager.get_font('medium', False)
            
            # 現在の入力状況
            if current_romaji:
                input_label = "入力中: " if self.japanese_mode else "Typing: "
                input_text = input_font.render(f"{input_label}{current_romaji}", True, YELLOW)
                
                # 背景
                bg_width = max(300, input_text.get_width() + 40)
                input_bg = pygame.Surface((bg_width, input_text.get_height() + 30))
                input_bg.set_alpha(200)
                input_bg.fill(BLACK)
                
                input_rect = input_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
                bg_rect = input_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
                
                self.screen.blit(input_bg, bg_rect)
                self.screen.blit(input_text, input_rect)
                
                # 期待される次の文字
                if expected_next:
                    expected_label = "次の文字: " if self.japanese_mode else "Next: "
                    expected_text = small_font.render(f"{expected_label}{'/'.join(expected_next)}", True, WHITE)
                    expected_rect = expected_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(expected_text, expected_rect)
    
    def draw_stage_info(self):
        current_stage = self.stage_manager.get_current_stage()
        
        # Stage name with Japanese font if needed (LARGER)
        stage_font = self.font_manager.get_font('large', self.japanese_mode)  # Changed to large
        stage_label = f"ステージ {current_stage.stage_id}: " if self.japanese_mode else f"Stage {current_stage.stage_id}: "
        stage_text = stage_font.render(f"{stage_label}{current_stage.name}", True, WHITE)
        
        # Background for stage info
        stage_bg = pygame.Surface((stage_text.get_width() + 20, stage_text.get_height() + 10))
        stage_bg.set_alpha(180)
        stage_bg.fill(BLACK)
        
        stage_bg_rect = pygame.Rect(SCREEN_WIDTH - stage_text.get_width() - 30, 5, stage_text.get_width() + 20, stage_text.get_height() + 10)
        self.screen.blit(stage_bg, stage_bg_rect)
        self.screen.blit(stage_text, (SCREEN_WIDTH - stage_text.get_width() - 20, 10))
        
        # Stage progress bar (for timed stages)
        if current_stage.duration > 0:
            progress = self.stage_manager.get_stage_progress()
            
            # Progress bar background
            progress_bg = pygame.Surface((180, 15))
            progress_bg.fill(GRAY)
            progress_bg_rect = pygame.Rect(SCREEN_WIDTH - 200, 50, 180, 15)
            self.screen.blit(progress_bg, progress_bg_rect)
            
            # Progress bar fill with gradient
            if progress > 0:
                progress_width = int(180 * progress)
                progress_surface = pygame.Surface((progress_width, 15))
                
                # Create gradient from green to yellow to red
                for x in range(progress_width):
                    ratio = x / 180
                    if ratio < 0.5:
                        # Green to yellow
                        color = (int(255 * ratio * 2), 255, 0)
                    else:
                        # Yellow to red
                        color = (255, int(255 * (1 - (ratio - 0.5) * 2)), 0)
                    
                    pygame.draw.line(progress_surface, color, (x, 0), (x, 15))
                
                self.screen.blit(progress_surface, (SCREEN_WIDTH - 200, 50))
    
    def draw_settings_screen(self):
        # Draw background
        bg = self.graphics_manager.get_image('background')
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_font = self.font_manager.get_font('large', False)
        title_text = title_font.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Language setting with button graphics
        button_img = self.graphics_manager.get_image('button')
        lang_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 230, 300, 50)
        lang_button_scaled = pygame.transform.scale(button_img, (300, 50))
        self.screen.blit(lang_button_scaled, lang_button_rect)
        
        lang_text = "日本語モード: ON" if self.japanese_mode else "Japanese Mode: OFF"
        lang_font = self.font_manager.get_font('medium', self.japanese_mode)
        lang_surface = lang_font.render(lang_text, True, WHITE)
        lang_rect = lang_surface.get_rect(center=lang_button_rect.center)
        self.screen.blit(lang_surface, lang_rect)
        
        # Instructions with buttons
        instructions = [
            ("J: Toggle Language", "J: 言語切り替え"),
            ("B: Back to Menu", "B: メニューに戻る")
        ]
        
        for i, (en_text, jp_text) in enumerate(instructions):
            instruction_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 350 + i * 60, 200, 40)
            instruction_button_scaled = pygame.transform.scale(button_img, (200, 40))
            self.screen.blit(instruction_button_scaled, instruction_button_rect)
            
            text = jp_text if self.japanese_mode else en_text
            instruction_font = self.font_manager.get_font('small', self.japanese_mode)
            instruction_surface = instruction_font.render(text, True, LIGHT_GRAY)
            instruction_rect = instruction_surface.get_rect(center=instruction_button_rect.center)
            self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_result_screen(self):
        # Draw background
        bg = self.graphics_manager.get_image('background')
        self.screen.blit(bg, (0, 0))
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Result text
        result_font = self.font_manager.get_font('large', self.japanese_mode)
        if self.player_hp <= 0:
            result_text_str = "ゲームオーバー" if self.japanese_mode else "GAME OVER"
            result_text = result_font.render(result_text_str, True, RED)
        else:
            result_text_str = "ステージクリア" if self.japanese_mode else "STAGE CLEAR"
            result_text = result_font.render(result_text_str, True, GREEN)
        
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(result_text, result_rect)
        
        # Score with background
        score_font = self.font_manager.get_font('medium', self.japanese_mode)
        score_text_str = f"最終スコア: {self.score}" if self.japanese_mode else f"Final Score: {self.score}"
        score_text = score_font.render(score_text_str, True, WHITE)
        
        score_bg = pygame.Surface((score_text.get_width() + 40, score_text.get_height() + 20))
        score_bg.set_alpha(150)
        score_bg.fill(BLACK)
        score_bg_rect = score_bg.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_bg, score_bg_rect)
        
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Control buttons
        button_img = self.graphics_manager.get_image('button')
        
        # Restart button
        restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 50)
        self.screen.blit(button_img, restart_button_rect)
        restart_font = self.font_manager.get_font('medium', self.japanese_mode)
        restart_text_str = "R: リスタート" if self.japanese_mode else "R: Restart"
        restart_text = restart_font.render(restart_text_str, True, WHITE)
        restart_rect = restart_text.get_rect(center=restart_button_rect.center)
        self.screen.blit(restart_text, restart_rect)
        
        # Title button
        title_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 50)
        title_button_scaled = pygame.transform.scale(button_img, (200, 40))
        self.screen.blit(title_button_scaled, (title_button_rect.x, title_button_rect.y + 5))
        title_font = self.font_manager.get_font('small', self.japanese_mode)
        title_text_str = "T: タイトルへ" if self.japanese_mode else "T: Title"
        title_text = title_font.render(title_text_str, True, LIGHT_GRAY)
        title_rect = title_text.get_rect(center=(title_button_rect.centerx, title_button_rect.centery + 5))
        self.screen.blit(title_text, title_rect)
    
    def reset_game(self):
        self.score = 0
        self.combo = 0
        self.player_hp = self.max_hp
        self.enemies = []
        self.current_target = None
        self.current_input = ""
        self.enemy_spawn_timer = 0
        self.stage_manager = StageManager()
        self.typing_handler = TypingInputHandler()
        
        # BGMをリセット
        if self.sound_manager.enabled:
            self.sound_manager.stop_sound('bgm')
        self.bgm_playing = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.TITLE:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.GAME
                        self.reset_game()
                    elif event.key == pygame.K_s:
                        self.state = GameState.SETTINGS
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.state == GameState.SETTINGS:
                    if event.key == pygame.K_j:
                        self.japanese_mode = not self.japanese_mode
                    elif event.key == pygame.K_b:
                        self.state = GameState.TITLE
                
                elif self.state == GameState.GAME:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.TITLE
                        # ゲーム終了時にBGMを停止
                        if self.sound_manager.enabled:
                            self.sound_manager.stop_sound('bgm')
                            self.bgm_playing = False
                    elif event.unicode and len(event.unicode) == 1:
                        # Accept both alphabetic characters and Japanese characters
                        char = event.unicode
                        if char.isalpha() or ord(char) > 127:  # Include Japanese characters
                            print(f"Input detected: '{char}' (ord: {ord(char)})")  # Debug
                            self.handle_typing_input(char)
                
                elif self.state == GameState.RESULT:
                    if event.key == pygame.K_r:
                        self.state = GameState.GAME
                        self.reset_game()
                    elif event.key == pygame.K_t:
                        self.state = GameState.TITLE
    
    def update(self):
        if self.state == GameState.GAME:
            # BGMを開始（1回だけ）
            if self.sound_manager.enabled and not self.bgm_playing:
                self.sound_manager.play_sound('bgm')
                self.bgm_playing = True
            
            # エラーフラッシュタイマーの更新
            if self.error_flash_timer > 0:
                self.error_flash_timer -= 1
            
            # Update stage manager
            self.stage_manager.update(1.0 / FPS)
            current_stage = self.stage_manager.get_current_stage()
            
            # Spawn enemies
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= current_stage.enemy_spawn_delay:
                if len(self.enemies) < current_stage.max_enemies:
                    self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # Update enemies
            self.update_enemies()
            
            # Check stage completion
            if self.stage_manager.is_stage_complete(len(self.enemies)):
                self.stage_manager.next_stage()
                self.player_hp = min(self.max_hp, self.player_hp + 20)  # Bonus HP
            
            # Check game over
            if self.player_hp <= 0:
                self.state = GameState.RESULT
    
    def draw(self):
        if self.state == GameState.TITLE:
            self.draw_title_screen()
        elif self.state == GameState.GAME:
            self.draw_game_screen()
        elif self.state == GameState.RESULT:
            self.draw_result_screen()
        elif self.state == GameState.SETTINGS:
            self.draw_settings_screen()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TypingGame()
    game.run()
