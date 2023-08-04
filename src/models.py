import torch
from transformers import T5ForConditionalGeneration, AutoTokenizer, AutoConfig
import ctranslate2

class T5():
    def __init__(self, model_path, tokenizer_path):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.model = T5ForConditionalGeneration.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.config = AutoConfig.from_pretrained(tokenizer_path)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()

    def generate(self, input_ids, max_length=200):
        with torch.no_grad(), torch.autocast(device_type='cuda', dtype=torch.bfloat16):
            output_ids = self.model.generate(input_ids, max_length=max_length, do_sample=True, num_beams=4, length_penalty=2, repetition_penalty=2.5)
        output_text = self.tokenizer.decode(output_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return output_text

    def get_config(self):
        return self.config
    
class T5_CT2():
    def __init__(self, model_path, tokenizer_path, compute_type="float32"):
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.model = ctranslate2.Translator(model_path, device='cuda' if torch.cuda.is_available() else 'cpu',  compute_type=compute_type)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.config = AutoConfig.from_pretrained(tokenizer_path)

    def generate(self, input_ids, max_length=200):
        input_tokens = self.tokenizer.convert_ids_to_tokens(input_ids.squeeze())
        results = self.model.translate_batch([input_tokens], beam_size=4, max_decoding_length=max_length, length_penalty=2, repetition_penalty=2.5)
        output_tokens = results[0].hypotheses[0]
        return self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(output_tokens), clean_up_tokenization_spaces=True)
    
    def get_config(self):
        return self.config