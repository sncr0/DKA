import streamlit as st
import pandas as pd
import uuid  # For generating unique patient IDs
from enum import Enum
from datetime import datetime
from patient.patient import Patient, DKASeverity  # Import your Patient class


def write_patient_data():
    st.subheader("🏥 Patient Info:")
    st.write(f"Patient ID: {st.session_state.patient_id}")
    st.write(f"Patient Name: {st.session_state.patient.name}")
    st.write(f"Patient Age: {st.session_state.patient.age}")
    st.write(f"Patient Weight: {st.session_state.patient.weight} kg")
    st.write(f"Patient Gender: {st.session_state.patient.gender}")


def write_patient_measurements(measurement_dict):
    st.subheader("📊 Patient Measurements:")
    for key, value in measurement_dict.items():
        st.write(f"{key}: {value}")


if "history" not in st.session_state:
    st.session_state.history = []

st.title("🩺 DKA Patient Management")


# Generate a unique patient ID
if "patient" not in st.session_state:
    st.subheader("➕ Create a Patient")

    st.session_state.patient_id = str(uuid.uuid4())

    # Basic patient info
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0, max_value=120, value=1)
    weight = st.number_input("Weight (kg)", min_value=0, value=1)
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

# Only show admission fields if patient is created
# if "patient" in st.session_state and len(st.session_state.history) == 0:
if "patient" in st.session_state and len(st.session_state.history) == 0:
    write_patient_data()
    patient = st.session_state.patient  # Retrieve stored patient

    sodium = st.number_input("Sodium (mmol/L)", min_value=100, max_value=170, value=140)
    potassium = st.number_input("Potassium (mmol/L)", min_value=2, max_value=7, value=4)
    chloride = st.number_input("Chloride (mmol/L)", min_value=70, max_value=130, value=100)
    bicarbonate = st.number_input("Bicarbonate (mmol/L)", min_value=5, max_value=40, value=22)
    pH = st.number_input("pH", min_value=6.5, max_value=7.8, value=7.3)
    glucose = st.number_input("Glucose (mg/dL)", min_value=0, value=100)
    if st.button("Admit"):
        patient.admit(sodium, potassium, chloride, bicarbonate, pH, glucose)
        if patient.admission_status == DKASeverity.SEVERE:
            st.write(f"❗ {patient.name} admitted: SEVERE")
        elif patient.admission_status == DKASeverity.MILD_MODERATE:
            st.write(f"⚠️ {patient.name} admitted: MODERATE")
        elif patient.admission_status == DKASeverity.MILD:
            st.write(f"✅ {patient.name} admitted: MILD")

        st.session_state.history.append(
            (
                {
                    "Time": datetime.now(),
                    "Sodium": sodium,
                    "Potassium": potassium,
                    "Chloride": chloride,
                    "Bicarbonate": bicarbonate,
                    "pH": pH,
                    "Glucose": glucose,
                },
                {
                }
            )
        )
        print(len(st.session_state.history))
        st.rerun()

# calculate anion gap
if "patient" in st.session_state and len(st.session_state.history) > 0:
    write_patient_data()
    write_patient_measurements(st.session_state.history[0])

    patient = st.session_state.patient

    if patient.admission_status:
        st.header("Patient Data")

        # GET GLUCOSE
        glucose_time, glucose = patient.get_glucose()
        st.write(f"Glucose: {glucose} at {glucose_time}")

        # GET ANION GAP
        anion_gap_time, anion_gap = patient.add_anion_gap(sodium, potassium, chloride, bicarbonate)
        st.write(f"Anion Gap: {anion_gap} at {anion_gap_time}")


        st.header("Recommendations")
        recommendations = []
        if anion_gap < 12:
            st.write("DKA Resolved")
            recommendations.append("DKA Resolved")
            # resolution time = start - finish
        elif anion_gap > 12:
            if not patient.insulin_drip:
                st.write("Start insulin drip at 0.1 units/kg/hr")
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
                    st.write("Run IV fluids 0.45 NS @ 250 cc / hr")
                    recommendations.append("Run IV fluids 0.45 NS @ 250 cc / hr")
                else:
                    st.write("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
                    recommendations.append("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
            elif corrected_sodium < 135:
                if potassium > 4:
                    st.write("Run IV fluids NS @ 250 cc / hr")
                    recommendations.append("Run IV fluids NS @ 250 cc / hr")
                else:
                    st.write("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
                    recommendations.append("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
        elif glucose < 250:
            if corrected_sodium > 135:
                if potassium > 4:
                    st.write("Run IV fluids D5 0.45 NS @ 250 cc / hr")
                    recommendations.append("Run IV fluids D5 0.45 NS @ 250 cc / hr")
                else:
                    st.write("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
                    recommendations.append("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
            elif corrected_sodium < 135:
                if potassium > 4:
                    st.write("Run IV fluids D5 NS @ 250 cc / hr")
                    recommendations.append("Run IV fluids D5 NS @ 250 cc / hr")
                else:
                    st.write("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
                    recommendations.append("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")

        # measure_glucose()
        st.write("Come back in 1 hour with blood sugar reading")
        recommendations.append("Come back in 1 hour with blood sugar reading")

        glucose = st.number_input("Glucose (mg/dL)", min_value=0, value=100, key=3)
        if st.button("Measure Glucose", key="{2}"):
            glucose_time, glucose = patient.add_glucose(glucose)

        st.write(f"Glucose: {glucose} at {glucose_time}")
        # EMERGENCY TREAMENT CHECK
        # if glucose < 100: HAPPY PATH
            # Give amp of D50 and decrease insulin drip by 50%
            # come back in 1 hour with blood sugar reading and goto DP get anion gap
        # if glucose > 100 and < 250:
            # if no current D5 solution:
                # add D5 to current IV fluids
                # cut insulin by 25%
            # if current D5 solution:
                # cut insulin by 50%
        # if glucose > 250:
            # did glucose drop enough?
            # if glucose dropped by <10%:
                # increase insulin drip by 25%
                # measure glucose()
            # if glucose dropped by >10%:
                # continue
        
        # measure sodium, potassium, chloride, bicarb, gluc
        # goto anion gap
        
    if st.button("View Patient Data"):
        st.write(st.session_state.patient.__dict__)  # Debugging view

# calculate anion gap

# sodium + K - Cl - Bicarb
# print anion gap


# DKA sev
# ph < 7 : severe
# 7 < ph < 7.24 : moderate
# 7.24 < ph : mild
# print dka sev



# decision point
    # calculate_anion_gap()
    # set_anion_gap()

    # if anion gap < 12:
        # dka resolved
        # resolution time = start - finish
    # if anion gap > 12:
        # if no insulin drip:
            # start insulin drip at 0.1 units/kg/hr
    
    # show anion gap and datetime
    # show glucose

    # CHECK ELECTROLYTES
    # if glucose > 250 
        # if corrective sodium > 135 (sodium + 0.4 * gluc - 5.5)
            # if K > 4:
                # run IV fluids 0.45 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr
        # if corrective sodium < 135
            # if K > 4:
                # run IV fluids NS @ 250 cc / hr
            # K < 4:
                # run IV fluids NS w 20 meq KCl @ 250 cc / hr
    # glucose < 250
        # if corrective sodium > 135 (sodium + 0.4 * gluc - 5.5)
            # if K > 4:
                # run IV fluids D5 0.45 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr
        # if corrective sodium < 135
            # if K > 4:
                # run IV fluids D5 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr
    
    # come back in 1 hour with blood sugar reading
    # measure_glucose()

    # EMERGENCY TREAMENT CHECK
    # if glucose < 100: HAPPY PATH
        # Give amp of D50 and decrease insulin drip by 50%
        # come back in 1 hour with blood sugar reading and goto DP get anion gap
    # if glucose > 100 and < 250:
        # if no current D5 solution:
            # add D5 to current IV fluids
            # cut insulin by 25%
        # if current D5 solution:
            # cut insulin by 50%
    # if glucose > 250:
        # did glucose drop enough?
        # if glucose dropped by <10%:
            # increase insulin drip by 25%
            # measure glucose()
        # if glucose dropped by >10%:
            # continue
    
    # measure sodium, potassium, chloride, bicarb, gluc
    # goto anion gap
        







# calculate anion gap

# sodium + K - Cl - Bicarb
# print anion gap

# DKA sev
# ph < 7 : severe
# 7 < ph < 7.24 : moderate
# 7.24 < ph : mild
# print dka sev

# decision point
    # calculate_anion_gap()
    # set_anion_gap()

    # if anion gap < 12:
        # dka resolved
        # resolution time = start - finish
    # if anion gap > 12:
        # if no insulin drip:
            # start insulin drip at 0.1 units/kg/hr
    
    # show anion gap and datetime
    # show glucose
    # if glucose > 250 
        # if corrective sodium > 135 (sodium + 0.4 * gluc - 5.5)
            # if K > 4:
                # run IV fluids 0.45 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr
        # if corrective sodium < 135
            # if K > 4:
                # run IV fluids NS @ 250 cc / hr
            # K < 4:
                # run IV fluids NS w 20 meq KCl @ 250 cc / hr
    # glucose < 250
        # if corrective sodium > 135 (sodium + 0.4 * gluc - 5.5)
            # if K > 4:
                # run IV fluids D5 0.45 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr
        # if corrective sodium < 135
            # if K > 4:
                # run IV fluids D5 NS @ 250 cc / hr
            # K < 4:
                # run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr
    
    # come back in 1 hour with blood sugar reading
    # measure_glucose()

    # EMERGENCY TREAMENT CHECK
    # come back in 1 hour with blood sugar reading and goto DP get anion gap
    # if glucose < 100:
        # Give amp of D50 and decrease insulin drip by 50%
        # come back in 1 hour with blood sugar reading and goto DP get anion gap
    # if glucose > 100 and < 250:
        # if no current D5 solution:
            # add D5 to current IV fluids
            # cut insulin by 25%
        # if current D5 solution:
            # cut insulin by 50%
    # if glucose > 250:
        # did glucose drop enough?
        # if glucose dropped by >10%:
            # CHECK FOR EMERGENCY ONCE MORE
            # measure glucose()
        # if glucose dropped by <10%:
            # continue
    
    # measure sodium, potassium, chloride, bicarb, gluc
    # goto anion gap
        

