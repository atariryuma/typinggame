#!/usr/bin/env python3

class RomajiConverter:
    def __init__(self):
        # ひらがなから可能なローマ字入力パターンのテーブル（複数の入力方法に対応）
        self.hiragana_to_romaji_patterns = {
            # 基本的な音
            'あ': ['a'], 'い': ['i'], 'う': ['u'], 'え': ['e'], 'お': ['o'],
            'か': ['ka'], 'き': ['ki'], 'く': ['ku'], 'け': ['ke'], 'こ': ['ko'],
            'が': ['ga'], 'ぎ': ['gi'], 'ぐ': ['gu'], 'げ': ['ge'], 'ご': ['go'],
            'さ': ['sa'], 'し': ['shi', 'si'], 'す': ['su'], 'せ': ['se'], 'そ': ['so'],
            'ざ': ['za'], 'じ': ['ji', 'zi'], 'ず': ['zu'], 'ぜ': ['ze'], 'ぞ': ['zo'],
            'た': ['ta'], 'ち': ['chi', 'ti'], 'つ': ['tsu', 'tu'], 'て': ['te'], 'と': ['to'],
            'だ': ['da'], 'ぢ': ['di'], 'づ': ['du'], 'で': ['de'], 'ど': ['do'],
            'な': ['na'], 'に': ['ni'], 'ぬ': ['nu'], 'ね': ['ne'], 'の': ['no'],
            'は': ['ha'], 'ひ': ['hi'], 'ふ': ['fu', 'hu'], 'へ': ['he'], 'ほ': ['ho'],
            'ば': ['ba'], 'び': ['bi'], 'ぶ': ['bu'], 'べ': ['be'], 'ぼ': ['bo'],
            'ぱ': ['pa'], 'ぴ': ['pi'], 'ぷ': ['pu'], 'ぺ': ['pe'], 'ぽ': ['po'],
            'ま': ['ma'], 'み': ['mi'], 'む': ['mu'], 'め': ['me'], 'も': ['mo'],
            'や': ['ya'], 'ゆ': ['yu'], 'よ': ['yo'],
            'ら': ['ra'], 'り': ['ri'], 'る': ['ru'], 'れ': ['re'], 'ろ': ['ro'],
            'わ': ['wa'], 'ゐ': ['wi'], 'ゑ': ['we'], 'を': ['wo'], 'ん': ['n', "n'", 'nn'],
            
            # 拗音（完全対応）
            'きゃ': ['kya'], 'きゅ': ['kyu'], 'きょ': ['kyo'],
            'しゃ': ['sha', 'sya'], 'しゅ': ['shu', 'syu'], 'しょ': ['sho', 'syo'],
            'ちゃ': ['cha', 'tya'], 'ちゅ': ['chu', 'tyu'], 'ちょ': ['cho', 'tyo'],
            'にゃ': ['nya'], 'にゅ': ['nyu'], 'にょ': ['nyo'],
            'ひゃ': ['hya'], 'ひゅ': ['hyu'], 'ひょ': ['hyo'],
            'みゃ': ['mya'], 'みゅ': ['myu'], 'みょ': ['myo'],
            'りゃ': ['rya'], 'りゅ': ['ryu'], 'りょ': ['ryo'],
            'ぎゃ': ['gya'], 'ぎゅ': ['gyu'], 'ぎょ': ['gyo'],
            'じゃ': ['ja', 'jya', 'zya'], 'じゅ': ['ju', 'jyu', 'zyu'], 'じょ': ['jo', 'jyo', 'zyo'],
            'びゃ': ['bya'], 'びゅ': ['byu'], 'びょ': ['byo'],
            'ぴゃ': ['pya'], 'ぴゅ': ['pyu'], 'ぴょ': ['pyo'],
            
            # 小文字系拗音（ひらがな）
            'きぇ': ['kye'], 'しぇ': ['she', 'sye'], 'ちぇ': ['che', 'tye'],
            'にぇ': ['nye'], 'ひぇ': ['hye'], 'みぇ': ['mye'], 'りぇ': ['rye'],
            'ぎぇ': ['gye'], 'じぇ': ['je', 'jye', 'zye'], 'びぇ': ['bye'], 'ぴぇ': ['pye'],
            
            # 小文字ぅ系（ひらがな）
            'くぁ': ['kwa'], 'くぃ': ['kwi'], 'くぅ': ['kwu'], 'くぇ': ['kwe'], 'くぉ': ['kwo'],
            'ぐぁ': ['gwa'], 'ぐぃ': ['gwi'], 'ぐぅ': ['gwu'], 'ぐぇ': ['gwe'], 'ぐぉ': ['gwo'],
            
            # その他（ひらがな）
            'つぃ': ['tsi'], 'でぃ': ['di'], 'でゅ': ['dyu'],
            'とぅ': ['tu'], 'どぅ': ['du'],
            'いぇ': ['ye'], 'うぇ': ['we'], 'うぉ': ['wo'],
            
            # 特殊な音
            'ー': ['-'], # 長音符
            
            # カタカナ（ひらがなと同じローマ字入力）
            'ア': ['a'], 'イ': ['i'], 'ウ': ['u'], 'エ': ['e'], 'オ': ['o'],
            'カ': ['ka'], 'キ': ['ki'], 'ク': ['ku'], 'ケ': ['ke'], 'コ': ['ko'],
            'ガ': ['ga'], 'ギ': ['gi'], 'グ': ['gu'], 'ゲ': ['ge'], 'ゴ': ['go'],
            'サ': ['sa'], 'シ': ['shi', 'si'], 'ス': ['su'], 'セ': ['se'], 'ソ': ['so'],
            'ザ': ['za'], 'ジ': ['ji', 'zi'], 'ズ': ['zu'], 'ゼ': ['ze'], 'ゾ': ['zo'],
            'タ': ['ta'], 'チ': ['chi', 'ti'], 'ツ': ['tsu', 'tu'], 'テ': ['te'], 'ト': ['to'],
            'ダ': ['da'], 'ヂ': ['di'], 'ヅ': ['du'], 'デ': ['de'], 'ド': ['do'],
            'ナ': ['na'], 'ニ': ['ni'], 'ヌ': ['nu'], 'ネ': ['ne'], 'ノ': ['no'],
            'ハ': ['ha'], 'ヒ': ['hi'], 'フ': ['fu', 'hu'], 'ヘ': ['he'], 'ホ': ['ho'],
            'バ': ['ba'], 'ビ': ['bi'], 'ブ': ['bu'], 'ベ': ['be'], 'ボ': ['bo'],
            'パ': ['pa'], 'ピ': ['pi'], 'プ': ['pu'], 'ペ': ['pe'], 'ポ': ['po'],
            'マ': ['ma'], 'ミ': ['mi'], 'ム': ['mu'], 'メ': ['me'], 'モ': ['mo'],
            'ヤ': ['ya'], 'ユ': ['yu'], 'ヨ': ['yo'],
            'ラ': ['ra'], 'リ': ['ri'], 'ル': ['ru'], 'レ': ['re'], 'ロ': ['ro'],
            'ワ': ['wa'], 'ヰ': ['wi'], 'ヱ': ['we'], 'ヲ': ['wo'], 'ン': ['n', "n'", 'nn'],
            
            # カタカナ拗音（完全対応）
            'キャ': ['kya'], 'キュ': ['kyu'], 'キョ': ['kyo'],
            'シャ': ['sha', 'sya'], 'シュ': ['shu', 'syu'], 'ショ': ['sho', 'syo'],
            'チャ': ['cha', 'tya'], 'チュ': ['chu', 'tyu'], 'チョ': ['cho', 'tyo'],
            'ニャ': ['nya'], 'ニュ': ['nyu'], 'ニョ': ['nyo'],
            'ヒャ': ['hya'], 'ヒュ': ['hyu'], 'ヒョ': ['hyo'],
            'ミャ': ['mya'], 'ミュ': ['myu'], 'ミョ': ['myo'],
            'リャ': ['rya'], 'リュ': ['ryu'], 'リョ': ['ryo'],
            'ギャ': ['gya'], 'ギュ': ['gyu'], 'ギョ': ['gyo'],
            'ジャ': ['ja', 'jya', 'zya'], 'ジュ': ['ju', 'jyu', 'zyu'], 'ジョ': ['jo', 'jyo', 'zyo'],
            'ビャ': ['bya'], 'ビュ': ['byu'], 'ビョ': ['byo'],
            'ピャ': ['pya'], 'ピュ': ['pyu'], 'ピョ': ['pyo'],
            
            # 小文字系拗音（追加）
            'キェ': ['kye'], 'シェ': ['she', 'sye'], 'チェ': ['che', 'tye'],
            'ニェ': ['nye'], 'ヒェ': ['hye'], 'ミェ': ['mye'], 'リェ': ['rye'],
            'ギェ': ['gye'], 'ジェ': ['je', 'jye', 'zye'], 'ビェ': ['bye'], 'ピェ': ['pye'],
            
            # 小文字ゥ系
            'クァ': ['kwa'], 'クィ': ['kwi'], 'クゥ': ['kwu'], 'クェ': ['kwe'], 'クォ': ['kwo'],
            'グァ': ['gwa'], 'グィ': ['gwi'], 'グゥ': ['gwu'], 'グェ': ['gwe'], 'グォ': ['gwo'],
            
            # 小文字ィ系追加
            'ツィ': ['tsi'], 'ディ': ['di'], 'デュ': ['dyu'],
            'トゥ': ['tu'], 'ドゥ': ['du'],
            
            # その他の外来語音
            'イェ': ['ye'], 'ウェ': ['we'], 'ウォ': ['wo'],
            'ヴィ': ['vi'], 'ヴェ': ['ve'], 'ヴォ': ['vo'], 'ヴャ': ['vya'], 'ヴュ': ['vyu'], 'ヴョ': ['vyo'],
            
            # 外来語用特殊文字
            'ファ': ['fa'], 'フィ': ['fi'], 'フェ': ['fe'], 'フォ': ['fo'],
            'ティ': ['ti'], 'ディ': ['di'],
            'ウィ': ['wi'], 'ウェ': ['we'], 'ウォ': ['wo'],
            'ヴァ': ['va'], 'ヴィ': ['vi'], 'ヴ': ['vu'], 'ヴェ': ['ve'], 'ヴォ': ['vo'],
        }
        
        # 逆変換テーブル（ローマ字からひらがな）
        self.romaji_to_hiragana = {}
        for hiragana, romaji_list in self.hiragana_to_romaji_patterns.items():
            for romaji in romaji_list:
                self.romaji_to_hiragana[romaji] = hiragana
        
    def get_possible_romaji_patterns(self, hiragana_char: str) -> list:
        """特定のひらがな文字に対する可能なローマ字入力パターンのリストを返す"""
        return self.hiragana_to_romaji_patterns.get(hiragana_char, [])
    
    def is_partial_match_any_pattern(self, input_romaji: str, hiragana_char: str) -> bool:
        """入力中のローマ字が、その文字のいずれかのパターンの一部かどうかチェック"""
        patterns = self.get_possible_romaji_patterns(hiragana_char)
        for pattern in patterns:
            if pattern.startswith(input_romaji):
                return True
        return False
    
    def get_matching_patterns(self, input_romaji: str, hiragana_char: str) -> list:
        """入力にマッチする可能性のあるパターンリストを返す"""
        patterns = self.get_possible_romaji_patterns(hiragana_char)
        matching = []
        for pattern in patterns:
            if pattern.startswith(input_romaji):
                matching.append(pattern)
        return matching
    
    def is_complete_match(self, input_romaji: str, hiragana_char: str) -> bool:
        """入力が完全にその文字のいずれかのパターンとマッチするかチェック"""
        patterns = self.get_possible_romaji_patterns(hiragana_char)
        return input_romaji in patterns
    
    def get_next_possible_chars(self, input_romaji: str, hiragana_char: str) -> list:
        """次に入力可能な文字のリストを返す"""
        matching_patterns = self.get_matching_patterns(input_romaji, hiragana_char)
        next_chars = set()
        for pattern in matching_patterns:
            if len(input_romaji) < len(pattern):
                next_chars.add(pattern[len(input_romaji)])
        return list(next_chars)

class TypingInputHandler:
    def __init__(self):
        self.converter = RomajiConverter()
        self.current_romaji_input = ""
        self.target_text = ""
        self.current_char_index = 0
        
    def set_target_text(self, text: str):
        """ターゲットテキストを設定"""
        self.target_text = text
        self.current_char_index = 0
        self.current_romaji_input = ""
        
    def get_current_target_char(self) -> str:
        """現在入力すべき文字を取得"""
        if self.current_char_index < len(self.target_text):
            return self.target_text[self.current_char_index]
        return ""
    
    def process_input(self, char: str) -> dict:
        """
        入力文字を処理（複数パターン対応版）
        戻り値: {
            'success': bool,  # 正しい入力か
            'char_completed': bool,  # 文字が完成したか
            'word_completed': bool,  # 単語が完成したか
            'expected_next': list  # 次に期待される文字のリスト
        }
        """
        result = {
            'success': False,
            'char_completed': False,
            'word_completed': False,
            'expected_next': []
        }
        
        if self.current_char_index >= len(self.target_text):
            return result
        
        target_char = self.get_current_target_char()
        test_input = self.current_romaji_input + char
        
        print(f"Processing: '{char}' for target '{target_char}', current input: '{self.current_romaji_input}' -> '{test_input}'")
        
        # 複数パターンでの部分一致チェック
        if self.converter.is_partial_match_any_pattern(test_input, target_char):
            self.current_romaji_input = test_input
            result['success'] = True
            print(f"Partial match found for '{test_input}' with '{target_char}'")
            
            # 文字完成チェック
            if self.converter.is_complete_match(test_input, target_char):
                result['char_completed'] = True
                self.current_char_index += 1
                self.current_romaji_input = ""
                print(f"Character '{target_char}' completed with '{test_input}'")
                
                # 単語完成チェック
                if self.current_char_index >= len(self.target_text):
                    result['word_completed'] = True
                    print(f"Word completed!")
        else:
            print(f"No match found for '{test_input}' with '{target_char}'")
        
        # 次に期待される文字のリストを設定
        if not result['word_completed']:
            current_target_char = self.get_current_target_char()
            if current_target_char:
                result['expected_next'] = self.converter.get_next_possible_chars(
                    self.current_romaji_input, current_target_char
                )
        
        return result
    
    def get_typed_portion(self) -> str:
        """入力済みの部分を取得"""
        return self.target_text[:self.current_char_index]
    
    def get_remaining_portion(self) -> str:
        """未入力の部分を取得"""
        return self.target_text[self.current_char_index:]
    
    def get_current_input_display(self) -> str:
        """現在の入力状況を表示用に取得"""
        if self.current_romaji_input:
            target_char = self.get_current_target_char()
            if target_char:
                patterns = self.converter.get_matching_patterns(self.current_romaji_input, target_char)
                return f"[{self.current_romaji_input}] ({'/'.join(patterns)})"
            return f"[{self.current_romaji_input}]"
        return ""
    
    def reset_current_char_input(self):
        """現在の文字の入力のみをリセット（単語の進行は保持）"""
        self.current_romaji_input = ""
    
    def get_progress_info(self) -> dict:
        """入力進行状況の詳細情報を取得"""
        return {
            'typed_chars': self.current_char_index,
            'total_chars': len(self.target_text),
            'current_romaji': self.current_romaji_input,
            'current_target_char': self.get_current_target_char(),
            'expected_next': self.converter.get_next_possible_chars(
                self.current_romaji_input, self.get_current_target_char()
            ) if self.get_current_target_char() else []
        }