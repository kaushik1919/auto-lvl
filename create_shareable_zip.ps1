# Quick script to create a shareable zip file
# Run this in PowerShell to package the game for your friend

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Shadow Platformer - Create Zip File  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$zipPath = "ShadowPlatformer_Game.zip"

# Remove old zip if exists
if (Test-Path $zipPath) {
    Write-Host "⚠️  Removing old zip file..." -ForegroundColor Yellow
    Remove-Item $zipPath
}

Write-Host "📦 Creating zip file..." -ForegroundColor Green
Compress-Archive -Path "dist\*" -DestinationPath $zipPath -CompressionLevel Optimal

if (Test-Path $zipPath) {
    $sizeInMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)
    Write-Host ""
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host "  File: $zipPath" -ForegroundColor White
    Write-Host "  Size: $sizeInMB MB" -ForegroundColor White
    Write-Host ""
    Write-Host "📤 Ready to share with your friend!" -ForegroundColor Cyan
    Write-Host "   Upload to Google Drive, Dropbox, or send via USB" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "✗ ERROR: Failed to create zip file" -ForegroundColor Red
}

Write-Host ""
