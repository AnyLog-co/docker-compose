let site_id = "Site1";
let store = flow.get('store');
if (!store) return null;

let tank = store["Enterprise B"]
    ?.[site_id]
    ?.liquidprocessing
    ?.tankstorage01
    ?.tank01;

if (!tank?.metric || !tank?.lotnumber) return null;

let row = {
    dbms: "enterprise_b",
    table: "kpi",
    timestamp: flow.get(`ts_${site_id}`) || flow.get('factory_timestamp') || new Date().toISOString(),
    site: site_id,
    lotnumberid: tank.lotnumber.lotnumber,
    oee: tank.metric.oee,
    performance: tank.metric.performance,
    quality: tank.metric.quality,
    availability: tank.metric.availability
};

msg.payload = JSON.stringify([row]);
return msg;