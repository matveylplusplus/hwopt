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
            f"INSERT OR IGNORE INTO {table_name} VALUES ({qstring})",
            entry_tuple_list,
        )
        # OR IGNORE makes sure that we don't crash if user enters an entry that duplicates another entry's primary key (sqlite just doesn't enter it)
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
    deadline_count_pairs = []
    prev_deduct = Decimal(0)

    # input
    varcount = 0
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    policy_name = input(" - policy name: ")
    independent_deadlines_count = int(input(" - # of independent deadlines: "))
    for i in range(independent_deadlines_count):
        deadvar = input(f"   - deadline variable {i+1}: ")
        try:
            # if you're giving a concrete date, let the parser interpret it and paste it in a nice format
            deadvar = str(parser.parse(deadvar))
        except parser.ParserError:
            # if user does not provide a concrete date, then their input is taken to be a variable
            deadvar = f"x{varcount}"
            varcount += 1
        deadvar_list.append((policy_name, deadvar))
        deadline_count = int(
            input(f"   - # of phases dependent on {deadvar}: ")
        )
        deadline_count_pairs.append((deadvar, deadline_count))
    for i in range(len(deadline_count_pairs)):
        # for formatting
        if i != 1 and deadline_count_pairs[i][1] > 1:
            print(f" - {deadline_count_pairs[i][0]} -")
        for j in range(deadline_count_pairs[i][1]):
            deduct = Decimal(1)
            hour_offset = 0
            if j != 0:
                hour_offset = int(input(f"   - hour offset {j}: "))
            if (
                i != len(deadline_count_pairs) - 1
                or j != deadline_count_pairs[i][1] - 1
            ):
                deduct = Decimal(
                    input(f"   - pct deduction {j+1} (from original grade): ")
                ) / Decimal(100)
                # print(f"deduct is {str(deduct)}")
                # print(f"difference is {str(deduct - prev_deduct)}")

            phase_list.append(
                (
                    policy_name,
                    str(deduct - prev_deduct),
                    deadline_count_pairs[i][0],
                    hour_offset,
                )
            )
            prev_deduct = deduct

    store("lp_templates", [(policy_name,)])  # <- comma is necessary!!
    store("lp_template_deadvars", deadvar_list)
    store("lp_template_deadvar_phases", phase_list)


def null_sieve(input_str: str):
    return None if input_str == "n/a" else input_str


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
    commute_factor = null_sieve(input(f"{format_str}commute factor: "))

    store(
        "assignment_templates",
        [(assignment_type, class_name, points, late_policy, commute_factor)],
    )


def insert_assignment():
    print("\nProvide the following information (or hit Ctrl+C to exit)...")
    format_str = " - "

    class_name = input(f"{format_str}class name: ")
    assignment_name = input(f"{format_str}assignment name: ")
    template = null_sieve(input(f"{format_str}template: "))

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
            SELECT DISTINCT deadline_variable 
            FROM lp_template_deadvar_phases
            WHERE late_policy_name = ? AND deadline_variable LIKE '%%x%%'
            """,
            (next(x for x in lp_checklist if x is not None),),
        )
        distinct_deadvars = c.fetchall()
    conn.close()

    deadvar_map_entries = []
    print(f"{format_str}deadlines{format_str}")
    for i in range(len(distinct_deadvars)):
        var_to_inspect = distinct_deadvars[i][0]
        deadvar_instance = var_to_inspect
        deadvar_instance = str(
            parser.parse(input(f"  {format_str}instance of {var_to_inspect}: "))
        )
        deadvar_map_entries.append(
            (assignment_name, class_name, var_to_inspect, deadvar_instance)
        )

    store(
        "assignments",
        [(assignment_name, class_name, *plc, template)],
    )
    store("deadvar_maps", deadvar_map_entries)


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


def generate_prindex_table():
    conn = connect_to_db()
    # conn.enable_load_extension(True)
    # conn.load_extension("")
    with conn:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TEMP TABLE p_parts AS
            SELECT assignments.assignment_name, CAST(lp_template_deadvar_phases.phase_value / (CAST(24*60*(julianday(datetime(deadvar_maps.deadline_instance, '+' || lp_template_deadvar_phases.hour_offset || ' hours')) - julianday('now', 'localtime')) AS INTEGER)) AS REAL) AS p_summand
            FROM assignments
            INNER JOIN deadvar_maps ON deadvar_maps.assignment_name = assignments.assignment_name AND deadvar_maps.class_name = assignments.class_name
            LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
            LEFT JOIN lp_template_deadvar_phases ON lp_template_deadvar_phases.late_policy_name = COALESCE(assignments.late_policy_name, assignment_templates.late_policy_name)
            WHERE 0 < p_summand AND p_summand <= phase_value;

            DELETE FROM assignments WHERE NOT EXISTS (SELECT * FROM p_parts WHERE p_parts.assignment_name = assignments.assignment_name);

            CREATE TEMP TABLE prindexes AS
            SELECT class_name, assignment_name, prindex, commute_factor*prindex AS cprindex
            FROM (
                SELECT assignments.assignment_name, assignments.class_name, major_maps.major_factor*COALESCE(assignments.points, assignment_templates.points)*(1.0/classes.total_class_points)*(SUM(p_parts.p_summand))*100000.0 as prindex, COALESCE(assignments.commute_factor, assignment_templates.commute_factor) AS commute_factor
                FROM p_parts
                INNER JOIN assignments ON assignments.assignment_name = p_parts.assignment_name
                LEFT JOIN assignment_templates ON assignment_templates.assignment_type = assignments.template AND assignment_templates.class_name = assignments.class_name
                INNER JOIN classes ON classes.class_name = COALESCE(assignments.class_name, assignment_templates.class_name)
                INNER JOIN major_maps ON major_maps.major_state = classes.major_state
                GROUP BY assignments.assignment_name
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
                print("\n-----------------------------------------------------")
                print(
                    pd.read_sql_query(
                        "SELECT * FROM prindexes ORDER BY prindex DESC", conn
                    ).to_string(index=False)
                )
                print("-----------------------------------------------------")
            elif sort == "2":
                print("\n-----------------------------------------------------")
                print(
                    pd.read_sql_query(
                        "SELECT * FROM prindexes ORDER BY cprindex DESC", conn
                    ).to_string(index=False)
                )
                print("-----------------------------------------------------")

    except KeyboardInterrupt:
        conn.close()


def get_menu_input() -> str:
    print("\nhwopt welcomes you. What would you like to do with hwopt?")
    print(" - (1) Generate prindex")
    print(" - (2) Insert into hwopt")
    print(" - (Ctrl+C) Quit hwopt")
    return input()


def process_menu_input(pick: str) -> int:
    if pick == "1":
        generate_prindex_table()
    elif pick == "2":
        insert_loop()
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
