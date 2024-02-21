# -*- coding: utf-8 -*-
"""qa_generation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1avQR-ANehLmyfDcKR_2A_IycxwCpTa-k

# QA Generation
This notebook shows how to use the `QAGenerationChain` to come up with question-answer pairs over a specific document.
This is important because often times you may not have data to evaluate your question-answer system over, so this is a cheap and lightweight way to generate it!


And You can find the origin notebook in [LangChain example](https://github.com/hwchase17/langchain/blob/master/docs/use_cases/evaluation/qa_generation.ipynb), and this example will show you how to set the LLM with GPTCache so that you can cache the data with LLM.

## Go into GPTCache

Please [install gptcache](https://gptcache.readthedocs.io/en/latest/index.html#) first, then we can initialize the cache.There are two ways to initialize the cache, the first is to use the map cache (exact match cache) and the second is to use the DataBse cache (similar search cache), it is more recommended to use the second one, but you have to install the related requirements.

> We will use [Milvus](https://milvus.io/) vector database to do similarity retrieval, so we need to install and start Milvus.
"""

from milvus import default_server
default_server.start()

"""Before running the example, make sure the `OPENAI_API_KEY` environment variable is set by executing `echo $OPENAI_API_KEY`. If it is not already set, it can be set by using `export OPENAI_API_KEY=YOUR_API_KEY` on Unix/Linux/MacOS systems or `set OPENAI_API_KEY=YOUR_API_KEY` on Windows systems. And there is `get_msg_func` for the cache settings:

> We can run `os.environ` to set the environment variable in colab.
"""

import os
openai_api_key = os.environ.get("OPENAI_API_KEY")

# get the content(only question) form the prompt to cache
def get_msg_func(data, **_):
    return data.get("messages")[-1].content

"""### 1. Init for exact match cache"""

from gptcache import cache
cache.init(pre_embedding_func=get_msg_func)
cache.set_openai_key()

"""### 2. Init for similar match cache

When initializing gptcahe, the following four parameters are configured:

- `pre_embedding_func`: pre-processing before extracting feature vectors, it will use the `get_msg_func` method
- `embedding_func`: the method to extract the text feature vector
- `data_manager`: DataManager for cache management
- `similarity_evaluation`: the evaluation method after the cache hit

The `data_manager` is used to audio feature vector, response text in the example, it takes [Milvus](https://milvus.io/docs) (please make sure it is started), you can also configure other vector storage, refer to [VectorBase API](https://gptcache.readthedocs.io/en/latest/references/manager.html#module-gptcache.manager.vector_data).
"""

from gptcache import cache
from gptcache.embedding import Onnx
from gptcache.manager import CacheBase, VectorBase, get_data_manager
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation


onnx = Onnx()
cache_base = CacheBase('sqlite')
vector_base = VectorBase('milvus', host='127.0.0.1', port='19530', dimension=onnx.dimension)
data_manager = get_data_manager(cache_base, vector_base)
cache.init(
    pre_embedding_func=get_msg_func,
    embedding_func=onnx.to_embeddings,
    data_manager=data_manager,
    similarity_evaluation=SearchDistanceEvaluation(),
    )
cache.set_openai_key()

"""After initializing the cache, you can use the LangChain Chat Models with `gptcache.adapter.langchain_models`. At this point **gptcache** will cache the answer, the only difference from the original example is to change `chat=ChatOpenAI(temperature=0)` to `chat = LangChainChat(chat=ChatOpenAI(temperature=0))`, which will be commented in the code block.

Then you will find that it will be more fast when search the similar content, let's play with it.

## Getting Started
"""

from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

text_splitter =  RecursiveCharacterTextSplitter(chunk_overlap=500, chunk_size=2000)

loader = TextLoader("./test.txt")

doc = loader.load()[0]

from langchain.chat_models import ChatOpenAI
from langchain.chains import QAGenerationChain
from gptcache.adapter.langchain_models import LangChainChat

# chat = ChatOpenAI(temperature=0) # using the following code to cache with gptcache
chat = LangChainChat(chat=ChatOpenAI(temperature=0))

chain = QAGenerationChain.from_llm(chat, text_splitter=text_splitter)

qa = chain.run(doc.page_content)

qa[10]
