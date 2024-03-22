#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:18:47 2024

@author: balqees
"""

import subprocess
import vcf
import pysam
import pandas as pd
from fpdf import FPDF
import pdfkit
vcf_file = "/home/balqees/Desktop/Racyca_Precision_Task/normal_sample.deepvariant.vcf"

# Step 1: Execute Bash commands
def run_bash_commands():
    # Create the vep_new directory and set permissions
    subprocess.run(['mkdir', '-p', '$HOME/vep_new'])
    subprocess.run(['chmod', '-R', 'a+rwx', '$HOME/vep_new'])
    subprocess.run(['cd', '$HOME/vep_new'], shell=True)

    # Download and extract the indexed cache
    subprocess.run(['cd', '$HOME/.vep'], shell=True)
    subprocess.run(['curl', '-O', 'https://ftp.ensembl.org/pub/release-111/variation/indexed_vep_cache/homo_sapiens_vep_111_GRCh38.tar.gz'])
    subprocess.run(['tar', 'xzf', 'homo_sapiens_vep_111_GRCh38.tar.gz'])

    # Download and process the FASTA files
    subprocess.run(['curl', '-O', 'https://ftp.ensembl.org/pub/release-111/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz'])
    subprocess.run(['gzip', '-d', 'Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz'])
    subprocess.run(['bgzip', 'Homo_sapiens.GRCh38.dna.primary_assembly.fa'])

    # Index the input VCF file
    subprocess.run(['bgzip', '-c', 'pindel.vcf', '>', 'pindel.vcf.gz'])
    subprocess.run(['tabix', '-p', 'vcf', 'pindel.vcf.gz'])

# Step 2: Parsing VCF Files
def parse_vcf(vcf_file):
    """
    Parse a VCF file and return a DataFrame containing variant information.
    """
    vcf_reader = vcf.Reader(open(vcf_file, 'r'))
    records = [rec for rec in vcf_reader]
    
    variant_data = []
    for record in records:
        variant_info = {
            'CHROM': record.CHROM,
            'POS': record.POS,
            'REF': record.REF,
            'ALT': str(record.ALT[0]),
            'QUAL': record.QUAL,
            'FILTER': record.FILTER
        }
        variant_data.append(variant_info)
    
    variants_df = pd.DataFrame(variant_data)
    return variants_df

# Step 3: Variant Classification
def parse_vep_output(vep_output):
    """
    Parse the VEP output and extract relevant annotations.
    (You'll need to implement this part based on the VEP output format)
    """
    # Implement parsing logic here
    pass

def classify_variant(row, vep_output):
    """
    Classify a variant based on ACMG guidelines and VEP annotations.
    """
    # Run the VEP Docker command for this variant
    vep_cmd = ['sudo', 'docker', 'run', '-v', '$HOME/vep_new:/data:Z', 'ensemblorg/ensembl-vep:release_111.0', 'vep', '--cache', '--offline', '--format', 'vcf', '--vcf', '--force_overwrite', '--tab', '--input_file', f'{row["CHROM"]}:{row["POS"]} {row["REF"]}>{row["ALT"]}', '--output_file', 'output/my_output.tsv']
    subprocess.run(vep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Parse the VEP output and extract relevant annotations
    annotations = parse_vep_output(vep_output)
    
    # Classify the variant based on ACMG guidelines and VEP annotations
    if row['QUAL'] >= 50 and annotations['IMPACT'] == 'HIGH':
        return 'Pathogenic'
    elif row['QUAL'] >= 40 and annotations['IMPACT'] == 'MODERATE':
        return 'Likely Pathogenic'
    else:
        return 'Unclassified'

def classify_variants(variants_df):
    """
    Apply variant classification to the DataFrame.
    """
    variants_df['ACMG_Classification'] = variants_df.apply(lambda row: classify_variant(row, None), axis=1)
    return variants_df

# Step 4: Report Generation
def generate_report(variants_df, patient_info):
    """
    Generate a PDF report containing variant information and ACMG classifications.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Clinical Report', 0, 1, align='C')
    
    # Patient Information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Patient Information', 0, 1)
    pdf.set_font('Arial', '', 10)
    for key, value in patient_info.items():
        pdf.cell(0, 6, f'{key}: {value}', 0, 1)
    
    # Variant Information
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Genomic Variant Information', 0, 1)
    pdf.set_font('Arial', 'B', 10)
    headers = ['Chromosome', 'Position', 'Reference Allele', 'Alternate Allele',
               'Variant Quality', 'Filter Status', 'ACMG Classification']
    pdf.cell(0, 6, ' '.join(headers), 0, 1)
    pdf.set_font('Arial', '', 10)
    for _, row in variants_df.iterrows():
        pdf.cell(0, 6, ' '.join([str(row[col]) for col in headers]), 0, 1)
    
    # Save the PDF report
    pdf.output('clinical_report.pdf', 'F')

# Example usage
run_bash_commands()
vcf_file = 'path/to/your/vcf_file.vcf'
variants_df = parse_vcf(vcf_file)
classified_variants_df = classify_variants(variants_df)

patient_info = {
    'Patient ID': '12345',
    'Date of Birth': '01/01/1990',
    'Gender': 'Male',
    'Ethnicity': 'Caucasian',
    'Family History': 'Maternal history of breast cancer'
}

generate_report(classified_variants_df, patient_info)


# Path to your HTML file
html_file = '/home/balqees/Desktop/Racyca_Precision_Task/clin_var_output2.tsv_summary.html'
# Output PDF file
output_file = '/home/balqees/Desktop/Racyca_Precision_Task/var_report.pdf'

# Convert HTML to PDF
pdfkit.from_file(html_file, output_file)





