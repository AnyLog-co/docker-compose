from blockchain_cmds import publish_policy
CONN = "http://50.116.13.109:32049"

DEVICE_POINTS = [
    "SIC-250-MEDIA_PV_L_per_min", # = 0.58
    "SIC-250-003_STATUS", # = STOPPED
    "HV-250-003_CMD", # = 0
    "TI-250-001_PV_Celsius", # = 29.6
    "SIC-250-002_SP_EU_1", # = L/min
    "SIC-250-006_PV_mL_per_min", # = 0
    "FIC-250-001_SP_SLPM", # = 10
    "UNIT-250_BATCH_ID", # = 2025120842503
    "HV-250-001_PV", # = CLOSED
    "UNIT-250_MSG1_VERIFY", # = 359459.0
    "SIC-250-008_PV_RPM", # = 402.42
    "PIC-250-001_PV_psi", # = 0.07
    "SIC-250-002_START_1", # = 0
    "TI-250-002_PV_Celsius", # = 29.7
    "FIC-250-003_PV_SLPM", # = 1.51
    "FCV-250-002_SP_percent", # = 42.36
    "SIC-250-008_SP_RPM", # = 400
    "FIC-250-001_ACTIVE", # = 1
    "SIC-250-006_SP_mL_per_min", # = 0
    "SIC-250-004_PV_L_per_min", # = 0
    "HV-250-002_PV", # = CLOSED
    "UNIT-250_RECIPE", # = PR_SUB_PROC
    "SIC-250-002_STATUS", # = Stopped
    "SIC-250-005_STATUS", # = STOPPED
    "SIC-250-004_SP_L_per_min", # = 0
    "SIC-250-MEDIA_MODE", # = AUTO
    "SIC-250-003_START", # = 0
    "SIC-250-005_MODE", # = AUTO
    "AIC-250-001_SP_percent", # = 30
    "TIC-250-001_ACTIVE", # = 1
    "WI-250-001_PV_kg", # = 189.55
    "UNIT-250_FORMULA", # = rBMN-42
    "SIC-250-005_SP_mL_per_min", # = 0
    "FIC-250-003_ACTIVE", # = 1
    "SIC-250-006_STATUS", # = STOPPED
    "FCV-250-003_PV_percent", # = 70.6
    "PIC-250-001_SP_psi", # = 0.1
    "SIC-250-005_START", # = 0
    "SIC-250-002_SP_1", # = 0
    "AIC-250-001_ACTIVE", # = 1
    "FIC-250-002_PV_SLPM", # = 2.13
    "TIC-250-002_PV_Celsius", # = 59.62
    "HV-250-005_PV", # = OPEN
    "FCV-250-001_PV_percent", # = 100
    "TIC-250-001_SP_Celsius", # = 30
    "AIC-250-001_PV_percent", # = 28.62
    "FCV-250-002_PV_percent", # = 42.89
    "TIC-250-002_SP_Celsius", # = 60
    "TIC-250-001_MODE", # = Auto
    "SIC-250-003_PV_L_per_min", # = 0
    "AIC-250-002_ACTIVE", # = 1
    "SIC-250-MEDIA_STATUS", # = RUNNING
    "AIC-250-003_SP_pH", # = 5.5
    "FIC-250-001_PV_SLPM", # = 10.32
    "TIC-250-002_ACTIVE", # = 1
    "FIC-250-002_SP_SLPM", # = 2.12
    "SIC-250-002_PV_EU_1", # = L/min
    "SIC-250-004_START", # = 0
    "SIC-250-008_MODE", # = Auto
    "SIC-250-004_STATUS", # = Stopped
    "SIC-250-006_START", # = 0
    "UNIT-250_MSG1_ACK", # = True
    "FCV-250-001_SP_percent", # = 100
    "TIC-250-001_PV_Celsius", # = 29.5
    "DI-250-010", # = 0
    "AIC-250-003_PV_pH", # = 5.48
    "UNIT-250_PHASE", # = PH_SUB_FEED2
    "AIC-250-003_ACTIVE", # = 1
    "TIC-250-002_MODE", # = Auto
    "SIC-250-003_SP_L_per_min", # = 0
    "SIC-250-002_PV_1", # = 0
    "SIC-250-008_START", # = 1
    "UNIT-250_MSG2", # = Starting Base Addition
    "UNIT-250_MSG1", # = Acknowledge when ready to start transfer in of Feed 2
    "FCV-250-003_SP_percent", # = 70
    "SIC-250-MEDIA_SP_L_per_min", # = 0.58
    "SIC-250-MEDIA_START", # = 1
    "FIC-250-003_SP_SLPM", # = 2
    "UNIT-250_STATE", # = Running
    "HV-250-003_PV", # = CLOSED
    "HV-250-004_MODE", # = Auto
    "SIC-250-005_PV_mL_per_min", # = 0
    "UNIT-250_MSG1_USER" # = 359264.0
]


def declare_device(device:str):
    new_policy = {
        "device": {
            "id": device,
            "parent": "sub",
            "namespace": f"Enterprise C/sub/{device}"
        }
    }

    publish_policy(conn=CONN, policy=new_policy)

def declare_sensor(uid:str, device:str, sensor:str):
    new_policy = {
        "sensor": {
            "id": uid,
            "sensor": sensor,
            "parent": device,
            "dbms": "manufacturing_historian",
            "table": f"{device.lower().replace('-', '_')}_{sensor.lower().replace('-', '_')}",
            "namespace": f"Enterprise C/sub/{device}/{sensor}"
        }
    }

    publish_policy(conn=CONN, policy=new_policy)


for point in DEVICE_POINTS:
    try:
        device, sensor = point.split("_",1)
        declare_device(device)
        declare_sensor(point, device, sensor)
    except:
        pass
        # print(f"fails: {point}")
