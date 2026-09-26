# Job lifecycle
One actor consumes start, finish and cancel events, including duplicates and
unexpected events. A job starts at most once. Done and cancelled are terminal;
later events leave their state unchanged. A running job may remain running if
neither finish nor cancel arrives. No automatic completion is promised.
