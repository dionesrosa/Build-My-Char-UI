from BuildMyChar import BuildMyChar

def main():
    builder = BuildMyChar()

    try:
        builder.coletar_informacoes()
        builder.gerar_nome()
        builder.criar_descricao_geral()
        builder.gerar_slogan()
        builder.criar_descricao()
        builder.gerar_saudacao()
        builder.gerar_etiquetas()
        builder.gerar_definicao()
        builder.imprimir_personagem()

    except KeyboardInterrupt:
        print("\nInterrupção do usuário detectada. Saindo sem problemas...")

if __name__ == "__main__":
    main()