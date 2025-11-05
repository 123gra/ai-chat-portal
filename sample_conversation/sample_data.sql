INSERT INTO chat_conversation (id, summary) VALUES (1, 'User asked about mutual funds.');
INSERT INTO chat_message (conversation_id, sender, content)
VALUES
(1, 'user', 'Hi, can you help me understand mutual funds?'),
(1, 'ai', 'Sure! Mutual funds pool money from investors to invest in stocks, bonds, etc.');
