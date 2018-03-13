


#Generic a* algorithm from AATC_AStar
Function A*
    # G = current distance to that node from start, F = estimated distance to target
    Define sets Open,Closed,cameFrame,g,f
    Set Start g = 0
    Set start f to estimated distance to f
    Set Found to false
    while the openset has not been exhausted:
        find nodeID of minimum of f  and set to current
        if current = Target :
            found <- True
            break loop
        end if

        remove current from openset and add to closed set
        for each neighbour of current:
            if node is closed:
                continue loop
            end if
            
            if node is not in the openset yet:
                add to openset and initialise g,f to infinity
            end if
            
            set tscore to obtain new node and add its cost to current g
            if tscore is larger ( longer path) than the current value for the neighbour:
                continue loop
            end if
            
            set the cameFrom to the current nodeID for the neighbour node
            set g for neighbour to tscore
            set f for neighbour to the g score + estimated distance to target
        end for

        remove current from f and g to reduce memory usage
        
    End while

    if Found = True:
        return Generate_Path_From_CameFrom(cameFrom)
    else:
        return Null
End Function





# Verify Certificates from AATC_CryptoBeta
function VerifyCertificates
    if length(chain_of_certificates) > MAX_ALLOWED_LENGTH:
        raise chain too long error
    end if

    basecerficiate <- chain.remove_first_item()
    Valid <- False
    for root_cert in root_certificates:
        if issuer(basecertificate) = name_of(root_cert):
            Valid <- True
            break loop
        end if
    end for

    if Valid and Connection_Object != Null:
        Valid <- Verify_Connection(Connection_Object)
    end if
    
    if Valid and Validate_Certificate(base_certificate,root_cert_public_key):
        Current_Public_key <- root_cert_public_key
        for cert in chain:
            if not Validate_Certificate(base_certificate,Current_Public_Key):
                return Invalid
            end if
        end for
    else:
        return Invalid
    end if
    
    return Valid
end function



#AATC_Monitor_Viewer generic pseudocode
xpixel <- 800
ypixel <- 550
Refresh_Delay <- 60
Exit <- "N"
while Exit != "Y":
    try:
        M <- Create_Monitor_Interface()
        M.Login("Username","Password")
        Camera <- Camera(xpixel,ypixel)
        while True:
            Camera.reset()
            sprites <- MakeSprites(M)
            for sprite in sprites:
                Camera.add(sprite)
            end for

            refresh <- False
            last_refresh <- time()
            while not refresh:
                camera.wipe()
                if time() < last_refresh+refresh_delay:
                    refresh <- True
                end if
                
                for event in events:
                    process_event(event)
                end for
                
                respond to keyboard presses
                Camera.recalculate_size()
                Camera.draw(#Draw function code
                    camera_limits <- calculate_limits()
                    for sprite in sprites:
                        if sprite in camera_limits:
                            draw_sprite(sprite)
                            if text_size(sprite) > limit:
                                draw_text(sprite)
                            end if
                        end if
                    end for
                    #End of draw function code
                    )
                update_screen()
            end while
        end while
        
    catch exception:
        display error
        Exit <- input("Should exit?")
    end catch

end while




######################################################

#AATC_Server_002 general connection system. User example
con <- Accept client connection
Send_To_Process(UserConnection,con)

#In process
DB <- Create DB Connection()
Crypto <- Create Encryption object(con)
Auth_Commands <- Authenticated command dictionary
Not_Auth_Commands <- Non authenticated command dictionary
Exit <-False
ClientID <- -1
while not Exit:
    try:
        data <- con.get_data()
        if ClientID != -1:
            Sucess,Message,Data <-Auth_Commands[data[0]](data[1])
        else:
            Sucess,Message,Data <-Not_Auth_Commands[data[0]](data[1])
    except:
        Sucess,Message,Data <- False,"Error",[]
        Output("An error occured")

    try:
        con.send(Sucess,Message,Data)
    except:
        Exit <- True

