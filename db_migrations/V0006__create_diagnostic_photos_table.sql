CREATE TABLE IF NOT EXISTS diagnostic_photos (
    id SERIAL PRIMARY KEY,
    diagnostic_id INTEGER NOT NULL,
    question_index INTEGER NOT NULL,
    photo_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_diagnostic_photos_diagnostic_id ON diagnostic_photos(diagnostic_id);
CREATE INDEX IF NOT EXISTS idx_diagnostic_photos_question_index ON diagnostic_photos(question_index);