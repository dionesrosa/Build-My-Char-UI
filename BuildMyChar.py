import os
import re
import json
import random
from groq import Groq

class BuildMyChar:
    # Classe para construir personagens, coletando informações do usuário e gerando descrições usando IA.
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Erro: variável de ambiente GROQ_API_KEY não encontrada.")
            return
    
        self.client = Groq(api_key=api_key)
        self.respostas = {}
        self.personagem = {}
        self.allTemplates = []
        self.charJsons = {
            "perguntas": "perguntas.json",
            "personagem_info": "temp/personagem_info.json",
            "personagem_geral": "temp/personagem_geral.json",
            "personagem_slogan": "temp/personagem_slogan.json",
            "personagem_descricao": "temp/personagem_descricao.json",
            "personagem_saudacao": "temp/personagem_saudacao.json",
            "personagem_etiquetas": "temp/personagem_etiquetas.json",
            "personagem_definicao": "temp/personagem_definicao.json",
            "personagem_definicoes": "temp/personagem_definicoes.json",
            "personagem_dialogos": "temp/personagem_dialogos.json",
            "personagem_templates": "templates/"
        }
    
    # Abre um arquivo JSON e retorna os dados como um dicionário. Se ocorrer um erro, imprime uma mensagem e retorna um dicionário vazio.
    def abrir_json(self, caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)

                # Se tiver a chave "string", retorna só ela
                if isinstance(dados, dict) and "string" in dados:
                    return dados["string"]

                # Se não tiver a chave, retorna o JSON inteiro
                return dados

        except Exception as e:
            print(f"Erro ao abrir JSON: {e}")
            return {}
    
    # Salva os dados em um arquivo JSON, formatando com indentação e sem caracteres ASCII.
    def salvar_json(self, caminho, dados):
        try:
            # Se for string, tenta converter pra JSON
            if isinstance(dados, str):
                try:
                    dados = json.loads(dados)  # tenta interpretar como JSON
                except json.JSONDecodeError:
                    dados = {"string": dados}  # não é JSON → salva como dict com índice "string"

            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")

    def extrair_json(self, texto):
        try:
            # Tenta extrair o conteúdo dentro de um bloco ```json ... ```
            match = re.search(r"```json\s*(\{.*?\})\s*```", texto, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            
            # Se não encontrar, tenta achar só o primeiro objeto JSON puro
            match = re.search(r"(\{.*\})", texto, re.DOTALL)
            
            if match:
                return json.loads(match.group(1))
            
            else:
                raise ValueError("JSON não encontrado na resposta.")
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
    
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

    # Envia um prompt para a IA e retorna a resposta formatada.
    def enviar_para_ia(self, prompt=None, system_prompt=None, max_tokens=1024, temperature=0.7, top_p=0.85, stop=None, model="llama-3.3-70b-versatile", json=False):
        if json:
            #response_format = {"type": "json_object"}
            response_format = None
            #extra = ", formatando respostas em JSON conforme solicitado"
            extra = ""
        else:
            response_format = None
            extra = ""
        
        if not system_prompt:
            system_prompt = {
                "role": "system",
                "content": f"Você é um assistente que ajuda a criar personagens para Character.ai{extra}."
            }
        else:
            system_prompt = {
                "role": "system",
                "content": system_prompt
            }
            
        messages = [system_prompt]
        if prompt:
            messages.append({
                "role": "user",
                "content": prompt
            })

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=top_p,
            stream=False,
            response_format=response_format,
            stop=stop,
        )
        
        return response.choices[0].message.content.strip()
    
    # Imprime as informações do personagem formatadas, destacando cada informação com estilo.
    def print_personagem_info(self, respostas):          
        print(self.formatar_texto("Informações do Personagem:", cor="amarelo", negrito=True))
        for k, v in self.respostas.items():
            print(self.formatar_texto(f"* {k}: {v}", cor="amarelo", italico=True))
    
    # Imprime a descrição geral do personagem, formatando o texto para destaque.
    def print_personagem_geral(self, descricao):          
        print(self.formatar_texto("Descrição Geral do Personagem:", cor="amarelo", negrito=True))
        print(self.formatar_texto(descricao, cor="amarelo", italico=True))
        
    # Imprime as definições do personagem, na categoria especificada, formatando o texto para destaque.
    def print_personagem_definicao(self, identificador):          
        print(self.formatar_texto("Definições do Personagem em: " + identificador, cor="amarelo", negrito=True))
        print(self.formatar_texto("\n".join(f"{k}: {v}" for k, v in self.personagem["Definição"][identificador].items() if v), cor="amarelo", italico=True))
    
    # Imprime os diálogos do personagem, formatando o texto para destaque.
    def print_personagem_dialogos(self, dialogos):          
        print(self.formatar_texto("Diálogos do Personagem:", cor="amarelo", negrito=True))
        print(self.formatar_texto(dialogos, cor="amarelo", italico=True))
        
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
            self.respostas = self.abrir_json(self.charJsons["personagem_info"])
            print(self.formatar_texto("Arquivo existente encontrado! Informações carregadas de: \"" + self.charJsons["personagem_info"] + "\"", cor="verde"))
            
            self.print_personagem_info(self.respostas)

        else:
            for i, (chave, pergunta_texto) in enumerate(perguntas.items(), start=1):
                pergunta_com_indice = f"{i} de {total}: {pergunta_texto}"
                resposta = self.perguntar(pergunta_com_indice)
                if resposta:
                    self.respostas[chave] = resposta
                    
            self.salvar_json(self.charJsons["personagem_info"], self.respostas)
            print(self.formatar_texto("Informações salvas com sucesso em: "+ self.charJsons["personagem_info"], cor="verde"))
        
            self.print_personagem_info(self.respostas)
            
    # Gera o nome do personagem, corrigindo capitalização e formatando conforme regras de nomes próprios em português.
    def gerar_nome(self):
        nome_input = self.respostas.get("Nome", "").strip()

        if not nome_input:
            genero_input = self.respostas.get("Gênero", "").strip()
            if not genero_input:
                genero_input = random.choice(["Masculino", "Feminino"])
            else:
                genero_input = genero_input.capitalize()

            system_prompt = f"""
            Você é um gerador criativo de nomes do gênero: {genero_input}.
            """

            prompt = f"""
            Gere 10 nomes do gênero {genero_input} diferentes, cada um com nome e sobrenome. Cada nome completo deve ter no máximo 20 caracteres.
            Cada nome deve conter nome e sobrenome completos, ambos com pelo menos 3 letras, sem iniciais, abreviações ou nomes com apenas uma palavra.
            Use preferencialmente nomes e sobrenomes comuns no Brasil, que soem naturais e fáceis de pronunciar em português.
            Retorne o resultado em formato JSON, sem explicações, comentários ou texto extra:

            {{
                "nomes": [
                    "Nome Sobrenome",
                    "Nome Sobrenome",
                    "..."
                ]
            }}
            """

            resposta_ia = self.enviar_para_ia(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=200,
                temperature=1.3,
                top_p=0.95,
                model="llama-3.3-70b-versatile",
                json=True
            )

            if not resposta_ia.strip():
                print(self.formatar_texto("Erro: Nome gerado está vazio. Por favor, forneça um nome manualmente.", cor="vermelho", negrito=True))
                nome_input = input(self.formatar_texto("Digite o nome do personagem (até 20 caracteres): ", cor="rosa", negrito=True)).strip()
            else:
                try:
                    nomes_json = json.loads(resposta_ia.strip())
                    if "nomes" in nomes_json and isinstance(nomes_json["nomes"], list) and nomes_json["nomes"]:
                        nome_input = random.choice(nomes_json["nomes"])
                    else:
                        raise ValueError("JSON malformado ou sem nomes.")
                except Exception as e:
                    print(self.formatar_texto(f"Erro ao interpretar nomes gerados: {e}", cor="vermelho", negrito=True))
                    nome_input = input(self.formatar_texto("Digite o nome do personagem (até 20 caracteres): ", cor="rosa", negrito=True)).strip()

        # Corrigir o nome com IA
        prompt = f"""
            Corrija e formate este nome para seguir as regras de nomes próprios em português:

            - Corrigir capitalização (ex: 'ana clara' deve virar 'Ana Clara')
            - Manter partículas como 'de', 'da', 'dos' em minúsculo
            - Adicionar acentos, se faltar
            - O nome completo deve ter no máximo 20 caracteres
            - Não adicionar ou remover palavras
            - Retorne apenas o nome corrigido, sem explicações, sem setas, sem texto extra.

            Nome a corrigir: {nome_input}

            Responda apenas com o nome corrigido, sem aspas ou blocos de código.
        """

        nome_corrigido = self.enviar_para_ia(
            prompt=prompt,
            max_tokens=20,
            temperature=0.8,
            top_p=0.8,
            model="llama-3.3-70b-versatile"
        ).strip()

        # Se nome foi realmente corrigido e está diferente
        if nome_corrigido and nome_corrigido != self.respostas.get("Nome", ""):
            self.respostas["Nome"] = nome_corrigido
            self.salvar_json(self.charJsons["personagem_info"], self.respostas)
            print(self.formatar_texto("Nome ajustado e atualizado com sucesso em: " + self.charJsons["personagem_info"], cor="ciano"))
            self.print_personagem_info(self.respostas)

        return nome_corrigido


    # Cria uma descrição geral do personagem com base nas informações coletadas, usando IA para gerar um texto criativo.
    def criar_descricao_geral(self):
        print(self.formatar_texto("\nVamos criar uma descrição geral do seu personagem, com base nas informações fornecidas.", cor="azul", negrito=True))

        # Já existe a descrição?
        if os.path.exists(self.charJsons["personagem_geral"]):
            self.personagem["Descrição Geral"] = self.abrir_json(self.charJsons["personagem_geral"])
            print(self.formatar_texto("Arquivo existente encontrado! Descrição Geral carregada de: \"" + self.charJsons["personagem_geral"] + "\"", cor="verde"))
            self.print_personagem_geral(self.personagem["Descrição Geral"])
            return

        # Gera resumo com base nas respostas
        resumo = "\n".join(f"{k.capitalize()}: {v}" for k, v in self.respostas.items())

        # Prompt com tom leve, humano e descritivo
        prompt = f"""
            Baseado nas informações abaixo, crie uma descrição geral clara e criativa do personagem, com até 7000 caracteres.
            Escreva a descrição somente em português do Brasil, sem nenhuma palavra em outro idioma.
            Não use frases de introdução como "Conheça..." ou "Apresentando...". Comece direto na descrição.
            Foque em descrever a aparência física, personalidade, gostos e desgostos, e outros detalhes relevantes.
            Evite clichês e generalizações. Use uma linguagem envolvente e que capture a essência do personagem.
            Use um texto fluido, direto e que descreva as características e personalidade do personagem.
            
            Informações:
            {resumo}
            
            Texto:
        """

        descricao = self.enviar_para_ia(
            prompt=prompt,
            max_tokens=4096,
            temperature=1,
            top_p=1,
            model="llama-3.3-70b-versatile"
        )

        if not descricao.strip():
            print(self.formatar_texto("Erro: descrição vazia ou inválida. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
            return

        # Salvar e mostrar
        self.personagem["Descrição Geral"] = descricao.strip()
        self.salvar_json(self.charJsons["personagem_geral"], self.personagem["Descrição Geral"])
        print(self.formatar_texto("Descrição Geral salva com sucesso em: "+ self.charJsons["personagem_geral"], cor="verde"))
        self.print_personagem_geral(self.personagem["Descrição Geral"])

    # Gera um slogan para o personagem, garantindo que esteja dentro de um intervalo específico de caracteres e coerente com a descrição geral.
    def gerar_slogan(self):
        print(self.formatar_texto("\nVamos criar um Slogan para seu personagem.", cor="azul", negrito=True))

        # Já existe um slogan?
        if os.path.exists(self.charJsons["personagem_slogan"]):
            self.personagem["Slogan"] = self.abrir_json(self.charJsons["personagem_slogan"])
            print(self.formatar_texto("Arquivo existente encontrado! Slogan carregado de: \"" + self.charJsons["personagem_slogan"] + "\"", cor="verde"))
            print(self.personagem["Slogan"] + " (" + str(len(self.personagem["Slogan"])) + " caracteres)")
            return self.personagem["Slogan"]

        descricao = self.personagem.get("Descrição Geral", "")

        def tentar_gerar_slogan():
            prompt = f"""
            Com base na descrição geral do personagem abaixo:

            {descricao}

            Crie um slogan com no máximo 50 caracteres que o personagem usaria para se descrever, usando uma frase impactante e memorável.

            Responda apenas com o slogan, sem aspas, explicações ou texto adicional.
            """
            return self.enviar_para_ia(
                prompt=prompt,
                max_tokens=20,
                temperature=0.6,
                top_p=0.9,
                model="llama-3.3-70b-versatile"
            ).strip()

        tentativa = 1
        max_tentativas = 3
        slogan = ""
        while tentativa <= max_tentativas:
            slogan = tentar_gerar_slogan()
            tamanho = len(slogan)
            if tamanho <= 50:
                break
            print(self.formatar_texto(f"Tentativa {tentativa}: \"{slogan}\" ({tamanho} caracteres) fora do intervalo.", cor="amarelo"))
            tentativa += 1

        # Se ainda assim não estiver no intervalo
        if not len(slogan) <= 50:
            print(self.formatar_texto("\nA IA não gerou um slogan dentro do intervalo após 3 tentativas.", cor="vermelho"))
            resposta = input("Deseja tentar mais 3 vezes? (s/n): ").strip().lower()
            if resposta == "s":
                tentativa = 1
                while tentativa <= max_tentativas:
                    slogan = tentar_gerar_slogan()
                    tamanho = len(slogan)
                    if tamanho <= 50:
                        break
                    print(self.formatar_texto(f"Nova tentativa {tentativa}: \"{slogan}\" ({tamanho} caracteres) fora do intervalo.", cor="amarelo"))
                    tentativa += 1

        self.personagem["Slogan"] = slogan
        self.salvar_json(self.charJsons["personagem_slogan"], slogan)
        print(self.formatar_texto("Slogan salvo com sucesso em: " + self.charJsons["personagem_slogan"], cor="verde"))
        print(slogan + " (" + str(len(slogan)) + " caracteres)")

        return slogan
    
    def criar_descricao(self):
        print(self.formatar_texto("\nVamos criar a descrição do personagem.", cor="azul", negrito=True))

        # Já existe uma descrição?
        if os.path.exists(self.charJsons["personagem_descricao"]):
            self.personagem["Descrição"] = self.abrir_json(self.charJsons["personagem_descricao"])
            print(self.formatar_texto("Arquivo existente encontrado! Descrição carregada de: \"" + self.charJsons["personagem_descricao"] + "\"", cor="verde"))
            print(self.personagem["Descrição"] + f" ({len(self.personagem['Descrição'])} caracteres)")
            return self.personagem["Descrição"]

        descricao_geral = self.personagem.get("Descrição Geral", "")

        def tentar_gerar_descricao():
            prompt = f"""
                Com base na descrição geral abaixo, crie uma descrição clara e criativa com até 500 caracteres:

                {descricao_geral}

                Responda apenas com a descrição, sem aspas, explicações ou texto extra.
            """
            return self.enviar_para_ia(
                prompt=prompt,
                max_tokens=600,
                temperature=0.6,
                top_p=0.9,
                model="llama-3.3-70b-versatile"
            ).strip()

        tentativa = 1
        max_tentativas = 3
        descricao = ""

        while tentativa <= max_tentativas:
            descricao = tentar_gerar_descricao()
            tamanho = len(descricao)
            if tamanho <= 500:
                break
            print(self.formatar_texto(f"Tentativa {tentativa}: {tamanho} caracteres (limite: 500).", cor="amarelo"))
            tentativa += 1

        if len(descricao) > 500:
            print(self.formatar_texto("\nA IA não conseguiu gerar uma descrição com até 500 caracteres após 3 tentativas.", cor="vermelho"))
            resposta = input("Deseja tentar mais 3 vezes? (s/n): ").strip().lower()
            if resposta == "s":
                tentativa = 1
                while tentativa <= max_tentativas:
                    descricao = tentar_gerar_descricao()
                    tamanho = len(descricao)
                    if tamanho <= 500:
                        break
                    print(self.formatar_texto(f"Nova tentativa {tentativa}: {tamanho} caracteres.", cor="amarelo"))
                    tentativa += 1

        self.personagem["Descrição"] = descricao
        self.salvar_json(self.charJsons["personagem_descricao"], descricao)
        print(self.formatar_texto("Descrição salva com sucesso em: " + self.charJsons["personagem_descricao"], cor="verde"))
        print(descricao + f" ({len(descricao)} caracteres)")

        return descricao
    
    # Gera uma saudação personalizada para o personagem, garantindo que esteja dentro dos limites de caracteres e coerente com a descrição geral.
    def gerar_saudacao(self):
        print(self.formatar_texto("\nVamos gerar a saudação do personagem.", cor="azul", negrito=True))

        # Já existe uma saudação?
        if os.path.exists(self.charJsons["personagem_saudacao"]):
            self.personagem["Saudação"] = self.abrir_json(self.charJsons["personagem_saudacao"])
            print(self.formatar_texto("Arquivo existente encontrado! Saudação carregada de: \"" + self.charJsons["personagem_saudacao"] + "\"", cor="verde"))
            print(self.personagem["Saudação"][:300] + ("..." if len(self.personagem["Saudação"]) > 300 else ""))
            print(f"({len(self.personagem['Saudação'])} caracteres)")
            return self.personagem["Saudação"]

        descricao_geral = self.personagem.get("Descrição Geral", "")

        prompt = f"""
            Com base na descrição abaixo, crie uma saudação que esse personagem usaria no início de qualquer chat.

            Seja coerente com a personalidade do personagem. Pode ser curta ou longa, desde que não ultrapasse 4096 caracteres.

            Descrição:
            {descricao_geral}

            Responda apenas com a saudação, sem aspas nem explicações.
        """

        # Gera novamente até estar dentro do limite
        while True:
            saudacao = self.enviar_para_ia(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                model="llama-3.3-70b-versatile"
            ).strip()

            if len(saudacao) <= 4096:
                break

            print(self.formatar_texto(f"Aviso: Saudação gerada com {len(saudacao)} caracteres. Gerando novamente...", cor="amarelo"))

        self.personagem["Saudação"] = saudacao
        self.salvar_json(self.charJsons["personagem_saudacao"], saudacao)

        print(self.formatar_texto("Saudação salva com sucesso em: " + self.charJsons["personagem_saudacao"], cor="verde"))
        print(saudacao[:300] + ("..." if len(saudacao) > 300 else ""))
        print(f"({len(saudacao)} caracteres)")

        return saudacao

    # Gera etiquetas para o personagem, classificando-o em até 5 categorias a partir de uma lista pré-definida.
    def gerar_etiquetas(self):
        print(self.formatar_texto("\nVamos gerar as etiquetas (máx. 5 categorias).", cor="azul", negrito=True))

        # Já existe um arquivo?
        if os.path.exists(self.charJsons["personagem_etiquetas"]):
            self.personagem["Etiquetas"] = self.abrir_json(self.charJsons["personagem_etiquetas"])
            print(self.formatar_texto("Arquivo existente encontrado! Etiquetas carregadas de: \"" + self.charJsons["personagem_etiquetas"] + "\"", cor="verde"))
            print(self.personagem["Etiquetas"])
            return self.personagem["Etiquetas"]

        descricao = self.personagem.get("Descrição Geral", "")

        prompt = f"""
            Com base na descrição geral abaixo, escolha **no máximo 5 etiquetas** para classificar esse personagem a partir da lista fornecida.

            Descrição:
            "{descricao}"

            Lista de etiquetas possíveis:
            Anime, Action, Adventure, Fantasy, Romance, Shy, Yandere, LGBTQIA, Platonic, Boss, Boyfriend, Girlfriend, Husband, Mafia, Wife, Human, Slice of Life, Classmate, Coworker, Schoolmate, RPG, Vampire, Love interest, One-sided, Magicverse, Royalverse, Comedy, Ноггог, Supernatural, Bully, Best friend, Brother, Ghost, Police, Professor, Roommate, Sister, Student, Teacher, Robot, Collegeverse, Heroverse, Vtuber, Coming of Age, Dystopian, Mystery/Thriller, Parody, Science Fiction, Apprentice, Colleague, Crime Boss, Enemy, Executive, Father, Gangster, Mentor, Mother, Fairy, Bossy, Diligent, Empathetic, Flirtatious, Jealous, Kind, Manipulative, Narcissistic, K-Pop, Drama, Officeworkverse, Sports, Coffeeverse

            Responda apenas com as etiquetas separadas por vírgula, sem explicações.
        """

        while True:
            etiquetas = self.enviar_para_ia(
                prompt=prompt,
                max_tokens=150,
                temperature=0.5,
                top_p=0.9,
                model="llama-3.3-70b-versatile"
            ).strip()

            # Valida quantidade de etiquetas
            etiquetas_lista = [e.strip() for e in etiquetas.split(",") if e.strip()]
            if len(etiquetas_lista) <= 5:
                break

            print(self.formatar_texto(f"Aviso: Foram retornadas {len(etiquetas_lista)} etiquetas. Gerando novamente...", cor="amarelo"))

        self.personagem["Etiquetas"] = ", ".join(etiquetas_lista)
        self.salvar_json(self.charJsons["personagem_etiquetas"], self.personagem["Etiquetas"])

        print(self.formatar_texto("Etiquetas salvas com sucesso em: " + self.charJsons["personagem_etiquetas"], cor="verde"))
        print(self.personagem["Etiquetas"])

        return self.personagem["Etiquetas"]

    # Gera um prompt para definir o personagem, formatando as informações de título, descrição e conteúdo.
    def gerar_prompt_definicao(self, dados):
        # Verifica se os dados contêm as chaves necessárias
        descricao_personagem = self.personagem.get("Descrição Geral", "")
        
        # Adicionando as perguntas com resposta formatada
        perguntas_json = json.dumps(
            [{"indice": p["indice"], "pergunta": p["pergunta"], "resposta": ""} for p in dados["perguntas"]],
            indent=4,
            ensure_ascii=False
        )
        
        instrucao = dados.get("instrucao", "")
        instrucao = f" ({instrucao})" if instrucao else ""

        # Formata o prompt com a descrição do personagem e as perguntas
        prompt = f"""
            Analise a descrição do personagem abaixo e responda as perguntas com base nessas descrições.
            Sua tarefa é completar um JSON com respostas extraídas de um texto fornecido.

            ### Instruções:
            - Leia atentamente a descrição do personagem.
            - Leia a lista de perguntas no formato JSON.
            - Para cada item, responda com base apenas nas informações fornecidas no texto.
            - Responda **apenas o JSON puro**, mantendo **apenas os campos "indice" e "resposta"** em cada item, sem explicações, sem texto adicional e sem blocos markdown (ex: ```json).
            - NÃO inclua nenhuma outra palavra, frase, explicação ou aspas extras.
            - Se a resposta não estiver clara no texto, não invente informações, apenas deixe o campo "resposta" como uma string vazia: "" (duas aspas sem espaço).

            #### Descrição do personagem:
            {descricao_personagem}

            #### Perguntas sobre o personagem{instrucao}:
            {perguntas_json}
            
            Responda SOMENTE com um JSON no seguinte formato:
            {{
    "cor_cabelo": "castanho escuro",
    "estilo_cabelo": "liso"
    ...
}}

            Não adicione comentários, explicações ou texto fora do JSON. Certifique-se de que o JSON esteja BEM FORMADO.
            """
            
        return prompt

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
                    self.personagem["Definição"][identificador] = self.abrir_json(novo_arquivo)
                    print(self.formatar_texto(f"Arquivo existente encontrado! Definição carregada de: \"{novo_arquivo}\"", cor="verde"))
                    self.print_personagem_definicao(identificador)
                    continue

                else:
                    prompt = self.gerar_prompt_definicao(dados)
                    
                    max_tentativas = 3
                    tentativa = 0
                    definicao = None
                    
                    while tentativa < max_tentativas:
                        resposta = self.enviar_para_ia(
                            prompt=prompt,
                            max_tokens=2048, 
                            temperature=1, 
                            top_p=1, 
                            model="llama-3.3-70b-versatile",
                            json=True
                        )
                        
                        # Verifica se a resposta é válida
                        if not resposta:
                            print(self.formatar_texto("Erro: Resposta vazia ou inválida da IA. Tente novamente.", cor="vermelho", negrito=True))
                            tentativa += 1
                            continue
                        
                        try:
                            definicao = self.extrair_json(resposta)
                            break  # Sai do loop se deu certo
                        
                        except ValueError as erro:
                            print(self.formatar_texto(f"Erro ao processar JSON da IA: {erro}. Tentando novamente...", cor="vermelho", negrito=True))
                            tentativa += 1
            
                    if definicao is None:
                        print(self.formatar_texto("Erro: Não foi possível obter um JSON válido após várias tentativas.", cor="vermelho", negrito=True))
                        return

                    # Salva a definição em um arquivo JSON
                    self.salvar_json(novo_arquivo, definicao)
                    
                    self.personagem["Definição"][identificador] = definicao
                    print(self.formatar_texto(f"Definição parcial salva com sucesso em: {novo_arquivo}", cor="verde"))
                    self.print_personagem_definicao(identificador)
                    continue


    def criar_dialogos(self):
        print(self.formatar_texto("\nVamos criar uma lista de dialogos para seu personagem, com base nas informações fornecidas.", cor="azul", negrito=True))

        # Já existe aos diálogos?
        if os.path.exists(self.charJsons["personagem_dialogos"]):
            self.personagem["Diálogos"] = self.abrir_json(self.charJsons["personagem_dialogos"])
            print(self.formatar_texto("Arquivo existente encontrado! Diálogos carregada de: \"" + self.charJsons["personagem_dialogos"] + "\"", cor="verde"))
            self.print_personagem_dialogos(self.personagem["Diálogos"])
            return

        # Gera rediálogos com base na descrição geral
        descricao = self.personagem.get("Descrição Geral", "")
        if not descricao:
            print(self.formatar_texto("Erro: Descrição Geral do personagem não encontrada. Por favor, crie uma descrição geral primeiro.", cor="vermelho", negrito=True))
            return

        dialogos_json = {
            "dialogos": [
                [
                    {
                        "user": "random_user_2",
                        "msg": "Márcia, você tem algum hobby?"
                    },
                    {
                        "user": "char",
                        "msg": "Sim, eu gosto de pintar e fazer jardinagem. E você, tem algum hobby?"
                    }
                ],
                [
                    {
                        "user": "user",
                        "msg": "Olá, você parece muito interessante. Posso conhecê-la melhor?"
                    },
                    {
                        "user": "char",
                        "msg": "Claro, eu sou Márcia. E você?"
                    }
                ],
                [
                    {
                        "user": "char",
                        "msg": "Ei, você gosta de música?"
                    },
                    {
                        "user": "random_user_2",
                        "msg": "Sim, adoro música! E você?"
                    }
                ],
                [
                    {
                        "user": "random_user_1",
                        "msg": "Márcia, você gosta de esportes?"
                    },
                    {
                        "user": "char",
                        "msg": "Gosto sim! Eu pratico yoga e adoro caminhadas ao ar livre."
                    }
                ],
                [
                    {
                        "user": "user",
                        "msg": "Márcia, qual é o seu filme favorito?"
                    },
                    {
                        "user": "char",
                        "msg": "Eu amo filmes de comédia romântica! Eles sempre me fazem rir."
                    }
                ]
            ]
        }
        
        prompt = f"""
            Você é um agente Json, responsável por criar conversas realistas entre um personagem fictício e outras pessoas, com base em sua descrição detalhada de personalidade, aparência, passado, profissão, etc.
            Com base na descrição do personagem abaixo, gere um Json de diálogos curtos entre o personagem e outros usuários. Cada diálogo deve conter um par de mensagens: pergunta e resposta.

            ### DESCRIÇÃO DO PERSONAGEM
            {descricao}

            ### Formato de saída obrigatório:
            {json.dumps(dialogos_json, indent=2, ensure_ascii=False)}
            
            ### Importante: 
            Nunca copie os dados do JSON acima, crie mensagens novas e únicas, que reflitam a personalidade e o estilo do personagem.

            A conversa deve:
            - Mostrar o jeito de falar, emoções e estilo próprio do personagem.
            - Misturar interações do 'char' com 'user', 'random_user_1', 'random_user_2', etc.
            - Incluir situações diferentes: papo leve, elogios, perguntas, provocações, conselhos, piadas, etc.
            - Ser bem natural, como se o personagem estivesse vivo.
            - Ter aproximadamente 40 pares de mensagens.
            - Usar mensagens curtas, naturais e diretas.
            - Nunca sair do formato do JSON acima, nem adicionar explicações extras.

            # Use 'user' para o usuário que está conversando.
            # Use 'char' para o personagem que está respondendo.
            # Use 'random_user_1', 'random_user_2', ... para nomes de usuários aleatórios diferentes entre si e do 'user'.
            # Cada mensagem deve ser curta, direta e natural, como se fosse uma conversa real.
            # As mensagens devem ser naturais, com fluxo de conversa, mostrando personalidade, jeito de falar e emoção do personagem.
            # Inclua pelo menos 20 pares de mensagens para mostrar diferentes situações e tons da conversa.
            # Misture perguntas do 'char' e dos 'random_user_x' para enriquecer o diálogo.
            # Mostre como o 'char' responde a dúvidas, provocações, elogios, dúvidas pessoais, etc.
            # Evite respostas muito longas; prefira mensagens curtas e diretas, com linguagem informal e estilo próprio do personagem.

            # Não adicione comentários, explicações ou texto fora do JSON. Certifique-se de que o JSON esteja BEM FORMADO.
            # Finalize sem nenhuma marcação extra, só o diálogo.
        """

        resposta = self.enviar_para_ia(
            prompt=prompt,
            max_tokens=4096,
            temperature=1.2,
            top_p=1,
            model="llama-3.3-70b-versatile",
            json=True
        ).strip()

        if not resposta:
            print(self.formatar_texto("Erro: resposta vazia ou inválida. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
            return

        # Salvar e mostrar
        self.personagem["Diálogos"] = json.loads(resposta)
        self.salvar_json(self.charJsons["personagem_dialogos"], self.personagem["Diálogos"])
        print(self.formatar_texto("Diálogos salvos com sucesso em: "+ self.charJsons["personagem_dialogos"], cor="verde"))
        self.print_personagem_dialogos(self.personagem["Diálogos"])
        
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
                        pergunta_resposta = dados_comp[pergunta_indice]
                        
                        pergunda_pronta = pergunta_texto.replace("{" + f"{pergunta_indice}" + "}", pergunta_resposta)
                        
                        if pergunta_texto:
                            if pergunta_resposta != "":
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
            
            for i, dialogo in enumerate(dialogos["dialogos"], start=1):
                if isinstance(dialogo, list) and len(dialogo) == 2:
                    user_a_type = dialogo[0].get("user", "")
                    user_a_msg = dialogo[0].get("msg", "")
                    user_b_type = dialogo[1].get("user", "")
                    user_b_msg = dialogo[1].get("msg", "")

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
        print(self.formatar_texto("Nome da personagem (" + str(len(self.respostas.get("Nome"))) + " de 20 caractéres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.respostas.get("Nome")))
        print("----------")
        print(self.formatar_texto("Slogan (" + str(len(self.personagem.get("Slogan"))) + " de 50 caractéres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Slogan")))
        print("----------")
        print(self.formatar_texto("Descrição (" + str(len(self.personagem.get("Descrição"))) + " de 500 caractéres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Descrição")))
        print("----------")
        print(self.formatar_texto("Saudação (" + str(len(self.personagem.get("Saudação"))) + " de 4096 caractéres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Saudação")))
        print("----------")
        etiquetas = self.personagem.get("Etiquetas")
        lista_etiquetas = [e.strip() for e in etiquetas.split(",") if e.strip()]
        print(self.formatar_texto("Etiquetas (" + str(len(lista_etiquetas)) + " de 5 etiquetas):", cor="ciano", negrito=True))
        print(self.formatar_texto(etiquetas))
        print("----------")
        print(self.formatar_texto("Definições (" + str(len(self.personagem.get("Definição Final"))) + " de 32000 caractéres):", cor="ciano", negrito=True))
        print(self.formatar_texto(self.personagem.get("Definição Final")))
        
        print("###################################")
        
        
# Verifica se o script está sendo executado diretamente 
if __name__ == "__main__":
    print("Este módulo não deve ser executado diretamente. Use o script principal para interagir com a classe BuildMyChar.")
    
    # ⚠️ Apenas para testes durante o desenvolvimento. Remover depois!
    print("Executando main.py para testes...")
    import os
    os.system("python main.py")
    