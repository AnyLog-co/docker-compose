let store = flow.get('store') || {};
let parts = msg.topic.split("/");

let current = store;
for (let i = 0; i < parts.length - 1; i++) {
    if (!current[parts[i]]) current[parts[i]] = {};
    current = current[parts[i]];
}

let value;
if (!isNaN(msg.payload) && msg.payload !== "") value = Number(msg.payload);
else if (msg.payload === "true" || msg.payload === "false") value = msg.payload === "true";
else value = msg.payload;

current[parts[parts.length - 1]] = value;

flow.set('store', store);
return msg;