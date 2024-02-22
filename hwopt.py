import sqlite3
from decimal import Decimal
from dateutil import parser
from collections import deque
import pandas as pd


def connect_to_db() -> sqlite3.Connection:
    conn = sqlite3.connect(f"hwopt.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def store(table_name: str, entry_tuple_list: list[tuple[str]]):
    conn = connect_to_db()
    # makes assumption that that all members of entry_tuple_list have exactly as many elements as entry_tuple_list[0] does...
    qstring = ("?," * (len(entry_tuple_list[0]) - 1)) + "?"
    with conn:
        c = conn.cursor()
        print("Inserting shit...")
        c.executemany(
            f"INSERT INTO {table_name} VALUES ({qstring})",
            entry_tuple_list,
        )
    conn.close()
    print("Done!")


# simpsing = simple + single
def get_simpsing_input(question_list: list[str]) -> tuple[str]:
    answer_list = []

    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    for i in range(len(question_list)):
        inp = input(f" - {question_list[i]}: ")
        answer_list.append(inp)

    return tuple(answer_list)


def insert_class():
    question_list = ["class name", "major or gened (m/g)", "total points"]
    entry = get_simpsing_input(question_list)
    store("classes", [entry])


def insert_late_policy():
    # init
    phase_list = []
    deadvar_list = []
    deadline_counts = []
    prev_deduct = Decimal(0)

    # input
    deadvar_count = 0
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    policy_name = input(" - policy name: ")
    independent_deadlines_count = int(input(" - # of independent deadlines: "))
    for i in range(independent_deadlines_count):
        deadvar_list.append((policy_name, deadvar_count))
        deadline_count = int(
            input(f"   - # of phases dependent on deadvar {deadvar_count}: ")
        )
        deadline_counts.append(deadline_count)
        deadvar_count += 1
    for i in range(len(deadline_counts)):
        # for formatting
        if i != 1 and deadline_counts[i] > 1:
            print(f" - deadvar {i} -")
        for j in range(deadline_counts[i]):
            deduct = Decimal(1)
            hour_offset = 0
            if j != 0:
                hour_offset = int(input(f"   - hour offset {j}: "))
            if i != len(deadline_counts) - 1 or j != deadline_counts[i] - 1:
                deduct = Decimal(
                    input(f"   - pct deduction {j+1} (from original grade): ")
                ) / Decimal(100)
                # print(f"deduct is {str(deduct)}")
                # print(f"difference is {str(deduct - prev_deduct)}")

            phase_list.append(
                (
                    policy_name,
                    str(deduct - prev_deduct),
                    i,
                    hour_offset,
                )
            )
            prev_deduct = deduct

    store("lp_templates", [(policy_name,)])  # <- comma is necessary!!
    store("lp_template_deadvars", deadvar_list)
    store("lp_template_deadvar_phases", phase_list)


def null_sieve(input_str: str):
    return (
        None
        if (input_str == "n/a" or input_str == "" or input_str == "NULL")
        else input_str
    )


def insert_assignment_template():
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    format_str = " - "

    class_name = input(f"{format_str}class name: ")
    assignment_type = input(f"{format_str}assignment type: ")
    points = null_sieve(input(f"{format_str}points: "))
    # parse fractions jic
    if points is not None and "/" in points:
        split_frac = points.split("/")
        points = str(Decimal(int(split_frac[0])) / Decimal(int(split_frac[1])))
    late_policy = null_sieve(input(f"{format_str}late policy: "))
    commute_factor = null_sieve(float(input(f"{format_str}commute factor: ")))

    if late_policy is not None:
        conn = connect_to_db()
        with conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT DISTINCT deadvar
                FROM lp_template_deadvar_phases
                WHERE late_policy_name = ?
                """,
                (late_policy,),
            )
            distinct_deadvars = c.fetchall()
        conn.close()

        deadvar_map_entries = []
        print(f"{format_str}deadlines{format_str}")
        for i in range(len(distinct_deadvars)):
            deadvar_date = null_sieve(
                input(f"  {format_str}deadvar {i} date: ")
            )
            deadvar_time = null_sieve(
                input(f"  {format_str}deadvar {i} time: ")
            )

            # if user has a non-null entry for deadvar_date or deadvar_time...
            if deadvar_date is not None or deadvar_time is not None:
                hour = None
                minute = None

                # if the string cannot be parsed it's user's fault
                date = (
                    str(parser.parse(deadvar_date))
                    if deadvar_date is not None
                    else deadvar_date
                )

                try:
                    parsed_time = parser.parse(deadvar_time)
                    hour = str(parsed_time.hour)
                    minute = str(parsed_time.minute)
                except (TypeError, parser.ParserError):
                    pass

                deadvar_map_entries.append(
                    (
                        assignment_type,
                        class_name,
                        i,
                        date,
                        hour,
                        minute,
                    )
                )

    store(
        "assignment_templates",
        [(assignment_type, class_name, points, late_policy, commute_factor)],
    )
    store("template_deadvar_maps", deadvar_map_entries)


def insert_assignment():
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    format_str = " - "

    class_name = input(f"{format_str}class name: ")
    template = null_sieve(input(f"{format_str}template: "))
    assignment_name = input(f"{format_str}assignment name: ")

    conn = connect_to_db()
    template_excerpt = (None, None, None)
    if template is not None:
        with conn:
            c = conn.cursor()
            c.execute(
                "SELECT points, late_policy_name, commute_factor FROM assignment_templates WHERE assignment_type = ? AND class_name = ?",
                (template, class_name),
            )
            template_excerpt = c.fetchone()

    loop_input_list = ["points", "late policy", "commute factor"]
    lp_checklist = deque()
    lp_checklist.append(template_excerpt[1])
    plc = []
    for i in range(len(template_excerpt)):
        post_str = (
            " (overriding template)" if template_excerpt[i] is not None else ""
        )
        inp = input(f"{format_str}{loop_input_list[i]}{post_str}: ")
        processed_inp = null_sieve(inp)
        if i == 0:
            processed_inp = (
                int(processed_inp)
                if processed_inp is not None
                else processed_inp
            )
        elif i == 1:
            lp_checklist.appendleft(processed_inp)
        elif i == 2:
            processed_inp = (
                str(Decimal(processed_inp))
                if processed_inp is not None
                else processed_inp
            )
        plc.append(processed_inp)

    with conn:
        c = conn.cursor()
        c.execute(
            """
            SELECT DISTINCT deadvar
            FROM lp_template_deadvar_phases
            WHERE late_policy_name = ?
            """,
            (next(x for x in lp_checklist if x is not None),),
        )
        distinct_deadvars = c.fetchall()

    template_excerpt2 = [(None, None)] * len(distinct_deadvars)
    # if the assignment uses a template and doesn't override its late policy...
    # (the template is assumed to be using a late policy in this case)
    if template is not None:
        with conn:
            c = conn.cursor()
            c.execute(
                """
                SELECT deadline_date, deadline_hour
                FROM template_deadvar_maps
                WHERE template_deadvar_maps.template = ? AND template_deadvar_maps.class_name = ?
                """,
                (template, class_name),
            )
            template_excerpt2 = c.fetchall()
    conn.close()

    deadvar_map_entries = []
    print(f"{format_str}deadlines{format_str}")
    for i in range(len(distinct_deadvars)):
        """add override message iff the template already has a mapping for that deadvar"""
        post_str = (
            " (overriding template)"
            if template_excerpt2[i][0] is not None
            else ""
        )
        deadvar_date = null_sieve(
            input(f"  {format_str}deadvar {i} date{post_str}: ")
        )

        post_str = (
            " (overriding template)"
            if template_excerpt2[i][1] is not None
            else ""
        )
        deadvar_time = null_sieve(
            input(f"  {format_str}deadvar {i} time{post_str}: ")
        )

        # if user has a non-null entry for deadvar_date or deadvar_time...
        if deadvar_date is not None or deadvar_time is not None:
            hour = None
            minute = None
            # if the string cannot be parsed it's user's fault
            date = (
                str(parser.parse(deadvar_date))
                if deadvar_date is not None
                else deadvar_date
            )

            try:
                parsed_time = parser.parse(deadvar_time)
                hour = str(parsed_time.hour)
                minute = str(parsed_time.minute)
            except (TypeError, parser.ParserError):
                pass

            deadvar_map_entries.append(
                (
                    assignment_name,
                    class_name,
                    i,
                    date,
                    hour,
                    minute,
                )
            )
    store(
        "assignments",
        [(assignment_name, class_name, *plc, template)],
    )
    store("assignment_deadvar_maps", deadvar_map_entries)


def insert_grade():
    pre_input_fix = " - "
    post_input_fix = ": "

    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    class_name = input(f"{pre_input_fix}class name{post_input_fix}")
    template = null_sieve(input(f"{pre_input_fix}template{post_input_fix}"))
    assignment_name = input(f"{pre_input_fix}assignment name{post_input_fix}")
    grade = input(f"{pre_input_fix}grade (pct){post_input_fix}")

    # fraction parse
    if grade is not None and "/" in grade:
        split_frac = grade.split("/")
        grade = str(Decimal(int(split_frac[0])) / Decimal(int(split_frac[1])))

    template_excerpt = None
    conn = connect_to_db()
    if template is not None:
        c = conn.cursor()
        c.execute(
            """
            SELECT points
            FROM assignment_templates
            WHERE assignment_type = ? AND class_name = ?
        """,
            (template, class_name),
        )
        template_excerpt = c.fetchone()
    post_point_str = (
        " (overriding template)" if template_excerpt is not None else ""
    )
    value_in_class_points = null_sieve(
        input(
            f"{pre_input_fix}assignment value in class points{post_point_str}{post_input_fix}"
        )
    )

    store(
        "gradebook",
        [(class_name, assignment_name, grade, value_in_class_points, template)],
    )


def get_insert_input() -> str:
    print("\nWhat would you like to insert?")
    print(" - (1) Class")
    print(" - (2) Late Policy")
    print(" - (3) Assignment Template")
    print(" - (4) Assignment")
    print(" - (5) Grade")
    print(" - (Ctrl+C) get me the hell outta here")
    return input()


def process_insert_input(pick: str):
    try:
        if pick == "1":
            insert_class()
        elif pick == "2":
            insert_late_policy()
        elif pick == "3":
            insert_assignment_template()
        elif pick == "4":
            insert_assignment()
        elif pick == "5":
            insert_grade()
    except KeyboardInterrupt:
        print()
        pass


def insert_loop():
    try:
        while True:
            process_insert_input(get_insert_input())
    except KeyboardInterrupt:
        pass


def generate_prindex_table():
    conn = connect_to_db()
    # conn.enable_load_extension(True)
    # conn.load_extension("")
    with conn:
        c = conn.cursor()
        c.executescript(
            """
            UPDATE assignments
            SET pct_loss = accum.passed_phase_sum
            FROM (
                SELECT assignments.class_name, assignments.assignment_name, SUM(phase_value) AS passed_phase_sum
                FROM assignments
                LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
                LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                WHERE CAST(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime')) AS INTEGER) <= 0
                GROUP BY class_name, assignment_name
                ) AS accum
            WHERE assignments.assignment_name = accum.assignment_name AND assignments.class_name = accum.class_name;

            CREATE TEMP TABLE assignment_deadlines AS
            SELECT 
                classes.class_name,
                assignments.assignment_name,
                CAST(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime')) AS INTEGER)

            CREATE TEMP TABLE complete_table AS
            SELECT
                classes.class_name,
                assignments.assignment_name,
                major_maps.major_state,
                major_maps.passing_grade,
                major_maps.starting_offset,
                lp_template_deadvar_phases.late_policy_name, lp_template_deadvar_phases.phase_value, 
                (CAST(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime')) AS INTEGER)) AS minutes_to_deadline
            FROM assignments
            INNER JOIN classes ON classes.class_name = assignments.assignment_name
            INNER JOIN major_maps ON major_maps.major_state = classes.major_state
            LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            INNER JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
            LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
            LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar

            CREATE TEMP TABLE dead_complete_table AS
            SELECT * 
            FROM complete_table 
            WHERE lp_templaet_deadvar_phases.

            CREATE TEMP TABLE p_parts AS
            SELECT 
                assignments.assignment_name, 
                assignments.class_name, 
                COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), 
                CAST(lp_template_deadvar_phases.phase_value / (CAST(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime')) AS INTEGER)) AS REAL) AS p_summand
            FROM assignments
            LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
            LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
            LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar

            CREATE TEMP TABLE class_point_losses AS
            SELECT class_name, COALESCE(SUM(point_losses), 0.0) AS total_points_lost
            FROM (
                SELECT 
                    classes.class_name, 
                    gradebook.assignment_name, (1.0 - gradebook.pct_grade) * COALESCE(gradebook.value_in_class_points, assignment_templates.points) AS point_losses
                FROM classes
                LEFT JOIN gradebook ON gradebook.class_name = classes.class_name
                LEFT JOIN assignment_templates ON assignment_templates.assignment_type = gradebook.template AND assignment_templates.class_name = gradebook.class_name
            )
            GROUP BY class_name;

            CREATE TEMP TABLE prindexes AS
            SELECT class_name, assignment_name, prindex, commute_factor*prindex AS cprindex
            FROM (
                SELECT 
                    assignments.assignment_name, 
                    assignments.class_name, 
                    (((1.0 - major_maps.starting_offset) * ((100.0 * class_point_losses.total_points_lost) / ((100.0 - major_maps.passing_grade) * classes.total_class_points))) + major_maps.starting_offset) * COALESCE(assignments.points, assignment_templates.points) * (1.0 / classes.total_class_points) * (SUM(p_parts.p_summand)) * 1000000.0 as prindex, 
                    COALESCE(assignments.commute_factor, assignment_templates.commute_factor) AS commute_factor
                FROM p_parts
                INNER JOIN assignments ON assignments.assignment_name = p_parts.assignment_name AND assignments.class_name = p_parts.class_name
                LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                INNER JOIN classes ON classes.class_name = assignments.class_name
                INNER JOIN class_point_losses ON class_point_losses.class_name = classes.class_name
                INNER JOIN major_maps ON major_maps.major_state = classes.major_state
                WHERE 0 < p_parts.p_summand AND p_parts.p_summand <= phase_value;
                GROUP BY assignments.assignment_name, assignments.class_name
                );
        """
        )
    try:
        while True:
            print("\nWould you like to:")
            print(" - (1) Sort by prindex")
            print(" - (2) Sort by c-prindex")
            print(" - (Ctrl+C) gtfoo")
            sort = input()
            if sort == "1":
                pretty_print(
                    "SELECT * FROM prindexes ORDER BY prindex DESC", conn
                )
            elif sort == "2":
                pretty_print(
                    "SELECT * FROM prindexes ORDER BY cprindex DESC", conn
                )

    except KeyboardInterrupt:
        conn.close()


def pretty_print(query: str, conn: sqlite3.Connection):
    print("\n-----------------------------------------------------")
    print(pd.read_sql_query(query, conn).to_string(index=False))
    print("-----------------------------------------------------")
    print(" - (Ctrl+C) this world is a heartless, frozen hell")


def view_loop():
    try:
        while True:
            print("\nWhich table would you like to view?")
            table_list = [
                "Classes",
                "Late Policies",
                "Assignment Templates",
                "Assignments",
                "Gradebook",
            ]
            dbtable_list = [
                "classes",
                "lp_templates",
                "assignment_templates",
                "assignments",
                "gradebook",
            ]

            for i in range(len(table_list)):
                print(f" - ({i+1}) {table_list[i]}")
            print(" - (Ctrl+C) please. i miss my family")
            pick = int(input())

            conn = connect_to_db()
            pretty_print(f"SELECT * FROM {dbtable_list[pick-1]};", conn)
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass

    except KeyboardInterrupt:
        pass


def get_menu_input() -> str:
    print("\nhwopt welcomes you. What would you like to do with hwopt?")
    print(" - (1) Generate prindex")
    print(" - (2) Insert into hwopt")
    print(" - (3) View tables")
    print(" - (Ctrl+C) Quit hwopt")
    return input()


def process_menu_input(pick: str) -> int:
    if pick == "1":
        generate_prindex_table()
    elif pick == "2":
        insert_loop()
    elif pick == "3":
        view_loop()
    else:
        return 0
    return 1


def menu_loop():
    try:
        while True:
            process_menu_input(get_menu_input())
    except KeyboardInterrupt:
        pass


def bye_bye():
    print("\nhwopt says bye bye!")


def main():
    menu_loop()
    bye_bye()


if __name__ == "__main__":
    main()
