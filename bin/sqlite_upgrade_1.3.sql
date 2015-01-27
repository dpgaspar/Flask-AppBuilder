CREATE TABLE ab_user_bk (id INTEGER NOT NULL,
                                first_name VARCHAR(64) NOT NULL,
                                last_name VARCHAR(64) NOT NULL,
                                username VARCHAR(32) NOT NULL,
                                password VARCHAR(256),
                                active BOOLEAN,
                                email VARCHAR(64) NOT NULL,
                                last_login DATETIME,
                                login_count INTEGER,
                                fail_login_count INTEGER,
                                created_on DATETIME,
                                changed_on DATETIME,
                                created_by_fk INTEGER,
                                changed_by_fk INTEGER,
                                PRIMARY KEY (id),
                                UNIQUE (username),
                                CHECK (active IN (0, 1)),
                                UNIQUE (email),
                                FOREIGN KEY(created_by_fk) REFERENCES ab_user (id),
                                FOREIGN KEY(changed_by_fk) REFERENCES ab_user (id));

                                INSERT INTO ab_user_bk (id, first_name, last_name, username, password, active, email,
                                                   last_login, login_count,fail_login_count, created_on, changed_on,
                                                    created_by_fk, changed_by_fk)
                                SELECT id, first_name, last_name, username, password, active, email,
                                                    last_login, login_count,fail_login_count, created_on, changed_on,
                                                    created_by_fk, changed_by_fk FROM ab_user;

                                DROP TABLE ab_user;

                                ALTER TABLE ab_user_bk RENAME TO ab_user;
