#!/usr/bin/env python3
import os

# FRNT HTML Template
frnt_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JASPR FRNT Complete Guide</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container { max-width: 900px; margin: 0 auto; background: white; }
        @media print { 
            body { background: white; }
            .page-break { page-break-after: always; }
            .no-break { page-break-inside: avoid; }
        }
        
        /* Title Page */
        .title-page {
            padding: 120px 60px 60px;
            text-align: center;
            border-bottom: 4px solid #0066cc;
            page-break-after: always;
        }
        .title-page h1 {
            font-size: 48px;
            color: #0066cc;
            margin-bottom: 30px;
            font-weight: 700;
        }
        .title-page .subtitle {
            font-size: 24px;
            color: #666;
            margin-bottom: 40px;
        }
        .title-page .description {
            font-size: 16px;
            color: #555;
            max-width: 700px;
            margin: 0 auto 80px;
            line-height: 1.8;
        }
        .title-page .meta {
            font-size: 14px;
            color: #888;
            border-top: 1px solid #ddd;
            padding-top: 30px;
        }
        
        /* TOC */
        .toc { 
            padding: 60px;
            page-break-after: always;
        }
        .toc h2 {
            font-size: 32px;
            color: #0066cc;
            margin-bottom: 40px;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 15px;
        }
        .toc ol {
            list-style: decimal;
            margin-left: 40px;
        }
        .toc li {
            margin-bottom: 12px;
            font-size: 16px;
        }
        .toc a {
            color: #0066cc;
            text-decoration: none;
        }
        
        /* Main Content */
        .content { padding: 60px; }
        section { margin-bottom: 60px; }
        h2 {
            font-size: 28px;
            color: #0066cc;
            margin-bottom: 20px;
            border-left: 5px solid #0066cc;
            padding-left: 20px;
            page-break-after: avoid;
        }
        h3 {
            font-size: 20px;
            color: #333;
            margin-top: 25px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }
        h4 {
            font-size: 16px;
            color: #555;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        p { margin-bottom: 15px; text-align: justify; }
        
        /* Lists */
        ol, ul { margin-left: 40px; margin-bottom: 15px; }
        li { margin-bottom: 8px; }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        th {
            background: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:nth-child(even) { background: #f9f9f9; }
        
        /* Code blocks */
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
            border-left: 4px solid #0066cc;
        }
        pre code { background: none; padding: 0; }
        
        /* Steps */
        .step {
            margin: 20px 0;
            padding: 15px;
            background: #f0f7ff;
            border-left: 4px solid #0066cc;
            page-break-inside: avoid;
        }
        .step-number {
            display: inline-block;
            width: 30px;
            height: 30px;
            background: #0066cc;
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        /* Boxes */
        .info-box, .warning-box, .tips-box {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            page-break-inside: avoid;
        }
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #ff9800;
        }
        .tips-box {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
        }
        
        /* Footer */
        footer {
            padding: 20px 60px;
            border-top: 1px solid #ddd;
            color: #888;
            font-size: 12px;
            text-align: center;
        }
        
        @media print {
            section { page-break-inside: avoid; }
            footer { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Title Page -->
        <div class="title-page">
            <h1>JASPR FRNT</h1>
            <p class="subtitle">Focus Reduction Neutralization Test</p>
            <p class="subtitle">Complete Analysis Guide</p>
            <p class="description">
                FRNT is used to measure neutralizing antibody titers in viral surveillance workflows. This comprehensive guide covers data import, analysis, and reporting using the JASPR platform.
            </p>
            <div class="meta">
                <p>Document Version: 1.0</p>
                <p>Date: October 2026</p>
                <p>Platform: JASPR Analysis Suite</p>
            </div>
        </div>
        
        <!-- Table of Contents -->
        <div class="toc">
            <h2>Table of Contents</h2>
            <ol>
                <li>Overview and Assay Description</li>
                <li>Supported Instruments</li>
                <li>Workflow Overview</li>
                <li>Step-by-Step Instructions</li>
                <li>File Naming Conventions</li>
                <li>Key Parameters</li>
                <li>Troubleshooting Guide</li>
                <li>Tips and Best Practices</li>
                <li>References</li>
            </ol>
        </div>
        
        <!-- Main Content -->
        <div class="content">
            <!-- Section 1: Overview -->
            <section>
                <h2>1. Overview and Assay Description</h2>
                <p>The Focus Reduction Neutralization Test (FRNT) is a quantitative viral neutralization assay that measures the ability of antibodies to inhibit viral infection. FRNT is a gold standard assay for determining neutralizing antibody titers in viral surveillance and vaccine efficacy studies.</p>
                <div class="info-box">
                    <strong>Assay Principle:</strong> FRNT measures the concentration of serum antibodies that reduce viral-induced cytopathic effect (CPE) by 50% compared to virus-only controls.
                </div>
                <h3>Key Characteristics</h3>
                <ul>
                    <li>Quantitative measurement of neutralizing antibodies</li>
                    <li>Multiple viral strains can be tested simultaneously</li>
                    <li>Supports serial dilutions of test serum</li>
                    <li>Provides IC50 values (50% inhibitory concentration)</li>
                    <li>Compatible with multiple imaging platforms</li>
                </ul>
            </section>
            
            <!-- Section 2: Supported Instruments -->
            <section>
                <h2>2. Supported Instruments</h2>
                <h3>CX5 (CellInsight CX5 HCS Platform)</h3>
                <p>The CX5 supports two different plate layout configurations:</p>
                <table>
                    <tr>
                        <th>Layout Type</th>
                        <th>Description</th>
                        <th>Use Case</th>
                    </tr>
                    <tr>
                        <td>VSS (Virus-Serum-Serum)</td>
                        <td>Virus varies across rows, serum across columns</td>
                        <td>Primary FRNT layout</td>
                    </tr>
                    <tr>
                        <td>SVV (Serum-Virus-Virus)</td>
                        <td>Serum varies across rows, virus across columns</td>
                        <td>Alternative layout</td>
                    </tr>
                </table>
                
                <h3>Cytation7 (BioTek Cytation 7)</h3>
                <p>The BioTek Cytation7 Cell Imaging Multimode Reader provides alternative high-content imaging capabilities for FRNT analysis with optimized plate layout support.</p>
            </section>
            
            <!-- Section 3: Workflow Overview -->
            <section>
                <h2>3. Workflow Overview</h2>
                <p>The FRNT analysis workflow in JASPR follows six main steps:</p>
                <div class="step">
                    <span class="step-number">1</span>
                    <strong>Load Data:</strong> Import raw data files (CSV/Excel) and experimental metadata key files
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <strong>Select Parser:</strong> Choose the appropriate parser based on instrument and plate layout
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <strong>Upload Data:</strong> Submit both data and key files to JASPR for processing
                </div>
                <div class="step">
                    <span class="step-number">4</span>
                    <strong>Review Analysis:</strong> Examine generated curves and IC50 calculations
                </div>
                <div class="step">
                    <span class="step-number">5</span>
                    <strong>Adjust Settings:</strong> Fine-tune analysis parameters if needed
                </div>
                <div class="step">
                    <span class="step-number">6</span>
                    <strong>Generate Report:</strong> Export results as formatted Excel report
                </div>
            </section>
            
            <!-- Section 4: Step-by-Step Instructions -->
            <section>
                <h2>4. Step-by-Step Instructions</h2>
                
                <h3>Step 1: Download Mock Data</h3>
                <ol>
                    <li>Navigate to http://localhost:8080</li>
                    <li>Locate the "Mock Data" section</li>
                    <li>Click "Download Mock Data"</li>
                    <li>Select FRNT bundle containing data and key files</li>
                </ol>
                
                <h3>Step 2: Access the Data Load Interface</h3>
                <ol>
                    <li>Click "Load Data" in the navigation menu</li>
                    <li>Select the appropriate parser for your data type</li>
                </ol>
                
                <h3>Step 3: Select Parser and Upload Files</h3>
                <p><strong>For CX5 VSS Layout:</strong></p>
                <ol>
                    <li>Parser: "FRNT Virus-Serum-Serum Plate Layout CX5"</li>
                    <li>Data file: spotfire_export_CX5VSS_mock_data.csv</li>
                    <li>Key file: FRNT RUN 3709_01012000_mock_keyfile.xlsx</li>
                </ol>
                
                <p><strong>For CX5 SVV Layout:</strong></p>
                <ol>
                    <li>Parser: "FRNT Serum-Virus-Virus Plate Layout CX5"</li>
                    <li>Data file: spotfire_export_CX5SVV_mock_data.csv</li>
                    <li>Key file: FRNT RUN 3559_01012000_mock_keyfile.xlsx</li>
                </ol>
                
                <p><strong>For Cytation7:</strong></p>
                <ol>
                    <li>Parser: "FRNT Virus-Serum-Serum Plate Layout Cytation7"</li>
                    <li>Data file: 01012000 FRNT Cytation7_mock_data.xlsx</li>
                    <li>Key file: FRNT RUN 3139_01012000_Cytation7_mock_keyfile.xlsx</li>
                </ol>
                <li>Click "Submit"</li>
                
                <h3>Step 4: Review Analysis Results</h3>
                <p>After successful data upload, navigate to the Analysis page:</p>
                <ul>
                    <li><strong>Curves Tab:</strong> View neutralization curves for each serum/virus combination</li>
                    <li><strong>Tables Tab:</strong> Review IC50 values and statistical measures</li>
                    <li>Use dropdown menus to select different virus/serum combinations</li>
                    <li>Examine curve fit quality and data distribution</li>
                </ul>
                
                <h3>Step 5: Adjust Settings (Optional)</h3>
                <p>Click "Settings" to fine-tune analysis parameters:</p>
                <table>
                    <tr>
                        <th>Setting</th>
                        <th>Purpose</th>
                        <th>Adjustment Range</th>
                    </tr>
                    <tr>
                        <td>Fit Visibility</td>
                        <td>Toggle which fitted lines appear on curves</td>
                        <td>All/Selected/None</td>
                    </tr>
                    <tr>
                        <td>Blank Correction</td>
                        <td>Adjust background/control well subtraction</td>
                        <td>None/Moderate/Aggressive</td>
                    </tr>
                    <tr>
                        <td>Axis Scale</td>
                        <td>Modify plot axis ranges</td>
                        <td>Auto/Manual custom range</td>
                    </tr>
                    <tr>
                        <td>Fitting Function</td>
                        <td>Select curve-fitting algorithm</td>
                        <td>Logistic, 4PL, 5PL</td>
                    </tr>
                </table>
                <p>Click "Execute" to apply changes and recalculate results.</p>
                
                <h3>Step 6: Generate and Download Report</h3>
                <ol>
                    <li>Click "Report" in the navigation menu</li>
                    <li>Review final results summary</li>
                    <li>Verify all IC50 values are displayed</li>
                    <li>Click "Download Report"</li>
                    <li>File will be saved as: <code>reportFRNT-[RUN_ID]_[DATE]_report.xlsx</code></li>
                </ol>
            </section>
            
            <!-- Section 5: File Naming Conventions -->
            <section>
                <h2>5. File Naming Conventions</h2>
                <h3>Data File Naming</h3>
                <p>FRNT data files follow these naming patterns:</p>
                <table>
                    <tr>
                        <th>Instrument/Layout</th>
                        <th>Filename Pattern</th>
                        <th>Example</th>
                    </tr>
                    <tr>
                        <td>CX5 VSS</td>
                        <td>spotfire_export_CX5VSS_*.csv</td>
                        <td>spotfire_export_CX5VSS_mock_data.csv</td>
                    </tr>
                    <tr>
                        <td>CX5 SVV</td>
                        <td>spotfire_export_CX5SVV_*.csv</td>
                        <td>spotfire_export_CX5SVV_mock_data.csv</td>
                    </tr>
                    <tr>
                        <td>Cytation7</td>
                        <td>[DATE] FRNT Cytation7_*.xlsx</td>
                        <td>01012000 FRNT Cytation7_mock_data.xlsx</td>
                    </tr>
                </table>
                
                <h3>Key File Naming</h3>
                <p>Experimental metadata key files use this pattern:</p>
                <pre>FRNT RUN [RUNID]_[DDMMYYYY]_[INSTRUMENT]_mock_keyfile.[xlsx|xls]</pre>
                
                <h3>Mock Data Examples</h3>
                <ul>
                    <li>spotfire_export_CX5VSS_mock_data.csv</li>
                    <li>spotfire_export_CX5SVV_mock_data.csv</li>
                    <li>FRNT RUN 3709_01012000_mock_keyfile.xlsx</li>
                    <li>FRNT RUN 3559_01012000_mock_keyfile.xlsx</li>
                    <li>FRNT RUN 3139_01012000_Cytation7_mock_keyfile.xlsx</li>
                    <li>01012000 FRNT Cytation7_mock_data.xlsx</li>
                </ul>
            </section>
            
            <!-- Section 6: Key Parameters -->
            <section>
                <h2>6. Key Parameters in FRNT Analysis</h2>
                <table>
                    <tr>
                        <th>Parameter</th>
                        <th>Definition</th>
                        <th>Units</th>
                        <th>Typical Range</th>
                    </tr>
                    <tr>
                        <td><strong>IC50</strong></td>
                        <td>Serum titer that gives 50% reduction in infected cells</td>
                        <td>Fold-dilution</td>
                        <td>10 - 10,000</td>
                    </tr>
                    <tr>
                        <td><strong>Virus</strong></td>
                        <td>Specific viral strain being tested</td>
                        <td>Categorical</td>
                        <td>Strain ID</td>
                    </tr>
                    <tr>
                        <td><strong>Serum</strong></td>
                        <td>Antibody serum sample identifier</td>
                        <td>Categorical</td>
                        <td>Sample ID</td>
                    </tr>
                    <tr>
                        <td><strong>Percent Inhibition</strong></td>
                        <td>Reduction in infected cells vs virus control</td>
                        <td>Percentage</td>
                        <td>0 - 100%</td>
                    </tr>
                    <tr>
                        <td><strong>Logistic Fit</strong></td>
                        <td>4-parameter logistic regression model</td>
                        <td>R² value</td>
                        <td>0.95 - 1.00</td>
                    </tr>
                    <tr>
                        <td><strong>Dilution Factor</strong></td>
                        <td>Serial dilution increment</td>
                        <td>Fold</td>
                        <td>2x, 3x, 10x</td>
                    </tr>
                </table>
            </section>
            
            <!-- Section 7: Troubleshooting -->
            <section>
                <h2>7. Troubleshooting Guide</h2>
                
                <h3>Common Issues and Solutions</h3>
                
                <h4>Issue: "Application Error" on upload</h4>
                <div class="warning-box">
                    <strong>Solutions:</strong>
                    <ul>
                        <li>Verify file structure matches mock data format</li>
                        <li>Check that both data file and key file are selected</li>
                        <li>Ensure parser selection matches your data type</li>
                        <li>Download fresh mock data bundles to verify correct structure</li>
                        <li>Check file encoding (UTF-8 recommended for CSV files)</li>
                    </ul>
                </div>
                
                <h4>Issue: Curves not displaying</h4>
                <div class="warning-box">
                    <strong>Solutions:</strong>
                    <ul>
                        <li>Confirm data file contains all required columns</li>
                        <li>Verify key file has correct serum and virus naming</li>
                        <li>Use Settings to adjust blank correction or axis scales</li>
                        <li>Reset session and retry upload</li>
                        <li>Check browser console for specific error messages</li>
                    </ul>
                </div>
                
                <h4>Issue: Unexpected IC50 values</h4>
                <div class="warning-box">
                    <strong>Solutions:</strong>
                    <ul>
                        <li>Review raw data in Curves tab for anomalies</li>
                        <li>Check blank well corrections in Settings</li>
                        <li>Verify viral titer and serum dilution series appropriateness</li>
                        <li>Try different fitting functions in Settings</li>
                        <li>Compare with positive control samples</li>
                    </ul>
                </div>
                
                <h4>Issue: File format not recognized</h4>
                <div class="warning-box">
                    <strong>Solutions:</strong>
                    <ul>
                        <li>Verify file extension matches parser requirements (.csv or .xlsx)</li>
                        <li>Check file is not corrupted (try opening with Excel/text editor)</li>
                        <li>Ensure delimiter is correct for CSV files (comma-separated)</li>
                        <li>Validate key file is proper Excel format</li>
                    </ul>
                </div>
            </section>
            
            <!-- Section 8: Tips and Best Practices -->
            <section>
                <h2>8. Tips and Best Practices</h2>
                
                <div class="tips-box">
                    <h3>General Best Practices</h3>
                    <ol>
                        <li><strong>Always use mock data first</strong> to familiarize yourself with the workflow</li>
                        <li><strong>Compare multiple serum/virus combinations</strong> to understand neutralization patterns</li>
                        <li><strong>Check raw data</strong> in curves tab before finalizing reports</li>
                        <li><strong>Use Settings to optimize fits</strong>, but always document any changes</li>
                        <li><strong>Download reports in Excel format</strong> for further analysis or sharing</li>
                        <li><strong>Maintain consistent naming conventions</strong> across all runs</li>
                    </ol>
                </div>
                
                <h3>Analysis Optimization Tips</h3>
                <ul>
                    <li><strong>Dilution Series Quality:</strong> Ensure your serum dilution series spans at least 3-4 orders of magnitude</li>
                    <li><strong>Positive Controls:</strong> Always include known neutralizing sera for validation</li>
                    <li><strong>Negative Controls:</strong> Include non-neutralizing sera and virus-only controls</li>
                    <li><strong>Replicates:</strong> Run samples in triplicate when possible for statistical robustness</li>
                    <li><strong>Curve Fitting:</strong> Review R² values (>0.95) to assess model fit quality</li>
                </ul>
                
                <h3>Data Quality Parameters</h3>
                <table>
                    <tr>
                        <th>Parameter</th>
                        <th>Target</th>
                        <th>Acceptable Range</th>
                    </tr>
                    <tr>
                        <td>R² (Model Fit)</td>
                        <td>>0.98</td>
                        <td>>0.95</td>
                    </tr>
                    <tr>
                        <td>CV (Replicates)</td>
                        <td>&lt;15%</td>
                        <td>&lt;25%</td>
                    </tr>
                    <tr>
                        <td>Control Well Signal</td>
                        <td>At full dynamic range</td>
                        <td>>80% of max</td>
                    </tr>
                    <tr>
                        <td>Positive Control IC50</td>
                        <td>Within historical range</td>
                        <td>±2 fold of expected</td>
                    </tr>
                </table>
            </section>
            
            <!-- Section 9: References -->
            <section>
                <h2>9. References</h2>
                <ul>
                    <li>JASPR Documentation and Support: http://localhost:8080/help</li>
                    <li>FRNT Assay Standards and Best Practices</li>
                    <li>Viral Serology Laboratory Standards</li>
                    <li>High Content Screening Analysis Protocols</li>
                    <li>CellInsight CX5 User Manual</li>
                    <li>BioTek Cytation7 Documentation</li>
                    <li>Statistical Methods for Dose-Response Analysis</li>
                    <li>JASPR Development Team Contact Information</li>
                </ul>
            </section>
        </div>
        
        <!-- Footer -->
        <footer>
            <p>JASPR FRNT Complete Guide | Document Version 1.0 | October 2026</p>
            <p>For support, contact the JASPR development team or visit http://localhost:8080</p>
        </footer>
    </div>
</body>
</html>
"""

# Write FRNT HTML
with open('/var/jaspr/example_data/Instructions/JASPR_FRNT_Complete_Guide.html', 'w') as f:
    f.write(frnt_html)
print("✓ FRNT guide created")
