-- Idempotent upgrade for an existing Omi database. Does not delete old captures.
CREATE TABLE IF NOT EXISTS sessions (id UUID PRIMARY KEY, device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE, started_at TIMESTAMP NOT NULL, ended_at TIMESTAMP, timezone VARCHAR, status VARCHAR NOT NULL DEFAULT 'recording');
CREATE TABLE IF NOT EXISTS geo_points (id UUID PRIMARY KEY, session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, timestamp TIMESTAMP NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL, altitude DOUBLE PRECISION, accuracy DOUBLE PRECISION, provider VARCHAR);
ALTER TABLE ring_records ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES sessions(id) ON DELETE SET NULL;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS session_id UUID REFERENCES sessions(id) ON DELETE SET NULL;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS transcript_path VARCHAR;
ALTER TABLE audio_records ADD COLUMN IF NOT EXISTS transcript_text TEXT;
CREATE TABLE IF NOT EXISTS ring_samples (id UUID PRIMARY KEY, ring_record_id UUID NOT NULL REFERENCES ring_records(id) ON DELETE CASCADE, timestamp TIMESTAMP NOT NULL, heart_rate INTEGER, spo2 INTEGER, signal_quality REAL, raw_payload JSONB);
CREATE TABLE IF NOT EXISTS feature_windows (id UUID PRIMARY KEY, session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE, t_start TIMESTAMP NOT NULL, t_end TIMESTAMP NOT NULL, latitude DOUBLE PRECISION, longitude DOUBLE PRECISION, r1 REAL, r2 REAL, r3 REAL, r_total REAL, heart_rate INTEGER, transcript TEXT, model_comment TEXT, quality_flags JSONB);
CREATE INDEX IF NOT EXISTS ix_sessions_device_started ON sessions(device_id, started_at DESC);
CREATE INDEX IF NOT EXISTS ix_geo_points_session_time ON geo_points(session_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_feature_windows_session_time ON feature_windows(session_id, t_start);
