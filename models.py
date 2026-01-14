from extensions import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=True)  # Added height
    medical_condition = db.Column(db.String(100), nullable=False)
    drug_name = db.Column(db.String(100), nullable=False)  # Changed from drug_type to drug_name
    severity = db.Column(db.String(50), nullable=False)
    allergies = db.Column(db.Text, nullable=True)  # Added allergies
    dose = db.Column(db.String(100), nullable=False)  # Changed to string to handle units
    dose_form = db.Column(db.String(50), nullable=True)  # tablet, syrup, injection, etc.
    frequency = db.Column(db.String(50), nullable=True)  # times per day
    duration = db.Column(db.String(50), nullable=True)  # treatment duration
    instructions = db.Column(db.Text, nullable=True)  # detailed instructions
    warnings = db.Column(db.Text, nullable=True)  # warnings and contraindications
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to dose calculations
    calculations = db.relationship('DoseCalculation', backref='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.name}>"

class Drug(db.Model):
    """Database model for drug information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    generic_name = db.Column(db.String(100), nullable=True)
    drug_class = db.Column(db.String(100), nullable=True)
    mechanism = db.Column(db.Text, nullable=True)
    indications = db.Column(db.Text, nullable=True)
    contraindications = db.Column(db.Text, nullable=True)
    side_effects = db.Column(db.Text, nullable=True)
    interactions = db.Column(db.Text, nullable=True)
    
    # Dosing information
    standard_dose_adult = db.Column(db.String(100), nullable=True)
    standard_dose_pediatric = db.Column(db.String(100), nullable=True)
    max_daily_dose = db.Column(db.String(100), nullable=True)
    
    # Available formulations
    formulations = db.relationship('DrugFormulation', backref='drug', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Drug {self.name}>"

class DrugFormulation(db.Model):
    """Different formulations and strengths of drugs"""
    id = db.Column(db.Integer, primary_key=True)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'), nullable=False)
    form_type = db.Column(db.String(50), nullable=False)  # tablet, capsule, syrup, injection
    strength = db.Column(db.String(50), nullable=False)  # 500mg, 5mg/5ml, etc.
    route = db.Column(db.String(50), nullable=True)  # oral, IV, IM, topical
    manufacturer = db.Column(db.String(100), nullable=True)
    market_availability = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f"<DrugFormulation {self.form_type} {self.strength}>"

class DoseCalculation(db.Model):
    """Store detailed dose calculations"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    
    # Calculation details
    base_dose = db.Column(db.Float, nullable=True)
    weight_adjusted_dose = db.Column(db.Float, nullable=True)
    age_adjustment_factor = db.Column(db.Float, nullable=True)
    condition_adjustment_factor = db.Column(db.Float, nullable=True)
    severity_adjustment_factor = db.Column(db.Float, nullable=True)
    final_calculated_dose = db.Column(db.Float, nullable=True)
    
    # Gemini API response
    gemini_response = db.Column(db.Text, nullable=True)
    calculation_method = db.Column(db.String(50), nullable=True)  # 'gemini_api' or 'fallback'
    
    # Verification
    verified_by_expert = db.Column(db.Boolean, default=False)
    expert_notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<DoseCalculation {self.id}>"

class MedicalCondition(db.Model):
    """Database model for medical conditions and their dose adjustments"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Dosing adjustments
    dose_reduction_factor = db.Column(db.Float, default=1.0)  # 1.0 = no change, 0.8 = 20% reduction
    contraindicated_drugs = db.Column(db.Text, nullable=True)  # JSON list of drugs to avoid
    special_monitoring = db.Column(db.Text, nullable=True)
    
    severity_adjustments = db.relationship('SeverityAdjustment', backref='condition', lazy=True)
    
    def __repr__(self):
        return f"<MedicalCondition {self.name}>"

class SeverityAdjustment(db.Model):
    """Severity-based dose adjustments for medical conditions"""
    id = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey('medical_condition.id'), nullable=False)
    severity_level = db.Column(db.String(20), nullable=False)  # mild, moderate, severe
    adjustment_factor = db.Column(db.Float, nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<SeverityAdjustment {self.severity_level}>"

class AuditLog(db.Model):
    """Log all dose calculations for audit purposes"""
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    drug_name = db.Column(db.String(100), nullable=False)
    calculated_dose = db.Column(db.String(100), nullable=False)
    calculation_method = db.Column(db.String(50), nullable=False)
    user_ip = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog {self.patient_name} - {self.drug_name}>"