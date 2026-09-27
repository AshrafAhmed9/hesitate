"""General patient guidance: the long tail of questions the policy table does
not cover. Indexed in Moss so the agent can answer from it, but it has no
PolicyRecord behind it -- the gate only enforces the handful of facts in
corpus/policy_records.py. Fictional, like the rest of the corpus."""

GUIDE_DOCS = [
    {"id": "patient_guide.txt#water", "text": "You may drink plain water while you fast. Avoid coffee, tea, juice, and chewing gum."},
    {"id": "patient_guide.txt#medication", "text": "Keep taking your usual medications with water unless your doctor has told you otherwise."},
    {"id": "patient_guide.txt#diabetes", "text": "If you take insulin or other diabetes medication, ask your doctor how to adjust it before you fast."},
    {"id": "patient_guide.txt#parking", "text": "Parking is free in the lot behind the building."},
    {"id": "patient_guide.txt#results", "text": "The clinic will call you when your results are ready, and they also appear in the patient portal."},
    {"id": "patient_guide.txt#reschedule", "text": "To reschedule or cancel, call the front desk or use the patient portal."},
    {"id": "patient_guide.txt#children", "text": "Children are welcome to come with you but must stay with an adult in the waiting room."},
]
