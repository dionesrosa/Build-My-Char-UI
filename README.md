<p align="center">
  <img src="images/cover.png" alt="Capa do Build My Char UI" style="height: 250px; margin: 50px;">
</p>

# Build My Char UI

Um gerador automatizado de personagens para plataformas como Character.AI.  
O script utiliza a API da Groq com o modelo LLaMA3 para criar personagens realistas e completos, a partir de dados fornecidos pelo usuário.

## ✨ Funcionalidades

- **Coleta de informações**: Pergunta ao usuário sobre características do personagem (nome, gênero, personalidade, etc).
- **Geração automática de nome**: Cria nomes completos, naturais e ajustados ao gênero, com validação e correção automática.
- **Descrição geral**: Gera uma descrição longa, detalhada e criativa do personagem, baseada nas respostas do usuário.
- **Slogan**: Cria um slogan curto e marcante, respeitando o limite de caracteres.
- **Descrição curta**: Gera uma descrição resumida (até 500 caracteres) para uso em perfis.
- **Saudação personalizada**: Cria uma saudação única, coerente com a personalidade do personagem.
- **Etiquetas (tags)**: Classifica o personagem em até 5 categorias, escolhidas de uma lista pré-definida.
- **Definição detalhada**: Preenche templates de definição (em JSON), extraindo informações específicas da descrição geral.
- **Diálogos realistas**: Gera uma lista de diálogos curtos e naturais, mostrando como o personagem interage em diferentes situações.
- **Exportação estruturada**: Salva todas as informações em arquivos JSON organizados, prontos para uso em Character.AI ou outros sistemas.
- **Impressão final**: Exibe todas as informações do personagem de forma organizada e formatada no terminal.
- **Personalização**: Fácil de expandir com novos templates de definição e perguntas.

## 🔧 Requisitos

- Python 3.8+
- Conta na Groq com uma chave de API ativa
- Dependências do projeto (ver abaixo)

## 🚀 Como usar

Clone o repositório:

```bash
git clone https://github.com/seu-usuario/Build-My-Char-UI.git
cd Build-My-Char-UI
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie um arquivo `.env` com sua chave da API:

```
GROQ_API_KEY=sua_chave_aqui
```

Execute o script principal:

```bash
python main.py
```

## 🛠️ Principais funções do sistema

- `coletar_informacoes()`: Pergunta ao usuário sobre o personagem e salva as respostas.
- `gerar_nome()`: Gera e corrige o nome do personagem.
- `criar_descricao_geral()`: Cria uma descrição longa e detalhada.
- `gerar_slogan()`: Cria um slogan curto e marcante.
- `criar_descricao()`: Gera uma descrição curta (até 500 caracteres).
- `gerar_saudacao()`: Cria uma saudação personalizada.
- `gerar_etiquetas()`: Seleciona até 5 etiquetas para classificar o personagem.
- `gerar_definicao()`: Preenche templates de definição com informações extraídas da descrição.
- `criar_dialogos()`: Gera diálogos realistas e variados.
- `imprimir_personagem()`: Exibe todas as informações do personagem de forma organizada.
- `done()`: Mostra um resumo final e parabeniza o usuário.

## 📄 Licença

Este projeto está licenciado sob a licença MIT.  
Veja o arquivo `LICENSE` para mais detalhes.

---

Feito por [Diones Souza](https://github.com/dionesrosa)
