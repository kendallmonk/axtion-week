#!/usr/bin/env python3
"""Generate an .ics of the Axtion Week for Apple Calendar.

    python3 tools/make-ics.py [outfile]        # default: axtion-week.ics

Import the result into a NEW calendar in Calendar.app rather than an
existing one, so the whole set can be deleted and re-imported in one move
when the week changes. Otherwise you are hunting two dozen recurring
series by hand.

Alternating weeks are real recurrence rules — INTERVAL=2 anchored to the
right Monday — rather than duplicated events, so nothing needs topping up
week to week.

MAINTENANCE
  ANCHOR_DROP must be a Monday that really is a drop-off week, and
  ANCHOR_PICK the Monday after it. If the alternation ever slips in real
  life the calendar will not self-correct: move the anchors forward to the
  next true pair and regenerate.

  UNTIL stops the recurrence on 30 Jun 2027, because the doc says The Arc
  moves into build in H2 2027 and that is "a rebuild of the week rather
  than an adjustment to it". Expiring beats a stale week running on.

DELIBERATELY NOT HERE
  Family time, Elliot's bedtime, Personal Projects, the 10pm stop, and
  Sunday's all-day family block. Sunday therefore carries only movement
  and breakfast.

  Meditation is the fifteen-minute window (8:15-8:30 / 7:45-8:00), not the
  ten solid minutes inside it. Blocking the window is the point: it stops
  the sit becoming another thing to be late for. Settled 21 Sep 2026; the
  1 November decision point is closed.

Do not commit the generated .ics. The site's password gate is client-side
only, so anything in this repo is served unprotected.
"""

import datetime as dt
import sys

TZ = "Asia/Makassar"                       # Bali, UTC+8, no DST
ANCHOR_DROP = dt.date(2026, 9, 21)         # Monday — a drop-off week
ANCHOR_PICK = dt.date(2026, 9, 28)         # the Monday after — pickup
UNTIL = "20270630T155959Z"                 # 30 Jun 2027 23:59:59 WITA

DAYNUM = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

# (summary, description, start, end, byday, cadence)
#   cadence: "weekly" (every week) | "drop" | "pick" (alternating)
EVENTS = [
    # --- every day -------------------------------------------------------
    ("Movement and Shower", "Fasted. No slow mornings. Health standards are set by the Health & Wellbeing Plan.",
     "06:00", "07:00", "MO,TU,WE,TH,FR,SA,SU", "weekly"),
    ("Family Breakfast", "Kate and Elliot. Together, before anything else starts.",
     "07:00", "07:45", "MO,TU,WE,TH", "weekly"),
    ("Family Breakfast", "Kate and Elliot. Runs to 8:00 at the weekend.",
     "07:00", "08:00", "FR,SA,SU", "weekly"),

    # --- drop-off week ---------------------------------------------------
    ("School Run \u2014 Drop-off", "My week. Kate picks up.",
     "07:45", "08:15", "MO,TU,WE", "drop"),
    ("Meditation", "Quiet. Intention. Begin. A fifteen-minute window to get ten solid minutes in. Settled 21 September 2026.",
     "08:15", "08:30", "MO,TU,WE", "drop"),
    ("Block A \u2014 KM + Signal", "Protected. The deepest work of the day. No admin, no other projects, nothing else gets in. Never reallocates.",
     "08:30", "11:30", "MO,TU,WE", "drop"),
    ("Block B \u2014 KM + Signal", "The weakest slot in the week. Plan it as such rather than expecting depth. Third in the losing order.",
     "12:00", "13:30", "MO,WE", "drop"),
    ("Business Admin", "The tail of Block B, so it never takes a fresh hour. Overflow goes to Friday.",
     "13:30", "14:30", "MO,WE", "drop"),
    ("Block B \u2014 KM + Signal", "No admin tail. Tuesday keeps the whole block.",
     "12:00", "14:30", "TU", "drop"),

    # --- pickup week -----------------------------------------------------
    ("Meditation", "Quiet. Intention. Begin. A fifteen-minute window to get ten solid minutes in. Kate does the drop-off this week.",
     "07:45", "08:00", "MO,TU,WE", "pick"),
    ("Block A \u2014 KM + Signal", "Protected. The deepest work of the day. No admin, no other projects, nothing else gets in. Never reallocates.",
     "08:00", "11:30", "MO,TU,WE", "pick"),
    ("Block B \u2014 KM + Signal", "The weakest slot in the week. Plan it as such rather than expecting depth. Third in the losing order.",
     "12:00", "13:00", "MO,WE", "pick"),
    ("Business Admin", "The tail of Block B, so it never takes a fresh hour. Overflow goes to Friday.",
     "13:00", "14:00", "MO,WE", "pick"),
    ("Block B \u2014 KM + Signal", "No admin tail. Tuesday keeps the whole block.",
     "12:00", "14:00", "TU", "pick"),
    ("School Run \u2014 Pickup", "My week. Kate dropped off.",
     "14:00", "14:30", "MO,TU,WE", "pick"),

    # --- lunch -----------------------------------------------------------
    ("Lunch", "Thirty minutes. Caf\u00e9 or at home.",
     "11:30", "12:00", "MO,TU,WE", "weekly"),
    ("Lunch with Kate", "Nanny has Elliot.",
     "11:30", "12:00", "TH", "weekly"),

    # --- Tuesday ---------------------------------------------------------
    ("Swim", "All three of us. The break that makes the long day work.",
     "14:30", "15:00", "TU", "weekly"),
    ("Block C \u2014 KM + Signal", "Anything needing an unbroken run belongs here by design, not by accident. Absorbs what Block A and Block B couldn't.",
     "15:00", "17:30", "TU", "weekly"),

    # --- Thursday --------------------------------------------------------
    ("Meditation", "Quiet. Intention. Begin. A fifteen-minute window to get ten solid minutes in. No school run either end today.",
     "07:45", "08:00", "TH", "weekly"),
    ("Block A \u2014 KM + Signal", "Protected. Nanny 8:00\u20134:00. No admin, no other projects.",
     "08:00", "11:30", "TH", "weekly"),
    ("Block B \u2014 MYLS / Arc / Unaserism / BA",
     "The only block that isn't KM or Signal. Allocated at the start of the week, not on the day. MYLS holds one block a month; The Arc has first claim on the rest through November 2026. The block never goes \u2014 its claimants do.",
     "12:00", "16:00", "TH", "weekly"),

    # --- Friday and Saturday ---------------------------------------------
    ("Life Admin", "Banking, errands, finances, and whatever overflowed from the admin hour on Monday and Wednesday. Not work \u2014 outside the 26.5. Traded hours come back here. No nanny cover, no block.",
     "08:00", "12:00", "FR", "weekly"),
    ("Me Time", "Surf, massage, whatever the week left no room for. Kate takes the same four hours. Traded hours come back here. No cover and it is simply gone.",
     "08:00", "12:00", "SA", "weekly"),
]


def esc(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """iCalendar lines wrap at 75 octets; continuations start with a space."""
    if len(line.encode("utf-8")) <= 75:
        return line
    out, chunk = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        limit = 75 if not out else 74
        if len(chunk) + len(b) > limit:
            out.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += b
    out.append(chunk.decode("utf-8"))
    return "\r\n ".join(out)


def first_on_or_after(anchor, byday):
    wanted = {DAYNUM[d] for d in byday.split(",")}
    for delta in range(7):
        day = anchor + dt.timedelta(days=delta)
        if day.weekday() in wanted:
            return day
    raise AssertionError("unreachable")


def build():
    if ANCHOR_DROP.weekday() != 0 or ANCHOR_PICK.weekday() != 0:
        sys.exit("FAIL: both anchors must be Mondays")
    if (ANCHOR_PICK - ANCHOR_DROP).days != 7:
        sys.exit("FAIL: anchors must be exactly one week apart")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//Axtion Week//Schedule//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:The Axtion Week",
        "X-WR-TIMEZONE:" + TZ,
        "X-WR-CALDESC:Work blocks\\, school runs and the fixed morning. Family time\\, bedtime and Personal Projects are deliberately not here.",
        "BEGIN:VTIMEZONE", "TZID:" + TZ,
        "BEGIN:STANDARD", "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0800", "TZOFFSETTO:+0800", "TZNAME:WITA",
        "END:STANDARD", "END:VTIMEZONE",
    ]

    for i, (summary, desc, start, end, byday, cadence) in enumerate(EVENTS):
        if cadence == "weekly":
            anchor, interval = ANCHOR_DROP, 1
        elif cadence == "drop":
            anchor, interval = ANCHOR_DROP, 2
        elif cadence == "pick":
            anchor, interval = ANCHOR_PICK, 2
        else:
            sys.exit("FAIL: unknown cadence %r" % cadence)

        day = first_on_or_after(anchor, byday)
        lines += [
            "BEGIN:VEVENT",
            "UID:axtion-%02d-%s@axtion-week" % (i, cadence),
            "DTSTAMP:" + stamp,
            "DTSTART;TZID=%s:%sT%s00" % (TZ, day.strftime("%Y%m%d"), start.replace(":", "")),
            "DTEND;TZID=%s:%sT%s00" % (TZ, day.strftime("%Y%m%d"), end.replace(":", "")),
            "RRULE:FREQ=WEEKLY;INTERVAL=%d;BYDAY=%s;WKST=MO;UNTIL=%s" % (interval, byday, UNTIL),
            "SUMMARY:" + esc(summary),
            "DESCRIPTION:" + esc(desc),
            "TRANSP:OPAQUE",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "axtion-week.ics"
    text = build()
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("wrote %s \u2014 %d events, ends %s"
          % (out, text.count("BEGIN:VEVENT"), UNTIL[:8]))
    print("Import into a NEW calendar in Calendar.app, not an existing one.")
