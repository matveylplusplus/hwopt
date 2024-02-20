PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
CREATE TABLE major_maps (
    major_state TEXT PRIMARY KEY CHECK (
        major_state == 'm'
        OR major_state == 'g'
    ),
    scaling_factor REAL NOT NULL,
    starting_offset REAL NOT NULL
);
INSERT INTO major_maps
VALUES('m', 3.0, 0.1);
INSERT INTO major_maps
VALUES('g', 2.3, 0.08);
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
VALUES('5x3', 0.05, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.05, 0, 24);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.05, 0, 48);
INSERT INTO lp_template_deadvar_phases
VALUES('5x3', 0.85, 0, 72);
INSERT INTO lp_template_deadvar_phases
VALUES('stand', 1.0, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.1, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.9, 0, 24);
INSERT INTO lp_template_deadvar_phases
VALUES('5xD', 0.05, 0, 0);
INSERT INTO lp_template_deadvar_phases
VALUES('5xD', 0.95, 1, 0);
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
        11.111111111111111604,
        'stand',
        0.25
    );
INSERT INTO assignment_templates
VALUES('midterm', 'cmsc351', 100.0, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('proj', 'cmsc330', NULL, '10x1', 0.6);
INSERT INTO assignment_templates
VALUES('midterm', 'cmsc330', 12.0, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('quiz', 'cmsc330', 2.5, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES(
        'hw',
        'stat410',
        5.5555555555555553581,
        'stand',
        0.25
    );
INSERT INTO assignment_templates
VALUES('midterm', 'stat410', 15.0, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('sa', 'psyc100', 50.0, '5xD', 0.1);
INSERT INTO assignment_templates
VALUES('midterm', 'psyc100', 75.0, 'stand', 0.1);
CREATE TABLE template_deadvar_maps (
    template TEXT,
    class_name TEXT,
    deadvar INT,
    deadline_date TEXT,
    deadline_hour INT,
    deadline_min INT,
    FOREIGN KEY (template, class_name) REFERENCES assignment_templates (assignment_type, class_name) ON DELETE CASCADE,
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
        'midterm'
    );
INSERT INTO assignments
VALUES('proj2', 'cmsc330', 5.0, NULL, NULL, 'proj');
INSERT INTO assignments
VALUES(
        'midterm1',
        'cmsc330',
        NULL,
        NULL,
        NULL,
        'midterm'
    );
INSERT INTO assignments
VALUES('quiz2', 'cmsc330', NULL, NULL, NULL, 'quiz');
INSERT INTO assignments
VALUES('hw4', 'cmsc351', NULL, NULL, NULL, 'hw');
INSERT INTO assignments
VALUES('hw3', 'stat410', NULL, NULL, NULL, 'hw');
INSERT INTO assignments
VALUES(
        'midterm1',
        'stat410',
        NULL,
        NULL,
        NULL,
        'midterm'
    );
INSERT INTO assignments
VALUES('proj1', 'cmsc330', 30.0, 'stand', NULL, 'proj');
INSERT INTO assignments
VALUES('sa-01', 'psyc100', NULL, NULL, NULL, 'sa');
INSERT INTO assignments
VALUES('sa-02', 'psyc100', NULL, NULL, NULL, 'sa');
CREATE TABLE assignment_deadvar_maps (
    assignment_name TEXT,
    class_name TEXT,
    deadvar INT,
    deadline_date TEXT,
    deadline_hour INT,
    deadline_min INT,
    FOREIGN KEY (assignment_name, class_name) REFERENCES assignments (assignment_name, class_name) ON DELETE CASCADE,
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
        'proj1',
        'cmsc330',
        0,
        '2024-05-10 00:00:00',
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
CREATE TABLE point_losses (
    class_name TEXT,
    assignment_name TEXT,
    point_loss REAL,
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON DELETE CASCADE
) COMMIT;