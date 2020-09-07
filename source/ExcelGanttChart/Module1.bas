Attribute VB_Name = "Module1"
Sub 設備()
    Dim GYO As Long, GYO_machine As Long, RETSU As Long, c As Long, d As Long, e As Long
    Dim sheet2_row As Integer, sheet3_row As Integer, sheet4_row As Integer
    Dim name As String, card As String
    Dim p As Integer
    Dim timestamp As Date
    Dim a As String, b As String
    Dim PRO As Boolean
    Dim info As String, pr As String, machine As String
    Dim Sheet1 As String, Sheet2 As String, Sheet3 As String, Sheet4 As String
    
    Sheet1 = "ガントチャート"
    Sheet2 = "センサーデータ"
    Sheet3 = "設備"
    Sheet4 = "作業者"
    
    Sheets(Sheet1).Range("B6:FW23").Value = ""
    Sheets(Sheet1).Range("B6:FW23").Interior.Color = RGB(255, 255, 255)
        
    sheet2_row = Sheets(Sheet2).Cells(Rows.Count, 1).End(xlUp).Row
    sheet3_row = Sheets(Sheet3).Cells(Rows.Count, 1).End(xlUp).Row
    sheet4_row = Sheets(Sheet4).Cells(Rows.Count, 1).End(xlUp).Row
    
    '作業者記入
    For GYO_machine = 2 To sheet3_row
        Sheets(Sheet1).Cells(GYO_machine * 2 + 2, 2).Value = Sheets(Sheet3).Cells(GYO_machine, 2).Value
    Next GYO_machine
    
    '作業
    PRO = False
    machine = ""
    pr = ""
    For GYO = 2 To sheet2_row
        If Sheets(Sheet2).Cells(GYO, 5) = 1 Then
            If Sheets(Sheet2).Cells(GYO, 2) = "on" Then
                timestamp = Sheets(Sheet2).Cells(GYO, 4).Value
                p = (Val(Left(timestamp, 2)) - 6) * 12 + 12
                If Mid(timestamp, 2, 1) = ":" Then
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 3, 2)) / 5, 0)
                Else
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 4, 2)) / 5, 0)
                End If
                name = Sheets(Sheet2).Cells(GYO, 1).Value
                For GYO_machine = 2 To sheet3_row
                    If Sheets(Sheet3).Cells(GYO_machine, 3).Value = name Then
                        Sheets(Sheet1).Cells(GYO_machine * 2 + 3, p).Value = "0"
                        For c = GYO + 1 To sheet2_row
                            If Sheets(Sheet2).Cells(c, 1).Value = name And Sheets(Sheet2).Cells(c, 2).Value = "Released" Then
                                card = Sheets(Sheet2).Cells(c, 6).Value
                                For e = 2 To sheet4_row
                                    If Sheets(Sheet4).Cells(e, 3) = card Then
                                        machine = Sheets(Sheet4).Cells(e, 2).Value
                                    End If
                                Next e
                            ElseIf Sheets(Sheet2).Cells(c, 2).Value = "on" And Sheets(Sheet2).Cells(c, 1).Value = name Then
                                Exit For
                            End If
                        Next c
                        For d = GYO + 1 To sheet2_row
                            If Sheets(Sheet2).Cells(d, 5).Value = 3 And Sheets(Sheet2).Cells(d, 1).Value = name And Sheets(Sheet2).Cells(d, 2).Value = "end" Then
                                pr = Sheets(Sheet2).Cells(d, 7).Value
                            ElseIf Sheets(Sheet2).Cells(d, 2).Value = "on" And Sheets(Sheet2).Cells(d, 1).Value = name Then
                                Exit For
                            End If
                        Next d
                        info = pr + " , " + machine
                        If PRO = False Then
                            Sheets(Sheet1).Cells(GYO_machine * 2 + 2, p).VerticalAlignment = xlBottom
                            Sheets(Sheet1).Cells(GYO_machine * 2 + 2, p).Value = info
                            PRO = True
                        Else
                            Sheets(Sheet1).Cells(GYO_machine * 2 + 2, p).VerticalAlignment = xlTop
                            Sheets(Sheet1).Cells(GYO_machine * 2 + 2, p).Value = info
                            PRO = False
                        End If
                        info = ""
                        machine = ""
                        pr = ""
                    End If
                Next GYO_machine
            Else
                timestamp = Sheets(Sheet2).Cells(GYO, 4).Value
                p = (Val(Left(timestamp, 2)) - 6) * 12 + 12
                If Mid(timestamp, 2, 1) = ":" Then
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 3, 2)) / 5, 0)
                Else
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 4, 2)) / 5, 0)
                End If
                name = Sheets(Sheet2).Cells(GYO, 1).Value
                For GYO_machine = 2 To sheet3_row
                    If Sheets(Sheet3).Cells(GYO_machine, 3).Value = name Then
                        Sheets(Sheet1).Cells(GYO_machine * 2 + 3, p).Value = "1"
                    End If
                Next GYO_machine
            End If
        End If
    Next GYO
    
    'イナズマ線
    For GYO = 7 To 20
        For RETSU = 12 To 200
            If Sheets(Sheet1).Cells(GYO, RETSU).Value = "0" Then
                If a <> "" Then
                    Sheets(Sheet1).Range(a, Cells(GYO, RETSU)).Interior.Color = RGB(0, 255, 0)
                End If
                a = Sheets(Sheet1).Cells(GYO, RETSU).Address
            ElseIf Sheets(Sheet1).Cells(GYO, RETSU) = "1" Then
                b = Sheets(Sheet1).Cells(GYO, RETSU).Address
                If a = "" Then
                    Sheets(Sheet1).Range(b).Interior.Color = RGB(0, 255, 0)
                    a = ""
                    b = ""
                Else
                    Sheets(Sheet1).Range(a, b).Interior.Color = RGB(0, 255, 0)
                    a = ""
                    b = ""
                End If
            End If
        Next RETSU
        If GYO Mod 2 = 1 Then
            a = ""
            b = ""
            Sheets(Sheet1).Range(Cells(GYO, 12), Cells(GYO, 200)).Value = ""
        End If
    Next GYO
End Sub



