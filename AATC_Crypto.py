#AATC crypto module
import codecs,recvall,ast,os,AATC_Config,AATC_CryptoBeta
from Crypto.Cipher import AES,PKCS1_OAEP
from Crypto.PublicKey import RSA

class Crypter:
    """
    A class to encrypt and decrypt a connection with AES. Takes a connection object and mode and sets up a secret key for both participants.
    This key is then used to create an AES object which encrypts and decrypts messages via the Encrypt and Decrypt functions.
    These strings must be in binary format. The length of the string will be padded to a length multiple of 16 in size.
    The object will communicate with another Crypter object via the socket and pass public keys.
    Best for use with communication with string versions of python objects and resulting converstion using 'ast' as this will remove padding whitespace.

    If in 'CLIENT' mode the Crypter will start communication. It will send a message ('PublicKey,(Client_Public_Key,)) and the server will return the servers public key.
    The CLIENT will then send an 'Exit' message to end communication.

    Per default the Crypter will assume it should generate the keys when __init__ is called. This can be disabled by creating the object with AutoGenerate set to False.

    Mode can be changed via SetMode. Normal options are 'CLIENT' and 'SERVER'.

    """
    def __init__(self, con, mode = "CLIENT",AutoGenerate = True):
        self._con = con
        self.SetMode(mode)                
        if AutoGenerate:
            self.GenerateKey()

    def SetMode(self,mode):
        self._mode = mode

    def GenerateKey(self,key_size = AATC_Config.DEFAULT_RSA_KEYSIZE):
        print("Generating encryption keys. Please stand by...")  #Generating keys takes a long time and have found no way to shorted key length
        if self._mode == "SERVER":
            self.ServerGenerateKey()
        elif self._mode == "CLIENT":
            self.ClientGenerateKey(key_size)
        else:
            raise ValueError("Crypter: Incorrect mode set")
        print("Encryption keys generated",self._AESKey)



    def ClientGenerateKey(self,RSA_KeySize,AES_KeySize= AATC_Config.DEFAULT_AES_KEYSIZE):   #Start the relevant key exchange system


        if AATC_Config.SET_ENCRYPTION_KEYS_ENABLE:   #Allows preset encryption keys to be used 
            self.SetEncryptionKeys(AATC_Config.SET_AES_KEY, AATC_Config.SET_IV_KEY)

        elif AATC_Config.ENCRYPTION_USE_PRESHARED_KEYS:     #Uses preshared certificates
            self.ClientPreSharedKeys(RSA_KeySize,AES_KeySize)

        else:
            self.ClientExchangeKeys(RSA_KeySize,AES_KeySize)    #Exchange AES keys using RSA
            

        self.Send(("Exit",()))
        Sucess,Message,Data = self.SplitData(self.Recv())
        if not Sucess:
            raise Exception("Server failed to exit"+Message)
                
                

    def ClientPreSharedKeys(self,RSA_KeySize,AES_KeySize):      #Swap keys using certificate authentication
        self.Send(("GetServerCertificateChain",()))
        Sucess,Message,CertificateChain = self.SplitData(self.Recv())
        if not Sucess:
            raise Exception("Server did not respond to command")

        if AES_KeySize not in AATC_Config.ALLOWED_AES_KEYSIZES:
            raise Exception("AES key size not in ALLOWED_AES_KEYSIZES. Change keysize to an allowed value")     #Only accept allowed key sizes 

        AESKey,IV = GenerateKeys(AES_KeySize)
        PublicKey = AATC_CryptoBeta.VerifyCertificates(CertificateChain,AATC_Config.ROOT_CERTIFICATES,self._con)        #Verify the certificate chain is valid.

        if PublicKey:   #If the chain is valid
            
            PKO = PKCS1_OAEP.new(RSA.import_key(PublicKey))
            EncryptedAESKey = PKO.encrypt(AESKey)
            EncryptedIV = PKO.encrypt(IV)
            self.SetEncryptionKeys(AESKey,IV)
            self.Send(("SetKey",(EncryptedAESKey,EncryptedIV)))     #Swap keys encrypted using server public key
            Sucess,Message,Data = self.SplitData(self.Recv())
            if not Sucess:
                raise Exception("Server rejected setting AES_Keys"+Message)     
            

        else:
            print("Certificate Chain is not valid")
            if AATC_Config.AUTO_GENERATE_FALLBACK:
                self.ClientExchangeKeys(RSA_KeySize,AES_KeySize)        #Fall back on key exchange if allowed
            else:
                raise Exception("Certificate Chain is not valid. Exception raised")     #Raise exception if not allowed
                
            

    def ClientExchangeKeys(self,RSA_KeySize,AES_KeySize):       #Exchange the keys using RSA encryption
        RSAKey = RSA.generate(RSA_KeySize)

        privateKey = RSAKey.exportKey("DER")
        publicKey = RSAKey.publickey().exportKey("DER")     #Get the RAS keys.

        self.Send(("GenerateKey",(publicKey,AES_KeySize)))   
        Sucess,Message,data = self.SplitData(self.Recv())     
        
        RSAPrivateKey = RSA.import_key(privateKey)
        RSAPrivateObject = PKCS1_OAEP.new(RSAPrivateKey)
        
        AESKey = RSAPrivateObject.decrypt(data[0])          #Decrypt the recieved keys
        IV = RSAPrivateObject.decrypt(data[1])

        if Sucess == False:
            raise Exception("Error occured while exchanging keys")
        
        self.SetEncryptionKeys(AESKey,IV)


    ################################################################

    def ServerGenerateKey(self):        #Server select the correct mode.
        if AATC_Config.SET_ENCRYPTION_KEYS_ENABLE:
            self.SetEncryptionKeys(AATC_Config.SET_AES_KEY, AATC_Config.SET_IV_KEY)            #Use preset keys if enabled

        self._Exit = False
        while not self._Exit:       #Start a server type loop (responds to commands from client)
            data = self.Recv()
            Command, Arguments = data[0],data[1]


            #Respond to relevant command
            if Command == "GenerateKey":
                Sucess,Message,Data = self.ServerGenerateKeys(Arguments)        

            elif Command == "GetServerCertificateChain":
                Sucess,Message,Data = self.GetServerCertificateChain(Arguments)

            elif Command == "SetKey":
                Sucess,Message,Data = self.ServerSetKey(Arguments)
                
                
            elif Command == "Exit":
                Sucess,Message,Data = True,"Exiting",[]
                self._Exit = True

            else:
                Sucess,Message,Data = False,"Command does not exist",[]

            self.Send((Sucess,Message,Data))

        if not hasattr(self,"_AESKey"):  #Only set if sucessfully setup.
            raise Exception("Failure during crypter setup")




    def ServerGenerateKeys(self,Arguments):     #Generate keys and encrypt with the provided RSA key
        publicKey,AES_KeySize = Arguments[0],Arguments[1]
        
        if AES_KeySize not in AATC_Config.ALLOWED_AES_KEYSIZES:
            AES_KeySize = AATC_Config.DEFAULT_AES_KEYSIZE    #If key size is not valid set size to default of AATC_Config.DEFAULT_AES_KEYSIZE
            
        AESKey,IV = GenerateKeys(AES_KeySize)
        
        PublicKeyObject = PKCS1_OAEP.new( RSA.import_key(publicKey))
        
        EncryptedAESKey = PublicKeyObject.encrypt(AESKey)
        EncryptedIV = PublicKeyObject.encrypt(IV)           #Encrypt AES keys

        self.SetEncryptionKeys(AESKey,IV)
        return True,"Instated encryption keys",[EncryptedAESKey,EncryptedIV]        #Return values to be sent

    def GetServerCertificateChain(self,Arguments = None):       #Respond to request to get certificate chain.
        return True,"Server Certificate Chain",AATC_Config.SERVER_CERTIFICATE_CHAIN

    def ServerSetKey(self,Arguments):               #Set provided keys encrypted with public key of server
        PKO = PKCS1_OAEP.new(RSA.import_key(AATC_Config.SERVER_PRIVATE_KEY))
        AESKey,IV = Arguments[0],Arguments[1]
        AESKey,IV = PKO.decrypt(AESKey),PKO.decrypt(IV)     #Decrypt keys
        
        if len(AESKey) in AATC_Config.ALLOWED_AES_KEYSIZES:     
            self.SetEncryptionKeys(AESKey,IV)
            return True,"Keys set",[]
        else:
            #self._Exit = True
            return False,"AES key size not in ALLOWED_AES_KEYSIZES:"+str(AATC_Config.ALLOWED_AES_KEYSIZES),[]
        




    ###############################################


    def SetEncryptionKeys(self,AESKey,IV):  #Set the encryption keys and AES encryption objects
        self._AESKey = AESKey
        self._IV = IV
        self._EncryptAES = AES.new(self._AESKey,AES.MODE_GCM,self._IV)    #Two seperate instances to encrypt and decrypt as non ECB AES is a stream cipher
        self._DecryptAES = AES.new(self._AESKey,AES.MODE_GCM,self._IV)    #Errors will occur if encrypt and decrypt are not equal in count.
            
                
        
    ##############################################

        
            
    def Encrypt(self,data):
        return self._EncryptAES.encrypt(data)

    def Decrypt(self,data):
        return self._DecryptAES.decrypt(data)

        
        
        
    def Send(self,data):
        self._con.sendall(codecs.encode(str(data)))
    def Recv(self):
        data = recvall.recvall(self._con)
        data = ast.literal_eval(codecs.decode(data))
        return data
    def SplitData(self,data):
        return data[0],data[1],data[2]




    
def GenerateKeys(AES_KeySize):  #Creates random keys using source which is cryptographically random
    AESKey = os.urandom(AES_KeySize)  # Here to allow regeneration of AES key while still in loop if required.
    IV     = os.urandom(AES_KeySize)
    return AESKey,IV


