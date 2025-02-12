from datetime import datetime
import random
from enum import Enum
import streamlit as st
import pandas as pd
import uuid  # For generating unique patient IDs


class DKASeverity(Enum):
    """Enum for classifying the severity of Diabetic Ketoacidosis (DKA)."""
    SEVERE = "Severe DKA"
    MILD_MODERATE = "Mild to Moderate DKA"
    MILD = "Mild DKA"


class Patient:
    def __init__(self, patient_id, name, age, weight, gender):
        """Initialize a patient with basic demographic info and empty lists for DKA-related data."""
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.weight = weight  # kg
        self.gender = gender

        self.insulin_drip = False
        self.vital_signs = []  # [(timestamp, heart_rate, blood_pressure, respiratory_rate)]
        self.glucose_levels = []  # [(timestamp, glucose_mg_dl)]
        self.ketone_levels = []  # [(timestamp, beta_hydroxybutyrate_mmol_L)]
        self.electrolytes = []  # [(timestamp, sodium, potassium, chloride, bicarbonate)]
        self.corrected_sodium = []  # [(timestamp, corrected_sodium)]
        self.pH_levels = []  # [(timestamp, pH)]
        self.anion_gap = []  # [(timestamp, anion_gap)]

    ###########################################################
    # Glucose
    ###########################################################
    def add_glucose(self, glucose_mg_dl):
        """Record blood glucose level."""
        time = datetime.now()
        self.glucose_levels.append((time, glucose_mg_dl))
        return time, self.glucose_levels[-1]

    def get_glucose(self):
        """Retrieve the latest glucose value."""
        return self.glucose_levels[-1] if self.glucose_levels else (None, None)

    ###########################################################
    # Electrolytes
    ###########################################################
    def add_electrolytes(self, sodium, potassium, chloride, bicarbonate):
        """Record electrolyte levels."""
        time = datetime.now()
        self.electrolytes.append((time, sodium, potassium, chloride, bicarbonate))
        return time, self.electrolytes[-1]

    def get_electrolytes(self):
        """Retrieve the latest electrolyte values."""
        return self.electrolytes[-1] if self.electrolytes else (None, None, None, None, None)

    ###########################################################
    # Corrected Sodium
    ###########################################################
    def add_corrected_sodium(self, sodium, glucose):
        """Record corrected sodium level."""
        time, sodium, _, _, _ = self.get_electrolytes()
        _, glucose = self.get_glucose()
        corrected_sodium = sodium + (0.016 * (glucose - 100))  # Using the standard formula
        self.corrected_sodium.append((time, corrected_sodium))
        return time, self.corrected_sodium[-1]

    def get_corrected_sodium(self):
        """Calculate the corrected sodium level based on glucose."""
        return self.corrected_sodium[-1] if self.corrected_sodium else (None, None)

    ###########################################################
    # Anion Gap
    ###########################################################
    def calculate_anion_gap(self, sodium, potassium, chloride, bicarbonate):
        """Calculate the anion gap: Na - (Cl + HCO3)."""
        return (sodium + potassium) - (chloride + bicarbonate)

    def add_anion_gap(self, sodium, potassium, chloride, bicarbonate):
        """Record anion gap calculation."""
        anion_gap = self.calculate_anion_gap(sodium, potassium, chloride, bicarbonate)
        time = datetime.now()
        self.anion_gap.append((time, anion_gap))
        return time, self.anion_gap[-1]

    def get_anion_gap(self):
        """Retrieve the latest anion gap value."""
        return self.anion_gap[-1] if self.anion_gap else (None, None)

    ###########################################################
    # pH
    ###########################################################
    def add_pH(self, pH):
        """Record blood pH level."""
        time = datetime.now()
        self.pH_levels.append((time, pH))
        return time, self.pH_levels[-1]

    def get_pH(self):
        """Retrieve the latest pH value."""
        return self.pH_levels[-1] if self.pH_levels else (None, None)


class DKATreatment:
    def __init__(self):
        self.patient: Patient = None
        self.admission_status: DKASeverity = None
        self.current_recommendations = []
        self.all_recommendations = []

    def check_resolution(self, anion_gap):
        """Check if DKA has resolved based on anion gap."""
        if anion_gap < 12:
            self.current_recommendations.append("✅ DKA Resolved")
            return True
        return False

    def determine_severity(self, pH):
        """Determine the severity of DKA based on pH value."""
        if pH < 7:
            return DKASeverity.SEVERE
        elif 7 < pH < 7.24:
            return DKASeverity.MILD_MODERATE
        else:
            return DKASeverity.MILD

    def admit_patient(self, patient):
        """Admit patient to the PCU or ICU based on DKA severity."""
        self.patient = patient

    def analyze_bloodwork(self, patient: Patient):
        _, glucose = patient.get_glucose()
        _, corrected_sodium = patient.get_corrected_sodium()
        _, anion_gap = patient.get_anion_gap()
        _, pH = patient.get_pH()
        _, sodium, potassium, chloride, bicarbonate = patient.get_electrolytes()

        if self.check_resolution(anion_gap):
            return self.current_recommendations
        if not patient.insulin_drip:
            self.current_recommendations.append("Start insulin drip at 0.1 units/kg/hr")
            patient.insulin_drip = True
        if glucose > 250:
            if corrected_sodium > 135:
                if potassium > 4:
                    self.current_recommendations.append("Run IV fluids 0.45 NS @ 250 cc / hr")
                elif potassium < 4:
                    self.current_recommendations.append("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
            elif corrected_sodium < 135:
                if potassium > 4:
                    self.current_recommendations.append("Run IV fluids NS @ 250 cc / hr")
                elif potassium < 4:
                    self.current_recommendations.append("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
        elif glucose < 250:
            if corrected_sodium > 135:
                if potassium > 4:
                    self.current_recommendations.append("Run IV fluids D5 0.45 NS @ 250 cc / hr")
                else:
                    self.current_recommendations.append("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
            elif corrected_sodium < 135:
                if potassium > 4:
                    self.current_recommendations.append("Run IV fluids D5 NS @ 250 cc / hr")
                else:
                    self.current_recommendations.append("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
        # st.write("Come back in 1 hour with electrolytes and blood sugar reading")
        self.current_recommendations.append("Come back in 1 hour with electrolytes and blood sugar reading")
        return self.current_recommendations

    def treat_patient(self, patient: Patient):
        """Simulates the treatment of a patient with random bloodwork values until DKA is resolved."""
        sodium, potassium, chloride, bicarbonate, pH, glucose = self.generate_random_bloodwork()

        self.admission_status = self.determine_severity(pH)
        self.log_bloodwork(sodium, potassium, chloride, bicarbonate, pH, glucose)
        self.print_bloodwork()

        while not self.check_resolution(patient.get_anion_gap()[1]):
            recommendations = self.analyze_bloodwork(patient)
            for rec in recommendations:
                print(f"- {rec}")
            self.all_recommendations.append(recommendations)
            sodium, potassium, chloride, bicarbonate, pH, glucose = self.generate_random_bloodwork()
            self.admission_status = self.determine_severity(pH)
            self.log_bloodwork(sodium, potassium, chloride, bicarbonate, pH, glucose)
            self.print_bloodwork()

    # needs API call
    def log_bloodwork(self, sodium, potassium, chloride, bicarbonate, pH, glucose):
        """Admit patient to PCU or ICU based on lab values."""
        self.patient.add_electrolytes(sodium, potassium, chloride, bicarbonate)
        self.patient.add_pH(pH)
        self.patient.add_glucose(glucose)
        self.patient.add_corrected_sodium(sodium, glucose)
        self.patient.add_anion_gap(sodium, potassium, chloride, bicarbonate)

    def generate_random_bloodwork(self):
        """Generate random bloodwork values for a patient."""
        sodium = random.uniform(120, 145)  # Normal: 135-145, DKA may be low or high
        potassium = random.uniform(2.5, 6.0)  # Normal: 3.5-5.0, DKA often high
        chloride = random.uniform(90, 110)  # Normal: 95-105, DKA slightly abnormal
        bicarbonate = random.uniform(5, 24)  # Normal: 22-28, DKA low (<18)
        pH = random.uniform(6.8, 7.45)  # Normal: 7.35-7.45, DKA low (<7.3)
        glucose = random.uniform(150, 600)  # Normal: 70-140, DKA high (>250)
        return sodium, potassium, chloride, bicarbonate, pH, glucose

    def print_bloodwork(self):
        """Print the latest bloodwork values for a patient."""
        time, sodium, potassium, chloride, bicarbonate = self.patient.get_electrolytes()
        time, pH = self.patient.get_pH()
        time, glucose = self.patient.get_glucose()
        time, anion_gap = self.patient.get_anion_gap()
        time, corrected_sodium = self.patient.get_corrected_sodium()
        print(f"\nTime: {time}, Sodium: {sodium}, Potassium: {potassium}, \
Chloride: {chloride}, Bicarbonate: {bicarbonate}")
        print(f"pH: {pH}, Glucose: {glucose}, Anion Gap: {anion_gap}, Corrected Sodium: {corrected_sodium}\n")


# Example usage
if __name__ == "__main__":
    patient = Patient(patient_id=str(uuid.uuid4()), name="John Doe", age=45, weight=70, gender="Male")
    dka_treatment = DKATreatment()
    dka_treatment.admit_patient(patient)
    dka_treatment.treat_patient(patient)

    # print(f"Patient: {patient.name}, Admission Status: {patient.admission_status.value}")
    # print(f"Anion Gap: {anion_gap}, Recommendations:")
    # for rec in recommendations:
    #     print(f"- {rec}")
    #   def generate_recommendations(self, patient: Patient):
    #     """Generate treatment recommendations based on patient data."""
    #     recommendations = []
    #     time, sodium, potassium, chloride, bicarbonate = patient.get_electrolytes()
    #     _, glucose = patient.get_glucose()
    #     _, anion_gap = patient.get_anion_gap()
    #     corrected_sodium = patient.get_corrected_sodium(sodium, glucose)

    #      if anion_gap < 12:
    #         recommendations.append("✅ DKA Resolved")
    #         return recommendations
    #     if not patient.insulin_drip:
    #         recommendations.append("Start insulin drip at 0.1 units/kg/hr")
    #         patient.insulin_drip = True
    #     if glucose > 250:
    #         if corrected_sodium > 135:
    #             if potassium > 4:
    #                 # st.write("Run IV fluids 0.45 NS @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids 0.45 NS @ 250 cc / hr")
    #             else:
    #                 # st.write("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids 0.45 NS w 20 meq KCl @ 250 cc / hr")
    #         elif corrected_sodium < 135:
    #             if potassium > 4:
    #                 # st.write("Run IV fluids NS @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids NS @ 250 cc / hr")
    #             else:
    #                 # st.write("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids NS w 20 meq KCl @ 250 cc / hr")
    #     elif glucose < 250:
    #         if corrected_sodium > 135:
    #             if potassium > 4:
    #                 # st.write("Run IV fluids D5 0.45 NS @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids D5 0.45 NS @ 250 cc / hr")
    #             else:
    #                 # st.write("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids D5 0.45 NS w 20 meq KCl @ 250 cc / hr")
    #         elif corrected_sodium < 135:
    #             if potassium > 4:
    #                 # st.write("Run IV fluids D5 NS @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids D5 NS @ 250 cc / hr")
    #             else:
    #                 # st.write("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
    #                 recommendations.append("Run IV fluids D5 NS w 20 meq KCl @ 250 cc / hr")
    #     # st.write("Come back in 1 hour with electrolytes and blood sugar reading")
    #     recommendations.append("Come back in 1 hour with electrolytes and blood sugar reading")
    #     return recommendations
