import time,codecs,socket,hashlib,AATC_Config,copy
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_PSS

def GenerateCertificate(Name,Issuer,NotBefore,NotAfter,PublicKey,IssuerPrivateKey):     #Create a certificate signed with issuer private key
    Certificate = {}
    Certificate["Name"] = Name
    Certificate["Issuer"] = Issuer
    Certificate["NotBefore"] = NotBefore
    Certificate["NotAfter"] = NotAfter
    Certificate["PublicKey"] = PublicKey

    SignatureSource = GetSignatureSource(Certificate)
    h = SHA256.new(SignatureSource)
    key = RSA.import_key(IssuerPrivateKey)
    Signature = PKCS1_PSS.new(key).sign(h)
    
    Certificate["Signature"] = Signature
    return Certificate

def VerifyCertificates(CertificateChain,RootCertificates,con = False, Reverse = False):     #Verify chain of certificates
    CertificateChain = copy.deepcopy(CertificateChain)  #To prevent loss of chain when verifing.
    if len(CertificateChain) > AATC_Config.MAX_CERTIFICATE_CHAIN_LENGTH:
        return False
    if Reverse:
        CertificateChain = CertificateChain[::-1]
    BaseCertificate = CertificateChain.pop(0)
    
    Valid = False
    for RootCert in RootCertificates:
        if BaseCertificate["Issuer"] == RootCert["Name"]:
            if ValidateCertificate(RootCert,RootCert["PublicKey"]):  #Checks that root certificate is in time bounds and that is ok.
                Valid = True
                break

    if Valid and con:
        Valid = VerifyBaseAddress(CertificateChain[len(CertificateChain)-1],con)    #Validates address of connectyion if connection is provided
    
        
    if Valid and ValidateCertificate(BaseCertificate,RootCert["PublicKey"]):        #Validates certificate chain.
        CurrentPublicKey = BaseCertificate["PublicKey"]
        for Certificate in CertificateChain:
            if not ValidateCertificate(Certificate,CurrentPublicKey):
                return False
            CurrentPublicKey = Certificate["PublicKey"]

    else:
        return False
    print("Valid Certificate Chain ")
    return CurrentPublicKey     #Only returns key if valid.
                



def ValidateCertificate(Certificate,IssuerPublicKey):       #Validate a single certificate , ensuring within time limits and is correctly signed
    if not( Certificate["NotBefore"] <= time.time() and Certificate["NotAfter"] >= time.time()):
        return False
    key = RSA.import_key(IssuerPublicKey)
    SignatureSource = GetSignatureSource(Certificate)
    h = SHA256.new(SignatureSource)
    Valid_Signature = PKCS1_PSS.new(key).verify(h,Certificate["Signature"])

    return Valid_Signature
    
def GetSignatureSource(Certificate):        #Obtains the string to be hashed for the signature
    SignatureSource = codecs.encode(str(Certificate["Name"]) + str(Certificate["Issuer"]) + str(Certificate["NotBefore"]) + str(Certificate["NotAfter"]) + str(hashlib.sha256(Certificate["PublicKey"]).hexdigest()))
    return SignatureSource
        
        


#Test Certificates and keys
RootCertificates = [{'Signature': b'qV\x98n\xa8\x0c\xe1\xde\xc6\xf8\xbdK\xd4>\xf3\xdf\xb1\xc2\x02\x06z\xbf\x83#\xa2\xd5)>&\xdf\xf1\xbcm5$\x15wB\x84/L&\x1aA\xa2=\xae\xe2\x92\xab\xed\x1bP\x02c)5IT\xc1\xcft\xf1gb\x11\xd0\xa1p\xd3\xcei\xbe\xb8\xb3t\x06\xbf/\xd6$i\xc2\xfbO\xb2\x94]\x02\xa1\xf9\xfe\xec9\xd12!\x91\xea\xcb\x13\x0b\x7f\xd7\xfc\xac\xb8F\xe5\xd3\x7f\xee$\xc7?#\x07\x01\x8f\xf9\xb1\xaex\x87\x07Z#\x9e', 'NotBefore': 1, 'Name': 'IssuerA', 'PublicKey': b'0\x81\x9f0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x81\x8d\x000\x81\x89\x02\x81\x81\x00\xcddI\xe9\xcbV\xc2\x931\n+\xc5\xef\xcc\xeft\xf8\x01\xe8s\x12\xe2\r)\xf8\x81\xb9\x1e\xcc\x06!n\xff\xd0=\xf1\x92\xa6\xd0\xff\x91~s\xf9pY\xde\xc2\xe4\x8e`\xd2\x02\xe8\xf2r\xa7=\xdbFK\x9a\x02b\x1a\xcdP\x07\x92>GU\x1a?\x89\x96\x89\x99\xf3b\xe5<\xfdJY\xd2\xc4]W\xe9j\x87\xb4\x82\xe0\xa8c\xa7\x87\xe2(\xb0\xa6\xc2M>\xab\xb5r\xd8\xdf\x10\x1a\x07\xd6\xc0\t\xb0\xa3Ng\x1aD%\xab\xb52\xad\x02\x03\x01\x00\x01', 'NotAfter': 10000000000000, 'Issuer': 'IssuerA'},
                    ]


PRIVATE_KEY = b'0\x82\x02]\x02\x01\x00\x02\x81\x81\x00\xcddI\xe9\xcbV\xc2\x931\n+\xc5\xef\xcc\xeft\xf8\x01\xe8s\x12\xe2\r)\xf8\x81\xb9\x1e\xcc\x06!n\xff\xd0=\xf1\x92\xa6\xd0\xff\x91~s\xf9pY\xde\xc2\xe4\x8e`\xd2\x02\xe8\xf2r\xa7=\xdbFK\x9a\x02b\x1a\xcdP\x07\x92>GU\x1a?\x89\x96\x89\x99\xf3b\xe5<\xfdJY\xd2\xc4]W\xe9j\x87\xb4\x82\xe0\xa8c\xa7\x87\xe2(\xb0\xa6\xc2M>\xab\xb5r\xd8\xdf\x10\x1a\x07\xd6\xc0\t\xb0\xa3Ng\x1aD%\xab\xb52\xad\x02\x03\x01\x00\x01\x02\x81\x80\x0e\x07\x17u<J\x04\xa8\x00\xe5l\xef\xeb\xdc\xd7M\xe9\xd2W\x89\xe4tC\xe9\xe5\xeb\x165\xa0A\x9a\xee\xf5\xd1\xc7)D\x96\xd8\x17\\\\\x82\x97:\xb1(\xa1\xae\xf2zr]x\x83v\x89-\x94XL\xb9\x8c\x07\xff\xc6\xa3\x91\xef\xf7\xb9\xb4\xeeY\xfb\x8d\xac\x18I\x8b|\xafJ\x84\xb9\x11\xd4\xf8Ys\x16x)\x84\x0f\xb7\xdd\xf8\x07n2"\xf4\x0c\xd8\xf3?\xfd\xdb\xba\xa08\xe0D\xee\xd5\xa3\x08G0+`\xd5\x8e\x82\x13{\x91\x02A\x00\xce\xa0\xfd\x86\x16\x94\xa8\x92\xd4\xe8\x8bn\x9d\x9c\x9f\xda\x03)A\xf1\x0eL\xd1\xf9\xf2e\xff\xecz\xb4\x80\x87\tj#\xe02\x86k\xaf\x8cx\xc1\x0c\x07l7C\xfc\xd5\xfeu\xec\xf0\x85\x01!\x96L\x13\x932\xb6\xef\x02A\x00\xfew\xa0|?fC\xab)C5\x8a\x163s\xce\x13\x1a\xde\x94W\xbb"\x89\x01\x92\x10\r\xd7\xe0\x9bc$\xb6U=\x1f\xf7\x16\xb5\x95\x87h2>S\xf3R`\x94\x7f\x9b8\x8d4\x02\x8b<\x14y\xfb\x1c\xd0#\x02A\x00\x84\xd3\xa6\xc5\xd8\xa4-\x8d^\x023\x07\xa3\x97\xf8\x86;\xfb\xfc\xa0\xca\x11\x85\xf5\x87\xe6\x1b\xd3W\xb9\xca\xd9\x83\xaa\xd0o!\xeb\x993\xdb8\x10\xd8\xfb\xb8\x8b\xfaO\x80\xfc\xb7\xaf\xdd\x99\x92u\x95\xd9G\xc8\x1b\x14\xcf\x02A\x00\xeb4g\x82p\x97u\xb4\x9fO \r\xa2\xb7\xac2\xae6\x07\xc5\xd5\xd1\x82\xfa`\x19A\xfd\x89\xacq\xf4\x11\xda\xf6\xae\xa8\xfd\x1a`|\xf5\xcb\xb9\xa5"\xb3\xa5P\xdf\xf1\x92\xe7\x92\x9c\xa0=R+\x1b\x14\xa0mA\x02@\x16\xcd\xbb\xc9\xfe\x93m\xc8\x85V\x8a\x1d\'I=\x1b5\xf1\'\xbe\x9biI\x03\xa4\x98@\x1f-\x84\x16\xa54\xc8\xc03C6\xc6\xc0\xf0yp\x97H\xd0\x94\xc0\x85\xe2\x94\xdd\xe7\x9f\xc3n|F\xfa\xd6\'Z\xe47'


##iRSAKey = RSA.generate(1024)
##ipk = iRSAKey.exportKey("DER")
##ipuk = iRSAKey.publickey().exportKey("DER")

# CERTIFICATE CHAIN MUST RUN FROM ROOT CERTIFIATE TO SERVER

def CreateTestChain(length,RSA_KeySize,PRIVATE_KEY,hostname="localhost"):       #Generates a chain used to test the program as well as the time taken to generate large chains.
    chain = []
    Issuer = "IssuerA"
    for x in range(length):
        x = str(x)
        RSAKey = RSA.generate(RSA_KeySize)
        pk = RSAKey.exportKey("DER")
        puk = RSAKey.publickey().exportKey("DER")

        if x == str(length-1):
            x = hostname
        cert = GenerateCertificate(x,Issuer,1,10000000000,puk,PRIVATE_KEY)
        Issuer = x
        PRIVATE_KEY = pk
        #print(cert,"\n\n Private Key :",pk,"\n"*2)
        chain.append(cert)
    return chain,pk


def VerifyBaseAddress(EndCertificate,con):      #Verify if connection is to the correct server. A server could register the certificate with the server domain name so that the client can ensure they have the correct certificate.
    address = con.getpeername()[0]
    try:
        domain = socket.gethostbyaddr(address)[0]
    except:
        domain = None

    if EndCertificate["Name"] not in [address,domain]:  #If it cannot link the certificate name to the domain or address then alert user
        print("[WARNING] The certificate name of the server could not be matched with the looked up domain name or address of the server")
        if AATC_Config.ALLOW_FAILED_DOMAIN_LOOKUP:
            print("Continuing anyway. Set ALLOW_FAILED_DOMAIN_LOOKUP to False to disable this behaviour")
            return True
        else:
            return False
    else:
        return True


