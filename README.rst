WorkTimeThing
========

Simple task time tracker::

    alias wtt='python3 -m worktimething'
    wtt b 141
    wtt b 142
    wtt e 142
    wtt b 143
    wtt  # shows a summary
    141 :   4h 49m
    142 :   2h 55m
    143 : * 1h 20m
    --------------------
    TOTAL :   9h 5m
    wtt a 141 5h3m  # Add time manually
    wtt s 141 2h30m  # Subtract time manually


Then get summaries in Jira work log format so that you don't have to worry about those any longer.
