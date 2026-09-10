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

CREATE TABLE sessions (
    id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    started_at TIMESTAMP NOT NULL, ended_at TIMESTAMP, timezone VARCHAR, status VARCHAR NOT NULL DEFAULT 'recording'
);
CREATE TABLE geo_points (
    id UUID PRIMARY KEY, session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION, accuracy DOUBLE PRECISION, provider VARCHAR
);
ALTER TABLE ring_records ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES sessions(id) ON DELETE SET NULL;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES sessions(id) ON DELETE SET NULL;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS transcript_path VARCHAR;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS transcript_text TEXT;
CREATE TABLE ring_samples (
    id UUID PRIMARY KEY, ring_record_id UUID NOT NULL REFERENCES ring_records(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL, heart_rate INTEGER, spo2 INTEGER, signal_quality REAL, raw_payload JSONB
);
CREATE TABLE feature_windows (
    id UUID PRIMARY KEY, session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    t_start TIMESTAMP NOT NULL, t_end TIMESTAMP NOT NULL, latitude DOUBLE PRECISION, longitude DOUBLE PRECISION,
    r1 REAL, r2 REAL, r3 REAL, r_total REAL, heart_rate INTEGER, transcript TEXT, model_comment TEXT, quality_flags JSONB
);
