-- Создание таблицы для хранения диагностик автомобилей
CREATE TABLE IF NOT EXISTS t_p70271656_max_bot_diagnosis.diagnostics (
    id SERIAL PRIMARY KEY,
    mechanic VARCHAR(100) NOT NULL,
    car_number VARCHAR(20) NOT NULL,
    mileage INTEGER NOT NULL,
    diagnostic_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для быстрого поиска
CREATE INDEX idx_car_number ON t_p70271656_max_bot_diagnosis.diagnostics(car_number);
CREATE INDEX idx_mechanic ON t_p70271656_max_bot_diagnosis.diagnostics(mechanic);
CREATE INDEX idx_created_at ON t_p70271656_max_bot_diagnosis.diagnostics(created_at);

-- Комментарии к таблице и полям
COMMENT ON TABLE t_p70271656_max_bot_diagnosis.diagnostics IS 'Таблица для хранения данных диагностик автомобилей';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.diagnostics.mechanic IS 'ФИО механика, проводившего диагностику';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.diagnostics.car_number IS 'Государственный номер автомобиля';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.diagnostics.mileage IS 'Пробег автомобиля в километрах';
COMMENT ON COLUMN t_p70271656_max_bot_diagnosis.diagnostics.diagnostic_type IS 'Тип диагностики: 5min, dhch, des';
