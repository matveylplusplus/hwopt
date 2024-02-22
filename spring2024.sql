PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
CREATE TABLE major_maps (
    major_state TEXT PRIMARY KEY CHECK (
        major_state == 'm'
        OR major_state == 'g'
    ),
    passing_grade REAL NOT NULL,
    starting_offset REAL NOT NULL
);
INSERT INTO major_maps
VALUES('m', 70.0, 0.4000000000000000222);
INSERT INTO major_maps
VALUES('g', 60.0, 0.2000000000000000111);
CREATE TABLE classes (
    class_name TEXT PRIMARY KEY,
    major_state TEXT NOT NULL,
    total_class_points INTEGER NOT NULL CHECK (total_class_points > 0),
    FOREIGN KEY (major_state) REFERENCES major_maps (major_state) ON UPDATE CASCADE
);
INSERT INTO classes
VALUES('cmsc351', 'm', 600);
INSERT INTO classes
VALUES('cmsc330', 'm', 100);
INSERT INTO classes
VALUES('psyc100', 'g', 950);
INSERT INTO classes
VALUES('stat410', 'm', 100);
CREATE TABLE lp_templates (late_policy_name TEXT PRIMARY KEY);
INSERT INTO lp_templates
VALUES('5x3');
INSERT INTO lp_templates
VALUES('stand');
INSERT INTO lp_templates
VALUES('10x1');
INSERT INTO lp_templates
VALUES('5xD');
CREATE TABLE lp_template_deadvars (
    late_policy_name TEXT,
    deadvar INT,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadvar)
);
INSERT INTO lp_template_deadvars
VALUES('5x3', 0);
INSERT INTO lp_template_deadvars
VALUES('stand', 0);
INSERT INTO lp_template_deadvars
VALUES('10x1', 0);
INSERT INTO lp_template_deadvars
VALUES('5xD', 0);
INSERT INTO lp_template_deadvars
VALUES('5xD', 1);
CREATE TABLE lp_template_deadvar_phases (
    late_policy_name TEXT,
    phase_value REAL CHECK (
        0 < phase_value
        AND phase_value <= 1
    ),
    deadvar INT,
    hour_offset INT,
    FOREIGN KEY (late_policy_name, deadvar) REFERENCES lp_template_deadvars (late_policy_name, deadvar) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadvar, hour_offset)
);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.050000000000000002775, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.050000000000000002775, 0, 24);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.050000000000000002775, 0, 48);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.84999999999999997779, 0, 72);
INSERT INTO lp_template_deadvar_phases
VALUES('stand', 1.0, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.10000000000000000555, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.9000000000000000222, 0, 24);
INSERT INTO lp_template_deadvar_phases
VALUES('5xD', 0.050000000000000002775, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('5xD', 0.94999999999999995559, 1, 0);
CREATE TABLE assignment_templates (
    assignment_type TEXT,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    commute_factor REAL CHECK (
        0 <= commute_factor
        AND commute_factor <= 1
    ),
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (assignment_type, class_name)
);
INSERT INTO assignment_templates
VALUES(
        'hw',
        'cmsc351',
        11.111111111111112492,
        'stand',
        0.25
    );
INSERT INTO assignment_templates
VALUES(
        'midterm',
        'cmsc351',
        100.0,
        'stand',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES(
        'proj',
        'cmsc330',
        NULL,
        '10x1',
        0.59999999999999997779
    );
INSERT INTO assignment_templates
VALUES(
        'midterm',
        'cmsc330',
        12.0,
        'stand',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES(
        'quiz',
        'cmsc330',
        2.5,
        'stand',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES(
        'hw',
        'stat410',
        5.5555555555555553581,
        'stand',
        0.25
    );
INSERT INTO assignment_templates
VALUES(
        'midterm',
        'stat410',
        15.0,
        'stand',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES(
        'sa',
        'psyc100',
        50.0,
        '5xD',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES(
        'midterm',
        'psyc100',
        75.0,
        'stand',
        0.10000000000000000555
    );
INSERT INTO assignment_templates
VALUES('lc', 'psyc100', 5.0, 'stand', 0.0);
INSERT INTO assignment_templates
VALUES('ws', 'psyc100', NULL, '5xD', 0.0);
CREATE TABLE template_deadvar_maps (
    template TEXT,
    class_name TEXT,
    deadvar INT,
    deadline_date TEXT,
    deadline_hour INT,
    deadline_min INT,
    FOREIGN KEY (template, class_name) REFERENCES assignment_templates (assignment_type, class_name) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (
        template,
        class_name,
        deadvar
    )
);
INSERT INTO template_deadvar_maps
VALUES('hw', 'cmsc351', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES('midterm', 'cmsc351', 0, NULL, 9, 55);
INSERT INTO template_deadvar_maps
VALUES('proj', 'cmsc330', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES('midterm', 'cmsc330', 0, NULL, 9, 25);
INSERT INTO template_deadvar_maps
VALUES('quiz', 'cmsc330', 0, NULL, 11, 55);
INSERT INTO template_deadvar_maps
VALUES('hw', 'stat410', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES('midterm', 'stat410', 0, NULL, 10, 55);
INSERT INTO template_deadvar_maps
VALUES('sa', 'psyc100', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES(
        'sa',
        'psyc100',
        1,
        '2024-05-17 00:00:00',
        23,
        59
    );
INSERT INTO template_deadvar_maps
VALUES('midterm', 'psyc100', 0, NULL, 22, 50);
INSERT INTO template_deadvar_maps
VALUES('lc', 'psyc100', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES('ws', 'psyc100', 0, NULL, 23, 59);
INSERT INTO template_deadvar_maps
VALUES(
        'ws',
        'psyc100',
        1,
        '2024-05-13 00:00:00',
        23,
        59
    );
CREATE TABLE assignments (
    assignment_name TEXT,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    commute_factor REAL CHECK (
        0 <= commute_factor
        AND commute_factor <= 1
    ),
    template TEXT,
    pct_loss REAL NOT NULL CHECK (
        0.0 <= pct_loss
        AND pct_loss <= 100.0
    ),
    submitted INT NOT NULL CHECK (
        submitted = 0
        OR submitted = 1
    ),
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    FOREIGN KEY (template, class_name) REFERENCES assignment_templates (assignment_type, class_name) ON UPDATE CASCADE,
    PRIMARY KEY (assignment_name, class_name)
);
INSERT INTO assignments
VALUES(
        'midterm2',
        'cmsc351',
        NULL,
        NULL,
        NULL,
        'midterm',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'proj2',
        'cmsc330',
        5.0,
        NULL,
        NULL,
        'proj',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'midterm1',
        'cmsc330',
        NULL,
        NULL,
        NULL,
        'midterm',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'quiz2',
        'cmsc330',
        NULL,
        NULL,
        NULL,
        'quiz',
        0.0,
        0
    );
INSERT INTO assignments
VALUES('hw4', 'cmsc351', NULL, NULL, NULL, 'hw', 0.0, 0);
INSERT INTO assignments
VALUES('hw3', 'stat410', NULL, NULL, NULL, 'hw', 0.0, 0);
INSERT INTO assignments
VALUES(
        'midterm1',
        'stat410',
        NULL,
        NULL,
        NULL,
        'midterm',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'sa-01',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'sa',
        5.0,
        0
    );
INSERT INTO assignments
VALUES(
        'sa-02',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'sa',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'quiz1',
        'cmsc330',
        NULL,
        NULL,
        NULL,
        'quiz',
        30.000000000000003551,
        1
    );
INSERT INTO assignments
VALUES(
        'hw1',
        'cmsc351',
        NULL,
        NULL,
        NULL,
        'hw',
        13.0,
        1
    );
INSERT INTO assignments
VALUES(
        'lc-01',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'lc',
        100.0,
        0
    );
INSERT INTO assignments
VALUES(
        'lc-02',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'lc',
        100.0,
        0
    );
INSERT INTO assignments
VALUES(
        'lc-03',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'lc',
        100.0,
        0
    );
INSERT INTO assignments
VALUES(
        'ws-03',
        'psyc100',
        38.0,
        NULL,
        NULL,
        'ws',
        5.0,
        0
    );
INSERT INTO assignments
VALUES(
        'ws-04',
        'psyc100',
        34.0,
        NULL,
        NULL,
        'ws',
        5.0,
        0
    );
INSERT INTO assignments
VALUES(
        'midterm1',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'midterm',
        0.0,
        0
    );
INSERT INTO assignments
VALUES(
        'ws-05',
        'psyc100',
        20.0,
        NULL,
        NULL,
        'ws',
        0.0,
        0
    );
CREATE TABLE assignment_deadvar_maps (
    assignment_name TEXT,
    class_name TEXT,
    deadvar INT,
    deadline_date TEXT,
    deadline_hour INT,
    deadline_min INT,
    FOREIGN KEY (assignment_name, class_name) REFERENCES assignments (assignment_name, class_name) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (
        assignment_name,
        class_name,
        deadvar
    )
);
INSERT INTO assignment_deadvar_maps
VALUES(
        'midterm2',
        'cmsc351',
        0,
        '2024-03-13 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'proj2',
        'cmsc330',
        0,
        '2024-02-27 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'midterm1',
        'cmsc330',
        0,
        '2024-03-05 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'quiz2',
        'cmsc330',
        0,
        '2024-02-23 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'hw4',
        'cmsc351',
        0,
        '2024-02-28 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'hw3',
        'stat410',
        0,
        '2024-02-23 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'midterm1',
        'stat410',
        0,
        '2024-02-28 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'sa-01',
        'psyc100',
        0,
        '2024-02-09 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'sa-02',
        'psyc100',
        0,
        '2024-02-23 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'quiz1',
        'cmsc330',
        0,
        '2024-02-09 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'hw1',
        'cmsc351',
        0,
        '2024-01-31 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'lc-01',
        'psyc100',
        0,
        '2024-01-31 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'lc-02',
        'psyc100',
        0,
        '2024-02-07 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'lc-03',
        'psyc100',
        0,
        '2024-02-14 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'ws-03',
        'psyc100',
        0,
        '2024-02-08 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'ws-04',
        'psyc100',
        0,
        '2024-02-15 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'midterm1',
        'psyc100',
        0,
        '2024-02-29 00:00:00',
        NULL,
        NULL
    );
INSERT INTO assignment_deadvar_maps
VALUES(
        'ws-05',
        'psyc100',
        0,
        '2024-03-01 00:00:00',
        NULL,
        NULL
    );
COMMIT;