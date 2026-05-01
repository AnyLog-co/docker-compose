// Function node: "Store Metadata Timestamp"
let meta = msg.payload;
if (typeof meta === "string") meta = JSON.parse(meta);

// Store factory-wide timestamp
flow.set('factory_timestamp', meta.generated_at);

// Optional: store per-site timestamp
for (let site in meta.virtual_devices) {
    flow.set(`ts_${site}`, meta.virtual_devices[site].timestamp);
}

return msg; // just passes it along