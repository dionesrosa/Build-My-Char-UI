import os
from dotenv import load_dotenv
import re
import json
import random
import time
from groq import Groq
import instructor
from pydantic import create_model, Field, ValidationError
from typing import List
from config import CONFIG
from config import PROMPT

load_dotenv()

class BuildMyCharUI:
    # Classe para construir personagens, coletando informações do usuário e gerando descrições usando IA.
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Erro: variável de ambiente GROQ_API_KEY não encontrada.")
            return
    
        self.client = instructor.patch(Groq(api_key=api_key))
        self.respostas = {}
        self.personagem = {}
        self.allTemplates = []
        self.charJsons = CONFIG["charJsons"]
        
        self.start()
    
    # Abre um arquivo JSON e retorna os dados como um dicionário. Se ocorrer um erro, imprime uma mensagem e retorna um dicionário vazio.
    def abrir_json(self, caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)

                # Se não tiver a chave, retorna o JSON inteiro
                return dados

        except Exception as e:
            print(f"Erro ao abrir JSON: {e}")
            return {}
    
    # Salva os dados em um arquivo JSON, formatando com indentação e sem caracteres ASCII.
    def salvar_json(self, caminho, dados):
        try:
            diretorio = os.path.dirname(caminho)
            
            if diretorio and not os.path.exists(diretorio):
                os.makedirs(diretorio, exist_ok=True)
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")
    
    # Formata o texto com cores e estilos ANSI, permitindo personalização de cor, negrito, itálico e sublinhado.
    def formatar_texto(self, texto, cor=None, negrito=False, italico=False, sublinhado=False):
        estilos = []

        cores = {
            "vermelho": "91",
            "verde": "92",
            "amarelo": "93",
            "azul": "94",
            "rosa": "95",
            "ciano": "96",
            "branco": "97",
            "cinza": "90",
            "preto": "30",
        }

        if cor and cor.lower() in cores:
            estilos.append(cores[cor.lower()])
        else:
            estilos.append("30")  # fallback para cinza escuro, que funciona melhor

        if negrito:
            estilos.append("1")
        if italico:
            estilos.append("3")
        if sublinhado:
            estilos.append("4")

        prefixo = f"\033[{';'.join(estilos)}m"
        reset = "\033[0m"

        return f"{prefixo}{texto}{reset}"

    def gerar_modelo(self, campos):
        return create_model("Modelo", **campos)

    def exec_ia(self,
        prompt_system:str="",
        prompt_user:str="",
        json_schema=None,
        *,
        model:str="llama3-70b-8192",
        temperature:float=1.0,
        top_p:float=1.0,
        retries:int=5,
        delay:int=1
    ):
        messages = []
        
        if prompt_system:
            messages.append({"role": "system", "content": prompt_system})
        else:
            raise ValueError("prompt_system é obrigatório.")
        
        if prompt_user != "":
            messages.append({"role": "user", "content": prompt_user})
        else:
            raise ValueError("prompt_user é obrigatório.")

        if json_schema is None:
            json_schema = {
                "resultado": (str, Field(..., description="Resultado da requisição"))
            }
        
        for retry in range(1, retries + 1):
            try:
                resposta = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_model=json_schema,
                    temperature=temperature,
                    top_p=top_p
                )

                return resposta.model_dump()
            
            except ValidationError as e:
                print(f"❌ Erro de validação na tentativa {retry}: {e}")
                
            except Exception as e:
                print(f"⚠️ Erro inesperado na tentativa {retry}: {e}")

            time.sleep(delay)

        print("❌ Não foi possível obter uma resposta válida após várias tentativas.")
        return None

    # Imprime a descrição do personagem
    def print_char(self, tipo, conteudo):
        if tipo == "geral":
            titulo = f"Descrição Geral do Personagem: ({len(conteudo)} caracteres)"
        elif tipo == "descricao":
            titulo = f"Descrição do Personagem: ({len(conteudo)} caracteres)"
        elif tipo == "slogan":
            titulo = f"Slogan do Personagem: ({len(conteudo)} caracteres)"
        elif tipo == "saudacao":
            titulo = f"Saudação do Personagem: ({len(conteudo)} caracteres)"
        elif tipo == "dialogos":
            titulo = f"Diálogos do Personagem: ({len(conteudo)} diálogos)"
        elif tipo == "info":
            titulo = f"Informações do Personagem: ({len(conteudo)} itens)"
        elif tipo == "etiquetas":
            titulo = f"Etiquetas do Personagem: ({len(conteudo)} itens)"
        
        if tipo != "definicao":
            print(self.formatar_texto(titulo, cor="amarelo", negrito=True))
               
        if type(conteudo) is str:
            if tipo == "definicao":
                count_perguntas = 0
                identificador = conteudo
                for pergunta in self.personagem["Definição"][identificador]:
                    if pergunta.get("resposta") and pergunta["resposta"].strip():
                        count_perguntas = count_perguntas + 1
                        
                titulo = f"Definições do Personagem em: {conteudo} ({count_perguntas} itens)"
                print(self.formatar_texto(titulo, cor="amarelo", negrito=True))
            
                for pergunta in self.personagem["Definição"][identificador]:
                    if pergunta.get("resposta") and pergunta["resposta"].strip():
                        print(
                            self.formatar_texto(f'{pergunta["pergunta"]}: ', cor="rosa", negrito=False, italico=True)
                            + self.formatar_texto(pergunta["resposta"], cor="azul", negrito=True, italico=True)
                        )
                            
                print("----")
                    
            else:
                print(self.formatar_texto(conteudo, cor="amarelo", italico=True))
            
        elif type(conteudo) is list:
            if tipo == "info":
                for k, v in conteudo.items():
                    print(self.formatar_texto(f"* {k}: {v}", cor="amarelo", italico=True))
                
            elif tipo == "etiquetas":
                for etiqueta in conteudo:
                    print(self.formatar_texto(f" - {etiqueta}", cor="amarelo", italico=True))
            
            elif tipo == "dialogos":
                print(conteudo)          
            
            else:
                print(conteudo)
        
        
    # Pergunta ao usuário por uma informação específica, formatando a pergunta e fornecendo uma dica para pular a resposta.
    def perguntar(self, texto):
        pergunta_formatada = self.formatar_texto(texto, cor="rosa", negrito=True)
        dica_formatada = self.formatar_texto(" (aperte Enter para pular): ", italico=True)
        resposta = input(pergunta_formatada + dica_formatada).strip()
        return resposta

    # Coleta informações do usuário sobre o personagem, perguntando uma série de questões definidas em um arquivo JSON.
    def coletar_informacoes(self):
        perguntas = self.abrir_json(self.charJsons["perguntas"])
        if not perguntas:
            print(self.formatar_texto("Erro: Não foi possível carregar as perguntas do arquivo JSON.", cor="vermelho", negrito=True))
            return
        
        total = len(perguntas)
        print(self.formatar_texto("Vamos coletar informações do seu personagem. Pode pular perguntas se quiser.", cor="azul", negrito=True))
        
        if os.path.exists(self.charJsons["personagem_info"]):
            abrir_informacoes = self.abrir_json(self.charJsons["personagem_info"])
            if abrir_informacoes and isinstance(abrir_informacoes.get("informacoes"), dict):
                self.respostas = abrir_informacoes.get("informacoes")
                print(self.formatar_texto("Arquivo existente encontrado! Informações carregadas de: \"" + self.charJsons["personagem_info"] + "\"", cor="verde")) 
                self.print_char("info",self.respostas)
                return

        else:
            for i, (chave, pergunta_texto) in enumerate(perguntas.items(), start=1):
                pergunta_com_indice = f"{i} de {total}: {pergunta_texto}"
                resposta = self.perguntar(pergunta_com_indice)
                if resposta:
                    self.respostas[chave] = resposta
                    
            temp_respostas = {
                "informacoes": self.respostas
            }
            self.salvar_json(self.charJsons["personagem_info"], temp_respostas)
            print(self.formatar_texto("Informações salvas com sucesso em: "+ self.charJsons["personagem_info"], cor="verde"))
        
            self.print_char("info",self.respostas)
            
    # Gera o nome do personagem, corrigindo capitalização e formatando conforme regras de nomes próprios em português.
    def gerar_nome(self):
        nome_input = self.respostas.get("Nome", "").strip()

        if not nome_input:
            genero_input = self.respostas.get("Gênero", "").strip()
            if not genero_input:
                genero_input = random.choice(["Masculino", "Feminino"])
            else:
                genero_input = genero_input.capitalize()

            result = self.exec_ia(
                PROMPT["PROMPT_GERADOR_NOME_SYSTEM"].format(genero=genero_input),
                PROMPT["PROMPT_GERADOR_NOME_USER"].format(genero=genero_input),
                self.gerar_modelo({
                    "nomes": List[self.gerar_modelo({
                        "nome": (str, Field(..., description="Primeiro nome do personagem")),
                        "sobrenome": (str, Field(..., description="Sobrenome do personagem")),
                        "nomecompleto": (str, Field(..., description="Junção do nome com o sobrenome")),
                    })]
                }),
                temperature=1.3,
                top_p=0.95,
                #model="llama-3.3-70b-versatile"
            )
            
            if result and isinstance(result.get("nomes"), list) and len(result["nomes"]) > 0:
                print(self.formatar_texto(f"Gerado {len(result['nomes'])} itens."))
                nome_input = random.choice(result["nomes"])
                
            else:            
                print(self.formatar_texto("Erro: Nome gerado está vazio. Por favor, forneça um nome manualmente.", cor="vermelho", negrito=True))
                nome_input = input(self.formatar_texto("Digite o nome do personagem (até 20 caracteres): ", cor="rosa", negrito=True)).strip()
                
            result = self.exec_ia(
                PROMPT["PROMPT_CORRETOR_NOME_SYSTEM"],
                PROMPT["PROMPT_CORRETOR_NOME_USER"].format(nome=nome_input),
                self.gerar_modelo({
                    "nome": (str, Field(..., description="Nome do personagem formatado e corrigido"))
                }),
                temperature=0.8,
                top_p=0.8,
            )

            if result and isinstance(result.get("nome"), str):
                nome_corrigido = result["nome"]
                print(self.formatar_texto("Nome corrigido: " + nome_corrigido + "."))
            
                # Se nome foi realmente corrigido e está diferente
                if nome_corrigido and nome_corrigido != self.respostas.get("Nome", ""):
                    self.respostas["Nome"] = nome_corrigido
                    
                    temp_respostas = {
                        "informacoes": self.respostas
                    }
                    
                    self.salvar_json(self.charJsons["personagem_info"], temp_respostas)
                    print(self.formatar_texto("Nome ajustado e atualizado com sucesso em: " + self.charJsons["personagem_info"], cor="ciano"))
                    self.print_personagem_info(self.respostas)

                return nome_corrigido
            else:
                print(self.formatar_texto("Erro: nome formatado vazio ou inválido. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
                return


    # Cria uma descrição geral do personagem com base nas informações coletadas, usando IA para gerar um texto criativo.
    def criar_descricao_geral(self):
        print(self.formatar_texto("\nVamos criar uma descrição geral do seu personagem, com base nas informações fornecidas.", cor="azul", negrito=True))

        # Já existe a descrição?
        if os.path.exists(self.charJsons["personagem_geral"]):
            abrir_descricao_geral = self.abrir_json(self.charJsons["personagem_geral"])
            if abrir_descricao_geral and isinstance(abrir_descricao_geral.get("descricao"), str):
                self.personagem["Descrição Geral"] = abrir_descricao_geral.get("descricao")
                print(self.formatar_texto("Arquivo existente encontrado! Descrição Geral carregada de: \"" + self.charJsons["personagem_geral"] + "\"", cor="verde"))
                self.print_char("geral", self.personagem["Descrição Geral"])
                return

        # Gera resumo com base nas respostas
        resumo = "\n".join(f"{k.capitalize()}: {v}" for k, v in self.respostas.items())

        result = self.exec_ia(
            PROMPT["PROMPT_DESCRICAO_GERAL_SYSTEM"],
            PROMPT["PROMPT_DESCRICAO_GERAL_USER"].format(resumo=resumo),
            self.gerar_modelo({
                "descricao": (str, Field(..., description="Descrição completa do personagem"))
            }),
            temperature=1,
            top_p=1,
            #model="llama-3.3-70b-versatile"
        )
        
        if result and isinstance(result.get("descricao"), str):
            # Salvar e mostrar
            self.personagem["Descrição Geral"] = result.get("descricao")
            self.salvar_json(self.charJsons["personagem_geral"], result)
            print(self.formatar_texto("Descrição Geral salva com sucesso em: "+ self.charJsons["personagem_geral"], cor="verde"))
            self.print_char("geral", self.personagem["Descrição Geral"])
        else:
            print(self.formatar_texto("Erro: descrição vazia ou inválida. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
            return

    # Gera um slogan para o personagem, garantindo que esteja dentro de um intervalo específico de caracteres e coerente com a descrição geral.
    def gerar_slogan(self):
        print(self.formatar_texto("\nVamos criar um Slogan para seu personagem.", cor="azul", negrito=True))

        # Já existe um slogan?
        if os.path.exists(self.charJsons["personagem_slogan"]):
            abrir_slogan = self.abrir_json(self.charJsons["personagem_slogan"])

            if abrir_slogan and isinstance(abrir_slogan.get("slogan"), str):
                self.personagem["Slogan"] = abrir_slogan.get("slogan")
                print(self.formatar_texto("Arquivo existente encontrado! Slogan carregado de: \"" + self.charJsons["personagem_slogan"] + "\"", cor="verde"))
                self.print_char("slogan",self.personagem["Slogan"])
                return

        descricao = self.personagem.get("Descrição Geral", "")
        
        while True:
            max_tentativas:int = 5
            max_caracteres:int = 50
            for tentativa in range(max_tentativas):
                result = self.exec_ia(
                    PROMPT["PROMPT_SLOGAN_SYSTEM"],
                    PROMPT["PROMPT_SLOGAN_USER"].format(descricao=descricao,max_caracteres=max_caracteres),
                    self.gerar_modelo({
                        "slogan": (str, Field(..., description="Slogan do personagem"))
                    }),
                    temperature=0.6,
                    top_p=0.9,
                    #model="llama-3.3-70b-versatile"
                )
                
                if result and isinstance(result.get("slogan"), str) and len(result.get("slogan")) <= max_caracteres:
                    self.personagem["Slogan"] = result.get("slogan")
                    self.salvar_json(self.charJsons["personagem_slogan"], result)
                    print(self.formatar_texto("Slogan salvo com sucesso em: " + self.charJsons["personagem_slogan"], cor="verde"))
                    self.print_char("slogan",self.personagem["Slogan"])

                    return
                
                else:
                    print(self.formatar_texto(f"O slogan passou do limite de {max_caracteres}: \"{result.get("slogan")}\" ({len(result.get("slogan"))} caracteres) fora do intervalo.", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break
    
    def criar_descricao(self):
        print(self.formatar_texto("\nVamos criar a descrição do personagem.", cor="azul", negrito=True))

        # Já existe uma descrição?
        if os.path.exists(self.charJsons["personagem_descricao"]):
            abrir_descricao = self.abrir_json(self.charJsons["personagem_descricao"])
            
            if abrir_descricao and isinstance(abrir_descricao.get("descricao"), str):
                self.personagem["Descrição"] = abrir_descricao.get("descricao")
                print(self.formatar_texto("Arquivo existente encontrado! Descrição carregada de: \"" + self.charJsons["personagem_descricao"] + "\"", cor="verde"))
                self.print_char("descricao", self.personagem["Descrição"])
                return

        descricao_geral = self.personagem.get("Descrição Geral", "")
        
        while True:
            max_tentativas:int = 5
            max_caracteres:int = 500
            for tentativa in range(max_tentativas):
                result = self.exec_ia(
                    PROMPT["PROMPT_DESCRICAO_SYSTEM"],
                    PROMPT["PROMPT_DESCRICAO_USER"].format(descricao_geral=descricao_geral,max_caracteres=max_caracteres),
                    self.gerar_modelo({
                        "descricao": (str, Field(..., description="Descrição do personagem"))
                    }),
                    temperature=0.6,
                    top_p=0.9,
                    #model="llama-3.3-70b-versatile"
                )
                
                if result and isinstance(result.get("descricao"), str) and len(result.get("descricao")) <= max_caracteres:
                    self.personagem["Descrição"] = result.get("descricao")
                    self.salvar_json(self.charJsons["personagem_descricao"], result)
                    print(self.formatar_texto("Descrição salva com sucesso em: " + self.charJsons["personagem_descricao"], cor="verde"))
                    self.print_char("descricao", self.personagem["Descrição"])

                    return
                
                else:
                    print(self.formatar_texto(f"A descrição passou do limite de {max_caracteres}: \"{result.get("descricao")}\" ({len(result.get("descricao"))} caracteres) fora do intervalo.", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break
    
    # Gera uma saudação personalizada para o personagem, garantindo que esteja dentro dos limites de caracteres e coerente com a descrição geral.
    def gerar_saudacao(self):
        print(self.formatar_texto("\nVamos gerar a saudação do personagem.", cor="azul", negrito=True))

        # Já existe uma saudação?
        if os.path.exists(self.charJsons["personagem_saudacao"]):
            abrir_saudacao = self.abrir_json(self.charJsons["personagem_saudacao"])
            
            if abrir_saudacao and isinstance(abrir_saudacao.get("saudacao"), str):
                self.personagem["Saudação"] = abrir_saudacao.get("saudacao")
                print(self.formatar_texto("Arquivo existente encontrado! Saudação carregada de: \"" + self.charJsons["personagem_saudacao"] + "\"", cor="verde"))
                self.print_char("saudacao",self.personagem["Saudação"])
                return self.personagem["Saudação"]

        descricao_geral = self.personagem.get("Descrição Geral", "")

        while True:
            max_tentativas:int = 5
            max_caracteres:int = 4096
            for tentativa in range(max_tentativas):
                result = self.exec_ia(
                    PROMPT["PROMPT_SAUDACAO_SYSTEM"],
                    PROMPT["PROMPT_SAUDACAO_USER"].format(descricao_geral=descricao_geral,max_caracteres=max_caracteres),
                    self.gerar_modelo({
                        "saudacao": (str, Field(..., description="Saudação do personagem"))
                    }),
                    temperature=0.7,
                    top_p=0.9,
                    #model="llama-3.3-70b-versatile"
                )
                
                if result and isinstance(result.get("saudacao"), str) and len(result.get("saudacao")) <= max_caracteres:
                    self.personagem["Saudação"] = result.get("saudacao")
                    self.salvar_json(self.charJsons["personagem_saudacao"], result)
                    print(self.formatar_texto("Saudação salva com sucesso em: " + self.charJsons["personagem_saudacao"], cor="verde"))
                    self.print_char("saudacao",self.personagem["Saudação"])
                    return
                
                else:
                    print(self.formatar_texto(f"A saudação passou do limite de {max_caracteres}: \"{result.get("saudacao")}\" ({len(result.get("saudacao"))} caracteres) fora do intervalo.", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break

    # Gera etiquetas para o personagem, classificando-o em até 5 categorias a partir de uma lista pré-definida.
    def gerar_etiquetas(self):
        print(self.formatar_texto("\nVamos gerar as etiquetas (máx. 5 categorias).", cor="azul", negrito=True))

        # Já existe um arquivo?
        if os.path.exists(self.charJsons["personagem_etiquetas"]):
            abrir_etiquetas = self.abrir_json(self.charJsons["personagem_etiquetas"])

            if abrir_etiquetas and isinstance(abrir_etiquetas.get("etiquetas"), list):
                self.personagem["Etiquetas"] = abrir_etiquetas.get("etiquetas")
                print(self.formatar_texto("Arquivo existente encontrado! Etiquetas carregadas de: \"" + self.charJsons["personagem_etiquetas"] + "\"", cor="verde"))
                self.print_char("etiquetas",self.personagem["Etiquetas"])
                return

        descricao = self.personagem.get("Descrição Geral", "")
        
        while True:
            max_tentativas:int = 5
            max_caracteres:int = 5
            for tentativa in range(max_tentativas):
                result = self.exec_ia(
                    PROMPT["PROMPT_ETIQUETAS_SYSTEM"],
                    PROMPT["PROMPT_ETIQUETAS_USER"].format(descricao=descricao),
                    self.gerar_modelo({
                        "etiquetas": (List[str], Field(..., description="Lista de etiquetas associadas ao personagem"))
                    }),
                    temperature=0.5,
                    top_p=0.9,
                    #model="llama-3.3-70b-versatile"
                )
                
                if result and isinstance(result.get("etiquetas"), list) and len(result.get("etiquetas")) <= max_caracteres:
                    self.personagem["Etiquetas"] = result.get("etiquetas")
                    self.salvar_json(self.charJsons["personagem_etiquetas"], result)
                    print(self.formatar_texto("Etiquetas salvas com sucesso em: " + self.charJsons["personagem_etiquetas"], cor="verde"))
                    self.print_char("etiquetas",self.personagem["Etiquetas"])

                    return

                else:
                    print(self.formatar_texto(f"O número de etiquetas selecionadas passou do limite de {max_caracteres}.", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break

    # Gera um prompt para definir o personagem, formatando as informações de título, descrição e conteúdo.
    def gerar_prompt_definicao(self, dados):
        lista_perguntas = []

        for pergunta in dados["perguntas"]:
            lista_perguntas.append({
                "pergunta_id": pergunta['indice'],
                "pergunta": pergunta['pergunta'],
                "resposta" : ""
            })

        Modelo = self.gerar_modelo({
            "perguntas": (List[self.gerar_modelo({
                "pergunta_id": (str, Field(..., description="Id da pergunta")),
                "pergunta": (str, Field(..., description="Pergunta a ser respondida")),
                "resposta": (str, Field(..., description="Resposta da pergunta")),
            })], Field(..., description="Lista de perguntas e respostas")),
        })
        

        instrucao = dados.get("instrucao", "")
        instrucao = f"- {instrucao}" if instrucao else ""

        # Verifica se os dados contêm as chaves necessárias
        descricao_personagem = self.personagem.get("Descrição Geral", "")
        
        while True:
            max_tentativas:int = 5
            for tentativa in range(max_tentativas):
                result = self.exec_ia(
                    PROMPT["PROMPT_INSTRUCAO_SYSTEM"],
                    PROMPT["PROMPT_INSTRUCAO_USER"].format(descricao=descricao_personagem, instrucao=instrucao, lista=lista_perguntas),
                    Modelo,
                    temperature=0.6,
                    top_p=0.9,
                    #model="llama-3.3-70b-versatile"
                )
     
                if result and isinstance(result.get("perguntas"), list):
                    return result
                
                else:
                    print(self.formatar_texto("Erro ao obter respostas.", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break
            
            return

    # Gera a definição do personagem, iterando sobre um template JSON e coletando informações específicas.
    def gerar_definicao(self):
        template_files = [f for f in os.listdir(self.charJsons["personagem_templates"]) if f.endswith('.json')]
        if not template_files:
            print(self.formatar_texto("Nenhum template de definição encontrada. Por favor, adicione templates JSON na pasta '" + self.charJsons["personagem_templates"] + "'.", cor="vermelho", negrito=True))
            return
        
        else:
            if "Definição" not in self.personagem:
                self.personagem["Definição"] = {}
    
            print(self.formatar_texto("\nVamos gerar a definição do personagem.", cor="azul", negrito=True))
            
            total = len(template_files)
            for i, file in enumerate(template_files, start=1):
                caminho = os.path.join(self.charJsons["personagem_templates"], file)
                msg = f"Verificando definição {i} de {total}: {caminho}"
                print(self.formatar_texto(msg, cor="amarelo", italico=True))

                # Abre o template JSON e carrega os dados
                load_template = self.abrir_json(caminho)
                if not isinstance(load_template, dict) or not load_template:
                    print(self.formatar_texto(f"Erro: Template '{file}' está vazio ou malformado. Verifique o arquivo JSON.", cor="vermelho", negrito=True))
                    continue
                
                # Adiciona o template carregado à lista de templates
                self.allTemplates.append(load_template)
                
                print(self.formatar_texto(f"Template '{file}' carregado com sucesso!", cor="verde"))
                
                # Se o template for um dicionário, pega o primeiro identificador e os dados
                identificador = list(load_template.keys())[0]
                dados = load_template[identificador]
                
                definicao_file = self.charJsons["personagem_definicao"]
                novo_arquivo = definicao_file.replace(".json", f"_{identificador}.json")
                
                # Já existe uma definição?
                if os.path.exists(novo_arquivo):
                    abrir_definicao = self.abrir_json(novo_arquivo)

                    if abrir_definicao and isinstance(abrir_definicao.get("perguntas"), list):
                        self.personagem["Definição"][identificador] = abrir_definicao.get("perguntas")
                        print(self.formatar_texto(f"Arquivo existente encontrado! Definição carregada de: \"{novo_arquivo}\"", cor="verde"))
                        self.print_char("definicao",identificador)
                        continue

                else:
                    result_perguntas = self.gerar_prompt_definicao(dados)
                    
                    if result_perguntas:
                        self.personagem["Definição"][identificador] = result_perguntas.get("perguntas")
                        self.salvar_json(novo_arquivo, result_perguntas)
                        print(self.formatar_texto(f"Definição parcial salva com sucesso em: {novo_arquivo}", cor="verde"))
                        self.print_char("definicao",identificador)
                        
                    else:
                        print(self.formatar_texto("Erro ao responder perguntas: Resposta vazia ou inválida da IA. Tente novamente.", cor="vermelho", negrito=True))
                    
                    continue


    def criar_dialogos(self):
        self.personagem["Diálogos"] = []
        
        print(self.formatar_texto("\nVamos criar uma lista de dialogos para seu personagem, com base nas informações fornecidas.", cor="azul", negrito=True))

        # Já existe aos diálogos?
        if os.path.exists(self.charJsons["personagem_dialogos"]):
            abrir_dialogos = self.abrir_json(self.charJsons["personagem_dialogos"])
            if abrir_dialogos and isinstance(abrir_dialogos.get("dialogos"), list):
                self.personagem["Diálogos"] = abrir_dialogos["dialogos"]
                print(self.formatar_texto("Arquivo existente encontrado! Diálogos carregada de: \"" + self.charJsons["personagem_dialogos"] + "\"", cor="verde"))
                self.print_char("dialogos",self.personagem["Diálogos"])
                
                if len(abrir_dialogos["dialogos"]) > 100:
                    return
                
                

        # Gera rediálogos com base na descrição geral
        descricao = self.personagem.get("Descrição Geral", "")

        while True:
            max_tentativas:int = 5
            for tentativa in range(max_tentativas):
                Modelo = self.gerar_modelo({
                    "dialogos": (List[
                        self.gerar_modelo({
                            "user1": (str, Field(..., description="Primeiro usuário")),
                            "msg1": (str, Field(..., description="Mensagem do primeiro usuário")),
                            "user2": (str, Field(..., description="Segundo usuário")),
                            "msg2": (str, Field(..., description="Mensagem do segundo usuário")),
                        })
                    ], Field(..., description="Diálogos entre usuários")),
                })
                
                result = self.exec_ia(
                    PROMPT["PROMPT_DIALOGOS_SYSTEM"],
                    PROMPT["PROMPT_DIALOGOS_USER"].format(descricao=descricao),
                    Modelo,
                    temperature=1.2,
                    top_p=0.95,
                    #model="llama-3.3-70b-versatile"
                )
                
                if result and isinstance(result.get("dialogos"), list):
                    for dialogo in result.get("dialogos"):
                        self.personagem["Diálogos"].append({
                            "user1": dialogo["user1"],
                            "msg1": dialogo["msg1"],
                            "user2": dialogo["user2"],
                            "msg2": dialogo["msg2"],
                        })
                    temp_dialogos = {}
                    temp_dialogos["dialogos"] = self.personagem["Diálogos"]
                    self.salvar_json(self.charJsons["personagem_dialogos"], temp_dialogos)
                    print(self.formatar_texto("Diálogos salvos com sucesso em: "+ self.charJsons["personagem_dialogos"], cor="verde"))
                    self.print_char("dialogos",self.personagem["Diálogos"])

                    return
                
                else:
                    print(self.formatar_texto("Erro na geração dos diálogos", cor="amarelo"))

            continuar = input(f"Deseja tentar mais {max_tentativas} vezes? (s/n): ").strip().lower()
            if continuar != 's':
                print("Encerrando...")
                break
  
    # Imprime todas as informações do personagem de forma organizada.
    def imprimir_personagem(self):
        templates = self.allTemplates
        dialogos = self.personagem.get("Diálogos", [])
        
        codigo = ""
        
        if not templates:
            print(self.formatar_texto(
                "Nenhum template carregado. Por favor, gere a definição primeiro.",
                cor="vermelho", negrito=True
            ))
            return
        
        print(self.formatar_texto(
            "\nVamos Gerar as Definições Gerais do Personagem:",
            cor="azul", negrito=True
        ))
        
        codigo += "----\n"
        codigo += self.formatar_texto("### DEFINIÇÕES DO PERSONAGEM ###", cor="rosa", negrito=True)
        codigo += "\n----\n"
        
        for i, template in enumerate(templates, start=1):
            if isinstance(template, dict) and template:
                identificador = list(template.keys())[0]
                dados = template[identificador]
                dados_comp = self.personagem["Definição"][identificador]
                status_perguntas = []

                titulo = dados.get("titulo", "")
                codigo_perguntas = "\n\n----\n"
                codigo_perguntas += "** " + self.formatar_texto(titulo, cor="ciano", negrito=True) + " **\n"
                codigo_perguntas += "----\n"
                
                for p, pergunta in enumerate(dados.get("perguntas", []), start=1):
                    try:
                        pergunta_indice = pergunta.get("indice", None)
                        pergunta_texto = pergunta.get("resposta", None)
                        pergunta_resposta = next((p for p in dados_comp if p["pergunta_id"] == pergunta_indice), None)
                        pergunta_resposta = pergunta_resposta["resposta"]
                        
                        pergunda_pronta = pergunta_texto.replace("{" + f"{pergunta_indice}" + "}", pergunta_resposta)
  
                        if pergunta_texto and pergunta_resposta:
                            codigo_perguntas += "- " + pergunda_pronta + "\n"
                            status_perguntas.append(pergunta_indice)
                                
                    except Exception as e:
                        print(self.formatar_texto(f"Erro ao processar a pergunta {p} do template {identificador}: {e}", cor="vermelho", negrito=True))
                        continue
                            
                codigo_perguntas += "----\n"  
                
                if len(status_perguntas) > 0:
                    codigo += codigo_perguntas
        
        # DIÁLOGOS
        if dialogos:
            codigo_dialogo = "\n\n\n\n----\n"
            codigo_dialogo += self.formatar_texto("### DIÁLOGOS DO PERSONAGEM ###", cor="rosa", negrito=True)
            codigo_dialogo += "\n----\n\n\n----\n"
            
            status_dialogos = []
            
            for i, dialogo in enumerate(dialogos, start=1):
                if isinstance(dialogo, dict) and len(dialogo) == 4:
                    user_a_type = dialogo.get("user1", "")
                    user_a_msg = dialogo.get("msg1", "")
                    user_b_type = dialogo.get("user2", "")
                    user_b_msg = dialogo.get("msg2", "")

                    # Verifica se o diálogo é válido
                    if not user_a_type or not user_b_type or not user_a_msg or not user_b_msg:
                        print(self.formatar_texto(f"Diálogo {i} inválido ou incompleto. Pulando...", cor="vermelho", negrito=True))
                        continue
                                   
                    # Formata o diálogo
                    user_a_type = user_a_type.strip()
                    user_a_msg = user_a_msg.strip()
                    user_b_type = user_b_type.strip()
                    user_b_msg = user_b_msg.strip()

                    codigo_dialogo += f"{{{{{user_a_type}}}}}: {user_a_msg}\n"
                    codigo_dialogo += f"{{{{{user_b_type}}}}}: {user_b_msg}\n"
                    codigo_dialogo += "----\n"
                    
                    status_dialogos.append(i)
                    
            if len(status_dialogos) > 0:
                codigo += codigo_dialogo

        codigo_final = {"codigo": codigo.strip()}
        
        self.personagem["Definição Final"] = codigo_final["codigo"]
        
        # Salva o código gerado em um arquivo JSON
        self.salvar_json(self.charJsons["personagem_definicoes"], codigo_final)
        if os.path.exists(self.charJsons["personagem_definicoes"]):
            print(self.formatar_texto("Definições gerais do personagem salvas com sucesso em: " + self.charJsons["personagem_definicoes"], cor="verde"))
            print("\n\n" + codigo)
        
    def done(self):
        print(self.formatar_texto("\n\nParabéns! Você completou a criação do seu personagem.", cor="verde", negrito=True))
        print(self.formatar_texto("Agora você pode usar o personagem em suas histórias, jogos ou qualquer outro projeto criativo!", cor="verde"))
        print(self.formatar_texto("Obrigado por usar o BuildMyChar! Até a próxima!", cor="verde", negrito=True))
        
        print(self.formatar_texto("\n\n\nSuas informações pro personagem estão abaixo:", cor="azul", negrito=True))
        print("###################################")
        print(self.formatar_texto("Nome da personagem (" + str(len(self.respostas.get("Nome"))) + " de 20 caracteres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.respostas.get("Nome")))
        print("----------")
        print(self.formatar_texto("Slogan (" + str(len(self.personagem.get("Slogan"))) + " de 50 caracteres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Slogan")))
        print("----------")
        print(self.formatar_texto("Descrição (" + str(len(self.personagem.get("Descrição"))) + " de 500 caracteres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Descrição")))
        print("----------")
        print(self.formatar_texto("Saudação (" + str(len(self.personagem.get("Saudação"))) + " de 4096 caracteres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Saudação")))
        print("----------")
        etiquetas = self.personagem.get("Etiquetas")
        lista_etiquetas = ", ".join(etiquetas)
        print(self.formatar_texto("Etiquetas (" + str(len(etiquetas)) + " de 5 etiquetas):", cor="ciano", negrito=True))
        print(self.formatar_texto(lista_etiquetas))
        print("----------")
        print(self.formatar_texto("Definições (" + str(len(self.personagem.get("Definição Final"))) + " de 32000 caracteres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Definição Final")))
        
        print("###################################")
        
    def start(self):
        self.coletar_informacoes()
        self.gerar_nome()
        self.criar_descricao_geral()
        self.gerar_slogan()
        self.criar_descricao()
        self.gerar_saudacao()
        self.gerar_etiquetas()
        self.gerar_definicao()
        self.criar_dialogos()
        self.criar_dialogos()
        self.criar_dialogos()
        self.imprimir_personagem()
        self.done()
        
        
# Verifica se o script está sendo executado diretamente 
if __name__ == "__main__":
    print("Este módulo não deve ser executado diretamente. Use o script principal para interagir com a classe BuildMyChar.")
