CREATE TABLE User(
    UserID INTEGER PRIMARY KEY AUTO_INCREMENT,
    Username TEXT,
    Password TEXT,
    PublicVisibleFlights INT,
    PermissionAdder INT ,
    ZoneCreatorPermission INT,
    ZoneRemoverPermission INT,
    ZoneModifierPermission INT)

CREATE TABLE Drone(
    DroneID INTEGER PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    DroneName TEXT,
    DroneType TEXT,
    DroneSpeed INT,
    DroneRange INT,
    DroneWeight REAL,
    FlightsFlown INT,
    LastCoords TEXT,
    LastBattery REAL,
    FOREIGN KEY(UserID) REFERENCES User(UserID))

CREATE TABLE Monitor(
    MonitorID INTEGER PRIMARY KEY AUTO_INCREMENT,
    MonitorName TEXT,
    MonitorPassword TEXT)


CREATE TABLE MonitorPermission(
    MonitorID INT ,
    UserID INT,
    LastAccessed TEXT,
    ExpiryDate TEXT,
    PRIMARY KEY(MonitorID,UserID),
    FOREIGN KEY(MonitorID) REFERENCES Monitor(MonitorID),
    FOREIGN KEY(UserID) REFERENCES User(UserID))


CREATE TABLE Flight(FlightID INTEGER PRIMARY KEY AUTO_INCREMENT,
                    DroneID INT,
                    StartCoords TEXT,
                    EndCoords TEXT,
                    StartTime REAL,
                    ETA REAL,
                    EndTime REAL,
                    Distance  REAL,
                    XOffset REAL ,
                    YOffset REAL ,
                    ZOffset REAL,
                    Completed INT,
                    FOREIGN KEY(DroneID) REFERENCES Drone(DroneID))


CREATE TABLE FlightWaypoints(
    FlightID INT,
    WaypointNumber INT,
    Coords TEXT,
    ETA REAL,
    BlockTime INT ,
    PRIMARY KEY(FlightID,WaypointNumber),
    FOREIGN KEY(FlightID) REFERENCES Flight(FlightID))



CREATE TABLE NoFlyZone(
    ZoneID INTEGER PRIMARY KEY AUTO_INCREMENT,
    StartCoord TEXT,
    EndCoord TEXT,
    Level INT,
    OwnerUserID INT,
    FOREIGN KEY(OwnerUserID) REFERENCES User(UserID))


CREATE TABLE DroneCredentials(DroneID INTEGER PRIMARY KEY AUTO_INCREMENT ,
                              DronePassword TEXT)


CREATE TABLE InputStack(chat_id INT ,
                        stack_pos INT,
                        value TEXT,
                        PRIMARY KEY(chat_id,stack_pos))

CREATE TABLE Sessions(chat_id INT PRIMARY KEY,
                      UserID INT)



