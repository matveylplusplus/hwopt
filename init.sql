CREATE TABLE IF NOT EXISTS major_maps (
    major_state TEXT PRIMARY KEY CHECK (
        major_state == 'm'
        OR major_state == 'g'
    ),
    major_factor REAL NOT NULL CHECK (
        0 < major_factor
        AND major_factor <= 1
    )
);
CREATE TABLE IF NOT EXISTS classes (
    class_name TEXT PRIMARY KEY,
    major_state TEXT NOT NULL,
    total_class_points INTEGER NOT NULL CHECK (total_class_points > 0),
    FOREIGN KEY (major_state) REFERENCES major_maps (major_state) ON UPDATE CASCADE
);
CREATE TABLE IF NOT EXISTS lp_templates (late_policy_name TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS lp_template_deadvars (
    late_policy_name TEXT,
    deadline_variable TEXT,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (late_policy_name, deadline_variable)
);
CREATE TABLE IF NOT EXISTS lp_template_deadvar_phases (
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
CREATE TABLE IF NOT EXISTS assignment_templates (
    assignment_type TEXT,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    commute_factor REAL CHECK (
        0 < commute_factor
        AND commute_factor <= 1
    ),
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    PRIMARY KEY (assignment_type, class_name)
);
CREATE TABLE IF NOT EXISTS assignments (
    assignment_name TEXT,
    class_name TEXT,
    points REAL,
    late_policy_name TEXT,
    commute_factor REAL CHECK (
        0 < commute_factor
        AND commute_factor <= 1
    ),
    template TEXT,
    FOREIGN KEY (class_name) REFERENCES classes (class_name) ON UPDATE CASCADE,
    FOREIGN KEY (late_policy_name) REFERENCES lp_templates (late_policy_name) ON UPDATE CASCADE,
    FOREIGN KEY (template, class_name) REFERENCES assignment_templates (assignment_type, class_name) ON UPDATE CASCADE,
    PRIMARY KEY (assignment_name, class_name)
);
CREATE TABLE IF NOT EXISTS deadvar_maps (
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