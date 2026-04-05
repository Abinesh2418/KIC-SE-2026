"""Canonical challenge metadata — seeded into the DB on first run."""

CATALOG = [
    {
        "order": 1,
        "title": "Challenge-1: Data Poisoning",
        "description": "Data poisoning challenge from the Yugam ML CTF repository. Manipulate the training data to change the model's prediction for a specific sample.",
        "category": "Data Poisoning",
        "difficulty": "Easy",
        "total_points": 2,
        "flag_points_max": 1,
        "explanation_points_max": 1,
        "resources": [
            {"display_name": "Gatekeeper_Challenge.ipynb", "local_name": "challenge1_Gatekeeper_Challenge.ipynb"},
            {"display_name": "gatekeeper_dataset.csv", "local_name": "challenge1_gatekeeper_dataset.csv"},
        ],
        "flags": [
            {"flag_content": "MLFEST{p01s0n_th3_w3ll_g4t3_f4lls}", "flag_order": 1, "points_value": 2, "description": "Final verification flag"},
        ],
    },
    {
        "order": 2,
        "title": "Challenge-2: Constrained Poisoning",
        "description": "Constrained data poisoning challenge from the Yugam ML CTF repository. Same goal as Challenge 1 but with constraints on how much you can modify.",
        "category": "Data Poisoning",
        "difficulty": "Medium",
        "total_points": 3,
        "flag_points_max": 1,
        "explanation_points_max": 2,
        "resources": [
            {"display_name": "Gatekeeper_Challenge-2.ipynb", "local_name": "challenge2_Gatekeeper_Challenge-2.ipynb"},
            {"display_name": "gatekeeper_dataset.csv", "local_name": "challenge2_gatekeeper_dataset.csv"},
        ],
        "flags": [
            {"flag_content": "MLFEST{sh4d0ws_sl1p_p4st_th3_l0ck3d_g4t3}", "flag_order": 1, "points_value": 3, "description": "Final verification flag"},
        ],
    },
    {
        "order": 3,
        "title": "Challenge-3: Model Repair",
        "description": "Model repair challenge from the Yugam ML CTF repository. A tampered model is provided — fix it to achieve 100%% accuracy on the test set.",
        "category": "Model Security",
        "difficulty": "Hard",
        "total_points": 4,
        "flag_points_max": 2,
        "explanation_points_max": 2,
        "resources": [
            {"display_name": "Gatkeepr_Challenge-3.ipynb", "local_name": "challenge3_Gatkeepr_Challenge-3.ipynb"},
            {"display_name": "gatekeeper_dataset.csv", "local_name": "challenge3_gatekeeper_dataset.csv"},
            {"display_name": "tampered_model.pkl", "local_name": "challenge3_tampered_model.pkl"},
        ],
        "flags": [
            {"flag_content": "MLFEST{r3wr1t3_th3_m1nd_r3cl41m_th3_g4t3}", "flag_order": 1, "points_value": 4, "description": "Final verification flag"},
        ],
    },
    {
        "order": 4,
        "title": "Challenge-4: Model Evaluation",
        "description": "Evaluation challenge from the Yugam ML CTF repository. A model that refuses to learn — make it predict with ROC-AUC >= 0.85.",
        "category": "Model Evaluation",
        "difficulty": "Expert",
        "total_points": 3,
        "flag_points_max": 2,
        "explanation_points_max": 1,
        "resources": [
            {"display_name": "The_Model_That_Refused_To_Learn.ipynb", "local_name": "challenge4_The_Model_That_Refused_To_Learn.ipynb"},
            {"display_name": "bank.csv", "local_name": "challenge4_bank.csv"},
        ],
        "flags": [
            {"flag_content": "MLFEST{4w4k3n_th3_sl33p1ng_s3nt1n3l}", "flag_order": 1, "points_value": 3, "description": "Final verification flag"},
        ],
    },
    {
        "order": 5,
        "title": "Challenge-5: Model Recovery",
        "description": "Model recovery challenge — rebuild the exact model from data alone. Recover the original linear regression weights.",
        "category": "Model Analysis",
        "difficulty": "Medium",
        "total_points": 5,
        "flag_points_max": 2,
        "explanation_points_max": 3,
        "resources": [
            {"display_name": "The_Weight_of_Truth.ipynb", "local_name": "challenge5_The_Weight_of_Truth.ipynb"},
            {"display_name": "dataset.csv", "local_name": "challenge5_dataset.csv"},
        ],
        "flags": [
            {"flag_content": "MLFEST{w31ght_0f_truth_r3v34l3d}", "flag_order": 1, "points_value": 5, "description": "Final verification flag"},
        ],
    },
]


def get_catalog_by_order():
    return {item["order"]: item for item in CATALOG}
