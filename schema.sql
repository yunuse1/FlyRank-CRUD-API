CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE
);

INSERT INTO tasks (title, done) 
SELECT 'Backend Task', false
WHERE NOT EXISTS (SELECT 1 FROM tasks);