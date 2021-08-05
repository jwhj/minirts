import torch
import pickle
from transformers import BertTokenizer


class BERTInstructionDict:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self._max_sentence_length = 16

    @property
    def pad_word_idx(self):
        return self.tokenizer.pad_token_id

    @property
    def pad_inst_idx(self):
        return len(self._idx2inst) + 1
    
    @property
    def total_vocab_size(self):
        return self.tokenizer.vocab_size

    def get_inst_idx(self, *args):
        return 0
    
    def set_max_sentence_length(self, n):
        self._max_sentence_length = n

    def parse(self, inst, should_pad):
        x = self.tokenizer(inst, return_length=True, truncation=True, max_length=self._max_sentence_length, padding=True)
        if should_pad:
            for _ in range(self._max_sentence_length-x['length']):
                x['input_ids'].append(self.tokenizer.pad_token_id)
        return x['input_ids'], x['length']