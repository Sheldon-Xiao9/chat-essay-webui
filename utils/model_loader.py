import os
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class ModelLoader:
    def __init__(self):
        self.chat_model = None
        self.embedding_model = None
        
    def load_chat_model(self):
        """加载本地chat模型"""
        if not self.chat_model:
            model_path = "models/chat"
            
            # 加载tokenizer和模型
            tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # 创建pipeline
            pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                return_full_text=False,  # 只返回新生成的文本
                do_sample=True,  # 使用采样
                max_new_tokens=2048,
                temperature=0.7,
                top_p=0.95,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                device_map="auto"
            )
            
            # 创建LangChain的LLM
            self.chat_model = HuggingFacePipeline(
                pipeline=pipe,
                model_kwargs={"temperature": 0.7}
            )
            
        return self.chat_model
    
    def load_embedding_model(self):
        """加载本地embedding模型"""
        if not self.embedding_model:
            model_kwargs = {'device': 'cuda'}
            encode_kwargs = {'normalize_embeddings': True}
            
            self.embedding_model = HuggingFaceEmbeddings(
                model_name="models/embedded",
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
        return self.embedding_model
