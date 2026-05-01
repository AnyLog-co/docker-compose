// --- Get existing content from context ---
let content = context.get('store') || [];

// --- Extract last part of topic ---
let parts = msg.topic.split("/");
let key = parts[parts.length - 1];

// --- Preserve native type ---
let value;
if (typeof msg.payload === "object" && msg.payload !== null) {
    value = JSON.parse(JSON.stringify(msg.payload));
} else if (typeof msg.payload === "string") {
    if (!isNaN(msg.payload) && msg.payload.trim() !== "") {
        value = Number(msg.payload);
    } else if (msg.payload === "true" || msg.payload === "false") {
        value = msg.payload === "true";
    } else {
        value = msg.payload;
    }
} else {
    value = msg.payload;
}

// --- If value is undefined/null, skip sending ---
if (value === undefined || value === null) {
    return null;  // exit, do not send
}

// --- Determine table name ---
let keyParts = key.split(".");
let table = keyParts[0].replace(/-/g, "_");
let column = keyParts.length > 1 ? keyParts.slice(1).join("_") : "value";

// --- If column is empty, skip sending ---
if (!column || column.trim() === "") {
    return null;
}

// --- Use updated timestamp from metadata ---
let now = flow.get('factory_timestamp_C') || new Date().toISOString();

// --- Merge into content array ---
let existingEntry = content.find(e => e.table === table);
if (existingEntry) {
    existingEntry[column] = value;
    existingEntry.timestamp = now;
} else {
    let storeEntry = {
        dbms: " manufacturing_historian",
        table: table,
        timestamp: now,
        [column]: value
    };
    content.push(storeEntry);
}

// --- Save back to context ---
context.set('store', content);

// --- Prepare MQTT message ---
// --- Prepare MQTT message ---
let mqttPayload = content
    .filter(e => e.table !== "metadata")   // <--- skip metadata table
    .map(e => {
        return {
            dbms: e.dbms,
            table: e.table,
            timestamp: e.timestamp,
            // only include keys with actual values (skip undefined/null)
            ...Object.fromEntries(
                Object.entries(e).filter(([k, v]) => !["dbms", "table", "timestamp"].includes(k) && v != null)
            )
        };
    });

// --- Skip sending if empty ---
if (mqttPayload.length === 0) return null;

msg.topic = "enterprisec";
msg.payload = JSON.stringify(mqttPayload);
return msg;
