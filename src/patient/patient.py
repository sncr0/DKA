from datetime import datetime
from enum import Enum


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

        # Store all data with timestamps
        self.admission_status = None  # PCU or ICU
        self.insulin_drip = False
        self.on_D5 = False
        self.vital_signs = []  # [(timestamp, heart_rate, blood_pressure, respiratory_rate)]
        self.glucose_levels = []  # [(timestamp, glucose_mg_dl)]
        self.ketone_levels = []  # [(timestamp, beta_hydroxybutyrate_mmol_L)]
        self.electrolytes = []  # [(timestamp, sodium, potassium, chloride, bicarbonate)]
        self.pH_levels = []  # [(timestamp, pH)]
        self.anion_gap = []  # [(timestamp, anion_gap)]
        self.blood_gases = []  # [(timestamp, pCO2, pO2)]
        self.insulin_doses = []  # [(timestamp, insulin_units)]
        self.fluid_intake = []  # [(timestamp, fluid_type, volume_ml)]
        self.urine_output = []  # [(timestamp, volume_ml)]
        self.medications = []  # [(timestamp, medication_name, dose, route)]
        self.notes = []  # [(timestamp, note)]
        self.consultations = []  # [(timestamp, consult_type, reason)]
        self.nursing_interventions = []  # [(timestamp, intervention_type, status)]
        self.labs = []  # [(timestamp, lab_test, result)]

    def determine_severity(self, pH):
        """Determine the severity of DKA based on lab values."""
        if pH < 7:
            return DKASeverity.SEVERE
        elif 7 < pH < 7.24:
            return DKASeverity.MILD_MODERATE
        else:
            return DKASeverity.MILD

    def admit(self, sodium, potassium, chloride, bicarbonate, pH, glucose, patient_id=None):
        """Admit patient to PCU or ICU based on lab values."""
        self.add_electrolytes(sodium, potassium, chloride, bicarbonate)
        self.add_pH(pH)
        self.add_glucose(glucose)
        self.admission_status = self.determine_severity(pH)

    def add_glucose(self, glucose_mg_dl):
        """Record blood glucose level."""
        self.glucose_levels.append((datetime.now(), glucose_mg_dl))

    def get_glucose(self):
        """Retrieve the latest glucose value."""
        time, glucose = self.glucose_levels[-1] if self.glucose_levels else (None, None)
        return time, glucose

    def get_corrected_sodium(self, sodium, glucose):
        """Calculate the corrected sodium level based on glucose."""
        _, sodium, _, _, _ = self.get_electrolytes()
        _, glucose = self.get_glucose()
        corrected_sodium = (sodium * 0.4 * glucose - 5.5)
        return corrected_sodium

    def add_electrolytes(self, sodium, potassium, chloride, bicarbonate):
        """Record electrolyte levels."""
        self.electrolytes.append((datetime.now(), sodium, potassium, chloride, bicarbonate))

    def get_electrolytes(self):
        """Retrieve the latest electrolyte values."""
        time, sodium, potassium, chloride, bicarbonate = self.electrolytes[-1] if self.electrolytes else (None, None, None, None, None)
        return time, sodium, potassium, chloride, bicarbonate

    def add_pH(self, pH):
        """Record blood pH level."""
        self.pH_levels.append((datetime.now(), pH))

    def calculate_anion_gap(self, sodium, potassium, chloride, bicarbonate):
        """Calculate the anion gap using the formula: Na - (Cl + HCO3)."""
        return (sodium + potassium) - (chloride + bicarbonate)

    def add_anion_gap(self, sodium, potassium, chloride, bicarbonate):
        """Record anion gap calculation."""
        anion_gap = self.calculate_anion_gap(sodium, potassium, chloride, bicarbonate)
        time = datetime.now()
        self.anion_gap.append((time, anion_gap))
        return time, anion_gap

    def get_anion_gap(self):
        """Retrieve the latest anion gap value."""
        return self.anion_gap[-1] if self.anion_gap else None

    def add_blood_gases(self, pCO2, pO2):
        """Record arterial blood gases."""
        self.blood_gases.append((datetime.now(), pCO2, pO2))

    def add_insulin_dose(self, insulin_units):
        """Record administered insulin dose."""
        self.insulin_doses.append((datetime.now(), insulin_units))

    def add_fluid_intake(self, fluid_type, volume_ml):
        """Record IV fluids given."""
        self.fluid_intake.append((datetime.now(), fluid_type, volume_ml))

    def add_urine_output(self, volume_ml):
        """Record urine output for fluid balance monitoring."""
        self.urine_output.append((datetime.now(), volume_ml))

    def add_medication(self, medication_name, dose, route):
        """Record medications given (e.g., potassium, bicarbonate, antiemetics)."""
        self.medications.append((datetime.now(), medication_name, dose, route))

    def add_lab_result(self, lab_test, result):
        """Store lab results such as glucose, potassium, phosphorus, etc."""
        self.labs.append((datetime.now(), lab_test, result))

    def add_nursing_intervention(self, intervention_type, status):
        """Log nursing interventions such as insulin infusion adjustments, vitals monitoring."""
        self.nursing_interventions.append((datetime.now(), intervention_type, status))

    def add_consultation(self, consult_type, reason):
        """Record consultations (e.g., diabetes educator, nephrology)."""
        self.consultations.append((datetime.now(), consult_type, reason))

    def add_note(self, note):
        """Add a general medical note."""
        self.notes.append((datetime.now(), note))

    def get_latest_measurements(self):
        """Retrieve the latest data points for quick reference."""
        return {
            "latest_vitals": self.vital_signs[-1] if self.vital_signs else None,
            "latest_glucose": self.glucose_levels[-1] if self.glucose_levels else None,
            "latest_ketones": self.ketone_levels[-1] if self.ketone_levels else None,
            "latest_pH": self.pH_levels[-1] if self.pH_levels else None,
            "latest_anion_gap": self.anion_gap[-1] if self.anion_gap else None,
            "latest_blood_gases": self.blood_gases[-1] if self.blood_gases else None,
            "latest_insulin": self.insulin_doses[-1] if self.insulin_doses else None,
            "latest_fluids": self.fluid_intake[-1] if self.fluid_intake else None,
        }

    def __str__(self):
        """Return a summary of the patient's current status."""
        return f"Patient {self.patient_id}: {self.name}, {self.age} y/o, {self.weight} kg\n" \
               f"Admission: {self.admission_status}\n" \
               f"Latest Glucose: {self.glucose_levels[-1] if self.glucose_levels else 'N/A'} mg/dL\n" \
               f"Latest Ketones: {self.ketone_levels[-1] if self.ketone_levels else 'N/A'} mmol/L\n" \
               f"Latest pH: {self.pH_levels[-1] if self.pH_levels else 'N/A'}\n" \
               f"Latest Insulin Dose: {self.insulin_doses[-1] if self.insulin_doses else 'N/A'} units"


# Example usage:
if __name__ == "__main__":
    patient = Patient(patient_id=1, name="John Doe", age=45, weight=70, gender="Male")

    # Simulating data collection based on DKA protocol
    patient.add_pH(6.9)
    patient.add_vital_signs(heart_rate=110, blood_pressure="90/60", respiratory_rate=28)
    patient.add_glucose(350)
    patient.add_ketones(4.2)
    patient.add_electrolytes(135, 3.2, 100, 12)
    patient.add_insulin_dose(10)
    patient.add_fluid_intake("Normal Saline", 1000)
    patient.add_nursing_intervention("Vital Signs Monitoring", "Every hour for 6 hours")
    patient.add_medication("Ondansetron", "4 mg", "IV")

    print(patient)
