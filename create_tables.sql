CREATE TABLE devices (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

CREATE TABLE ring_records (
    id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    file_path VARCHAR NOT NULL,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audio_records (
    id UUID PRIMARY KEY,
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    file_path VARCHAR NOT NULL,
    sample_rate INTEGER,
    channels INTEGER,
    sample_width INTEGER,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);