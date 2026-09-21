param([string]$InputFile, [string]$OutputFile,
    [ValidateSet('docx-to-pdf', 'pdf-to-docx')][string]$Direction,
    [string]$OwnerFile, [string]$CancelFile)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$app = $null
$doc = $null
$bootstrap = $null
$security = $null
$owned = $false
$links = $null
$updateFields = $null
$updatePrintLinks = $null
$code = 0
$existing = @(Get-Process WINWORD -ErrorAction SilentlyContinue | ForEach-Object { $_.Id })
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class WordWindowProcess {
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr window, out uint process);
}
'@
function Check-Cancel {
    if ($CancelFile -and (Test-Path -LiteralPath $CancelFile)) { throw 'Conversion cancelled.' }
}
try {
    Check-Cancel
    $app = New-Object -ComObject Word.Application
    # Word exposes Hwnd on Window, not Application. A temporary blank document
    # identifies this COM instance before any user input file is opened.
    $bootstrap = $app.Documents.Add()
    [uint32]$wordProcessId = 0
    [void][WordWindowProcess]::GetWindowThreadProcessId([IntPtr]$bootstrap.Windows.Item(1).Hwnd, [ref]$wordProcessId)
    if (-not $wordProcessId -or $existing -contains $wordProcessId) {
        throw 'Could not obtain an independent Word instance. Please try again.'
    }
    $owned = $true
    $process = Get-Process -Id $wordProcessId
    if ($OwnerFile) {
        @{ pid = $wordProcessId; created = $process.StartTime.ToUniversalTime().ToFileTimeUtc().ToString() } |
            ConvertTo-Json -Compress | Set-Content -LiteralPath $OwnerFile -Encoding UTF8
    }
    $bootstrap.Close(0)
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($bootstrap)
    $bootstrap = $null
    $app.Visible = $false
    $app.DisplayAlerts = 0
    $security = $app.AutomationSecurity
    # msoAutomationSecurityForceDisable = 3
    $app.AutomationSecurity = 3
    $links = $app.Options.UpdateLinksAtOpen
    $updateFields = $app.Options.UpdateFieldsAtPrint
    $updatePrintLinks = $app.Options.UpdateLinksAtPrint
    $app.Options.UpdateLinksAtOpen = $false
    $app.Options.UpdateFieldsAtPrint = $false
    $app.Options.UpdateLinksAtPrint = $false
    if ($Direction -eq 'pdf-to-docx' -and [double]$app.Version -lt 15) {
        throw 'PDF to DOCX requires Microsoft Word 2013 or later.'
    }
    Check-Cancel
    # Keep the optional argument list short. Word's COM marshaler can reject
    # explicit Missing/null values for the later Open parameters.
    if ($Direction -eq 'pdf-to-docx') {
        # OpenNoRepairDialog avoids the hidden PDF recovery/format dialog.
        $doc = $app.Documents.OpenNoRepairDialog($InputFile, $false, $true, $false)
    } else {
        $doc = $app.Documents.Open($InputFile, $false, $true, $false)
    }
    Check-Cancel
    if ($Direction -eq 'docx-to-pdf') {
        # PDF, no viewer, print quality, all pages, document content without markup.
        $doc.ExportAsFixedFormat($OutputFile, 17, $false, 0, 0, 1, 1, 0)
    } else {
        # wdFormatDocumentDefault = 16
        $doc.SaveAs2($OutputFile, 16)
    }
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    [Console]::Error.WriteLine($_.InvocationInfo.PositionMessage)
    $code = 1
} finally {
    if ($bootstrap) {
        try { $bootstrap.Close(0) } catch { }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($bootstrap)
    }
    if ($doc) {
        try { $doc.Close(0) } catch { }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)
    }
    if ($app) {
        if ($owned) {
            try {
                if ($null -ne $security) { $app.AutomationSecurity = $security }
                if ($null -ne $links) { $app.Options.UpdateLinksAtOpen = $links }
                if ($null -ne $updateFields) { $app.Options.UpdateFieldsAtPrint = $updateFields }
                if ($null -ne $updatePrintLinks) { $app.Options.UpdateLinksAtPrint = $updatePrintLinks }
            } catch { }
            try { $app.Quit(0) } catch { }
        }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
}
exit $code
