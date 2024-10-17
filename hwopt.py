import sqlite3
from decimal import Decimal
from dateutil import parser
from collections import deque
import pandas as pd

"""
started on the second
thought it would be done in a weekend
finished on the twenty second
what a fucked up day
"""


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
                    input(f"   - pct deduction {j+1} (from the ORIGINAL grade; do not format as 0.x!): ")
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


def parse_frac(input_str: str) -> str:
    if input_str is not None and "/" in input_str:
        split_frac = input_str.split("/")
        input_str = str(
            Decimal(int(split_frac[0])) / Decimal(int(split_frac[1]))
        )
    return input_str


def insert_assignment_template():
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    format_str = " - "

    class_name = input(f"{format_str}class name: ")
    assignment_type = input(f"{format_str}assignment type: ")
    points = parse_frac(null_sieve(input(f"{format_str}points: ")))
    late_policy = null_sieve(input(f"{format_str}late policy: "))
    commute_factor = null_sieve(input(f"{format_str}commute factor: "))

    # set to 1.0 by default if user enters null value
    commute_factor = (
        str(Decimal(commute_factor)) if commute_factor is not None else str(1.0)
    )

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

    if deadvar_map_entries != []:
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
            processed_inp = parse_frac(processed_inp)
        elif i == 1:
            lp_checklist.appendleft(processed_inp)
        elif i == 2:
            processed_inp = (
                str(Decimal(processed_inp))
                if processed_inp is not None
                else 1.0
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
        [(assignment_name, class_name, *plc, template, 0.0, 0)],
    )
    store("assignment_deadvar_maps", deadvar_map_entries)


def grade_assignment():
    pre_input_fix = " - "
    post_input_fix = ": "

    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    class_name = input(f"{pre_input_fix}class name{post_input_fix}")
    assignment_name = input(f"{pre_input_fix}assignment name{post_input_fix}")
    grade = input(
        f"{pre_input_fix}grade (point score / point total){post_input_fix}"
    )

    # fraction parse
    split_frac = grade.split("/")
    grade = str(Decimal(int(split_frac[0])) / Decimal(int(split_frac[1])))

    conn = connect_to_db()
    with conn:
        c = conn.cursor()
        c.execute(
            f"""
                  UPDATE assignments
                  SET pct_loss = (1.0 - ?)*100.0
                  WHERE class_name = ? AND assignment_name = ? AND submitted = 1
                  """,
            (grade, class_name, assignment_name),
        )
    conn.close()
    print("Graded!")


def submit_assignment():
    """
    6.3.24 Interpretation.
        Takes in:
            1. an assignment
            2. a submission date for said assignment (subdate)
        and sets the following values in hwopt.db's respective assignments table entry:
            1. submitted -> 1
            2. pct_loss -> whatever pct_loss is (or would be) at subdate

        This essentially 'fixes' the pct_loss to a certain value so that it does not automatically change after a deadline is passed (as it would by default).

        Note, however, that this does *not* drop the assignment from the database. Submitted assignments (under the current design) need to remain in the database for:
            1) later grading, if applicable (which can change your pct_loss for the class).
            2) keeping track of your total pct_loss for the class, which is relevant for prindex calculation.

        Furthermore -- as of writing -- this function does not drop the submitted assignment from the prindex table generated in generate_prindex_table().

    6.5.24 Interpretation.
        The SQL script that is executed looks almost identical to the one in update_loss() (making one naturally suspect duplication), but there's a crucial difference in that update_loss()'s block is fixed to update loss w.r.t the current time, whereas this method updates loss w.r.t a time you provide.
    """
    pre_input_fix = " - "
    post_input_fix = ": "

    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    class_name = input(f"{pre_input_fix}class name{post_input_fix}")
    assignment_name = input(f"{pre_input_fix}assignment name{post_input_fix}")
    datetime_submit = input(
        f"{pre_input_fix}datetime of submission{post_input_fix}"
    )
    if datetime_submit != "now":
        datetime_submit = str(parser.parse(datetime_submit))

    conn = connect_to_db()
    with conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE assignments
            SET 
                submitted = 1,
                pct_loss = accum.passed_phase_sum
            FROM (
                SELECT 
                    assignments.class_name,
                    assignments.assignment_name,
                    SUM(CASE WHEN (ROUND(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday(?, 'localtime'))) <= 0.0) THEN phase_value ELSE 0.0 END) * 100.0 AS passed_phase_sum
                FROM assignments
                    LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                    LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
                    LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                    LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                WHERE assignments.class_name = ? AND assignments.assignment_name = ? AND assignments.submitted = 0
                GROUP BY assignments.class_name, assignments.assignment_name
                ) AS accum
            WHERE assignments.class_name = ? AND assignments.assignment_name = ? AND assignments.submitted = 0
            """,
            (
                datetime_submit,
                class_name,
                assignment_name,
                class_name,
                assignment_name,
            ),
        )
    conn.close()
    print("Submitted!")


def get_insert_input() -> str:
    print("\nWhat would you like to insert?")
    print(" - (1) Class")
    print(" - (2) Late Policy")
    print(" - (3) Assignment Template")
    print(" - (4) Assignment")
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
    except KeyboardInterrupt:
        print()
        pass


def insert_loop():
    try:
        while True:
            process_insert_input(get_insert_input())
    except KeyboardInterrupt:
        pass


def update_loss():
    conn = connect_to_db()
    with conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE assignments
            SET pct_loss = accum.passed_phase_sum
            FROM (
                SELECT 
                    assignments.class_name,
                    assignments.assignment_name,
                    SUM(CASE WHEN (ROUND(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime'))) <= 0) THEN phase_value ELSE 0.0 END) * 100.0 AS passed_phase_sum
                FROM assignments
                    LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                    LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
                    LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                    LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
                GROUP BY assignments.class_name, assignments.assignment_name
                ) AS accum
            WHERE assignments.assignment_name = accum.assignment_name AND assignments.class_name = accum.class_name AND assignments.submitted = 0
            """
        )
    conn.close()


def generate_prindex_table():
    """
    Generates prindex table by forming 3 subsidiary temp tables whose info is used to form a 4th temp table (the prindex table) that gets presented to user.

    Prindex table does not show submitted assignments.
    """
    update_loss()
    conn = connect_to_db()
    with conn:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TEMP TABLE p_parts AS
            SELECT 
                assignments.assignment_name, 
                assignments.class_name, 
                COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date) AS deadline_date, 
                CAST(lp_template_deadvar_phases.phase_value / (CAST(24*60*(julianday(datetime(COALESCE(assignment_deadvar_maps.deadline_date, template_deadvar_maps.deadline_date), '+' || (lp_template_deadvar_phases.hour_offset + COALESCE(assignment_deadvar_maps.deadline_hour, template_deadvar_maps.deadline_hour)) || ' hours', '+' || COALESCE(assignment_deadvar_maps.deadline_min, template_deadvar_maps.deadline_min) || ' minutes')) - julianday('now', 'localtime')) AS INTEGER)) AS REAL) AS p_summand
            FROM assignments
            LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
            LEFT JOIN assignment_deadvar_maps ON assignment_deadvar_maps.assignment_name = assignments.assignment_name AND assignment_deadvar_maps.class_name = assignments.class_name AND assignment_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
            LEFT JOIN template_deadvar_maps ON template_deadvar_maps.template = assignment_templates.assignment_type AND template_deadvar_maps.class_name = assignment_templates.class_name AND template_deadvar_maps.deadvar = lp_template_deadvar_phases.deadvar
            WHERE 0 < p_summand AND p_summand <= phase_value AND assignments.submitted == 0;

            CREATE TEMP TABLE class_point_losses AS
            SELECT class_name, major_state, total_class_points, COALESCE(SUM(point_losses), 0.0) AS total_points_lost
            FROM (
                SELECT 
                    classes.class_name,
                    classes.major_state, 
                    classes.total_class_points,
                    assignments.assignment_name, 
                    (assignments.pct_loss / 100.0) * COALESCE(assignments.points, assignment_templates.points) AS point_losses
                FROM classes
                LEFT JOIN assignments ON assignments.class_name = classes.class_name
                LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            )
            GROUP BY class_name;

            CREATE TEMP TABLE the_rest AS 
            SELECT 
                assignments.class_name,
                assignments.assignment_name,
                COALESCE(assignments.points, assignment_templates.points) AS points,
                COALESCE(assignments.commute_factor, assignment_templates.commute_factor) AS commute_factor,
                (((1.0 - (major_maps.passing_grade / 100.0)) * class_point_losses.total_class_points) - class_point_losses.total_points_lost) AS scale
            FROM assignments
            LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            INNER JOIN class_point_losses ON class_point_losses.class_name = assignments.class_name
            INNER JOIN major_maps ON major_maps.major_state = class_point_losses.major_state
            WHERE assignments.submitted == 0;

            CREATE TEMP TABLE prindexes AS
            SELECT class_name, assignment_name, prindex, commute_factor*prindex AS cprindex, due_date
            FROM (
                SELECT 
                    the_rest.assignment_name, 
                    the_rest.class_name, 
                    (CASE WHEN (the_rest.points < the_rest.scale) THEN (the_rest.points / the_rest.scale) ELSE 1.0 END) * (SUM(p_parts.p_summand)) * 100000.0 as prindex, 
                    the_rest.commute_factor AS commute_factor,
                    p_parts.deadline_date AS due_date
                FROM p_parts
                INNER JOIN the_rest ON the_rest.assignment_name = p_parts.assignment_name AND the_rest.class_name = p_parts.class_name
                GROUP BY the_rest.assignment_name, the_rest.class_name
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
            try:
                while True:
                    pass
            except KeyboardInterrupt:
                pass

    except KeyboardInterrupt:
        conn.close()


def reset():
    conn = connect_to_db()
    with conn:
        c = conn.cursor()
        print("Deleting shit...")
        c.executescript(
            """
            DELETE FROM assignments;
            DELETE FROM template_deadvar_maps;
            DELETE FROM assignment_templates;
            DELETE FROM assignment_deadvar_maps;
            DELETE FROM classes;
        """
        )
    conn.close()
    print("Done!")


def pretty_print(query: str, conn: sqlite3.Connection):
    print("\n-----------------------------------------------------")
    print(pd.read_sql_query(query, conn).to_string(index=False))
    print("-----------------------------------------------------")
    print(" - (Ctrl+C) this world is a heartless, frozen hell")


def view_loop():
    try:
        while True:
            update_loss()
            print("\nWhich table would you like to view?")
            table_list = [
                "Classes",
                "Late Policies",
                "Assignment Templates",
                "Assignments",
            ]
            dbtable_list = [
                "classes",
                "lp_templates",
                "assignment_templates",
                "assignments",
            ]

            for i in range(len(table_list)):
                print(f" - ({i+1}) {table_list[i]}")
            print(" - (Ctrl+C) please. i miss my family")
            pick = int(input())

            conn = connect_to_db()
            if pick == 1:
                with conn:
                    c = conn.cursor()
                    c.executescript(
                        """
                    CREATE TEMP TABLE class_point_losses AS
                    SELECT class_name, major_state, total_class_points, (COALESCE(SUM(point_losses), 0.0)/total_class_points)*100 AS total_pct_loss
                    FROM (
                        SELECT 
                            classes.class_name,
                            classes.major_state, 
                            classes.total_class_points,
                            assignments.assignment_name, 
                            (assignments.pct_loss / 100.0) * COALESCE(assignments.points, assignment_templates.points) AS point_losses
                        FROM classes
                        LEFT JOIN assignments ON assignments.class_name = classes.class_name
                        LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                    )
                    GROUP BY class_name;
                    """
                    )
                pretty_print(
                    f"SELECT * FROM {dbtable_list[pick-1]} JOIN class_point_losses ON classes.class_name = class_point_losses.class_name;",
                    conn,
                )
                conn.close()
            else:
                pretty_print(f"SELECT * FROM {dbtable_list[pick-1]};", conn)
                conn.close()
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
    print(" - (3) Reset academic term")
    print(" - (4) View tables")
    print(" - (5) Grade an assignment")
    print(" - (6) Submit an assignment")
    print(" - (Ctrl+C) Quit hwopt")
    return input()


def process_menu_input(pick: str) -> int:
    if pick == "1":
        generate_prindex_table()
    elif pick == "2":
        insert_loop()
    elif pick == "3":
        reset()
    elif pick == "4":
        view_loop()
    elif pick == "5":
        grade_assignment()
    elif pick == "6":
        submit_assignment()
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
