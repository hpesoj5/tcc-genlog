from auth import authenticate

def main():
    sheet = authenticate()
    print("success!")
    
if __name__ == '__main__':
    main()