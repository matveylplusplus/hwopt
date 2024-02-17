PRAGMA foreign_keys=OFF;
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
INSERT INTO major_maps VALUES('g',0.625);
INSERT INTO major_maps VALUES('m',1.0);
CREATE TABLE classes (
    class_name TEXT PRIMARY KEY,
    major_state TEXT NOT NULL,
    total_class_points INTEGER NOT NULL CHECK (total_class_points > 0),
    FOREIGN KEY (major_state) REFERENCES major_maps (major_state) ON UPDATE CASCADE
);
INSERT INTO classes VALUES('cmsc351','m',600);
INSERT INTO classes VALUES('cmsc330','m',100);
CREATE TABLE lp_templates (late_policy_name TEXT PRIMARY KEY);
INSERT INTO lp_templates VALUES('5x3');
INSERT INTO lp_templates VALUES('stand');
CREATE TABLE lp_template_deadvars (
    late_policy_name TEXT,
    deadline_variable TEXT,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadline_variable)
);
INSERT INTO lp_template_deadvars VALUES('5x3','x1');
INSERT INTO lp_template_deadvars VALUES('stand','x1');
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
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.050000000000000002775,'x1',0);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.050000000000000002775,'x1',24);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.050000000000000002775,'x1',48);
INSERT INTO lp_template_deadvar_phases VALUES('5x3',0.84999999999999997779,'x1',72);
INSERT INTO lp_template_deadvar_phases VALUES('stand',1.0,'x1',0);
CREATE TABLE assignments (
    assignment_name TEXT PRIMARY KEY,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE
);
CREATE TABLE deadvar_maps (
    assignment_name TEXT,
    late_policy_name TEXT,
    deadline_variable TEXT,
    deadline_instance TEXT NOT NULL,
    FOREIGN KEY (assignment_name) REFERENCES assignments (assignment_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name, deadline_variable) REFERENCES lp_template_deadvars (late_policy_name, deadline_variable) ON UPDATE CASCADE,
    PRIMARY KEY (
        assignment_name,
        late_policy_name,
        deadline_variable
    )
);
CREATE TABLE assignment_templates (
    assignment_type TEXT,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE PRIMARY KEY (assignment_type, class_name)
);
INSERT INTO assignment_templates VALUES('hw','cmsc351',9.0909090909090917165,'stand');
COMMIT;
