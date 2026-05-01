let site = "Site1";
let store = flow.get('store');
if (!store) return null;

let tank = store["Enterprise B"]
    ?.[site]
    ?.liquidprocessing
    ?.tankstorage01
    ?.tank01;

if (!tank?.processdata || !tank?.lotnumber) return null;

let row = {
    dbms: "enterprise_b",
    table: "processing",
    timestamp: flow.get(`ts_${site}`) || flow.get('factory_timestamp') || new Date().toISOString(),
    site,
    lotnumberid: tank.lotnumber.lotnumber,
    state: tank.processdata.state?.name,
    duration: tank.processdata.state?.duration,
    flowrate: tank.processdata.process?.flowrate,
    temperature: tank.processdata.process?.temperature,
    weight: tank.processdata.process?.weight
};

msg.payload = JSON.stringify([row]);
return msg;
