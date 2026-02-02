-- Добавление полей phone и pin_code к таблице mechanics
ALTER TABLE mechanics ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE mechanics ADD COLUMN IF NOT EXISTS pin_code VARCHAR(4);
ALTER TABLE mechanics ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE mechanics ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Обновление существующих записей тестовыми данными
UPDATE mechanics SET phone = '+79001234567', pin_code = '1234' WHERE name = 'Подкорытов С.А.' AND phone IS NULL;
UPDATE mechanics SET phone = '+79001234568', pin_code = '5678' WHERE name = 'Костенко В.Ю.' AND phone IS NULL;
UPDATE mechanics SET phone = '+79001234569', pin_code = '9012' WHERE name = 'Иванюта Д.И.' AND phone IS NULL;
UPDATE mechanics SET phone = '+79001234570', pin_code = '3456' WHERE name = 'Загороднюк Н.Д.' AND phone IS NULL;

-- Создание уникального индекса для phone
CREATE UNIQUE INDEX IF NOT EXISTS idx_mechanics_phone_unique ON mechanics(phone);

-- Добавление поля mechanic_id в diagnostics
ALTER TABLE diagnostics ADD COLUMN IF NOT EXISTS mechanic_id INTEGER;