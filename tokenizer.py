import re
from typing import Dict, List, Optional, Set


class Tokenizer:
    @staticmethod
    def tokenize(html: str, stop_words: Optional[Set] = None) -> List[str]:
        if stop_words is None:
            return re.findall(r'[a-zA-Z0-9]+', html)
        else:
            tmp = re.findall(r'[a-zA-Z0-9]+', html)
            ret = []
            for item in tmp:
                if item not in stop_words:
                    ret.append(item)
            return ret

    @staticmethod
    def compute_word_frequencies(word_list: List[str]) -> Dict[str, int]: # O(n)
        ret = {}
        for token in word_list:                                                 # n
            token_lower = token.lower()                                         # 1
            if token_lower in ret:
                ret[token_lower] += 1                                           # 1
            else:
                ret[token_lower] = 1                                            # 1
        return ret

    @staticmethod
    def print(token_freq: Dict[str, int]): # O(nlogn)
        if len(token_freq) == 0: return # 1

        for key, value in sorted(token_freq.items(), key=lambda item: item[1], reverse=True):   # nlogn + n
            print(f"{key} {value}")                                                             # 1

