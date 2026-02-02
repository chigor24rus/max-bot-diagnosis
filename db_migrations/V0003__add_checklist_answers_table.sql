-- Создание таблицы для хранения ответов на пункты чек-листа диагностики "5-ти минутка"
CREATE TABLE IF NOT EXISTS t_p70271656_max_bot_diagnosis.checklist_answers (
    id SERIAL PRIMARY KEY,
    diagnostic_id INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    answer_type VARCHAR(50) NOT NULL,
    answer_value TEXT,
    sub_answers JSONB,
    photo_urls TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_diagnostic FOREIGN KEY (diagnostic_id) REFERENCES t_p70271656_max_bot_diagnosis.diagnostics(id)
);

-- Индексы для быстрого поиска
CREATE INDEX idx_checklist_diagnostic_id ON t_p70271656_max_bot_diagnosis.checklist_answers(diagnostic_id);
CREATE INDEX idx_checklist_question_number ON t_p70271656_max_bot_diagnosis.checklist_answers(question_number);

-- Комментарии
COMMENT ON TABLE t_p70271656_max_bot_diagnosis.checklist_answers IS 'Ответы на пункты чек-листа диагностики 5-ти минутка';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.diagnostic_id IS 'ID связанной диагностики';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.question_number IS 'Номер вопроса (1-55)';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.question_text IS 'Текст вопроса';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.answer_type IS 'Тип ответа: single, multiple, text, level';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.answer_value IS 'Основной ответ';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.sub_answers IS 'Вложенные подответы в JSON формате';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.checklist_answers.photo_urls IS 'Массив URL фотографий';