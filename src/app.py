import streamlit as st
import pandas as pd
import uuid  # For generating unique patient IDs
from enum import Enum
from datetime import datetime
from patient.patient import Patient, DKASeverity  # Import your Patient class


def write_patient_data():
    st.header("🏥 Patient Info", divider='gray')
    # st.write(f"Patient ID: {st.session_state.patient_id}")
    # st.write(f"Patient Name: {st.session_state.patient.name}")
    # st.write(f"Patient Age: {st.session_state.patient.age}")
    # st.write(f"Patient Weight: {st.session_state.patient.weight} kg")
    # st.write(f"Patient Gender: {st.session_state.patient.gender}")
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

    # Convert dictionary to DataFrame
    df = pd.DataFrame(patient_data)

    # Display DataFrame in Streamlit
    st.dataframe(df, hide_index=True, )
    # st.write(df.to_string(index=False, header=False))
    # patient_data = pd.DataFrame([
    #     ["Patient ID", st.session_state.patient_id],
    #     ["Name", st.session_state.patient.name],
    #     ["Age", st.session_state.patient.age],
    #     ["Weight (kg)", st.session_state.patient.weight],
    #     ["Gender", st.session_state.patient.gender]
    # ])

    # # Display DataFrame without column headers
    # st.dataframe(patient_data.style.hide(axis="columns"))


def write_patient_measurements(measurements):
    st.subheader("🧪 Laboratory Studies")
    # df = pd.DataFrame(measurements)

    # # Display DataFrame in Streamlit
    # st.dataframe(df, hide_index=True)
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

    # Convert measurements into a DataFrame
    df = pd.DataFrame({
        "Test": filtered_measurements.keys(),
        "Value": filtered_measurements.values(),
        "Units": [units[test] for test in filtered_measurements.keys()]  # Assign units dynamically
    })

    # Display DataFrame in Streamlit
    st.dataframe(df, hide_index=True)
    # Convert measurements into a DataFrame
    # df = pd.DataFrame({
    #     "Test": measurements.keys(),
    #     "Value": measurements.values(),
    #     "Units": [units[test] for test in measurements.keys()]  # Match unit to each test
    # })

    # # Display DataFrame in Streamlit
    # st.dataframe(df, hide_index=True)
    # # for key, value in measurements.items():
    # #     st.write(f"{key}: {value}")


def write_patient_recommendations(recommendations):
    st.subheader("💡     Recommendations to the Clinician:")
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

# Only show admission fields if patient is created
# if "patient" in st.session_state and len(st.session_state.history) == 0:
if "patient" in st.session_state:
    write_patient_data()
    if len(st.session_state.history) == 0:
        patient = st.session_state.patient  # Retrieve stored patient
        st.header("🧪 Input Initial Laboratory Results", divider='gray')
        sodium = st.number_input("Sodium (mmol/L)", min_value=100, max_value=170, value=140)
        potassium = st.number_input("Potassium (mmol/L)", min_value=2, max_value=7, value=4)
        chloride = st.number_input("Chloride (mmol/L)", min_value=70, max_value=130, value=100)
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
                    {
                    }
                )
            )
            st.rerun()

# # calculate anion gap
# if "patient" in st.session_state and len(st.session_state.history) > 0:
#     write_patient_data()
    else:

        # write_patient_measurements(st.session_state.history[0])

        patient = st.session_state.patient

        if patient.admission_status:
            print(st.session_state.history)
            for history_item in st.session_state.history:
                time = history_item[0]["Time"]
                st.header(f"📊 Patient Data at {time}", divider="gray")
                print('history_item')
                print(history_item[0])
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
            # GET GLUCOSE
            # # glucose_time, glucose = patient.get_glucose()
            # # st.write(f"Glucose: {glucose} at {glucose_time}")

            # # GET ANION GAP
            # electrolyte_time, sodium, potassium, chloride, bicarbonate = patient.get_electrolytes()
            # anion_gap_time, anion_gap = patient.add_anion_gap(sodium, potassium, chloride, bicarbonate)
            # st.write(f"Anion Gap: {anion_gap} at {anion_gap_time}")

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
            st.write("Come back in 1 hour with electrolytes and blood sugar reading")
            recommendations.append("Come back in 1 hour with electrolytes and blood sugar reading")
            # # measure_glucose()
            # st.write("Come back in 1 hour with blood sugar reading")
            # recommendations.append("Come back in 1 hour with blood sugar reading")

            # glucose = st.number_input("Glucose (mg/dL)", min_value=0, value=100, key=3)
            # if st.button("Measure Glucose", key="{2}"):
            #     glucose_time, glucose = patient.add_glucose(glucose)

            #     # st.write(f"Glucose: {glucose} at {glucose_time}")
            # #     # EMERGENCY TREAMENT CHECK
            # if glucose < 100:
            #     st.write("Give amp of D50 and decrease insulin drip by 50%")
            #     patient.on_D5 = True
            #     recommendations.append("Give amp of D50 and decrease insulin drip by 50%")
            #     # come back in 1 hour with blood sugar reading and goto DP get anion gap
            # elif glucose > 100 and glucose < 250:
            #     if not patient.on_D5:
            #         st.write("Add D5 to current IV fluids")
            #         recommendations.append("Add D5 to current IV fluids")
            #         st.write("Cut insulin by 25%")
            #         recommendations.append("Cut insulin by 25%")
            #     else: 
            #         st.write("Cut Insulin by 50%")
            #         recommendations.append("Cut Insulin by 50%")
            # elif glucose > 250:
            #     if glucose < 0.9 * glucose:
            #         # if no current D5 solution:
            # add D5 to current IV fluids
            # cut insulin by 25%
        # if current D5 solution:
            # cut insulin by 50%
            #         # cut insulin by 25%
            #     else:
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

            st.header("🧪 Input Subsequent Laboratory Results", divider='gray')
            sodium = st.number_input("Sodium (mmol/L)", min_value=100, max_value=170, value=140)
            potassium = st.number_input("Potassium (mmol/L)", min_value=2, max_value=7, value=4)
            chloride = st.number_input("Chloride (mmol/L)", min_value=70, max_value=130, value=100)
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
                st.rerun()

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
        

