-- Initialize the database.
-- Drop any existing data and create empty tables.

-- initialize old data. we dont drop user after initialized
-- DROP TABLE IF EXISTS user; 
-- DROP TABLE IF EXISTS post;
-- DROP TABLE IF EXISTS comments;
-- DROP TABLE IF EXISTS ranks;


-- CREATE TABLE user (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   username TEXT UNIQUE NOT NULL,
--   password TEXT NOT NULL,
--   useremail TEXT UNIQUE NOT NULL,
--   register_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   last_login TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   user_type VARCHAR(10) DEFAULT 'user',
--   nickname TEXT DEFAULT 'nickname',
--   About TEXT DEFAULT 'About me',
--   website TEXT DEFAULT '#',
--   pfp TEXT DEFAULT '#',
--  status VARCHAR DEFAULT 'active'
-- );



-- CREATE TABLE post (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   title TEXT NOT NULL,
--   body TEXT NOT NULL,
--   img_url TEXT DEFAULT NONE
--   -- FOREIGN KEY (author_id) REFERENCES user (id),
-- );

-- CREATE TABLE comments (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   author_id INTEGER NOT NULL,
--   created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   body TEXT NOT NULL,
--   post_id INTEGER NOT NULL,
--   retweet_id INTEGER NOT NULL DEFAULT 0
-- );

--current user (user_id) follows profile user (id)
-- CREATE TABLE follow(
--   user_id INTEGER NOT NULL,
--   follows_id INTEGER NOT NULL
-- );

-- CREATE TABLE likes(
--   user_id INTEGER NOT NULL,
--   post_id INTEGER NOT NULL
-- );

-- CREATE TABLE ranks (
--         user_id INTEGER,
--         rank float,
--         points INTERGER default 1 );

-- DELETE FROM user;
-- INSERT INTO user(id,username,password,useremail,user_type) VALUES (1,'admin','admin','admin@heroku.com','admin');
-- UPDATE user SET user_type='admin' WHERE id=1;
-- SELECT * FROM user;
-- ALTER TABLE user ADD nickname TEXT DEFAULT 'nickname';


-- CREATE TABLE friendlist(
--   user_id INTEGER NOT NULL,
--   follows_id INTEGER NOT NULL,
--   friendrequest VARCHAR NOT NULL DEFAULT 'unsend',
--   friendship VARCHAR NOT NULL DEFAULT 'notfriend',
--   friend_since TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );
-- CREATE TABLE messages(
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     sender_id INTEGER NOT NULL,
--     receiver_id INTEGER NOT NULL,
--     msg TEXT NOT NULL,
--     read_status VARCHAR DEFAULT 'unread',
--     created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
-- );