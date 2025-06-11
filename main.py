from BuildMyChar import BuildMyCharUI

def main():
    try:
        BuildMyCharUI()
        
    except KeyboardInterrupt:
        print("\nInterrupção do usuário detectada. Saindo sem problemas...")

if __name__ == "__main__":
    main()