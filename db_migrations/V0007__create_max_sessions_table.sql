CREATE TABLE IF NOT EXISTS max_sessions (
    user_id TEXT PRIMARY KEY,
    session_data JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_max_sessions_updated_at ON max_sessions(updated_at);