#AATC crypto module
# Diffie-Hellman from 'pip install diffiehellman '
#import diffiehellman.diffiehellman as DH
import codecs,recvall,ast,binascii,os
from Crypto.Cipher import AES
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
        if AutoGenerate:
            self.GenerateKey()

    def SetMode(self,mode):
        self.mode = mode

    def GenerateKey(self,key_size = 2048):
        print("Generating encryption keys. Please stand by...")  #Generating keys takes a long time and have found no way to shorted key length
        if self.mode == "SERVER":
            self.ServerGenerateKey()
        elif self.mode == "CLIENT":
            self.ClientGenerateKey(key_size)
        else:
            raise ValueError("Crypter: Incorrect mode set")
        print("Encryption keys generated",self.shared_key)



    def ClientGenerateKey(self,RSA_KeySize,AES_KeySize):
        RSAKey = RSA.generate(RSA_KeySize)

        privateKey = RSAKey.exportKey("DER")
        publicKey = RSAKey.publicKey().exportKey("DER")

        self.Send(("ExchangeKey",(publicKey,AES_KeySize)))   #Format ("ExchangeKey",("a1b2c3.....",))
        data = self.Recv()
        Sucess,Message = data[0],data[1]        #Format (Sucess,("a2c3d4..."))
        if Sucess == False:
            raise Exception("Error occured while exchanging keys")

        self.Send(("Exit",()))
        data = self.Recv()
        if data[0] == False:
            raise Exception("Server failed to commit to exit")

        RSAPrivateObject = RSA.importKey(privateKey)
        
        self.AESKey = RSAPrivateObject.decrypt(Message)
        self.AES = AES.new(self.AESKey)



    def ServerGenerateKey(self):

        Exit = False
        while not Exit:
            data = self.Recv()
            Command, Arguments = data[0],data[1]

            if Command == "ExchangeKey":
                publicKey,AES_KeySize = Arguments[0],Arguments[1]
                if AES_KeySize not in [16,24,32]:
                    AES_KeySize = 32    #If key size is not valid set size to default of 32
                    
                self.AESKey = binascii.b2a_hex(os.urandom(AES_KeySize))  # Here to allow regeneration of AES key while still in loop if required.
                
                PublicKeyObject = RSA.importKey(publicKey)
                EncryptedAESKey = PublicKeyObject.encrypt(self.AESKey,"x")[0]
                self.Send((True,(self.AESKey,)))
                
            elif Command == "Exit":
                self.Send((True,()))
                Exit = True

            else:
                self.Send((False,("Command does not exist",)))

        self.AES = AES.new(self.AESKey)
                
                
        
        
        


##    def DHServerGenerateKey(self):
##        DifHel = DH.DiffieHellman()
##        
##
##        Exit = False
##        while not Exit :
##            data = self.Recv()
##            Command, Arguments = data[0],data[1]
##
##            if Command == "PublicKey":
##                try:
##                    DifHel.generate_public_key()
##                    DifHel.generate_shared_secret(Arguments[0])
##                    self.Send(("PublicKey",(DifHel.public_key,)))
##                except:
##                    self.Send((False,()))
##
##            elif Command == "Exit":
##                self.Send((True,()))
##                Exit = True
##
##        self.shared_key = DifHel.shared_key[0:32]
##        self.AES = AES.new(self.shared_key)
##                
##        
##
##
##    def DHClientGenerateKey(self,key_size):
##        DifHel = DH.DiffieHellman()
##        DifHel.generate_public_key()
##
##        
##        self.Send(("PublicKey",(DifHel.public_key,)))
##        data = self.Recv()
##        if data[0] == False:
##            raise Exception("Error occured while transmitting public key")
##        DifHel.generate_shared_secret(data[1][0])
##        
##        self.Send(("Exit",()))
##        data = self.Recv()
##        if data[0] == False:
##            raise Exception("Server failed to commit to exit")
##        
##        self.shared_key = DifHel.shared_key[0:32]
##        self.AES = AES.new(self.shared_key)
        
        
        
            
    def Encrypt(self,data):
        pad_size = 16-len(data)%16
        data += b" "*pad_size
        return self.AES.encrypt(data)

    def Decrypt(self,data):
##        pad_size = 16-len(data)%16      # - should not be nessesary as data will come in 16 size blocks and change in message would thwart decryption.
##        data += b" "*pad_size
        return self.AES.decrypt(data)

        
        
        
    def Send(self,data):
        self.con.sendall(codecs.encode(str(data)))
    def Recv(self):
        try:
            data = recvall.recvall(self.con)
            data = ast.literal_eval(codecs.decode(data))
            #      (Command,Arguments)
            return data
        except Exception as e:
            print("Error in Cryptor while receiving ",e)
