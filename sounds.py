import pygame
import numpy as np
from typing import Dict

class SoundManager:
    def __init__(self):
        self.enabled = False
        
        # 複数の設定を試す
        audio_configs = [
            # WSL/Linux用設定
            {'frequency': 22050, 'size': -16, 'channels': 2, 'buffer': 512},
            {'frequency': 44100, 'size': -16, 'channels': 2, 'buffer': 1024},
            {'frequency': 22050, 'size': 16, 'channels': 1, 'buffer': 512},
            # フォールバック設定
            {'frequency': 11025, 'size': -16, 'channels': 1, 'buffer': 256},
        ]
        
        for config in audio_configs:
            try:
                pygame.mixer.quit()  # 既存の設定をクリア
                pygame.mixer.pre_init(**config)
                pygame.mixer.init()
                
                # テストサウンドを作成して再生テスト
                test_sound = self.create_test_sound()
                if test_sound:
                    self.enabled = True
                    print(f"Audio system initialized with config: {config}")
                    break
                    
            except Exception as e:
                print(f"Audio config {config} failed: {e}")
                continue
        
        if not self.enabled:
            print("Warning: All audio configurations failed, running in silent mode")
            # PulseAudioやALSAの設定を試す
            import os
            additional_drivers = ['pulse', 'alsa', 'dummy', 'winmm']
            
            for driver in additional_drivers:
                try:
                    os.environ['SDL_AUDIODRIVER'] = driver
                    pygame.mixer.quit()
                    pygame.mixer.init()
                    test_sound = self.create_test_sound()
                    if test_sound:
                        self.enabled = True
                        print(f"Audio enabled with {driver} driver")
                        break
                except Exception as e:
                    print(f"{driver} driver failed: {e}")
                    continue
            
            if not self.enabled:
                print("Audio unavailable - this is normal in WSL environments without audio setup")
                print("Game will continue without sound effects")
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        if self.enabled:
            self.generate_sounds()
        
    def create_test_sound(self):
        """テスト用の簡単なサウンドを作成"""
        try:
            sample_rate = pygame.mixer.get_init()[0] if pygame.mixer.get_init() else 22050
            duration = 0.1
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(440 * 2 * np.pi * t) * 0.1
            
            # サンプルフォーマットを確認
            if pygame.mixer.get_init()[1] < 0:  # signed
                wave = (wave * 32767).astype(np.int16)
            else:  # unsigned
                wave = ((wave + 1) * 32767).astype(np.uint16)
            
            # チャンネル数に応じて調整
            channels = pygame.mixer.get_init()[2] if pygame.mixer.get_init() else 2
            if channels == 2:
                stereo_wave = np.array([wave, wave]).T
                stereo_wave = np.ascontiguousarray(stereo_wave)  # C-contiguous配列にする
                return pygame.sndarray.make_sound(stereo_wave)
            else:
                wave = np.ascontiguousarray(wave)  # C-contiguous配列にする
                return pygame.sndarray.make_sound(wave)
        except Exception as e:
            print(f"Test sound creation failed: {e}")
            return None
    
    def generate_sounds(self):
        try:
            # ミキサーの設定を確認
            mixer_info = pygame.mixer.get_init()
            print(f"Mixer initialized: frequency={mixer_info[0]}, size={mixer_info[1]}, channels={mixer_info[2]}")
            
            self.sounds['hit'] = self.generate_hit_sound()
            self.sounds['defeat'] = self.generate_defeat_sound()
            self.sounds['damage'] = self.generate_damage_sound()
            self.sounds['type'] = self.generate_type_sound()
            self.sounds['error'] = self.generate_error_sound()
            self.sounds['bgm'] = self.generate_bgm()
            print(f"Generated {len(self.sounds)} sounds successfully")
        except Exception as e:
            print(f"Sound generation failed: {e}")
            print("Continuing without sound effects")
            self.enabled = False
        
    def _create_sound_wave(self, duration: float, frequency: float, envelope_func=None, volume: float = 0.5) -> pygame.mixer.Sound:
        """サウンド作成のヘルパー関数"""
        mixer_info = pygame.mixer.get_init()
        if not mixer_info:
            return None
        
        sample_rate, bit_depth, channels = mixer_info
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # 基本波形を生成
        wave = np.sin(frequency * 2 * np.pi * t)
        
        # エンベロープを適用
        if envelope_func:
            wave = wave * envelope_func(t)
        
        # 音量調整
        wave = wave * volume
        
        # ビット深度に応じて変換
        if bit_depth == 8:
            wave = ((wave + 1) * 127.5).astype(np.uint8)
        elif bit_depth == -8:
            wave = (wave * 127).astype(np.int8)
        elif bit_depth == 16:
            wave = ((wave + 1) * 32767.5).astype(np.uint16)
        elif bit_depth == -16:
            wave = (wave * 32767).astype(np.int16)
        else:
            wave = (wave * 32767).astype(np.int16)
        
        # チャンネル数に応じて調整
        if channels == 1:
            wave = np.ascontiguousarray(wave)
            return pygame.sndarray.make_sound(wave)
        else:  # stereo
            stereo_wave = np.array([wave, wave]).T
            stereo_wave = np.ascontiguousarray(stereo_wave)
            return pygame.sndarray.make_sound(stereo_wave)
    
    def generate_hit_sound(self) -> pygame.mixer.Sound:
        return self._create_sound_wave(0.1, 800, lambda t: np.exp(-t * 10), 0.3)
    
    def generate_defeat_sound(self) -> pygame.mixer.Sound:
        return self._create_sound_wave(0.3, 1200, lambda t: np.exp(-t * 5), 0.4)
    
    def generate_damage_sound(self) -> pygame.mixer.Sound:
        return self._create_sound_wave(0.5, 200, lambda t: (1 - t / 0.5), 0.2)
    
    def generate_type_sound(self) -> pygame.mixer.Sound:
        return self._create_sound_wave(0.05, 600, lambda t: np.exp(-t * 20), 0.1)
    
    def generate_error_sound(self) -> pygame.mixer.Sound:
        return self._create_sound_wave(0.2, 150, lambda t: (1 - t / 0.2), 0.3)
    
    def generate_bgm(self) -> pygame.mixer.Sound:
        """ゾンビバトル風のダークなBGMを生成"""
        mixer_info = pygame.mixer.get_init()
        if not mixer_info:
            return None
        
        duration = 12.0  # 12秒のループ（より長く）
        sample_rate, bit_depth, channels = mixer_info
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # ダークなマイナーキーのメロディ（A minor scale）
        # Am - F - C - G progression
        chord_freqs = [
            [220.0, 261.63, 329.63],  # Am chord
            [174.61, 220.0, 261.63],  # F chord  
            [130.81, 164.81, 196.0],  # C chord
            [196.0, 246.94, 293.66]   # G chord
        ]
        
        melody = np.zeros_like(t)
        bass = np.zeros_like(t)
        
        # 各コードを3秒ずつ演奏
        for i, chord in enumerate(chord_freqs):
            start_time = i * duration / 4
            end_time = (i + 1) * duration / 4
            mask = (t >= start_time) & (t < end_time)
            chord_t = t[mask] - start_time
            
            # 重厚なコード音
            for j, freq in enumerate(chord):
                envelope = 0.5 + 0.5 * np.cos(chord_t * 2 * np.pi / 3)  # ゆっくりとした変調
                melody[mask] += np.sin(freq * 2 * np.pi * chord_t) * envelope * 0.1
            
            # 重いベースライン
            bass_freq = chord[0] / 2  # オクターブ下
            bass_envelope = np.exp(-chord_t * 0.5) * (0.8 + 0.2 * np.sin(chord_t * 8))
            bass[mask] += np.sin(bass_freq * 2 * np.pi * chord_t) * bass_envelope * 0.15
        
        # ドラム的なリズム（ノイズベース）
        drum_pattern = np.zeros_like(t)
        beat_interval = duration / 16  # 16ビート
        for beat in range(16):
            beat_start = beat * beat_interval
            beat_end = beat_start + beat_interval * 0.2
            mask = (t >= beat_start) & (t < beat_end)
            if beat % 4 == 0:  # 強拍
                noise = np.random.normal(0, 0.3, np.sum(mask))
                drum_pattern[mask] = noise * np.exp(-(t[mask] - beat_start) * 20)
        
        # 合成
        bgm = melody + bass + drum_pattern * 0.2
        bgm = bgm * 0.25  # 音量調整
        
        # ビット深度に応じて変換
        if bit_depth == 8:
            bgm = ((bgm + 1) * 127.5).astype(np.uint8)
        elif bit_depth == -8:
            bgm = (bgm * 127).astype(np.int8)
        elif bit_depth == 16:
            bgm = ((bgm + 1) * 32767.5).astype(np.uint16)
        elif bit_depth == -16:
            bgm = (bgm * 32767).astype(np.int16)
        else:
            bgm = (bgm * 32767).astype(np.int16)
        
        # チャンネル数に応じて調整
        if channels == 1:
            bgm = np.ascontiguousarray(bgm)
            return pygame.sndarray.make_sound(bgm)
        else:  # stereo
            stereo_bgm = np.array([bgm, bgm]).T
            stereo_bgm = np.ascontiguousarray(stereo_bgm)
            return pygame.sndarray.make_sound(stereo_bgm)
    
    def play_sound(self, sound_name: str):
        if self.enabled and sound_name in self.sounds:
            try:
                if sound_name == 'bgm':
                    # BGMはループ再生
                    self.sounds[sound_name].play(-1)  # -1 で無限ループ
                else:
                    self.sounds[sound_name].play()
            except Exception as e:
                print(f"Failed to play sound {sound_name}: {e}")
    
    def stop_sound(self, sound_name: str):
        """特定のサウンドを停止"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
    def stop_all_sounds(self):
        """すべてのサウンドを停止"""
        if self.enabled:
            pygame.mixer.stop()
    
    def set_volume(self, volume: float):
        if self.enabled:
            for sound in self.sounds.values():
                sound.set_volume(volume)
    
    def set_sound_volume(self, sound_name: str, volume: float):
        """特定のサウンドの音量を設定"""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)