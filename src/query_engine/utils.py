import re

START_CODE_TAG = "BEGIN```"
END_CODE_TAG = "```END"


def extract_sql_query(sql_query):
    match = re.search(r'```sql\s+(.*?)\s+```', sql_query, re.DOTALL)
    if match:
        return match.group(1).strip()
    elif sql_query:
        return sql_query
    else:
        return ""


def extract_sql_custom(response: str, separator: str = "```") -> str:
    print(f"extract_sql, response={response}")
    code = response
    sql_code = ""
    match = re.search(
        rf"{START_CODE_TAG}(.*)({END_CODE_TAG}|{END_CODE_TAG.replace('<', '</')})",
        code,
        re.DOTALL,
    )
    print(f"extract_sql, match={match}")

    if match:
        sql_code = match.group(1).strip()
        print(f"extract_sql, match.group, sql_code={sql_code}")

    if len(code.split(separator)) > 1:
        sql_code = code.split(separator)[1]
        print(f"extract_sql, split, sql_code={sql_code}")

    return sql_code


def extract_code(response: str, separator: str = "```") -> str:
    code = response
    match = re.search(
        rf"{START_CODE_TAG}(.*)({END_CODE_TAG}|{END_CODE_TAG.replace('<', '</')})",
        code,
        re.DOTALL,
    )
    if match:
        code = match.group(1).strip()
    if len(code.split(separator)) > 1:
        code = code.split(separator)[1]

    code = code.replace("python", "")

    if "fig.show()" in code:
        code = code.replace("fig.show()", "fig")

    return code
