Sub Sample1()
Dim i As Long, k As Long, lastRow As Long, wS As Worksheet
Dim sN As String, myFlg As Boolean
With Worksheets("Sheet1")
lastRow = .Cells(Rows.Count, "A").End(xlUp).Row
.Range("AI:AI").Insert
'M列(空)に注文日カラムから取得した注文月を入れる
Range(.Cells(2, "AI"), .Cells(lastRow, "AI")).Formula = "=MONTH(A2)"
'12ヶ月分のループ開始
For i = 1 To 12
  'シート名
  sN = i & "月"
  For k = 2 To Worksheets.Count
    If Worksheets(k).Name = sN Then
      myFlg = True
      Exit For
    End If
  Next k
  '上記sNのシートなければシート追加
  If myFlg = False Then
    Worksheets.Add after:=Worksheets(i)
    ActiveSheet.Name = sN
  End If
  Set wS = Worksheets(sN)
  wS.Cells.Clear
  .Range("A1").AutoFilter field:=35, Criteria1:=i
  Range(.Cells(1, "A"), .Cells(lastRow, "AH")).SpecialCells(xlCellTypeVisible).Copy wS.Range("A1")
  wS.Columns.AutoFit
  wS.Move after:=Worksheets(i)
  myFlg = False
Next i
.AutoFilterMode = False
.Range("AI:AI").Delete
End With
MsgBox "完了"
End Sub
