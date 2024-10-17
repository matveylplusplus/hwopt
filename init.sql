PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE major_maps (
    major_state TEXT PRIMARY KEY CHECK (
        major_state == 'm'
        OR major_state == 'g'
    ),
    passing_grade REAL NOT NULL
);
INSERT INTO major_maps VALUES('m',70.0);
INSERT INTO major_maps VALUES('g',60.0);
CREATE TABLE classes (
    class_name TEXT PRIMARY KEY,
    major_state TEXT NOT NULL,
    total_class_points INTEGER NOT NULL CHECK (total_class_points > 0),
    FOREIGN KEY (major_state) REFERENCES major_maps (major_state) ON UPDATE CASCADE
);
CREATE TABLE lp_templates (late_policy_name TEXT PRIMARY KEY);
INSERT INTO lp_templates VALUES('5x3');
INSERT INTO lp_templates VALUES('stand');
INSERT INTO lp_templates VALUES('10x1');
INSERT INTO lp_templates VALUES('5xD');
INSERT INTO lp_templates VALUES('5x1');
INSERT INTO lp_templates VALUES('15x3');
INSERT INTO lp_templates VALUES('15x1');
CREATE TABLE lp_template_deadvars (
    late_policy_name TEXT,
    deadvar INT,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadvar)
);
INSERT INTO lp_template_deadvars VALUES('5x3',0);
INSERT INTO lp_template_deadvars VALUES('stand',0);
INSERT INTO lp_template_deadvars VALUES('10x1',0);
INSERT INTO lp_template_deadvars VALUES('5xD',0);
INSERT INTO lp_template_deadvars VALUES('5xD',1);
INSERT INTO lp_template_deadvars VALUES('5x1',0);
INSERT INTO lp_template_deadvars VALUES('15x3',0);
INSERT INTO lp_template_deadvars VALUES('15x1',0);
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
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.0500000000000000027,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.0500000000000000027,0,24);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.0500000000000000027,0,48);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.849999999999999977,0,72);
INSERT INTO lp_template_deadvar_phases VALUES('stand',1.0,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('10x1',0.100000000000000005,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('10x1',0.900000000000000022,0,24);
INSERT INTO lp_template_deadvar_phases VALUES('5xD',0.0500000000000000027,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('5xD',0.949999999999999955,1,0);
INSERT INTO lp_template_deadvar_phases VALUES('5x1',0.0500000000000000027,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('5x1',0.949999999999999955,0,24);
INSERT INTO lp_template_deadvar_phases VALUES('15x3',0.149999999999999994,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('15x3',0.149999999999999994,0,24);
INSERT INTO lp_template_deadvar_phases VALUES('15x3',0.149999999999999994,0,48);
INSERT INTO lp_template_deadvar_phases VALUES('15x3',0.550000000000000044,0,72);
INSERT INTO lp_template_deadvar_phases VALUES('15x1',0.149999999999999994,0,0);
INSERT INTO lp_template_deadvar_phases VALUES('15x1',0.849999999999999977,0,24);
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
COMMIT;
