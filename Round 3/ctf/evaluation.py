"""
Evaluation endpoints for the 5 CTF challenges.
These mirror the FastAPI evaluation_api — notebooks POST files here and
receive a flag on success.

Endpoints:
  POST /evaluate/challenge-1   → tampered_data.csv
  POST /evaluate/challenge-2   → tampered_data.csv
  POST /evaluate/challenge-3   → fixed_model.pkl
  POST /evaluate/challenge-4   → predictions.csv
  POST /evaluate/challenge-5   → model.pkl
"""
import io
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from django.contrib.auth import get_user_model

from .models import Challenge, Flag, UserFlag

User = get_user_model()

# ── Helpers ──────────────────────────────────────────────────────

FEATURE_COLS = ["Night_Activity", "Trust_Index", "Contribution", "Conflict_Score"]
EXPECTED_COLS = ["ID"] + FEATURE_COLS + ["Label"]
AUC_THRESHOLD = 0.85


def _flag_for_challenge(order, user=None):
    """Return the flag string for a given challenge order.
    If *user* is provided, return that user's unique per-user flag.
    Falls back to the global Flag if no per-user flag exists."""
    if user is not None:
        uf = UserFlag.objects.filter(user=user, challenge__order=order).first()
        if uf:
            return uf.flag_value
    # Fallback to global flag
    flag = Flag.objects.filter(challenge__order=order, flag_order=1).first()
    return flag.flag_content if flag else None


def _resolve_user(request):
    """Identify the submitting user.

    1. If the request is from an authenticated session → use request.user.
    2. Otherwise look for a 'username' field in POST data (sent by notebooks).
    3. Returns None if no user can be identified.
    """
    if request.user.is_authenticated:
        return request.user
    username = request.POST.get("username")
    if username:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
    return None


def _dataset_path(local_name):
    """Absolute path to a challenge file."""
    return settings.CHALLENGE_FILES_DIR / local_name


def _success(flag, message, **extra):
    return JsonResponse({"result": "success", "flag": flag, "message": message, **extra})


def _failure(message, **extra):
    return JsonResponse({"result": "failure", "flag": None, "message": message, **extra})


def _error(message, status=400):
    return JsonResponse({"result": "error", "detail": message}, status=status)


# ── Challenge 1 — Data Poisoning ─────────────────────────────────

@csrf_exempt
@require_POST
def evaluate_challenge_1(request):
    """
    Accepts a tampered CSV. Trains LogisticRegression on submitted data.
    If last row (ID=10) predicted as Citizen (0) → flag.
    """
    f = request.FILES.get("file")
    if not f or not f.name.endswith(".csv"):
        return _error("Please upload a CSV file.")

    try:
        df = pd.read_csv(io.BytesIO(f.read()))
    except Exception as e:
        return _error(f"Could not parse CSV: {e}")

    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        return _error(f"CSV is missing required columns: {missing}")

    from sklearn.linear_model import LogisticRegression

    X = df[FEATURE_COLS].values
    y = df["Label"].values

    try:
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
    except Exception as e:
        return _error(f"Model training failed: {e}", status=500)

    last_row = df[FEATURE_COLS].iloc[[-1]].values
    prediction = int(model.predict(last_row)[0])
    proba = model.predict_proba(last_row)[0]

    confidence = {
        "citizen_confidence": round(float(proba[0]), 4),
        "thief_confidence": round(float(proba[1]), 4),
    }

    user = _resolve_user(request)

    if prediction == 0:
        return _success(
            _flag_for_challenge(1, user=user),
            "The Gatekeeper has been fooled! The thief is classified as a Citizen.",
            **confidence,
        )
    else:
        return _failure(
            "The thief is still correctly identified. The Gatekeeper was not fooled.",
            **confidence,
        )


# ── Challenge 2 — Constrained Data Poisoning ─────────────────────

@csrf_exempt
@require_POST
def evaluate_challenge_2(request):
    """
    Same goal as Challenge 1, but last row (ID=10) and Label column must
    remain unchanged from the original dataset.
    """
    f = request.FILES.get("file")
    if not f or not f.name.endswith(".csv"):
        return _error("Please upload a CSV file.")

    try:
        submitted = pd.read_csv(io.BytesIO(f.read()))
    except Exception as e:
        return _error(f"Could not parse CSV: {e}")

    missing = [c for c in EXPECTED_COLS if c not in submitted.columns]
    if missing:
        return _error(f"CSV is missing required columns: {missing}")

    # Load original
    original_path = _dataset_path("challenge2_gatekeeper_dataset.csv")
    try:
        original = pd.read_csv(original_path)
    except FileNotFoundError:
        return _error("Reference dataset not found on the server. Contact the organiser.", status=500)

    if len(submitted) != len(original):
        return _failure("Row count does not match the original dataset.")

    # Guard: last row must be unchanged
    last_original = original.iloc[-1][FEATURE_COLS + ["Label"]].reset_index(drop=True)
    last_submitted = submitted.iloc[-1][FEATURE_COLS + ["Label"]].reset_index(drop=True)
    if not last_original.equals(last_submitted):
        return _failure(
            "Tampering detected! The last row (ID = 10) has been modified. "
            "This row is protected and must remain unchanged. Submission rejected.",
            tampering_detected=True,
            tampered_location="last row (ID = 10)",
        )

    # Guard: Label column must be identical
    if not original["Label"].reset_index(drop=True).equals(
        submitted["Label"].reset_index(drop=True)
    ):
        return _failure(
            "Tampering detected! The Label column has been modified. "
            "Label values are protected and must remain unchanged. Submission rejected.",
            tampering_detected=True,
            tampered_location="Label column",
        )

    from sklearn.linear_model import LogisticRegression

    X = submitted[FEATURE_COLS].values
    y = submitted["Label"].values

    try:
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
    except Exception as e:
        return _error(f"Model training failed: {e}", status=500)

    last_row = submitted[FEATURE_COLS].iloc[[-1]].values
    prediction = int(model.predict(last_row)[0])
    proba = model.predict_proba(last_row)[0]

    confidence = {
        "citizen_confidence": round(float(proba[0]), 4),
        "thief_confidence": round(float(proba[1]), 4),
    }

    user = _resolve_user(request)

    if prediction == 0:
        return _success(
            _flag_for_challenge(2, user=user),
            "The Gatekeeper was fooled again! The thief slipped past undetected.",
            **confidence,
        )
    else:
        return _failure(
            "The thief is still correctly identified. The Gatekeeper held its ground.",
            **confidence,
        )


# ── Challenge 3 — Fix the Corrupted Model ────────────────────────

@csrf_exempt
@require_POST
def evaluate_challenge_3(request):
    """
    Accepts a .pkl model file. Loads it, predicts on the gatekeeper dataset.
    Must achieve exactly 100% accuracy.
    """
    f = request.FILES.get("file")
    if not f or not f.name.endswith(".pkl"):
        return _error("Please upload a .pkl model file.")

    import joblib

    try:
        submitted_model = joblib.load(io.BytesIO(f.read()))
    except Exception as e:
        return _error(f"Could not load model: {e}")

    if not hasattr(submitted_model, "predict"):
        return _error("Uploaded file does not appear to be a valid scikit-learn model.")

    dataset_path = _dataset_path("challenge3_gatekeeper_dataset.csv")
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        return _error("Reference dataset not found on the server. Contact the organiser.", status=500)

    X = df[FEATURE_COLS].values
    y = df["Label"].values

    try:
        preds = submitted_model.predict(X)
    except Exception as e:
        return _error(f"Model prediction failed: {e}")

    correct = int((preds == y).sum())
    total = len(y)
    accuracy = round(correct / total, 4)

    user = _resolve_user(request)

    if accuracy == 1.0:
        return _success(
            _flag_for_challenge(3, user=user),
            "The Gatekeeper is fully restored! Every single record is classified correctly.",
            accuracy=accuracy,
        )
    else:
        return _failure(
            f"Not quite. The model correctly classified {correct}/{total} records "
            f"— accuracy: {accuracy * 100:.1f}%. You need 100%.",
            accuracy=accuracy,
        )


# ── Challenge 4 — Model Evaluation (ROC-AUC >= 0.85) ──────────────

@csrf_exempt
@require_POST
def evaluate_challenge_4(request):
    """
    Accepts predictions.csv (column: prediction).
    Reproduces y_test from bank.csv using the exact same preprocessing
    pipeline (random_state=42), then computes ROC-AUC.
    """
    f = request.FILES.get("file")
    if not f or not f.name.endswith(".csv"):
        return _error("Please upload a CSV file.")

    try:
        pred_df = pd.read_csv(io.BytesIO(f.read()))
    except Exception as e:
        return _error(f"Could not parse CSV: {e}")

    if "prediction" not in pred_df.columns:
        return _error("CSV must have a column named 'prediction'.")

    y_pred = pred_df["prediction"].values

    if not all((y_pred >= 0) & (y_pred <= 1)):
        return _error("All prediction values must be probabilities in the range [0, 1].")

    # Reproduce y_test from the bank marketing dataset
    from sklearn.preprocessing import LabelEncoder, StandardScaler
    from sklearn.model_selection import train_test_split

    dataset_path = _dataset_path("challenge4_bank.csv")
    try:
        df_bank = pd.read_csv(dataset_path, sep=";")
    except FileNotFoundError:
        return _error("Reference dataset not found on the server. Contact the organiser.", status=500)

    df_work = df_bank.copy()
    df_work["y"] = (df_work["y"] == "yes").astype(int)

    cat_cols = df_work.select_dtypes(include="object").columns.tolist()
    le = LabelEncoder()
    for col in cat_cols:
        df_work[col] = le.fit_transform(df_work[col])

    df_yes = df_work[df_work["y"] == 1]
    df_no = df_work[df_work["y"] == 0].sample(len(df_yes), random_state=42)
    df_bal = pd.concat([df_yes, df_no]).sample(frac=1, random_state=42).reset_index(drop=True)

    X = df_bal.drop("y", axis=1).values.astype(float)
    y_true = df_bal["y"].values.astype(int)

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    _, _, _, y_test = train_test_split(
        X, y_true, test_size=0.20, random_state=42, stratify=y_true
    )

    if len(y_pred) != len(y_test):
        return _failure(
            f"Row count mismatch: submitted {len(y_pred)} predictions "
            f"but test set has {len(y_test)} samples.",
        )

    # Compute AUC (trapezoidal — descending sort)
    def compute_auc(y_t, y_s):
        y_t = np.array(y_t, dtype=float)
        y_s = np.array(y_s, dtype=float)
        order = np.argsort(y_s)[::-1]
        y_t_sorted = y_t[order]
        P = int(y_t.sum())
        N = len(y_t) - P
        tpr, fpr = [0.0], [0.0]
        tp = fp = 0
        for label in y_t_sorted:
            if label == 1:
                tp += 1
            else:
                fp += 1
            tpr.append(tp / P)
            fpr.append(fp / N)
        return round(sum(
            (fpr[i] - fpr[i - 1]) * (tpr[i] + tpr[i - 1]) / 2
            for i in range(1, len(fpr))
        ), 4)

    y_pred_class = (y_pred >= 0.5).astype(int)
    accuracy = round(float((y_pred_class == y_test).mean()), 4)
    auc = compute_auc(y_test, y_pred)

    user = _resolve_user(request)

    if auc >= AUC_THRESHOLD:
        return _success(
            _flag_for_challenge(4, user=user),
            "The Sentinel is awake! Your model generalises well on the test set.",
            roc_auc=auc,
            accuracy=accuracy,
        )
    else:
        return _failure(
            f"The Sentinel is still struggling. "
            f"ROC-AUC: {auc:.4f} (need >= {AUC_THRESHOLD}). "
            f"Accuracy: {accuracy:.4f}. Keep debugging the pipeline.",
            roc_auc=auc,
            accuracy=accuracy,
        )


# ── Challenge 5 — Recover Model Weights ──────────────────────────

@csrf_exempt
@require_POST
def evaluate_challenge_5(request):
    """
    Accepts a .pkl LinearRegression model.
    Must achieve R²=1.0, MSE=0.0, max_abs_error=0.0 on dataset.csv.
    """
    f = request.FILES.get("file")
    if not f or not f.name.endswith(".pkl"):
        return _error("Please upload a .pkl model file.")

    import joblib

    try:
        submitted_model = joblib.load(io.BytesIO(f.read()))
    except Exception as e:
        return _error(f"Could not load model: {e}")

    if not hasattr(submitted_model, "predict"):
        return _error("Uploaded file does not appear to be a valid scikit-learn model (missing predict method).")

    dataset_path = _dataset_path("challenge5_dataset.csv")
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        return _error("Reference dataset not found on the server. Contact the organiser.", status=500)

    required = ["X1", "X2", "y"]
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        return _error(f"Reference dataset is missing columns: {missing_cols}", status=500)

    X = df[["X1", "X2"]].values.astype(float)
    y_true = df["y"].values.astype(float)

    try:
        y_pred = submitted_model.predict(X).astype(float)
    except Exception as e:
        return _error(f"Model prediction failed: {e}")

    residuals = y_true - y_pred
    max_abs_error = float(np.max(np.abs(residuals)))
    mse = float(np.mean(residuals ** 2))

    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else (1.0 if ss_res == 0 else 0.0)

    weights_info = {}
    if hasattr(submitted_model, "coef_"):
        weights_info["coefficients"] = submitted_model.coef_.tolist()
    if hasattr(submitted_model, "intercept_"):
        weights_info["intercept"] = float(submitted_model.intercept_)

    is_perfect = (r2 == 1.0) and (max_abs_error == 0.0) and (mse == 0.0)

    user = _resolve_user(request)

    if is_perfect:
        return _success(
            _flag_for_challenge(5, user=user),
            "Perfect fit! You have recovered the exact weights of the original model.",
            r2_score=r2,
            mse=mse,
            max_abs_error=max_abs_error,
            **weights_info,
        )
    else:
        return _failure(
            f"Not a perfect fit. "
            f"R² = {r2} (need exactly 1.0). "
            f"Max absolute error = {max_abs_error} (need exactly 0). "
            f"MSE = {mse} (need exactly 0). "
            f"Keep analysing the data.",
            r2_score=r2,
            mse=mse,
            max_abs_error=max_abs_error,
            **weights_info,
        )
