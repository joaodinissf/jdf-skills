---- MODULE claim ----
EXTENDS Naturals, FiniteSets

CONSTANTS Workers

VARIABLES status, pc, sends
vars == <<status, pc, sends>>

Init == /\ status = "pending"
        /\ pc = [w \in Workers |-> "idle"]
        /\ sends = 0

\* claim.py:9 — read the status
Read(w) == /\ pc[w] = "idle"
           /\ status = "pending"
           /\ pc' = [pc EXCEPT ![w] = "read"]
           /\ UNCHANGED <<status, sends>>

\* claim.py:11-13 — claim and send
Claim(w) == /\ pc[w] = "reading"
            /\ status' = "claimed"
            /\ sends' = sends + 1
            /\ pc' = [pc EXCEPT ![w] = "done"]

Next == \E w \in Workers : Read(w) \/ Claim(w)

Spec == Init /\ [][Next]_vars

AtMostOneSend == sends <= 1
====
