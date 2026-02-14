ALTER TABLE t_p70271656_max_bot_diagnosis.diagnostics ADD COLUMN completed boolean NOT NULL DEFAULT false;

UPDATE t_p70271656_max_bot_diagnosis.diagnostics SET completed = true;