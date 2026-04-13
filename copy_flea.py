# -*- coding: utf-8 -*-
"""Copy flea tables from 성훈 DB into 원본 DB (overwrite)."""
import sqlite3

SRC = r"c:\workspace\파일합치기최종\mompjt 성훈\db.sqlite3"
DST = r"c:\workspace\파일합치기최종\mompjt원본\db.sqlite3"

con = sqlite3.connect(DST)
con.execute("ATTACH DATABASE ? AS src", (SRC,))
cur = con.cursor()


def copy_table(name: str) -> None:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({name})")]
    placeholders = ",".join("?" * len(cols))
    cur.execute(f"DELETE FROM {name}")
    rows = cur.execute(f"SELECT {', '.join(cols)} FROM src.{name}").fetchall()
    if rows:
        cur.executemany(
            f"INSERT INTO {name} ({', '.join(cols)}) VALUES ({placeholders})",
            rows,
        )
        cur.execute(
            f"UPDATE sqlite_sequence SET seq=(SELECT MAX(id) FROM {name}) WHERE name=?",
            (name,),
        )
    print(name, "copied", len(rows))


for table in ["board_fleareport", "board_fleacomment", "board_fleaitem"]:
    copy_table(table)

con.commit()
con.close()
