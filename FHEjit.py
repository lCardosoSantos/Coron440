from gmpy2 import mpz
import gmpy2
import random
import time
from utils import *
from numbapro import autojit, jit

tgt='cpu' ##Target para o autojit

class rng:
    "gerador de numeros-pseudo aleatorios"
    def __init__(self,seed,  gam, n):
        '''gera numeros no range [0, 2**gam], gera n elementos'''
        self.seed, self.gam, self.n = seed, gam, n
        self.list=[None for i in range(self.n)]
    def __getitem__(self, index): return self.list[index]
    def __setitem__(self, index, valor):
        self.list[index]=valor
    def __iter__(self):
        random.seed(self.seed)
        for i in range(self.n):
            rand=mpz(random.getrandbits(self.gam))
            if self.list[i]!=None: yield self.list[i]
            else:
                yield rand
    
def randList(B):
    l=[0 for i in range(B)]
    l[random.randint(0,B-1)]=1
    return l
      
class  pk:
    '''classe para os elementos da chave, publicos e provados'''
    @autojit(target=tgt)
    def __init__(self, pr):
        t=-time.clock()
        self.pr=pr
        while True:
            self.p=gmpy2.next_prime(random.getrandbits(pr['eta']))
            if len(self.p)==pr['eta']: break
        #print (self.p)
        self.q0=random.randint(0, (mpz(2)**pr['gam'])/self.p)
        self.x0=self.q0*self.p

        '''geração da lista de ruido delta'''
        self.se1=int(time.time()) #usando tempo como seed para os rngs. TODO: passar tempo para função de Hash com retorno int
        self.f1=rng(self.se1, pr['gam'], pr['tau'])
        self.delta=[(chi%self.p)+self.p-random.randint(0,mpz(2)**(pr['lam']+pr['eta']))* self.p - random.randint(-(mpz(2)**pr['rho']), mpz(2)**pr['rho']) for chi in self.f1]
        #alterar self.delta para laço for chi in f1#

        '''geração do vetor s'''
        assert pr['Theta']%15==0 #Theta tem que ser um multiplo de theta
        B=int(pr['Theta']/15)
        self.s=[1]+[0 for i in range(B-1)]
        for i in range(15-1):
            self.s=self.s+randList(B)

        '''geração do elemento u1'''
        self.kappa=pr['gam']+pr['eta']+2
        self.se2=int(time.time())
        self.f2=rng(self.se2, self.kappa+1, pr['Theta'])
        self.f2[0]=0 #seta elemento u1 como sendo zero
        somatorio=0
        i=0
        for u in self.f2:
            somatorio += u*self.s[i]
            i+=1
        soma=mpz(round((mpz(2)**self.kM43 officer's capappa)/self.p))
        self.u1=soma-somatorio

        '''geração de deltaPrime = encryptações do vetor sigma'''
        self.se3=int(time.time())
        self.f3=rng(self.se2, pr['gam'], pr['Theta'])
        self.deltaPrM43 officer's capime=[chi%self.p + random.randint(0, mpz(2)**(pr['gam']+pr['eta']/self.p)/self.p) * self.p - 2*random.randint(-(mpz(2)**pr['rho']), mpz(2)**pr['rho']) -si for chi,si in zip(self.f3, self.s)]

        '''geração da chave para picles'''
        self.pkAsk={'se1':self.se1, 'x0':self.x0, 'delta': self.delta}
        self.pk={'pkAsk':self.pkAsk, 'se2': self.se2, 'u1': self.u1, 'se3': self.se3, 'deltaPrime': self.deltaPrime, 'pr':self.pr}

        self.sk=self.s
        t+=time.clock()
        #print('keygem em: ', t, 'segundos  par==', pr['ty'])

        
    def returnKeys(self):
        return self.sk, self.pk

@autojit(target=tgt)        
def encrypt(pk, m): #todo: criar classe para cyphertext, com noise, e depth, assim como CORON et. al.
    assert m==0 or m==1
    x0=pk['pkAsk']['x0']
    f1=rng(pk['pkAsk']['se1'], pk['pr']['gam'], pk['pr']['tau'])
    soma=0
    for chi, delta in zip(f1, pk['pkAsk']['delta']):
        soma += (chi-delta)*random.randint(0, mpz(2)**pk['pr']['alpha'])
    r=random.randint(-mpz(2)**pk['pr']['rho'], mpz(2)**pk['pr']['rho'])
    c=modNear(m+2*r+2*soma, x0)
    return c

def add(pk, c1, c2):
    return modNear(c1+c2, pk['pkAsk']['x0'])

def mul(pk, c1, c2):
    return modNear(c1*c2, pk['pkAsk']['x0'])

@autojit(target=tgt)
def expand(pk, c):
    #mensagem do programador: sacrifique um bode quando chamar essa função
    n=4 #bits of precision for the u1/2**kappa (u1)has len=148450bits
    pr=pk['pr']
    kappa=pr['gam']+pr['eta']+2
    f2=rng(pk['se2'], kappa+1, pr['Theta'])
    f2[0]=pk['u1']
    gmpy2.get_context().precision=300000
    k=mpz(2)**kappa
    y=[u/k for u in f2]
    z=[modNear(c*yi, 2) for yi in y]
    gmpy2.get_context().precision=n
    zprime=[float(zi) for zi in z]
    gmpy2.get_context().precision=300000
    return zprime

@autojit(target=tgt)    
def decrypt(sk, c, z):
    e=zip(sk, z)
    soma=0
    for si, zi in zip(sk, z):
        soma+= si*zi
    soma=int(round(soma))
    m=(c-soma)%2
    return m

def recrypt(pk, c, z):
    pass


def keyValidation(pk_, sk):
    '''verifica se a chave passada gera decriptações validas de '0' e '1' '''
    c=encrypt(pk_, 0)
    c1=encrypt(pk_, 1)
    z=expand(pk_, c)
    z1=expand(pk_,c1)
    m=decrypt(sk, c, z)
    m1=decrypt(sk, c1, z1)
    if m==0 and m1==1: return True
    else: return False

def testeKeyGen():
    '''teste apenas para geração de chaves'''
    #parametros de acordo com coron.
    toy=    {'ty':"toy",   'lam':42,'rho':26,'eta':988, 'gam':147456,  'Theta':150, 'pksize':0.076519, 'seclevel':42.0,'alpha':936, 'tau':158}
    small=  {'ty':"small", 'lam':52,'rho':41,'eta':1558,'gam':843033,  'Theta':555, 'pksize':0.437567, 'seclevel':52.0,'alpha':1476,'tau':572}
    medium= {'ty':"medium",'lam':62,'rho':56,'eta':2128,'gam':4251866, 'Theta':2070,'pksize':2.207241, 'seclevel':62.0,'alpha':2016,'tau':2110}
    large=  {'ty':"large", 'lam':72,'rho':71,'eta':2698,'gam':19575950,'Theta':7965,'pksize':10.303797,'seclevel':72.0,'alpha':2556,'tau':7659}
    
    print('iniciando teste de geração de chaves para Coron 440: jit mode=', tgt)
    for par in [toy, small, medium, large]:
        if par['ty']=='large':
            a=input('parametro large: risco de instabilidades. continuar? <y/n>')
            if a != 'y': quit(0)
        kt=-time.clock()
        key= pk(par)
        kt+=time.clock()
        print('%s gerada em %f segundos' %(par['ty'], kt))
    
def teste():
    import gc
    print('pyFHE, baseado no trabalho 440 de coron')
    #parametros de acordo com coron.
    toy=       {'ty':"toy",   'lam':42,'rho':26,'eta':988, 'gam':147456,  'Theta':150, 'pksize':0.076519, 'seclevel':42.0,'alpha':936, 'tau':158}
    small=	{'ty':"small", 'lam':52,'rho':41,'eta':1558,'gam':843033,  'Theta':555, 'pksize':0.437567, 'seclevel':52.0,'alpha':1476,'tau':572}
    medium=	{'ty':"medium",'lam':62,'rho':56,'eta':2128,'gam':4251866, 'Theta':2070,'pksize':2.207241, 'seclevel':62.0,'alpha':2016,'tau':2110}
    large=	{'ty':"large", 'lam':72,'rho':71,'eta':2698,'gam':19575950,'Theta':7965,'pksize':10.303797,'seclevel':72.0,'alpha':2556,'tau':7659}

    print('Test')
    it=0
    for par in [toy, small, medium, large]:
        kt=-time.clock()
        key= pk(par)
        kt+=time.clock()
        sk, pk_ = key.returnKeys()
        while not keyValidation(pk_, sk):
            key= pk(par)
            sk, pk_ = key.returnKeys()
            print('key not valid')
        print('key found!')
        enctime=-time.clock()
        c=encrypt(pk_, 0)
        enctime+=time.clock()
        
        #c1=encrypt(pk_, 1)
        etime=-time.clock()
        z=expand(pk_, c)
        etime+=time.clock()
        #z1=expand(pk_,c1)
        mtime=-time.clock()
        m=decrypt(sk, c, z)
        mtime+=time.clock()
        #m1=decrypt(sk, c1, z1)

        #ca=add(pk_, c, c1)
        #cm=mul(pk_, c, c1)
        #ma=decrypt(sk, ca, expand(pk_, ca))
        #m=decrypt(sk, cm, expand(pk_, cm))
        f=open('fhe440.txt', 'a')
        f.write(par[it]['ty'])
        f.write("=="+str(kt)+"\n")
        f.write('Kg= %f, encrypt = %f, decrypt = %f, expand = %f \n\n' %(kt, enctime, mtime, etime))
        f.close()
        
        #print("0=>%d  1=>%d  | 0+1=>%d  | 0x1=>%d" %(m, m1, ma, mm))
        gc.collect()
        #write(pk_, 'pk_'+key.pr['ty']+'.bin')
        #write(sk, 'sk_'+key.pr['ty']+'.bin')

if __name__=='__main__':
    #teste()
    print('codigo rodando')
    testeKeyGen()

'''
TODO: testar o código gerando varios encrypt e decrypts por chave
        =>resultado: encrypts e decrips de uma chave que encryptou direito
        sempre encrypta e decrypta direito.
        resultado: testar validade de chave, e, fazer add e mul com elas.
'''                                                                                                               
