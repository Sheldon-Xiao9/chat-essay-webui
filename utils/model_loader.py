import os
import torch
from langchain_community.llms import HuggingFacePipeline
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

class ModelLoader:
    def __init__(self):
        self.chat_model = None
        self.embedding_model = None
        self.model = None  # 保存原始模型引用
        self.tokenizer = None  # 保存tokenizer引用
        
    def cleanup(self):
        """清理模型资源"""
        if self.model is not None:
            try:
                # 删除模型
                del self.model
                self.model = None
                # 清空CUDA缓存
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception as e:
                print(f"Error cleaning up model: {e}")
                
        if self.tokenizer is not None:
            try:
                del self.tokenizer
                self.tokenizer = None
            except Exception as e:
                print(f"Error cleaning up tokenizer: {e}")
                
        if self.chat_model is not None:
            try:
                del self.chat_model
                self.chat_model = None
            except Exception as e:
                print(f"Error cleaning up chat_model: {e}")
                
        if self.embedding_model is not None:
            try:
                del self.embedding_model
                self.embedding_model = None
            except Exception as e:
                print(f"Error cleaning up embedding_model: {e}")
        
    def load_chat_model(self):
        """加载本地chat模型"""
        if not self.chat_model:
            model_path = "models/chat"
            
            # 加载tokenizer和模型
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # 创建pipeline
            pipe = pipeline(
                task="text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                return_full_text=False,  # 只返回新生成的文本
                do_sample=True,  # 使用采样
                max_new_tokens=2048,
                temperature=0.7,
                top_p=0.95,
                top_k=50,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
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
