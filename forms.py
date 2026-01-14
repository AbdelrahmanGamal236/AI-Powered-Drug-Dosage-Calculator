from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class PatientForm(FlaskForm):
    # Basic patient information
    name = StringField("Patient Name", validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField("Age (years)", validators=[DataRequired(), NumberRange(min=0, max=120)])
    weight = FloatField("Weight (kg)", validators=[DataRequired(), NumberRange(min=0.5, max=500)])
    height = FloatField("Height (cm)", validators=[Optional(), NumberRange(min=30, max=300)])
    
    # Medical information
    medical_condition = SelectField("Primary Medical Condition", choices=[
        ("normal", "No specific condition"),
        ("hypertension", "Hypertension"),
        ("diabetes_type1", "Diabetes Type 1"),
        ("diabetes_type2", "Diabetes Type 2"),
        ("kidney_disease", "Chronic Kidney Disease"),
        ("liver_disease", "Liver Disease"),
        ("heart_disease", "Heart Disease"),
        ("asthma", "Asthma"),
        ("copd", "COPD"),
        ("epilepsy", "Epilepsy"),
        ("depression", "Depression"),
        ("anxiety", "Anxiety Disorder"),
        ("arthritis", "Arthritis"),
        ("osteoporosis", "Osteoporosis"),
        ("cancer", "Cancer"),
        ("thyroid_disorder", "Thyroid Disorder"),
        ("other", "Other (specify in notes)")
    ], validators=[DataRequired()])
    
    # Drug information
    drug_name = StringField("Drug Name", validators=[DataRequired(), Length(min=2, max=100)],
                           render_kw={"placeholder": "Enter generic or brand name"})
    
    severity = SelectField("Condition Severity", choices=[
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
        ("critical", "Critical")
    ], validators=[DataRequired()])
    
    # Additional information
    allergies = TextAreaField("Known Allergies", validators=[Optional(), Length(max=500)],
                             render_kw={"placeholder": "List any known drug allergies"})
    
    notes = TextAreaField("Additional Notes", validators=[Optional(), Length(max=1000)],
                         render_kw={"placeholder": "Any additional medical information"})
    
    submit = SubmitField("Calculate Dose")

class DrugSearchForm(FlaskForm):
    """Form for searching drug information"""
    drug_name = StringField("Search Drug", validators=[DataRequired()])
    search = SubmitField("Search")

class ExpertReviewForm(FlaskForm):
    """Form for expert review of dose calculations"""
    calculation_id = IntegerField("Calculation ID", validators=[DataRequired()])
    expert_name = StringField("Expert Name", validators=[DataRequired()])
    verification_status = SelectField("Verification Status", choices=[
        ("approved", "Approved"),
        ("needs_adjustment", "Needs Adjustment"),
        ("rejected", "Rejected")
    ], validators=[DataRequired()])
    expert_notes = TextAreaField("Expert Notes", validators=[Optional(), Length(max=1000)])
    recommended_dose = StringField("Recommended Dose (if different)", validators=[Optional()])
    submit = SubmitField("Submit Review")

class DrugDatabaseForm(FlaskForm):
    """Form for adding drugs to the database"""
    name = StringField("Drug Name", validators=[DataRequired(), Length(min=2, max=100)])
    generic_name = StringField("Generic Name", validators=[Optional(), Length(max=100)])
    drug_class = StringField("Drug Class", validators=[Optional(), Length(max=100)])
    mechanism = TextAreaField("Mechanism of Action", validators=[Optional(), Length(max=1000)])
    indications = TextAreaField("Indications", validators=[Optional(), Length(max=1000)])
    contraindications = TextAreaField("Contraindications", validators=[Optional(), Length(max=1000)])
    side_effects = TextAreaField("Common Side Effects", validators=[Optional(), Length(max=1000)])
    interactions = TextAreaField("Drug Interactions", validators=[Optional(), Length(max=1000)])
    
    standard_dose_adult = StringField("Standard Adult Dose", validators=[Optional(), Length(max=100)])
    standard_dose_pediatric = StringField("Standard Pediatric Dose", validators=[Optional(), Length(max=100)])
    max_daily_dose = StringField("Maximum Daily Dose", validators=[Optional(), Length(max=100)])
    
    submit = SubmitField("Add Drug")

class FormulationForm(FlaskForm):
    """Form for adding drug formulations"""
    drug_id = SelectField("Drug", coerce=int, validators=[DataRequired()])
    form_type = SelectField("Formulation Type", choices=[
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("syrup", "Syrup/Liquid"),
        ("injection", "Injection"),
        ("cream", "Cream/Ointment"),
        ("drops", "Drops"),
        ("inhaler", "Inhaler"),
        ("patch", "Patch"),
        ("suppository", "Suppository")
    ], validators=[DataRequired()])
    
    strength = StringField("Strength", validators=[DataRequired(), Length(max=50)],
                          render_kw={"placeholder": "e.g., 500mg, 5mg/5ml"})
    
    route = SelectField("Route of Administration", choices=[
        ("oral", "Oral"),
        ("iv", "Intravenous"),
        ("im", "Intramuscular"),
        ("sc", "Subcutaneous"),
        ("topical", "Topical"),
        ("inhalation", "Inhalation"),
        ("rectal", "Rectal"),
        ("transdermal", "Transdermal")
    ], validators=[Optional()])
    
    manufacturer = StringField("Manufacturer", validators=[Optional(), Length(max=100)])
    market_availability = SelectField("Market Availability", choices=[
        ("1", "Available"),
        ("0", "Not Available")
    ], coerce=int, default=1)
    
    submit = SubmitField("Add Formulation")