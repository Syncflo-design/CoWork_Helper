# Word PDF export hangs: check guide layout through Word's page view instead

**Date:** 2026-11-23 · **Where:** this Windows machine, Word COM from PowerShell

## What bit us
`Documents.Open(...).ExportAsFixedFormat(pdf, 17)` hung forever (hidden WINWORD at high CPU) on every
document, including the Com-Struct Test Record that exported fine on 20 Nov. `SaveAs2(pdf, 17)` and XPS
export (`18`) hung the same way. Opening the document and `ComputeStatistics(2)` (page count) still worked
instantly, so the documents were fine and the fixed-format export path was the problem.

## Workaround
Render each page through Word's own page layout, no PDF engine involved:

```powershell
$d = $w.Documents.Open($docx, $false, $true)
$d.ActiveWindow.View.Type = 3            # print layout
$pane = $d.ActiveWindow.ActivePane
for ($i = 1; $i -le $pane.Pages.Count; $i++) {
  [IO.File]::WriteAllBytes("p$i.emf", $pane.Pages.Item($i).EnhMetaFileBits)
}
```

Then Pillow on Windows opens the EMF: `im = Image.open(f); im.load(dpi=36); im.convert("RGB")` and paste the
pages onto one contact sheet to eyeball the layout.

## Also
- Copy the .docx to the scratchpad first (Word on S: is slow / hangs on open).
- After a hang, stop only the hidden WINWORD your command started (no window title, start time = your run);
  never kill Word blindly, the user may have documents open.
- docx `keepNext` on a caption paragraph is what keeps "caption + screenshot" on one page; without it Word
  leaves the caption at the bottom and moves the picture over.
