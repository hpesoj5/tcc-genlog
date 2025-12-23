from gen import genlog

def main():
    cont = "y"
    while cont == 'y' or cont == 'Y':
        genlog()
        cont = ""
        while(cont != 'y' and cont != 'Y' and cont != 'n' and cont != 'N'):
            cont = input("Continue? (y/n) ")
    
if __name__ == "__main__":
    main()