import pickle

def write(obj, name):
    '''faz uma coserva de obj no arquivo name'''
    with open(name, 'wb') as arq:
        pickle.dump(obj, arq, protocol=0)

def read(name):
    '''abre o pote name e retorna o pickles'''
    with open(name, 'rb') as arq:
        return pickle.load(arq)

def qNear(a,b):
    '''retorna quociente de a por b arrendondado para o inteiro mais proximo'''
    return (2*a+b)//(2*b)

def modNear(a,b):
    '''retorna a mod b no intervalo de [-(b/2), b/2]'''
    return a-b*qNear(a,b)
