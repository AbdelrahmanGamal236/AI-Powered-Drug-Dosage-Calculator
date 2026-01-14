from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db  
from flask_sqlalchemy import SQLAlchemy
from forms import PatientForm
import os
import google.generativeai as genai
import json
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'  

db.init_app(app)  

# Configure Gemini API
api_key = os.environ.get('GEMINI_API_KEY', "api Key")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

from models import Patient, Drug, DoseCalculation

@app.route("/", methods=["GET", "POST"])
def index():
    form = PatientForm()
    if form.validate_on_submit():
        name = form.name.data
        age = form.age.data
        weight = form.weight.data
        height = form.height.data
        medical_condition = form.medical_condition.data
        drug_name = form.drug_name.data
        severity = form.severity.data
        allergies = form.allergies.data

        try:
            # Calculate dose using Gemini API
            dose_result = calculate_dose_with_gemini(
                weight, age, height, medical_condition, drug_name, severity, allergies
            )

            # Save patient record
            new_patient = Patient(
                name=name, age=age, weight=weight, height=height,
                medical_condition=medical_condition, drug_name=drug_name,
                severity=severity, allergies=allergies,
                dose=dose_result['calculated_dose'],
                dose_form=dose_result['dose_form'],
                frequency=dose_result['frequency'],
                duration=dose_result['duration'],
                instructions=dose_result['instructions'],
                warnings=dose_result['warnings']
            )
            db.session.add(new_patient)
            db.session.commit()

            flash(f"Dose calculated successfully: {dose_result['calculated_dose']} {dose_result['dose_form']}", "success")
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"Error calculating dose: {str(e)}", "danger")
            return redirect(url_for("index"))

    patients = Patient.query.all()
    return render_template("index.html", form=form, patients=patients)

@app.route("/patient/<int:patient_id>")
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patient_detail.html", patient=patient)

@app.route("/api/drug-info/<drug_name>")
def get_drug_info(drug_name):
    """API endpoint to get drug information"""
    try:
        drug_info = get_drug_information(drug_name)
        return jsonify(drug_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_dose_with_gemini(weight, age, height, medical_condition, drug_name, severity, allergies):
    """Calculate drug dose using Gemini API with comprehensive medical guidelines"""
    
    prompt = f"""
    As a clinical pharmacist, calculate the appropriate drug dosage for the following patient:
    
    Patient Information:
    - Age: {age} years
    - Weight: {weight} kg
    - Height: {height} cm
    - Medical Condition: {medical_condition}
    - Drug Requested: {drug_name}
    - Severity: {severity}
    - Known Allergies: {allergies if allergies else 'None'}
    
    Please provide a comprehensive dosage calculation including:
    1. Calculated dose (mg or appropriate unit)
    2. Dose form (tablets, syrup, injection, etc.)
    3. Frequency (times per day)
    4. Duration of treatment
    5. Special instructions
    6. Warnings and contraindications
    7. Available market formulations
    8. Alternative drugs if applicable
    
    Consider:
    - Age-based dosing adjustments
    - Weight-based calculations
    - Medical condition interactions
    - Severity adjustments
    - Standard clinical guidelines
    - Available tablet/syrup strengths in the market
    
    Format your response as JSON with the following structure:
    {{
        "calculated_dose": "dose with unit",
        "dose_form": "form of medication",
        "frequency": "how often per day",
        "duration": "treatment duration",
        "instructions": "detailed administration instructions",
        "warnings": "important warnings and contraindications",
        "market_formulations": ["available strengths"],
        "alternatives": ["alternative medications if needed"],
        "calculation_breakdown": "explanation of how dose was calculated"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group()
            dose_info = json.loads(json_str)
        else:
            # Fallback parsing if JSON format is not perfect
            dose_info = parse_gemini_response(response_text)
        
        return dose_info
        
    except Exception as e:
        # Fallback to basic calculation if API fails
        return fallback_dose_calculation(weight, age, medical_condition, drug_name, severity)

def parse_gemini_response(response_text):
    """Parse Gemini response when JSON format is not perfect"""
    dose_info = {
        "calculated_dose": "Consult healthcare provider",
        "dose_form": "As prescribed",
        "frequency": "As directed",
        "duration": "As prescribed",
        "instructions": "Please consult with a healthcare professional",
        "warnings": "Consult healthcare provider before use",
        "market_formulations": [],
        "alternatives": [],
        "calculation_breakdown": response_text
    }
    
    # Try to extract key information using regex
    dose_match = re.search(r'dose[:\s]*([0-9.]+\s*(?:mg|g|ml|units?))', response_text, re.IGNORECASE)
    if dose_match:
        dose_info["calculated_dose"] = dose_match.group(1)
    
    freq_match = re.search(r'frequency[:\s]*([0-9]+\s*times?\s*per\s*day)', response_text, re.IGNORECASE)
    if freq_match:
        dose_info["frequency"] = freq_match.group(1)
    
    return dose_info

def get_drug_information(drug_name):
    """Get detailed drug information from Gemini API"""
    
    prompt = f"""
    Provide comprehensive information about the drug: {drug_name}
    
    Include:
    1. Generic and brand names
    2. Drug class and mechanism of action
    3. Common indications
    4. Standard dosing ranges
    5. Available formulations and strengths
    6. Common side effects
    7. Contraindications
    8. Drug interactions
    9. Special populations (pediatric, geriatric, pregnancy)
    
    Format as JSON with appropriate keys.
    """
    
    try:
        response = model.generate_content(prompt)
        return {"information": response.text}
    except Exception as e:
        return {"error": f"Unable to fetch drug information: {str(e)}"}

def fallback_dose_calculation(weight, age, medical_condition, drug_name, severity):
    """Fallback calculation method when API is unavailable"""
    
    # Basic calculation similar to original system
    base_dose = weight * 5  # Conservative base dose
    
    # Age adjustments
    if age < 12:
        base_dose *= 0.5
    elif age > 65:
        base_dose *= 0.8
    
    # Severity adjustments
    severity_multiplier = {
        "mild": 1.0,
        "moderate": 1.2,
        "severe": 1.5
    }
    base_dose *= severity_multiplier.get(severity.lower(), 1.0)
    
    # Medical condition adjustments
    if 'kidney' in medical_condition.lower():
        base_dose *= 0.7
    elif 'liver' in medical_condition.lower():
        base_dose *= 0.6
    elif 'heart' in medical_condition.lower():
        base_dose *= 0.8
    
    return {
        "calculated_dose": f"{round(base_dose, 2)} mg",
        "dose_form": "Tablet/Capsule",
        "frequency": "2-3 times per day",
        "duration": "As prescribed by physician",
        "instructions": "Take with food. Consult healthcare provider for exact dosing.",
        "warnings": "This is a basic calculation. Please consult a healthcare professional.",
        "market_formulations": ["Various strengths available"],
        "alternatives": ["Consult pharmacist for alternatives"],
        "calculation_breakdown": f"Basic calculation: {weight}kg × 5mg/kg with adjustments for age and condition"
    }

@app.route("/export-patients")
def export_patients():
    """Export patient data for analysis"""
    patients = Patient.query.all()
    patient_data = []
    
    for patient in patients:
        patient_data.append({
            "name": patient.name,
            "age": patient.age,
            "weight": patient.weight,
            "height": patient.height,
            "medical_condition": patient.medical_condition,
            "drug_name": patient.drug_name,
            "calculated_dose": patient.dose,
            "dose_form": patient.dose_form,
            "frequency": patient.frequency
        })
    
    return jsonify(patient_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True,port = 5002)