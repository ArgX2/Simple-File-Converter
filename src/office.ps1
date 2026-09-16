param([string]$InputFile, [string]$OutputFile, [int]$Format)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$app = $null
$deck = $null
$security = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $security = $app.AutomationSecurity
    $app.AutomationSecurity = 3
    $deck = $app.Presentations.Open($InputFile, -1, 0, 0)
    $app.AutomationSecurity = $security
    $deck.SaveAs($OutputFile, $Format)
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
} finally {
    if ($deck) { $deck.Close(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck) }
    if ($app) {
        if ($null -ne $security) { $app.AutomationSecurity = $security }
        # PowerPoint may share the user's application instance: do not Quit it.
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
}
