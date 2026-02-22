import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { Platform, Alert } from 'react-native';
import { LOGO_BASE64 } from '../assets/images/logoBase64';

export interface PDFData {
  diagnosis_id: string;
  crop: string;
  disease: string;
  confidence: number;
  severity: number;
  stage: string;
  description: string;
  symptoms: string;
  treatment_approach: string;
  pesticides: Array<{
    name: string;
    dosage: string;
    frequency: string;
  }>;
  prevention_steps: string;
  date: string;
}

export const generateDiagnosisPDF = async (data: PDFData) => {
  // Use a premium Google Font and a highly professional layout
  const htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>Smart Crop Health | Official Diagnosis Report</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
          body { 
            font-family: 'Inter', sans-serif; 
            color: #1a1a1a; 
            line-height: 1.6; 
            padding: 40px; 
            max-width: 800px; 
            margin: 0 auto; 
            background-color: #ffffff;
          }
          
          /* Header & Branding */
          .header { 
            display: flex; 
            justify-content: space-between; 
            align-items: flex-start;
            border-bottom: 3px solid #1b5e20; 
            padding-bottom: 24px; 
            margin-bottom: 32px; 
          }
          .brand-col {
            display: flex;
            align-items: center;
            gap: 16px;
          }
          .logo-img {
            width: 50px;
            height: 50px;
            border-radius: 8px;
            object-fit: cover;
          }
          .brand-info h1 {
            color: #1b5e20; 
            font-size: 28px; 
            font-weight: 700; 
            margin: 0;
            letter-spacing: -0.5px;
          }
          .brand-info p {
            color: #666;
            margin: 4px 0 0 0;
            font-size: 14px;
            font-weight: 500;
          }
          .meta-col {
            text-align: right;
            font-size: 13px;
            color: #555;
          }
          .meta-col div { margin-bottom: 4px; }
          .report-id {
            font-weight: 700;
            color: #1b5e20;
            font-family: monospace;
            font-size: 15px;
          }

          /* Sections */
          .section { 
            margin-bottom: 32px; 
            page-break-inside: avoid;
          }
          .section-title { 
            font-size: 18px; 
            font-weight: 600; 
            color: #2e7d32; 
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid #e0e0e0; 
            padding-bottom: 8px; 
            margin-bottom: 16px; 
          }

          /* Grid Data */
          .diagnosis-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 16px; 
            background: #f8fcf8; 
            border: 1px solid #e8f5e9;
            padding: 24px; 
            border-radius: 12px; 
          }
          .grid-item {
            display: flex;
            flex-direction: column;
          }
          .label { 
            font-weight: 600; 
            color: #666; 
            font-size: 12px; 
            text-transform: uppercase; 
            margin-bottom: 4px;
            letter-spacing: 0.5px;
          }
          .value { 
            font-size: 20px; 
            font-weight: 700; 
            color: #1a1a1a; 
          }

          /* Visual Indicators */
          .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            margin-top: 8px;
          }
          .badge-healthy { background: #e8f5e9; color: #2e7d32; }
          .badge-warning { background: #fff3e0; color: #ef6c00; }
          .badge-danger { background: #ffebee; color: #c62828; }

          .severity-bar { 
            height: 8px; 
            width: 100%; 
            background: #e0e0e0; 
            border-radius: 4px; 
            margin-top: 8px; 
            overflow: hidden; 
          }
          .severity-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #4caf50, #ff9800, #f44336); 
          }

          /* Typography Elements */
          .prose {
            color: #444;
            font-size: 15px;
            line-height: 1.7;
          }
          .prose strong {
            color: #1a1a1a;
          }

          /* Table for Pesticides */
          .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
          }
          .data-table th, .data-table td {
            text-align: left;
            padding: 12px 16px;
            border-bottom: 1px solid #eee;
          }
          .data-table th {
            background-color: #f5f5f5;
            color: #555;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
          }
          .data-table td {
            font-size: 15px;
            color: #333;
          }
          .data-table tr:last-child td {
            border-bottom: none;
          }
          .no-data {
            background: #f9f9f9;
            padding: 16px;
            border-radius: 8px;
            color: #666;
            font-style: italic;
            font-size: 14px;
          }

          /* Footer */
          .footer { 
            margin-top: 60px; 
            text-align: center; 
            font-size: 12px; 
            color: #888; 
            border-top: 1px solid #ddd; 
            padding-top: 24px; 
            page-break-inside: avoid;
          }
          .signature-area {
            display: flex;
            justify-content: flex-end;
            margin-top: 40px;
            margin-bottom: 20px;
          }
          .signature-box {
            text-align: center;
            width: 250px;
          }
          .signature-line {
            border-bottom: 1px solid #999;
            margin-bottom: 8px;
            height: 40px;
          }
          .signature-title {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="brand-col">
            <img class="logo-img" src="${LOGO_BASE64}" alt="Smart Crop Health Logo" />
            <div class="brand-info">
              <h1>Smart Crop Health</h1>
              <p>Official Health Assessment Report</p>
            </div>
          </div>
          <div class="meta-col">
            <div>Report ID: <span class="report-id">#${data.diagnosis_id.toUpperCase().substring(0, 8)}</span></div>
            <div>Date Generated: <strong>${data.date}</strong></div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">Diagnostic Summary</div>
          <div class="diagnosis-grid">
            <div class="grid-item">
              <span class="label">Crop Profile</span>
              <span class="value">${data.crop}</span>
            </div>
            <div class="grid-item">
              <span class="label">Detected Condition</span>
              <span class="value" style="color: ${data.disease === 'Healthy' ? '#2e7d32' : '#c62828'}">${data.disease}</span>
            </div>
            <div class="grid-item">
              <span class="label">AI Confidence Score</span>
              <span class="value">${data.confidence.toFixed(1)}%</span>
            </div>
            <div class="grid-item">
              <span class="label">Infection Severity</span>
              <span class="value">${data.severity.toFixed(1)}%</span>
              <div class="severity-bar">
                <div class="severity-fill" style="width: ${data.severity}%"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">Clinical Details</div>
          <div class="prose">
            <p><strong>Condition Overview:</strong> ${data.description}</p>
            <p><strong>Observed Symptoms:</strong> ${data.symptoms}</p>
            <p><strong>Growth Stage:</strong> ${data.stage}</p>
          </div>
        </div>

        <div class="section">
          <div class="section-title">Treatment Protocol</div>
          <div class="prose">
            <p><strong>Primary Approach:</strong> ${data.treatment_approach}</p>
          </div>
          
          ${data.pesticides.length > 0 ? `
            <table class="data-table">
              <thead>
                <tr>
                  <th>Recommended Chemical Agent</th>
                  <th>Dosage Concentration</th>
                  <th>Application Frequency</th>
                </tr>
              </thead>
              <tbody>
                ${data.pesticides.map(p => `
                  <tr>
                    <td><strong>${p.name}</strong></td>
                    <td>${p.dosage}</td>
                    <td>${p.frequency}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          ` : `
            <div class="no-data">
              No specific chemical interventions are required at this time. Focus on continued observation and preventative care.
            </div>
          `}
        </div>

        <div class="section">
          <div class="section-title">Preventative Maintenance & Best Practices</div>
          <div class="prose">
            <p>${data.prevention_steps}</p>
          </div>
        </div>

        <div class="signature-area">
          <div class="signature-box">
            <div class="signature-line"></div>
            <div class="signature-title">AI System Authorization</div>
          </div>
        </div>

        <div class="footer">
          <strong>Smart Crop Health</strong> - Empowering Sustainable Farming Globally<br>
          This document is generated by an Artificial Intelligence diagnostic tool.<br>
          © ${new Date().getFullYear()} Professional Agricultural Solutions. All rights reserved.
        </div>
      </body>
    </html>
  `;

  try {
    if (Platform.OS === 'web') {
      // WEB SPECIFIC SOLUTION: Instead of printing the app screen, inject an iframe with the HTML and print that.
      console.log('Generating PDF via Web Iframe...');
      return new Promise((resolve) => {
        // Create an invisible iframe
        const iframe = document.createElement('iframe');
        iframe.style.position = 'absolute';
        iframe.style.width = '0px';
        iframe.style.height = '0px';
        iframe.style.border = 'none';

        // Append it to the document body
        document.body.appendChild(iframe);

        // Write the HTML content into the iframe's document
        const iframeDoc = iframe.contentWindow?.document || iframe.contentDocument;
        if (iframeDoc) {
          iframeDoc.open();
          iframeDoc.write(htmlContent);
          iframeDoc.close();
        }

        // Wait a tiny bit for styles to compute, then print
        setTimeout(() => {
          iframe.contentWindow?.focus();
          iframe.contentWindow?.print();

          // Cleanup after printing dialogue is closed (or immediately after triggering)
          setTimeout(() => {
            document.body.removeChild(iframe);
            resolve('Web Print Initiated');
          }, 1000);
        }, 500);
      });
    } else {
      // MOBILE SOLUTION: Generate standard PDF file
      const { uri } = await Print.printToFileAsync({ html: htmlContent });
      console.log('PDF initial URI:', uri);

      const fileName = `SmartCropHealth_Report_${data.diagnosis_id.substring(0, 6)}.pdf`.replace(/\s+/g, '_');
      const newUri = (FileSystem as any).cacheDirectory + fileName;

      await FileSystem.moveAsync({
        from: uri,
        to: newUri
      });

      console.log('PDF moved to:', newUri);

      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(newUri, {
          UTI: 'com.adobe.pdf',
          mimeType: 'application/pdf',
          dialogTitle: 'Download Crop Diagnosis Report'
        });
      } else {
        Alert.alert('Sharing Not Available', 'Your device does not support file sharing/saving.');
      }

      return newUri;
    }
  } catch (error) {
    console.error('Error generating/sharing PDF:', error);
    Alert.alert('Error', 'Failed to generate the report. Please try again.');
    throw error;
  }
};
