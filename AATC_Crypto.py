#AATC crypto module
import codecs,recvall,ast,binascii,os,AATC_Config
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
        self.con = con
        self.SetMode(mode)
        if AATC_Config.PRE_SHARED_ENCRYPTION_KEYS_ENABLE:   #Allows preshared encryption keys to be used 
            self.SetEncryptionKeys(AATC_Config.PRE_SHARED_AES_KEY, AATC_Config.PRE_SHARED_IV_KEY)
                
        elif AutoGenerate:
            self.GenerateKey()

    def SetMode(self,mode):
        self.mode = mode

    def GenerateKey(self,key_size = AATC_Config.DEFAULT_RSA_KEYSIZE):
        print("Generating encryption keys. Please stand by...")  #Generating keys takes a long time and have found no way to shorted key length
        if self.mode == "SERVER":
            self.ServerGenerateKey()
        elif self.mode == "CLIENT":
            self.ClientGenerateKey(key_size)
        else:
            raise ValueError("Crypter: Incorrect mode set")
        print("Encryption keys generated",self.AESKey)



    def ClientGenerateKey(self,RSA_KeySize,AES_KeySize= AATC_Config.DEFAULT_AES_KEYSIZE):
        RSAKey = RSA.generate(RSA_KeySize)

        privateKey = RSAKey.exportKey("DER")
        publicKey = RSAKey.publickey().exportKey("DER")

        self.Send(("ExchangeKey",(publicKey,AES_KeySize)))   #Format ("ExchangeKey",("a1b2c3.....",))
        data = self.Recv()
        Sucess,Message = data[0],data[1]        #Format (Sucess,("a2c3d4..."))
        if Sucess == False:
            raise Exception("Error occured while exchanging keys")

        self.Send(("Exit",()))
        data = self.Recv()
        if data[0] == False:
            raise Exception("Server failed to commit to exit")
        
        RSAPrivateKey = RSA.import_key(privateKey)
        RSAPrivateObject = PKCS1_OAEP.new(RSAPrivateKey)
        
        self.AESKey = RSAPrivateObject.decrypt(Message[0])
        self.IV = RSAPrivateObject.decrypt(Message[1])
        
        self.SetEncryptionKeys(self.AESKey,self.IV)
                




    def ServerGenerateKey(self):

        Exit = False
        while not Exit:
            data = self.Recv()
            Command, Arguments = data[0],data[1]

            if Command == "ExchangeKey":
                publicKey,AES_KeySize = Arguments[0],Arguments[1]
                if AES_KeySize not in AATC_Config.ALLOWED_AES_KEYSIZES:
                    AES_KeySize = AATC_Config.DEFAULT_AES_KEYSIZE    #If key size is not valid set size to default of AATC_Config.DEFAULT_AES_KEYSIZE
                    
                self.AESKey = binascii.b2a_hex(os.urandom(AES_KeySize//2))  # Here to allow regeneration of AES key while still in loop if required.
                self.IV = binascii.b2a_hex(os.urandom(AES_KeySize//2)) 
                
                RSAPrivateKey = RSA.import_key(publicKey)
                PublicKeyObject = PKCS1_OAEP.new(RSAPrivateKey)
                
                EncryptedAESKey = PublicKeyObject.encrypt(self.AESKey)
                EncryptedIV = PublicKeyObject.encrypt(self.IV)
                self.Send((True,(EncryptedAESKey,EncryptedIV)))
                
            elif Command == "Exit":
                self.Send((True,()))
                Exit = True

            else:
                self.Send((False,("Command does not exist",)))

        self.SetEncryptionKeys(self.AESKey,self.IV)


    def SetEncryptionKeys(self,AESKey,IV):
        self.AESKey = AESKey
        self.IV = IV
        self.EncryptAES = AES.new(self.AESKey,AES.MODE_GCM,self.IV)    #Two seperate instances to encrypt and decrypt as non ECB AES is a stream cipher
        self.DecryptAES = AES.new(self.AESKey,AES.MODE_GCM,self.IV)    #Errors will occur if encrypt and decrypt are not equal in count.
                
                
        
        
        

        
        
            
    def Encrypt(self,data):
##        pad_size = 16-len(data)%16
##        data += b" "*pad_size
        return self.EncryptAES.encrypt(data)

    def Decrypt(self,data):
##        pad_size = 16-len(data)%16      # - should not be nessesary as data will come in 16 size blocks and change in message would thwart decryption.
##        data += b" "*pad_size
        return self.DecryptAES.decrypt(data)

        
        
        
    def Send(self,data):
        self.con.sendall(codecs.encode(str(data)))
    def Recv(self):
        data = recvall.recvall(self.con)
        data = ast.literal_eval(codecs.decode(data))
        #      (Command,Arguments)
        return data

