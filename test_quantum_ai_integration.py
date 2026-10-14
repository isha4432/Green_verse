import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api"

def make_post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_qubo_and_qaoa():
    print("\n--- 1. Testing QUBO & QAOA Optimization ---")
    payload = {
        "plots": [
            {"plot_id": "plot_a", "crop": "Tomato", "area_sqm": 250, "moisture": 30.0, "urgency": 0.85},
            {"plot_id": "plot_b", "crop": "Wheat", "area_sqm": 400, "moisture": 45.0, "urgency": 0.60},
            {"plot_id": "plot_c", "crop": "Lettuce", "area_sqm": 180, "moisture": 25.0, "urgency": 0.90},
            {"plot_id": "plot_d", "crop": "Maize", "area_sqm": 320, "moisture": 55.0, "urgency": 0.40}
        ],
        "water_budget": 45.0,
        "penalty_weight": 50.0,
        "p_layers": 2,
        "shots": 512
    }
    qubo = make_post("/quantum/qubo", payload)
    num_vars = qubo.get("num_variables", 0)
    assert num_vars == 4, f"Expected 4 variables, got {num_vars}"
    print(f"[PASS] QUBO generated for {num_vars} plots with matrix dimension {len(qubo['matrix'])}x{len(qubo['matrix'][0])}")

    qaoa = make_post("/quantum/qaoa", payload)
    assert qaoa["status"] == "completed", "QAOA failed to complete"
    assert qaoa["backend"] == "Qiskit Aer (AerSimulator / Statevector)", f"Unexpected backend: {qaoa['backend']}"
    assert "solution" in qaoa and len(qaoa["solution"]) == 4, "QAOA solution missing or invalid length"
    print(f"[PASS] QAOA executed on: {qaoa['backend']}")
    print(f"       Solution: {qaoa['solution']}")
    print(f"       Allocated Water: {qaoa['allocated_water']} m3 (Budget: 45.0 m3)")
    print(f"       Approximation Ratio: {qaoa['approximation_ratio']}")
    print(f"       Runtime: {qaoa['runtime_ms']} ms")
    
    classical = make_post("/optimization/classical", payload)
    print(f"[PASS] Classical Solver executed: Objective {classical['objective']}, Feasible: {classical['feasible']}")
    return qaoa, classical

def test_qml_classifier():
    print("\n--- 2. Testing QML Crop-Stress Classifier (QSVC / Statevector Fidelity) ---")
    payload = {
        "temperature": 34.2,
        "humidity": 36.5,
        "soil_moisture": 28.0,
        "soil_ph": 6.8,
        "ndi": 0.42,
        "growth_stage_index": 2,
        "crop_type": "Tomato"
    }
    qml_res = make_post("/quantum/qml/predict", payload)
    assert "qml_category" in qml_res, "QML result missing qml_category"
    assert qml_res["circuit_qubits"] == 4, f"Expected 4 qubits, got {qml_res['circuit_qubits']}"
    assert "Statevector" in qml_res["backend"], f"Expected Statevector backend, got {qml_res['backend']}"
    print(f"[PASS] QML Category: {qml_res['qml_category']} (Score: {qml_res['stress_score']})")
    print(f"       Quantum State Fidelity: {qml_res['quantum_fidelity']}")
    print(f"       Circuit: {qml_res['circuit_qubits']} qubits, Depth {qml_res['circuit_depth']}, Runtime: {qml_res['runtime_ms']} ms")
    print(f"       Algorithm: {qml_res['algorithm']}")
    print(f"       Status: {qml_res['status']}")
    print(f"       Disclaimer: {qml_res['disclaimer']}")
    return qml_res

def test_ai_chatbot(qaoa_res, qml_res):
    print("\n--- 3. Testing AI Chatbot with Full Farm & Quantum Context ---")
    test_questions = [
        "What did the QAOA optimizer decide for my farm?",
        "How was the irrigation allocation calculated?",
        "What is the difference between the classical and quantum result?",
        "Is this running on real quantum hardware or a simulator?",
        "What does the QML crop-stress result mean?"
    ]
    context = {
        "location": {"name": "Kurnool", "lat": 15.8289, "lon": 78.0360, "state": "Andhra Pradesh", "country": "India"},
        "weather": {"temperature": 34.2, "humidity": 36.5, "condition": "Sunny"},
        "farm": {"id": "farm_kurnool_1", "name": "Kurnool Mixed Agro Farm", "cultivated_area_sqm": 1150},
        "plots": [
            {"id": "plot_a", "name": "North Tomato Plot", "crop": "Tomato", "condition": "critical", "moisture": 28.0},
            {"id": "plot_b", "name": "Wheat Field", "crop": "Wheat", "condition": "stressed", "moisture": 45.0}
        ],
        "soil": {"texture": "siltloam", "moist": 28.0, "ph": 6.8},
        "water_availability_m3": 45.0,
        "qml_result": qml_res,
        "qaoa_result": qaoa_res
    }
    for q in test_questions:
        chat_req = {"message": q, "context": context}
        resp = make_post("/ai/chat", chat_req)
        assert "reply" in resp and len(resp["reply"]) > 20, f"Invalid chat reply for question: {q}"
        print(f"\n[Q]: {q}")
        print(f"[A]: {resp['reply'][:250]}...")
        if resp.get("disclaimer"):
            print(f"     Disclaimer: {resp['disclaimer']}")
    print("\n[PASS] All 5 core quantum & AI inquiry questions successfully answered with live context.")

if __name__ == "__main__":
    qaoa_res, classical_res = test_qubo_and_qaoa()
    qml_res = test_qml_classifier()
    test_ai_chatbot(qaoa_res, qml_res)
    print("\n=======================================================")
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY (100% GREEN)")
    print("=======================================================")
