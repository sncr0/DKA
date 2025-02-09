import streamlit as st
import pandas as pd
from enum import Enum


# Initialize session state
if "patients" not in st.session_state:
    st.session_state.patients = []
if "page" not in st.session_state:
    st.session_state.page = "list_patients" #  Default view


# Function to switch views
def start_creating():
    st.session_state.page = "add_patient"
    print(st.session_state.page)


def save_patient(name):  # , age, weight, gender, glucose, pH, bicarbonate, ketones):
    """Save the new patient and return to the list view."""
#     new_patient = Patient(patient_id=len(st.session_state.patients) + 1, name=name, age=age, weight=weight, gender=gender)
#     new_patient.determine_severity(glucose, pH, bicarbonate, ketones)
    st.session_state.patients.append(name)
    st.session_state.page = "list_patients"  # Switch back to patient list


# Page layout
st.title("🩺 DKA Patient Management")
if st.session_state.page == "add_patient":
    print("creating")
    st.subheader("➕ Create a New Patient")

    name = st.text_input("Patient Name")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.session_state.page = "list_patients"  # Return to list view
            st.rerun()
    with col2:
        if st.button("Create"):
            if name: #and age and weight and glucose and pH and bicarbonate and ketones:
                save_patient(name)#, age, weight, gender, glucose, pH, bicarbonate, ketones)
                st.success(f"✅ {name} added successfully!")
                st.session_state.page = "list_patients"
                st.rerun()
            else:
                st.error("❌ Please fill in all fields!")
elif st.session_state.page == "list_patients":
    print("runing")
    col1, col2 = st.columns([2, 1])  # Patient list (left) and "Create Patient" button (right)

    with col2:
        st.button("➕ Create Patient", on_click=start_creating)
    st.subheader("📋 Patient List")

    if st.session_state.patients:
        #  patient_data = [p.get_summary() for p in st.session_state.patients]
        df = pd.DataFrame(st.session_state.patients)
        st.dataframe(df)
    else:
        st.info("No patients added yet. Click 'Create Patient' to register a new patient.")
