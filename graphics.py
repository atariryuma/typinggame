import pygame
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Tuple, List
import io
import os
from pathlib import Path
import math
import random

class GraphicsManager:
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, List[pygame.Surface]] = {}
        self.create_graphics()
        self.create_animations()
    
    def create_graphics(self):
        self.images['zombie'] = self.create_zombie_sprite()
        self.images['runner'] = self.create_runner_sprite()
        self.images['shooter'] = self.create_shooter_sprite()
        self.images['background'] = self.create_background()
        self.images['button'] = self.create_button()
        self.images['textbox'] = self.create_textbox()
        self.images['hp_bar_bg'] = self.create_hp_bar_bg()
        self.images['hp_bar'] = self.create_hp_bar()
    
    def create_zombie_sprite(self) -> pygame.Surface:
        """高品質なピクセルアートゾンビスプライト"""
        size = 80
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # ピクセルアート風の詳細なゾンビ
        # 体（破れたシャツ）
        body_color = (60, 80, 60)  # ダークグリーン
        draw.rectangle([25, 30, 55, 70], fill=body_color)
        # シャツの破れ
        draw.rectangle([30, 35, 32, 45], fill=(40, 60, 40))
        draw.rectangle([45, 40, 47, 50], fill=(40, 60, 40))
        
        # 頭（腐った肌色）
        head_color = (120, 140, 100)
        draw.rectangle([20, 10, 60, 35], fill=head_color)
        # 頭の傷
        draw.rectangle([25, 15, 27, 20], fill=(80, 40, 40))
        draw.rectangle([50, 12, 52, 18], fill=(80, 40, 40))
        
        # 目（赤く光る）
        draw.rectangle([25, 18, 30, 23], fill=(255, 50, 50))
        draw.rectangle([50, 18, 55, 23], fill=(255, 50, 50))
        # 瞳孔
        draw.rectangle([27, 20, 28, 21], fill=(100, 0, 0))
        draw.rectangle([52, 20, 53, 21], fill=(100, 0, 0))
        
        # 口（開いている）
        draw.rectangle([35, 25, 45, 30], fill=(40, 20, 20))
        # 歯
        draw.rectangle([37, 25, 38, 28], fill=(200, 200, 180))
        draw.rectangle([42, 25, 43, 28], fill=(200, 200, 180))
        
        # 腕（ゾンビ特有の動き）
        arm_color = (100, 120, 80)
        draw.rectangle([10, 35, 25, 45], fill=arm_color)  # 左腕
        draw.rectangle([55, 40, 70, 50], fill=arm_color)  # 右腕
        
        # 手
        draw.rectangle([5, 40, 15, 50], fill=head_color)
        draw.rectangle([65, 45, 75, 55], fill=head_color)
        
        # 足
        leg_color = (40, 60, 80)  # ズボン
        draw.rectangle([25, 70, 35, 78], fill=leg_color)
        draw.rectangle([45, 70, 55, 78], fill=leg_color)
        
        # 靴
        draw.rectangle([20, 75, 40, 78], fill=(20, 20, 20))
        draw.rectangle([40, 75, 60, 78], fill=(20, 20, 20))
        
        return self.pil_to_pygame(img)
    
    def create_runner_sprite(self) -> pygame.Surface:
        size = 50
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Body (orange, more lean)
        draw.ellipse([12, 18, 38, 45], fill=(255, 165, 0))
        
        # Head
        draw.ellipse([15, 3, 35, 23], fill=(255, 140, 0))
        
        # Eyes (glowing)
        draw.ellipse([18, 8, 22, 12], fill=(255, 255, 0))
        draw.ellipse([28, 8, 32, 12], fill=(255, 255, 0))
        
        # Speed lines
        for i in range(3):
            y = 20 + i * 8
            draw.line([0, y, 10, y], fill=(255, 255, 255), width=2)
        
        return self.pil_to_pygame(img)
    
    def create_shooter_sprite(self) -> pygame.Surface:
        size = 65
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Body (purple, bulkier)
        draw.ellipse([8, 22, 57, 58], fill=(128, 0, 128))
        
        # Head
        draw.ellipse([18, 5, 47, 35], fill=(148, 0, 211))
        
        # Eyes (menacing)
        draw.ellipse([23, 12, 28, 17], fill=(255, 0, 0))
        draw.ellipse([37, 12, 42, 17], fill=(255, 0, 0))
        
        # Weapon (gun barrel)
        draw.rectangle([50, 20, 62, 25], fill=(64, 64, 64))
        
        # Armor plating
        draw.rectangle([15, 30, 50, 35], fill=(75, 0, 130))
        draw.rectangle([15, 40, 50, 45], fill=(75, 0, 130))
        
        return self.pil_to_pygame(img)
    
    def create_background(self) -> pygame.Surface:
        """ピクセルアート風の詳細な背景"""
        img = Image.new('RGB', (1200, 800), (15, 15, 30))  # より暗い夜空
        draw = ImageDraw.Draw(img)
        
        # 詳細なピクセルアート都市のスカイライン
        buildings = [
            {'x1': 0, 'y1': 620, 'x2': 180, 'y2': 800, 'style': 'apartment'},
            {'x1': 180, 'y1': 580, 'x2': 320, 'y2': 800, 'style': 'office'},
            {'x1': 320, 'y1': 600, 'x2': 460, 'y2': 800, 'style': 'residential'},
            {'x1': 460, 'y1': 540, 'x2': 600, 'y2': 800, 'style': 'skyscraper'},
            {'x1': 600, 'y1': 590, 'x2': 740, 'y2': 800, 'style': 'office'},
            {'x1': 740, 'y1': 560, 'x2': 880, 'y2': 800, 'style': 'apartment'},
            {'x1': 880, 'y1': 610, 'x2': 1020, 'y2': 800, 'style': 'residential'},
            {'x1': 1020, 'y1': 570, 'x2': 1200, 'y2': 800, 'style': 'factory'}
        ]
        
        for building in buildings:
            x1, y1, x2, y2 = building['x1'], building['y1'], building['x2'], building['y2']
            style = building['style']
            
            # 建物の基本色
            if style == 'skyscraper':
                base_color = (8, 8, 20)
            elif style == 'office':
                base_color = (12, 12, 25)
            elif style == 'apartment':
                base_color = (15, 10, 20)
            elif style == 'residential':
                base_color = (10, 15, 18)
            else:  # factory
                base_color = (20, 15, 10)
            
            # 建物本体
            draw.rectangle([x1, y1, x2, y2], fill=base_color)
            
            # 建物の詳細
            if style == 'skyscraper':
                # 高層ビルの特徴
                for floor in range(y1 + 20, y2, 25):
                    # フロア区切り
                    draw.rectangle([x1, floor, x2, floor + 2], fill=(25, 25, 40))
                    # 窓の列
                    for wx in range(x1 + 15, x2 - 15, 25):
                        if random.random() > 0.4:  # ランダムに点灯
                            color = (255, 255, 200) if random.random() > 0.8 else (80, 80, 120)
                            draw.rectangle([wx, floor + 5, wx + 12, floor + 18], fill=color)
                            # 窓枠
                            draw.rectangle([wx - 1, floor + 4, wx + 13, floor + 19], outline=(40, 40, 60), width=1)
            
            elif style == 'office':
                # オフィスビル
                for floor_y in range(y1 + 15, y2, 20):
                    for wx in range(x1 + 12, x2 - 12, 18):
                        if random.random() > 0.3:
                            color = (120, 140, 180) if random.random() > 0.7 else (60, 60, 90)
                            draw.rectangle([wx, floor_y, wx + 10, floor_y + 12], fill=color)
            
            elif style == 'apartment':
                # アパート
                for floor_y in range(y1 + 12, y2, 15):
                    for wx in range(x1 + 8, x2 - 8, 15):
                        if random.random() > 0.5:
                            color = (180, 160, 120) if random.random() > 0.6 else (40, 35, 50)
                            draw.rectangle([wx, floor_y, wx + 8, floor_y + 8], fill=color)
            
            # 屋上の詳細
            if style in ['skyscraper', 'office']:
                # アンテナ
                antenna_x = x1 + (x2 - x1) // 2
                draw.rectangle([antenna_x, y1 - 20, antenna_x + 2, y1], fill=(100, 100, 100))
                # 赤いライト
                draw.rectangle([antenna_x - 1, y1 - 20, antenna_x + 3, y1 - 18], fill=(255, 50, 50))
        
        # 改善された月
        moon_x, moon_y = 950, 80
        # 月の本体
        draw.ellipse([moon_x, moon_y, moon_x + 80, moon_y + 80], fill=(220, 220, 200))
        # 月のクレーター
        draw.ellipse([moon_x + 15, moon_y + 20, moon_x + 25, moon_y + 30], fill=(200, 200, 180))
        draw.ellipse([moon_x + 45, moon_y + 35, moon_x + 55, moon_y + 45], fill=(200, 200, 180))
        draw.ellipse([moon_x + 30, moon_y + 50, moon_x + 40, moon_y + 60], fill=(200, 200, 180))
        
        # 星とちらつき効果
        for _ in range(80):
            x = random.randint(0, 1200)
            y = random.randint(0, 400)
            # さまざまなサイズの星
            star_size = random.choice([1, 2, 3])
            brightness = random.randint(180, 255)
            color = (brightness, brightness, brightness)
            
            if star_size == 1:
                draw.rectangle([x, y, x + 1, y + 1], fill=color)
            elif star_size == 2:
                draw.rectangle([x, y, x + 2, y + 2], fill=color)
                # 十字の光
                draw.rectangle([x - 1, y + 1, x + 3, y + 1], fill=(brightness//2, brightness//2, brightness//2))
                draw.rectangle([x + 1, y - 1, x + 1, y + 3], fill=(brightness//2, brightness//2, brightness//2))
            else:  # 大きな星
                draw.rectangle([x, y, x + 3, y + 3], fill=color)
                # 大きな十字光
                draw.rectangle([x - 2, y + 1, x + 5, y + 2], fill=(brightness//3, brightness//3, brightness//3))
                draw.rectangle([x + 1, y - 2, x + 2, y + 5], fill=(brightness//3, brightness//3, brightness//3))
        
        # 薄い雲
        for _ in range(5):
            cloud_x = random.randint(100, 1000)
            cloud_y = random.randint(50, 200)
            cloud_color = (25, 25, 35)
            # 雲の形状を不規則に
            for i in range(8):
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-8, 8)
                draw.ellipse([cloud_x + offset_x, cloud_y + offset_y, 
                            cloud_x + offset_x + 40, cloud_y + offset_y + 15], fill=cloud_color)
        
        return self.pil_to_pygame(img)
    
    def create_button(self) -> pygame.Surface:
        img = Image.new('RGBA', (200, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Button background with gradient effect
        draw.rounded_rectangle([0, 0, 200, 50], radius=10, fill=(70, 70, 100))
        draw.rounded_rectangle([2, 2, 198, 48], radius=8, fill=(90, 90, 130))
        draw.rounded_rectangle([4, 4, 196, 46], radius=6, fill=(110, 110, 160))
        
        return self.pil_to_pygame(img)
    
    def create_textbox(self) -> pygame.Surface:
        img = Image.new('RGBA', (120, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Text box with border
        draw.rounded_rectangle([0, 0, 120, 30], radius=5, fill=(240, 240, 240))
        draw.rounded_rectangle([2, 2, 118, 28], radius=3, outline=(100, 100, 100), width=2)
        
        return self.pil_to_pygame(img)
    
    def create_hp_bar_bg(self) -> pygame.Surface:
        img = Image.new('RGBA', (200, 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # HP bar background
        draw.rounded_rectangle([0, 0, 200, 20], radius=10, fill=(60, 0, 0))
        draw.rounded_rectangle([2, 2, 198, 18], radius=8, fill=(100, 0, 0))
        
        return self.pil_to_pygame(img)
    
    def create_hp_bar(self) -> pygame.Surface:
        img = Image.new('RGBA', (196, 16), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # HP bar fill (gradient)
        for x in range(196):
            red = 255 - int(x * 100 / 196)
            green = int(x * 150 / 196)
            color = (red, green, 0)
            draw.line([x, 0, x, 16], fill=color)
        
        return self.pil_to_pygame(img)
    
    def pil_to_pygame(self, pil_image: Image.Image) -> pygame.Surface:
        # Convert PIL image to pygame surface
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()
        
        return pygame.image.fromstring(data, size, mode)
    
    def create_animations(self):
        """アニメーションフレームを作成"""
        self.animations['zombie_walk'] = self.create_zombie_walk_animation()
        self.animations['runner_walk'] = self.create_runner_walk_animation()
        self.animations['shooter_walk'] = self.create_shooter_walk_animation()
    
    def create_zombie_walk_animation(self) -> List[pygame.Surface]:
        """ゾンビの歩行アニメーション（4フレーム）"""
        frames = []
        
        for frame in range(4):
            # フレームごとに少しずつ位置を調整
            size = 80
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 歩行に合わせた体の揺れ
            sway = math.sin(frame * math.pi / 2) * 2
            bob = abs(math.sin(frame * math.pi / 2)) * 1
            
            # ベーススプライトをコピーして変更
            body_color = (60, 80, 60)
            head_color = (120, 140, 100)
            arm_color = (100, 120, 80)
            leg_color = (40, 60, 80)
            
            # 体（わずかに揺れる）
            offset_x = int(sway)
            offset_y = int(bob)
            
            draw.rectangle([25 + offset_x, 30 - offset_y, 55 + offset_x, 70 - offset_y], fill=body_color)
            
            # 頭
            draw.rectangle([20 + offset_x, 10 - offset_y, 60 + offset_x, 35 - offset_y], fill=head_color)
            draw.rectangle([25 + offset_x, 15 - offset_y, 27 + offset_x, 20 - offset_y], fill=(80, 40, 40))
            draw.rectangle([50 + offset_x, 12 - offset_y, 52 + offset_x, 18 - offset_y], fill=(80, 40, 40))
            
            # 目
            draw.rectangle([25 + offset_x, 18 - offset_y, 30 + offset_x, 23 - offset_y], fill=(255, 50, 50))
            draw.rectangle([50 + offset_x, 18 - offset_y, 55 + offset_x, 23 - offset_y], fill=(255, 50, 50))
            draw.rectangle([27 + offset_x, 20 - offset_y, 28 + offset_x, 21 - offset_y], fill=(100, 0, 0))
            draw.rectangle([52 + offset_x, 20 - offset_y, 53 + offset_x, 21 - offset_y], fill=(100, 0, 0))
            
            # 口
            draw.rectangle([35 + offset_x, 25 - offset_y, 45 + offset_x, 30 - offset_y], fill=(40, 20, 20))
            
            # 腕（歩行に合わせて動く）
            arm_swing = math.sin(frame * math.pi / 2) * 5
            draw.rectangle([10 + int(arm_swing), 35 + offset_x, 25 + int(arm_swing), 45 + offset_x], fill=arm_color)
            draw.rectangle([55 - int(arm_swing), 40 + offset_x, 70 - int(arm_swing), 50 + offset_x], fill=arm_color)
            
            # 足（歩行アニメーション）
            leg_offset = math.sin(frame * math.pi / 2) * 3
            draw.rectangle([25 + int(leg_offset), 70, 35 + int(leg_offset), 78], fill=leg_color)
            draw.rectangle([45 - int(leg_offset), 70, 55 - int(leg_offset), 78], fill=leg_color)
            
            # 靴
            draw.rectangle([20 + int(leg_offset), 75, 40 + int(leg_offset), 78], fill=(20, 20, 20))
            draw.rectangle([40 - int(leg_offset), 75, 60 - int(leg_offset), 78], fill=(20, 20, 20))
            
            frames.append(self.pil_to_pygame(img))
        
        return frames
    
    def create_runner_walk_animation(self) -> List[pygame.Surface]:
        """ランナーの高速移動アニメーション"""
        frames = []
        for frame in range(6):  # より高速なアニメーション
            size = 70
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 高速移動エフェクト
            lean = math.sin(frame * math.pi / 3) * 8  # より大きな傾き
            
            # 体（前傾姿勢）
            body_color = (255, 140, 0)
            draw.rectangle([20 + int(lean), 25, 45 + int(lean), 55], fill=body_color)
            
            # 頭
            head_color = (255, 120, 0)
            draw.rectangle([15 + int(lean), 8, 40 + int(lean), 28], fill=head_color)
            
            # 目（集中した表情）
            draw.rectangle([20 + int(lean), 15, 24 + int(lean), 18], fill=(255, 255, 100))
            draw.rectangle([32 + int(lean), 15, 36 + int(lean), 18], fill=(255, 255, 100))
            
            # 足（高速移動）
            leg_motion = math.sin(frame * math.pi / 1.5) * 12
            draw.rectangle([20 + int(leg_motion), 55, 25 + int(leg_motion), 68], fill=(100, 60, 0))
            draw.rectangle([35 - int(leg_motion), 55, 40 - int(leg_motion), 68], fill=(100, 60, 0))
            
            # スピードライン
            for i in range(5):
                line_y = 15 + i * 10
                draw.rectangle([0, line_y, 15, line_y + 2], fill=(255, 255, 255))
            
            frames.append(self.pil_to_pygame(img))
        
        return frames
    
    def create_shooter_walk_animation(self) -> List[pygame.Surface]:
        """シューターの警戒歩行アニメーション"""
        frames = []
        for frame in range(4):
            size = 85
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 警戒しながらの歩行
            bob = math.sin(frame * math.pi / 2) * 1
            
            # 体（重装備）
            body_color = (80, 0, 80)
            draw.rectangle([25, 30 - int(bob), 60, 65 - int(bob)], fill=body_color)
            
            # 頭
            head_color = (100, 0, 120)
            draw.rectangle([25, 8 - int(bob), 55, 35 - int(bob)], fill=head_color)
            
            # 目（警戒）
            draw.rectangle([30, 18 - int(bob), 35, 23 - int(bob)], fill=(255, 0, 0))
            draw.rectangle([45, 18 - int(bob), 50, 23 - int(bob)], fill=(255, 0, 0))
            
            # 武器（常に構えている）
            weapon_sway = math.sin(frame * math.pi / 4) * 2
            draw.rectangle([55 + int(weapon_sway), 25 - int(bob), 75 + int(weapon_sway), 30 - int(bob)], fill=(40, 40, 40))
            
            # 足（重い歩行）
            leg_step = int(math.sin(frame * math.pi / 2) * 4)
            draw.rectangle([30 + leg_step, 65, 38 + leg_step, 78], fill=(40, 0, 60))
            draw.rectangle([47 - leg_step, 65, 55 - leg_step, 78], fill=(40, 0, 60))
            
            frames.append(self.pil_to_pygame(img))
        
        return frames
    
    def get_image(self, name: str) -> pygame.Surface:
        return self.images.get(name, pygame.Surface((1, 1)))
    
    def get_animation_frame(self, animation_name: str, frame: int) -> pygame.Surface:
        """アニメーションフレームを取得"""
        if animation_name in self.animations:
            frames = self.animations[animation_name]
            return frames[frame % len(frames)]
        return self.get_image('zombie')  # フォールバック

class FontManager:
    def __init__(self):
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.setup_fonts()
    
    def setup_fonts(self):
        # Check for downloaded font first
        current_dir = Path(__file__).parent
        downloaded_font = current_dir / "fonts" / "NotoSansJP-Regular.ttf"
        
        # Try to find Japanese fonts including WSL Windows fonts
        japanese_fonts = [
            str(downloaded_font),  # Downloaded font
            '/mnt/c/Windows/Fonts/NotoSansJP-VF.ttf',  # WSL Windows Noto Sans JP
            '/mnt/c/Windows/Fonts/BIZ-UDGothicR.ttc',  # WSL Windows BIZ UD Gothic
            '/mnt/c/Windows/Fonts/msgothic.ttc',  # WSL Windows MS Gothic
            '/mnt/c/Windows/Fonts/meiryo.ttc',  # WSL Windows Meiryo
            '/mnt/c/Windows/Fonts/msmincho.ttc',  # WSL Windows MS Mincho
            'C:/Windows/Fonts/msgothic.ttc',  # Windows
            'C:/Windows/Fonts/meiryo.ttc',  # Windows
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',  # macOS
            '/System/Library/Fonts/Hiragino Sans GB.ttc',  # macOS alternative
            '/usr/share/fonts/truetype/takao-gothic/TakaoGothic.ttf',  # Linux
            '/usr/share/fonts/truetype/noto-cjk/NotoSansCJK-Regular.ttc',  # Linux
        ]
        
        japanese_font = None
        for font_path in japanese_fonts:
            try:
                if os.path.exists(font_path):
                    japanese_font = pygame.font.Font(font_path, 32)
                    print(f"Japanese font loaded: {font_path}")
                    break
                else:
                    print(f"Font not found: {font_path}")
            except (FileNotFoundError, OSError) as e:
                print(f"Failed to load font {font_path}: {e}")
                continue
        
        if japanese_font is None:
            # Try system fonts with specific names
            system_font_names = [
                'msgothic',
                'meiryo', 
                'ms gothic',
                'takao gothic',
                'noto sans cjk jp',
                'dejavu sans',
                'liberation sans'
            ]
            
            for font_name in system_font_names:
                try:
                    japanese_font = pygame.font.SysFont(font_name, 32)
                    if japanese_font:
                        print(f"System Japanese font loaded: {font_name}")
                        break
                except:
                    continue
        
        if japanese_font is None:
            # Try to download font if not found
            try:
                from download_font import download_japanese_font
                downloaded_path = download_japanese_font()
                if downloaded_path:
                    japanese_font = pygame.font.Font(downloaded_path, 32)
                    print(f"Downloaded and loaded Japanese font: {downloaded_path}")
            except Exception as e:
                print(f"Failed to download font: {e}")
        
        if japanese_font is None:
            japanese_font = pygame.font.Font(None, 32)
            print("Warning: No Japanese font found, using default font")
        
        # Set up font sizes (larger fonts for better visibility)
        self.fonts['japanese_large'] = japanese_font  # 32px
        
        # Get the actual font file path for creating different sizes
        font_file_path = None
        for font_path in japanese_fonts:
            if os.path.exists(font_path):
                try:
                    # Test if this font works
                    test_font = pygame.font.Font(font_path, 32)
                    font_file_path = font_path
                    break
                except:
                    continue
        
        try:
            if font_file_path:
                self.fonts['japanese_medium'] = pygame.font.Font(font_file_path, 28)  # Increased from 24
                self.fonts['japanese_small'] = pygame.font.Font(font_file_path, 24)   # Increased from 18
                self.fonts['japanese_xlarge'] = pygame.font.Font(font_file_path, 48)  # New extra large
                print(f"All Japanese font sizes created from: {font_file_path}")
            else:
                self.fonts['japanese_medium'] = pygame.font.Font(None, 28)
                self.fonts['japanese_small'] = pygame.font.Font(None, 24)
                self.fonts['japanese_xlarge'] = pygame.font.Font(None, 48)
        except Exception as e:
            print(f"Error creating font sizes: {e}")
            self.fonts['japanese_medium'] = pygame.font.Font(None, 28)
            self.fonts['japanese_small'] = pygame.font.Font(None, 24)
            self.fonts['japanese_xlarge'] = pygame.font.Font(None, 48)
        
        # English fonts (also increased sizes)
        self.fonts['english_xlarge'] = pygame.font.Font(None, 56)  # New extra large
        self.fonts['english_large'] = pygame.font.Font(None, 48)
        self.fonts['english_medium'] = pygame.font.Font(None, 36)  # Increased from 32
        self.fonts['english_small'] = pygame.font.Font(None, 28)   # Increased from 24
    
    def get_font(self, name: str, japanese: bool = False) -> pygame.font.Font:
        prefix = 'japanese_' if japanese else 'english_'
        font_key = prefix + name
        font = self.fonts.get(font_key, self.fonts.get('english_medium'))
        return font