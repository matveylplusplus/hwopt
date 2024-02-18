PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
CREATE TABLE major_maps (
    major_state TEXT PRIMARY KEY CHECK (
        major_state == 'm'
        OR major_state == 'g'
    ),
    major_factor REAL NOT NULL CHECK (
        0 < major_factor
        AND major_factor <= 1
    )
);
INSERT INTO major_maps
VALUES('m', 1.0);
INSERT INTO major_maps
VALUES('g', 0.8);
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
VALUES('stat410', 'm', 100);
INSERT INTO classes
VALUES('psyc100', 'g', 950);
CREATE TABLE lp_templates (late_policy_name TEXT PRIMARY KEY);
INSERT INTO lp_templates
VALUES('stand');
INSERT INTO lp_templates
VALUES('10x1');
INSERT INTO lp_templates
VALUES('may13');
INSERT INTO lp_templates
VALUES('may17');
CREATE TABLE lp_template_deadvars (
    late_policy_name TEXT,
    deadline_variable TEXT,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadline_variable)
);
INSERT INTO lp_template_deadvars
VALUES('stand', 'x0');
INSERT INTO lp_template_deadvars
VALUES('10x1', 'x0');
INSERT INTO lp_template_deadvars
VALUES('may13', 'x0');
INSERT INTO lp_template_deadvars
VALUES('may13', '2024-05-13 23:59:00');
INSERT INTO lp_template_deadvars
VALUES('may17', 'x0');
INSERT INTO lp_template_deadvars
VALUES('may17', '2024-05-17 23:59:00');
CREATE TABLE lp_template_deadvar_phases (
    late_policy_name TEXT,
    phase_value REAL CHECK (
        0 < phase_value
        AND phase_value <= 1
    ),
    deadline_variable TEXT,
    hour_offset INT,
    FOREIGN KEY (late_policy_name, deadline_variable) REFERENCES lp_template_deadvars (late_policy_name, deadline_variable) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadline_variable, hour_offset)
);
INSERT INTO lp_template_deadvar_phases
VALUES('stand', 1.0, 'x0', 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.1, 'x0', 0);
INSERT INTO lp_template_deadvar_phases
VALUES('10x1', 0.9, 'x0', 24);
INSERT INTO lp_template_deadvar_phases
VALUES('may13', 0.05, 'x0', 0);
INSERT INTO lp_template_deadvar_phases
VALUES('may13', 0.95, '2024-05-13 23:59:00', 0);
INSERT INTO lp_template_deadvar_phases
VALUES('may17', 0.05, 'x0', 0);
INSERT INTO lp_template_deadvar_phases
VALUES('may17', 0.95, '2024-05-17 23:59:00', 0);
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
VALUES('proj', 'cmsc330', NULL, '10x1', 0.6);
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
VALUES(
        'hw',
        'stat410',
        5.555555555555559799,
        'stand',
        0.25
    );
INSERT INTO assignment_templates
VALUES('midterm', 'stat410', 15.0, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('midterm', 'cmsc330', 12.0, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('ws', 'psyc100', NULL, 'may13', 0.0);
INSERT INTO assignment_templates
VALUES('quiz', 'cmsc330', 2.5, 'stand', 0.1);
INSERT INTO assignment_templates
VALUES('sa', 'psyc100', 50.0, 'may17', 0.1);
INSERT INTO assignment_templates
VALUES('midterm', 'psyc100', 75.0, 'stand', 0.1);
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
VALUES('proj2', 'cmsc330', 5.0, NULL, NULL, 'proj');
INSERT INTO assignments
VALUES('proj1', 'cmsc330', 30.0, 'stand', NULL, 'proj');
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
VALUES('ws-03', 'psyc100', 38.0, NULL, NULL, 'ws');
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
VALUES(
        'midterm2',
        'cmsc351',
        NULL,
        NULL,
        NULL,
        'midterm'
    );
INSERT INTO assignments
VALUES('quiz2', 'cmsc330', NULL, NULL, NULL, 'quiz');
INSERT INTO assignments
VALUES('sa-01', 'psyc100', NULL, NULL, NULL, 'sa');
INSERT INTO assignments
VALUES('ws-04', 'psyc100', 34.0, NULL, NULL, 'ws');
INSERT INTO assignments
VALUES(
        'midterm1',
        'psyc100',
        NULL,
        NULL,
        NULL,
        'midterm'
    );
INSERT INTO assignments
VALUES('sa-02', 'psyc100', NULL, NULL, NULL, 'sa');
INSERT INTO assignments
VALUES('ws-05', 'psyc100', 20.0, NULL, NULL, 'ws');
CREATE TABLE deadvar_maps (
    assignment_name TEXT,
    class_name TEXT,
    deadline_variable TEXT,
    deadline_instance TEXT NOT NULL,
    FOREIGN KEY (assignment_name, class_name) REFERENCES assignments (assignment_name, class_name) ON DELETE CASCADE,
    PRIMARY KEY (
        assignment_name,
        class_name,
        deadline_variable
    )
);
INSERT INTO deadvar_maps
VALUES('proj2', 'cmsc330', 'x0', '2024-02-27 23:59:00');
INSERT INTO deadvar_maps
VALUES('proj1', 'cmsc330', 'x0', '2024-05-10 23:59:00');
INSERT INTO deadvar_maps
VALUES('hw3', 'stat410', 'x0', '2024-02-23 23:59:00');
INSERT INTO deadvar_maps
VALUES(
        'midterm1',
        'stat410',
        'x0',
        '2024-02-28 10:55:00'
    );
INSERT INTO deadvar_maps
VALUES(
        'midterm1',
        'cmsc330',
        'x0',
        '2024-03-05 09:25:00'
    );
INSERT INTO deadvar_maps
VALUES(
        'midterm2',
        'cmsc351',
        'x0',
        '2024-03-13 09:55:00'
    );
INSERT INTO deadvar_maps
VALUES('quiz2', 'cmsc330', 'x0', '2024-02-23 11:55:00');
INSERT INTO deadvar_maps
VALUES(
        'midterm1',
        'psyc100',
        'x0',
        '2024-02-29 22:49:00'
    );
INSERT INTO deadvar_maps
VALUES('sa-02', 'psyc100', 'x0', '2024-02-23 23:59:00');
INSERT INTO deadvar_maps
VALUES('ws-05', 'psyc100', 'x0', '2024-03-01 23:59:00');
COMMIT;