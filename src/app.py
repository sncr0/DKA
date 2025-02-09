import streamlit as st
import pandas as pd
import uuid  # For generating unique patient IDs
from enum import Enum
from datetime import datetime
from patient.patient import Patient, DKASeverity  # Import your Patient class


def write_patient_data():
    st.header("👤 Patient Info", divider='gray')
    patient_data = {
        "Patient Attribute": ["Patient ID", "Name", "Age", "Weight (kg)", "Gender"],
        "Details": [
            st.session_state.patient_id,
            st.session_state.patient.name,
            st.session_state.patient.age,
            st.session_state.patient.weight,
            st.session_state.patient.gender,
        ],
    }
    df = pd.DataFrame(patient_data)
    st.dataframe(df, hide_index=True, )


def write_patient_measurements(measurements):
    st.subheader("🧪 Laboratory Studies")
    units = {
        "Sodium": "mmol/L",
        "Potassium": "mmol/L",
        "Chloride": "mmol/L",
        "Bicarbonate": "mmol/L",
        "pH": "pH scale",
        "Glucose": "mg/dL",
        "Anion Gap": "mmol/L"
    }

    filtered_measurements = {key: value for key, value in measurements.items() if key != "Time"}

    df = pd.DataFrame({
        "Test": filtered_measurements.keys(),
        "Value": filtered_measurements.values(),
        "Units": [units[test] for test in filtered_measurements.keys()]  # Assign units dynamically
    })
    st.dataframe(df, hide_index=True)


def write_patient_recommendations(recommendations):
    st.subheader("💡     Recommendations to the Clinician:")
    print(f"empty recommendations: {recommendations}")
    for recommendation in recommendations:
        st.write(recommendation)


if "history" not in st.session_state:
    st.session_state.history = []

st.title("🩺 DKA Patient Management")


# Generate a unique patient ID
if "patient" not in st.session_state:
    st.subheader("➕ Create a Patient")

    st.session_state.patient_id = str(uuid.uuid4())

    # Basic patient info
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=75)
    weight = st.number_input("Weight (kg)", min_value=0, value=75)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])

    if st.button("Create"):
        if name:
            # Store patient in session state
            st.session_state.patient = Patient(
                patient_id=st.session_state.patient_id, name=name, age=age, weight=weight, gender=gender
            )
            st.success(f"{name} added successfully!")
            st.rerun()
        else:
            st.error("❌ Please enter a name!")


if "patient" in st.session_state:
    write_patient_data()
    if len(st.session_state.history) == 0:
        patient = st.session_state.patient  # Retrieve stored patient
        st.header("🧪 Input Initial Laboratory Results", divider='gray')
        sodium = st.number_input("Sodium (mmol/L)", min_value=100, max_value=170, value=140)
        potassium = st.number_input("Potassium (mmol/L)", min_value=2, max_value=7, value=4)
        chloride = st.number_input("Chloride (mmol/L)", min_value=70, max_value=1300, value=100)
        bicarbonate = st.number_input("Bicarbonate (mmol/L)", min_value=5, max_value=40, value=22)
        pH = st.number_input("pH", min_value=6.5, max_value=7.8, value=7.3)
        glucose = st.number_input("Glucose (mg/dL)", min_value=0, value=100)
        if st.button("Admit"):
            patient.admit(sodium, potassium, chloride, bicarbonate, pH, glucose)
            anion_gap_time, anion_gap = patient.add_anion_gap(sodium, potassium, chloride, bicarbonate)
            if patient.admission_status == DKASeverity.SEVERE:
                st.write(f"❗ {patient.name} admitted: SEVERE")
            elif patient.admission_status == DKASeverity.MILD_MODERATE:
                st.write(f"⚠️ {patient.name} admitted: MODERATE")
            elif patient.admission_status == DKASeverity.MILD:
                st.write(f"✅ {patient.name} admitted: MILD")

            st.session_state.history.append(
                (
                    {
                        "Time": datetime.now().strftime("%H:%M - %m/%d/%Y"),
                        "Sodium": sodium,
                        "Potassium": potassium,
                        "Chloride": chloride,
                        "Bicarbonate": bicarbonate,
                        "pH": pH,
                        "Glucose": glucose,
                        "Anion Gap": anion_gap,
                    },
                    ["Start insulin drip at 0.1 units/kg/hr"]
                )
            )
            st.rerun()

    else:
        patient = st.session_state.patient

        if patient.admission_status:
            print(st.session_state.history)
            for idx, history_item in enumerate(st.session_state.history):
                time = history_item[0]["Time"]
                st.header(f"📊 {idx+1}: Patient Data", divider="gray")
                st.header(f"🕒 {time}")
                print('history_item')
                print(history_item[0])
                print(history_item[1])
                # st.header(f"Results & Recommendations at {time}")
                write_patient_measurements(history_item[0])
                write_patient_recommendations(history_item[1])

            electrolyte_time = st.session_state.history[-1][0]["Time"]
            sodium = st.session_state.history[-1][0]["Sodium"]
            potassium = st.session_state.history[-1][0]["Potassium"]
            chloride = st.session_state.history[-1][0]["Chloride"]
            bicarbonate = st.session_state.history[-1][0]["Bicarbonate"]
            pH = st.session_state.history[-1][0]["pH"]
            glucose = st.session_state.history[-1][0]["Glucose"]
            anion_gap = st.session_state.history[-1][0]["Anion Gap"]

            recommendations = []
            print(recommendations)
            if anion_gap < 12:
                recommendations.append("DKA Resolved")
                # resolution time = start - finish
            elif anion_gap > 12:
                if not patient.insulin_drip:
                    recommendations.append("Start insulin drip at 0.1 units/kg/hr")
                    patient.insulin_drip = True

            # GET ELECTROLYTES
            electrolyte_time, sodium, potassium, chloride, bicarbonate = patient.get_electrolytes()

            # GET CORRECTED SODIUM
            corrected_sodium = patient.get_corrected_sodium(sodium, glucose)

            # CHECK ELECTROLYTES
            if glucose > 250:
                if corrected_sodium > 135:
                    if potassium > 4:
                        # st.write("Run IV fluids 0.45 NS @ 250 cc / hr")
                        recommendations.append("Run IV fluids 0.45 NS @ 250 cc / hr")
                    else:
                        # st.write("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
                        recommendations.append("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
                elif corrected_sodium < 135:
                    if potassium > 4:
                        # st.write("Run IV fluids NS @ 250 cc / hr")
                        recommendations.append("Run IV fluids NS @ 250 cc / hr")
                    else:
                        # st.write("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
                        recommendations.append("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
            elif glucose < 250:
                if corrected_sodium > 135:
                    if potassium > 4:
                        # st.write("Run IV fluids D5 0.45 NS @ 250 cc / hr")
                        recommendations.append("Run IV fluids D5 0.45 NS @ 250 cc / hr")
                    else:
                        # st.write("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
                        recommendations.append("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
                elif corrected_sodium < 135:
                    if potassium > 4:
                        # st.write("Run IV fluids D5 NS @ 250 cc / hr")
                        recommendations.append("Run IV fluids D5 NS @ 250 cc / hr")
                    else:
                        # st.write("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
                        recommendations.append("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
            # st.write("Come back in 1 hour with electrolytes and blood sugar reading")
            recommendations.append("Come back in 1 hour with electrolytes and blood sugar reading")

            st.header("🧪 Input Subsequent Laboratory Results", divider='gray')
            sodium = st.number_input("Sodium (mmol/L)", min_value=100, max_value=170, value=140)
            potassium = st.number_input("Potassium (mmol/L)", min_value=2, max_value=7, value=4)
            chloride = st.number_input("Chloride (mmol/L)", min_value=70, max_value=1300, value=100)
            bicarbonate = st.number_input("Bicarbonate (mmol/L)", min_value=5, max_value=40, value=22)
            pH = st.number_input("pH", min_value=6.5, max_value=7.8, value=7.3)
            glucose = st.number_input("Glucose (mg/dL)", min_value=0, value=100)

            if st.button("Add Laboratory Results"):
                anion_gap_time, anion_gap = patient.add_anion_gap(sodium, potassium, chloride, bicarbonate)
                now = datetime.now().strftime("%H:%M - %m/%d/%Y")
                st.session_state.history.append(
                    (
                        {
                            "Time": now,
                            "Sodium": sodium,
                            "Potassium": potassium,
                            "Chloride": chloride,
                            "Bicarbonate": bicarbonate,
                            "pH": pH,
                            "Glucose": glucose,
                            "Anion Gap": anion_gap,
                        },
                        recommendations
                    )
                )
                recommendations = []
                st.rerun()

    if st.button("View Patient Data"):
        st.write(st.session_state.patient.__dict__)  # Debugging view