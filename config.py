CONFIG = {
    "charJsons": {
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
}

PROMPT = {}

PROMPT["PROMPT_GERADOR_NOME_SYSTEM"] = "Você é um gerador criativo de nomes do gênero: {genero}."
PROMPT["PROMPT_GERADOR_NOME_USER"] = """
Gere 10 nomes completos do gênero {genero}.
Cada nome deve conter um primeiro nome e um sobrenome, ambos com pelo menos 3 letras.
Não use abreviações, letras iniciais isoladas ou nomes únicos (ex: “J. Silva” ou “Carlos”).
Cada nome completo deve ter no máximo 20 caracteres.
Use nomes e sobrenomes comuns no Brasil, fáceis de pronunciar em português.
Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_CORRETOR_NOME_SYSTEM"] = "Você é um gerador corretor de formatação de nomes próprios.",
PROMPT["PROMPT_CORRETOR_NOME_USER"] = """
Corrija e formate este nome para seguir as regras de nomes próprios em português:

- Corrigir capitalização (ex: 'ana clara' deve virar 'Ana Clara')
- Manter partículas como 'de', 'da', 'dos' em minúsculo
- Adicionar acentos, se faltar
- O nome completo deve ter no máximo 20 caracteres
- Não adicionar ou remover palavras
- Retorne apenas o nome corrigido, sem explicações, sem setas, sem texto extra.

Nome a corrigir: {nome}

Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_DESCRICAO_GERAL_SYSTEM"] = "Você é um gerador criativo de histórias de personagens."
PROMPT["PROMPT_DESCRICAO_GERAL_USER"] = """
Baseado nas informações abaixo, crie uma descrição completa, clara e criativa do personagem, com o máximo de detalhes possiveis com até 10000 caracteres.
Escreva a descrição somente em português do Brasil, sem nenhuma palavra em outro idioma.
Não use frases de introdução como "Conheça..." ou "Apresentando...". Comece direto na descrição.
Foque em descrever a aparência física, personalidade, gostos e desgostos, e outros detalhes relevantes.
Evite clichês e generalizações. Use uma linguagem envolvente e que capture a essência do personagem.
Use um texto fluido, direto e que descreva as características e personalidade do personagem.

Informações:
{resumo}

Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_SLOGAN_SYSTEM"] = "Você é um gerador criativo de slogan de personagens."
PROMPT["PROMPT_SLOGAN_USER"] = """
Com base na descrição do personagem abaixo:

{descricao}

Crie um slogan claro e criativo para o personagem, que chegue perto dos {max_caracteres} caracteres, use uma frase impactante e memorável.
Não ultrapasse o limite de {max_caracteres} caracteres.
Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_DESCRICAO_SYSTEM"] = "Você é um gerador criativo de descrição de personagens."
PROMPT["PROMPT_DESCRICAO_USER"] = """
Com base na descrição do personagem abaixo:

{descricao_geral}

Crie uma descrição clara e criativa para o personagem, que chegue perto dos {max_caracteres} caracteres que o personagem usaria para falar sobre ele e sua história.
Não ultrapasse o limite de {max_caracteres} caracteres.
Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_SAUDACAO_SYSTEM"] = "Você é um gerador criativo de saudações para um personagem."
PROMPT["PROMPT_SAUDACAO_USER"] = """
Com base na descrição do personagem abaixo:

{descricao_geral}

Crie uma saudação com no máximo {max_caracteres} caracteres, que esse personagem usaria no início de qualquer conversa.
Seja coerente com a personalidade do personagem.
Pode ser curta ou longa, desde que não ultrapasse {max_caracteres} caracteres.
Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_ETIQUETAS_SYSTEM"] = """
Você é um organizador de etiquetas para um personagem, com base na sua descrição.
Sua tarefa é escolher até 5 etiquetas da lista abaixo para o personagem.

Lista de etiquetas possíveis:
Anime, Action, Adventure, Fantasy, Romance, Shy, Yandere, LGBTQIA, Platonic, Boss, Boyfriend, Girlfriend, Husband, Mafia, Wife, Human, Slice of Life, Classmate, Coworker, Schoolmate, RPG, Vampire, Love interest, One-sided, Magicverse, Royalverse, Comedy, Ноггог, Supernatural, Bully, Best friend, Brother, Ghost, Police, Professor, Roommate, Sister, Student, Teacher, Robot, Collegeverse, Heroverse, Vtuber, Coming of Age, Dystopian, Mystery/Thriller, Parody, Science Fiction, Apprentice, Colleague, Crime Boss, Enemy, Executive, Father, Gangster, Mentor, Mother, Fairy, Bossy, Diligent, Empathetic, Flirtatious, Jealous, Kind, Manipulative, Narcissistic, K-Pop, Drama, Officeworkverse, Sports, Coffeeverse
"""
PROMPT["PROMPT_ETIQUETAS_USER"] = """
Com base na descrição do personagem abaixo:

{descricao}

Escolha no máximo 5 etiquetas listadas acima, para classificar esse personagem.
Não use nenhuma outra etiqueta, a não ser as que estão na lista acima.
Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_INSTRUCAO_SYSTEM"] = "Você é um interpretador de textos, responsável por responder perguntas."
PROMPT["PROMPT_INSTRUCAO_USER"] = """
Com base na descrição do personagem abaixo:

{descricao}

Analise a descrição do personagem e responda as perguntas solicitadas, seguindo as instruções fornecidas.

### Instruções:
- Leia atentamente a descrição do personagem.
- Para cada item, responda com base apenas nas informações fornecidas no texto.
- Se a resposta não estiver clara no texto, não invente informações, apenas deixe o campo "resposta" como uma string vazia: "" (duas aspas sem espaço).
Não esqueça de completar os itens de pergunta_id, pergunta e resposta.
{instrucao}

Lista de perguntas:
{lista}

Retorne apenas em formato JSON, sem explicações ou comentários.
"""

PROMPT["PROMPT_DIALOGOS_SYSTEM"] = "Você é um gerador criativo de diálogos entre personagens."
PROMPT["PROMPT_DIALOGOS_USER"] = """
Com base na descrição abaixo do personagem principal:

{descricao}

Gere 20 pares de mensagens entre o personagem principal ('char') e outras pessoas, no formato JSON.

### Regras de formatação:

- 'char' é o personagem principal descrito acima.
- 'user' é a pessoa que está conversando com ele diretamente.
- 'random_user_1', 'random_user_2', etc., são personagens secundários criados pela IA. Cada um tem personalidade e forma de falar própria.
- Misture os pares: 'char' com 'user' e 'char' com 'random_user_x'.
- Em cada par, uma mensagem deve ser de outro personagem (user ou random_user_x) e a outra é a resposta do 'char'.
- O 'char' também pode iniciar a conversa em alguns pares.
- A ordem dos falantes pode variar entre os pares.
- O retorno deve ser **apenas** um JSON bem formatado com os pares de conversa.

### Estilo das mensagens:

- Mensagens devem ser curtas, naturais, informais e com tom de conversa do dia a dia.
- Reflita a personalidade, emoções e **modo de falar único do 'char'**, incluindo:
  - Sotaques regionais
  - Gírias ou expressões locais
  - Maneirismos verbais
- O mesmo vale para os outros personagens (user e random_user_x): cada um pode ter sotaque ou estilo de fala distinto. Mostre isso claramente nas falas.
- Misture contextos e situações diferentes:
  - Elogios, dúvidas, provocações, piadas, conselhos, desabafos, etc.
- Evite falas longas, forçadas ou muito formais.
- Não inclua explicações, instruções ou comentários fora do JSON.

Retorne apenas em formato JSON, sem explicações ou comentários.
"""