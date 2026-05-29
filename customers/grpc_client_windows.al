<run grpc client where
    name = persistence-ds_data and
    ip = 192.168.1.211 and
    port = 50055 and
    grpc_dir =  C:\Users\oshad\AnyLog-code\docker-compose\customers and
    proto = dados and
    function = WatchTable and
    request = WatchRequest and
    response = DataRow and
    service = PersistenceService and
    policy = dados and
    value = (
        table_id = ds_data
    )>