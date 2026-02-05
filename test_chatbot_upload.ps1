
$uri = "http://localhost:5000/api/chatbot/upload"
$imagePath = "c:\Users\maddy\OneDrive\Desktop\SE-Project-AI-Crop-Disease-Diagnosis-System-\sample.JPG"

if (-not (Test-Path $imagePath)) {
    Write-Error "Sample image not found at $imagePath. Please provide a valid image path."
    exit 1
}

$boundary = [System.Guid]::NewGuid().ToString() 
$LF = "`r`n"

$fileBytes = [System.IO.File]::ReadAllBytes($imagePath)
$fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)

$bodyLines = ( 
    "--$boundary",
    "Content-Disposition: form-data; name=`"image`"; filename=`"sample.JPG`"",
    "Content-Type: image/jpeg",
    "",
    $fileEnc,
    "--$boundary--$LF" 
) -join $LF

$headers = @{
    "Content-Type" = "multipart/form-data; boundary=$boundary"
}

try {
    Write-Host "Sending request to $uri..."
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $bodyLines
    Write-Host "Response received:"
    $response | ConvertTo-Json -Depth 5
}
catch {
    Write-Error $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
}
