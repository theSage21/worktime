WorkTimeThing
=============

Simple task time tracker.

To install::

    python3 -m pip install --user worktimething
    alias wtt='python3 -m worktimething'

`wtt` stores records in plain JSON in the current directory. The file is called `db.json`. I usually have a git repo for my work notes and so I just use wtt from that folder.

To start recording time::

    wtt b 141  # begin work on 141
    wtt b 142  # begin work on 142
    wtt b 143  # begin work on 143

At any time you can see a summary by just typing `wtt` in the terminal::

    wtt  # shows a summary
    141 :   4h 49m
    142 :   2h 55m
    143 : * 1h 20m
    --------------------
    TOTAL :   9h 5m


Sometimes when you want to edit time manually you can do that too::

    wtt a 141 5h3m  # Add time
    wtt s 141 2h30m  # Subtract time


At the end of the day you can just copy paste the times into Jira work logs and have a local record of what you did.
