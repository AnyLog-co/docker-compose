// --- Parse payload ---
let meta = msg.payload;
if (typeof meta === "string") meta = JSON.parse(meta);

// --- Extract 'sum' updated_at (epoch ms) ---
let updatedMs = meta?.virtual_devices?.sum?.updated_at;
if (!updatedMs) return null;

// --- Ensure monotonic milliseconds ---
let lastMs = flow.get('last_sum_epoch_ms') || 0;

// If same or older timestamp, bump by 1 ms
if (updatedMs <= lastMs) {
    updatedMs = lastMs + 1;
}

// Save epoch for next comparison
flow.set('last_sum_epoch_ms', updatedMs);

// --- Convert to ISO-8601 (milliseconds ONLY) ---
let isoTimestamp = new Date(updatedMs).toISOString();

// --- Save for data generator ---
flow.set('factory_timestamp_C', isoTimestamp);

// --- Output (optional) ---
msg.payload = { updated_at: isoTimestamp };
return msg;