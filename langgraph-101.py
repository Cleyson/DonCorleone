from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv
import streamlit as st
from openai import RateLimitError
import sys

# Configuração da página
st.set_page_config(page_title="Don Corleone AI", page_icon="🍝")


# Carrega as variáveis do .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Define o modelo
try:
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=API_KEY
    )
    model_loaded = True
except Exception as e:
    st.error("⚠️ Erro ao carregar o modelo. Verifique sua chave da API.")
    st.stop()

# Ferramenta de busca web
@tool
def search_web(query: str = "") -> str:
    """Searches the web using Tavily and returns results for the given query."""
    try:
        tavily_tool = TavilySearchResults()
        return tavily_tool.invoke({"query": query})
    except Exception as e:
        print(f"Erro na busca web: {e}", file=sys.stderr)
        return "Não foi possível realizar a busca no momento."

# Template de prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é Don Corleone. Seja direto, imponente e objetivo."),
    ("human", "{input}")
])

# Pipeline de execução
chain: Runnable = prompt | model | StrOutputParser()

# Interface Streamlit
st.title("🍝 DON CORLEONE ☠️")
st.write("Faça sua pergunta ao Don Corleone")

user_input = st.text_input("Sua pergunta:")

if st.button("Perguntar") and user_input:
    try:
        with st.spinner("Don Corleone está pensando..."):
            resposta = chain.invoke({"input": user_input})
            
        st.subheader("Resposta do Don Corleone:")
        st.write(resposta)
        
        # Opcional: Adicionar busca web
        if "pesquise" in user_input.lower():
            with st.spinner("Consultando os contatos..."):
                web_result = search_web(user_input)
            st.subheader("Resultados da pesquisa:")
            st.write(web_result)
    
    except RateLimitError:
        st.error("⚠️ **Créditos Insuficientes**")
        st.warning("""
        Parece que você atingiu o limite de créditos disponíveis em sua conta.
        
        **O que fazer agora?**
        - Verifique o saldo da sua conta OpenAI
        - Atualize seu plano ou adicione mais créditos
        - Entre em contato com o suporte se precisar de ajuda
        """)
    
    except Exception as e:
        st.error("❌ Ocorreu um erro inesperado")
        st.warning("Por favor, tente novamente mais tarde ou entre em contato com o suporte.")
        print(f"Erro inesperado: {e}", file=sys.stderr)
