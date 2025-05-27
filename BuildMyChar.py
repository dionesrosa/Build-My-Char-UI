import os
import json
import random
from groq import Groq

class BuildMyChar:
    """Classe para construir personagens, coletando informações do usuário e gerando descrições usando IA."""
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("Erro: variável de ambiente GROQ_API_KEY não encontrada.")
            return
    
        self.client = Groq(api_key=api_key)
        self.respostas = {}
        self.personagem = {}
        self.charJsons = {
            "perguntas": "perguntas.json",
            "personagem_info": "temp/personagem_info.json",
            "personagem_geral": "temp/personagem_geral.json",
            "personagem_slogan": "temp/personagem_slogan.json",
            "personagem_descricao": "temp/personagem_descricao.json",
            "personagem_saudacao": "temp/personagem_saudacao.json",
            "personagem_etiquetas": "temp/personagem_etiquetas.json",
            "personagem_definicao": "temp/personagem_definicao.json",
            "personagem_dialogos": "temp/personagem_dialogos.json"
        }
    
    """Abre um arquivo JSON e retorna os dados como um dicionário. Se ocorrer um erro, imprime uma mensagem e retorna um dicionário vazio."""
    def abrir_json(self, caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        except Exception as e:
            print(f"Erro ao abrir JSON: {e}")
            return {}
    
    """Salva os dados em um arquivo JSON, formatando com indentação e sem caracteres ASCII."""   
    def salvar_json(self, caminho, dados):
        try:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Erro ao salvar JSON: {e}")

    """Formata o texto com cores e estilos ANSI, permitindo personalização de cor, negrito, itálico e sublinhado."""
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

    """Envia um prompt para a IA e retorna a resposta formatada."""
    def enviar_para_ia(self, prompt=None, system_prompt=None, max_tokens=1024, temperature=0.7, top_p=0.85, stop=None, model="llama3-70b-8192"):
        if not system_prompt:
            system_prompt = {
                "role": "system",
                "content": "Você é um assistente que ajuda a criar personagens para Character.ai, formatando respostas conforme solicitado."
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
            model=model,
            messages=messages,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            top_p=top_p,
            stream=False,
            stop=stop,
        )
        
        return response.choices[0].message.content.strip()
    
    """Imprime as informações do personagem formatadas, destacando cada informação com estilo."""
    def print_personagem_info(self, respostas):          
        print(self.formatar_texto("Informações do Personagem:", cor="amarelo", negrito=True))
        for k, v in self.respostas.items():
            print(self.formatar_texto(f"* {k}: {v}", cor="amarelo", italico=True))
    
    """Imprime a descrição geral do personagem, formatando o texto para destaque."""
    def print_personagem_geral(self, descricao):          
        print(self.formatar_texto("Descrição Geral do Personagem:", cor="amarelo", negrito=True))
        print(self.formatar_texto(descricao, cor="amarelo", italico=True))
    
    """Pergunta ao usuário por uma informação específica, formatando a pergunta e fornecendo uma dica para pular a resposta."""            
    def perguntar(self, texto):
        pergunta_formatada = self.formatar_texto(texto, cor="rosa", negrito=True)
        dica_formatada = self.formatar_texto(" (aperte Enter para pular): ", italico=True)
        resposta = input(pergunta_formatada + dica_formatada).strip()
        return resposta

    """Coleta informações do usuário sobre o personagem, perguntando uma série de questões definidas em um arquivo JSON."""
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
            
    """Gera o nome do personagem, corrigindo capitalização e formatando conforme regras de nomes próprios em português."""
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
            Retorne o resultado em formato JSON assim, sem explicações, comentários ou texto extra:

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
                max_tokens=250,
                temperature=1.3,
                top_p=0.95,
                model="llama3-70b-8192"
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

        - Corrigir capitalização (ex: "ana clara" deve virar "Ana Clara")
        - Manter partículas como "de", "da", "dos" em minúsculo
        - Adicionar acentos, se faltar
        - O nome completo deve ter no máximo 20 caracteres
        - Não adicionar ou remover palavras
        - Retorne apenas o nome corrigido, sem explicações, sem setas, sem texto extra.

        Nome a corrigir: "{nome_input}"
        """

        nome_corrigido = self.enviar_para_ia(
            prompt=prompt,
            max_tokens=50,
            temperature=0.2,
            top_p=0.8,
            model="llama3-70b-8192"
        ).strip()

        # Se nome foi realmente corrigido e está diferente
        if nome_corrigido and nome_corrigido != self.respostas.get("Nome", ""):
            self.respostas["Nome"] = nome_corrigido
            self.salvar_json(self.charJsons["personagem_info"], self.respostas)
            print(self.formatar_texto("Nome ajustado e atualizado com sucesso em: " + self.charJsons["personagem_info"], cor="ciano"))
            self.print_personagem_info(self.respostas)

        return nome_corrigido


    """Cria uma descrição geral do personagem com base nas informações coletadas, usando IA para gerar um texto criativo."""
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
            Baseado nas informações abaixo, crie uma descrição geral clara e criativa do personagem, com até 5000 caracteres.
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
            max_tokens=2048,
            temperature=0.7,
            top_p=0.95,
            model="llama3-70b-8192"
        )

        if not descricao.strip():
            print(self.formatar_texto("Erro: descrição vazia ou inválida. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
            return

        # Salvar e mostrar
        self.personagem["Descrição Geral"] = descricao.strip()
        self.salvar_json(self.charJsons["personagem_geral"], self.personagem["Descrição Geral"])
        print(self.formatar_texto("Descrição Geral salva com sucesso em: "+ self.charJsons["personagem_geral"], cor="verde"))
        self.print_personagem_geral(self.personagem["Descrição Geral"])

    """Gera um slogan para o personagem, garantindo que esteja dentro de um intervalo específico de caracteres e coerente com a descrição geral."""  
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

            "{descricao}"

            Crie um slogan entre 40 e 50 caracteres que o personagem usaria para se descrever, usando uma frase impactante e memorável.

            Responda apenas com o slogan, sem aspas, explicações ou texto adicional.
            """
            return self.enviar_para_ia(
                prompt=prompt,
                max_tokens=60,
                temperature=0.3,
                top_p=0.9,
                model="llama3-70b-8192"
            ).strip()

        tentativa = 1
        max_tentativas = 3
        slogan = ""
        while tentativa <= max_tentativas:
            slogan = tentar_gerar_slogan()
            tamanho = len(slogan)
            if 40 <= tamanho <= 50:
                break
            print(self.formatar_texto(f"Tentativa {tentativa}: \"{slogan}\" ({tamanho} caracteres) fora do intervalo.", cor="amarelo"))
            tentativa += 1

        # Se ainda assim não estiver no intervalo
        if not 40 <= len(slogan) <= 50:
            print(self.formatar_texto("\nA IA não gerou um slogan dentro do intervalo após 3 tentativas.", cor="vermelho"))
            resposta = input("Deseja tentar mais 3 vezes? (s/n): ").strip().lower()
            if resposta == "s":
                tentativa = 1
                while tentativa <= max_tentativas:
                    slogan = tentar_gerar_slogan()
                    tamanho = len(slogan)
                    if 40 <= tamanho <= 50:
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

                "{descricao_geral}"

                Responda apenas com a descrição, sem aspas, explicações ou texto extra.
            """
            return self.enviar_para_ia(
                prompt=prompt,
                max_tokens=600,
                temperature=0.6,
                top_p=0.9,
                model="llama3-70b-8192"
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
    
    """Gera uma saudação personalizada para o personagem, garantindo que esteja dentro dos limites de caracteres e coerente com a descrição geral."""
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
            Com base na descrição geral abaixo, crie uma saudação que esse personagem usaria no início de qualquer chat.

            Seja coerente com a personalidade do personagem. Pode ser curta ou longa, desde que não ultrapasse 4096 caracteres.

            Descrição:
            "{descricao_geral}"

            Responda apenas com a saudação, sem aspas nem explicações.
        """

        # Gera novamente até estar dentro do limite
        while True:
            saudacao = self.enviar_para_ia(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9,
                model="llama3-70b-8192"
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
                model="llama3-70b-8192"
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

    def gerar_prompt_definicao(self, titulo, descricao, conteudo, descricao_personagem):
        prompt = f"""
            Aqui está a descrição geral do personagem:
            \"\"\"
            {descricao_personagem}
            \"\"\"

            Sua tarefa é preencher os dados solicitados abaixo com base **apenas** nas informações explícitas fornecidas acima.

            # {titulo} ({descricao})
            {conteudo}

            Formato da resposta:
            Retorne um objeto JSON, sendo que os índices serão a informação que esta sendo pedida de forma resumida, Exemplo: Nome, Idade, Gênero, etc.
            Não use comentários, explicações ou texto fora do JSON.
            Se algum valor não puder ser definido com clareza, use `null`, `false`, ou `""` (string vazia), conforme o tipo. **Não invente ou deduza.**
    
            Preencha apenas os campos relevantes para esta seção e deixe os outros de fora se não forem mencionados ou claros.

            IMPORTANTE:
            - Responda **apenas** com o JSON válido.
            - Não escreva texto fora do JSON.
            - Não inclua campos genéricos ou suposições.
        """.strip()

        return prompt



    def gerar_definicao(self):
        load_template = self.abrir_json("template.json")
        if not load_template:
            print(self.formatar_texto("Erro: Não foi possível carregar o template de definição.", cor="vermelho", negrito=True))
            return
        
        print(self.formatar_texto("\nVamos gerar a definição do personagem.", cor="azul", negrito=True))
        
        #definicao = {}
        
        total = len(load_template)
        for i, (chave, dados) in enumerate(load_template.items(), start=1):
            caminho = f"temp/personagem_definicao_{chave}.json"
            msg = f"Gerando definição {i} de {total}: {caminho}"
            print(self.formatar_texto(msg, cor="amarelo", italico=True))
            
            char_titulo = dados.get("titulo", "").strip()
            char_descricao = dados.get("descricao", "").strip()
            char_conteudo = dados.get("conteudo", "").strip()
            
            descricao = self.personagem.get("Descrição Geral", "").strip()
            if not descricao:
                print(self.formatar_texto("Erro: Descrição Geral do personagem não encontrada. Por favor, crie uma descrição geral primeiro.", cor="vermelho", negrito=True))
                return
            
            if not char_titulo or not char_descricao or not char_conteudo:
                print(self.formatar_texto("Erro: Dados de definição incompletos. Verifique o template JSON.", cor="vermelho", negrito=True))
                return

            prompt = self.gerar_prompt_definicao(char_titulo, char_descricao, char_conteudo, descricao)

            resposta = self.enviar_para_ia(
                prompt=prompt,
                system_prompt="Você é um assistente que ajuda a criar personagens para Character.ai, formatando respostas conforme solicitado.",
                max_tokens=200, 
                temperature=0.51, 
                top_p=0.8, 
                model="llama-3.3-70b-versatile"
            ).strip()
            
            if not resposta:
                print(self.formatar_texto("Erro: Resposta vazia da IA. Tente novamente ou revise as informações.", cor="vermelho", negrito=True))
                return
            
            print(resposta)
            
            return

            """print(self.formatar_texto(f"\n{titulo}", cor="amarelo", negrito=True))
            print(descricao)
            
            if conteudo:
                print(self.formatar_texto("Dica:", cor="ciano") + f"\n{conteudo}")

            resposta = input(self.formatar_texto("\nSua resposta: ", cor="verde")).strip()
            definicao[chave] = resposta

        # Aqui você pode salvar ou imprimir a definição gerada
        print(self.formatar_texto("\nDefinição final gerada:", cor="azul", negrito=True))
        print(json.dumps(definicao, indent=2, ensure_ascii=False))"""
        


    def imprimir_personagem(self):
        print("\n\n--- Personagem Completo ---\n")
        for chave, valor in self.personagem.items():
            print(f"{chave}:\n{valor}\n")
            
if __name__ == "__main__":
    print("Este módulo não deve ser executado diretamente. Use o script principal para interagir com a classe BuildMyChar.")
    exit(0)