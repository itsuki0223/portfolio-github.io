Attribute VB_Name = "Module3"
Sub 製品()
    Dim GYO As Long, GYO_machine As Long, RETSU As Long, c As Long, d As Long, e As Long, f As Long
    Dim sheet2_row As Integer, sheet3_row As Integer, sheet4_row As Integer
    Dim name As String, card As String
    Dim p As Integer
    Dim timestamp As Date
    Dim a As String, b As String
    Dim PRO As Boolean
    Dim info As String, pr As String, machine As String, product As String, machine_name As String
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
    
    '製品
    PRO = False
    machine_name = ""
    pr = ""
    For GYO = 2 To sheet2_row
        If Sheets(Sheet2).Cells(GYO, 5) = 3 Then
            If Sheets(Sheet2).Cells(GYO, 2) = "start" Then
                timestamp = Sheets(Sheet2).Cells(GYO, 4).Value
                p = (Val(Left(timestamp, 2)) - 6) * 12 + 12
                If Mid(timestamp, 2, 1) = ":" Then
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 3, 2)) / 5, 0)
                Else
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 4, 2)) / 5, 0)
                End If
                machine = Sheets(Sheet2).Cells(GYO, 1).Value
                product = Sheets(Sheet2).Cells(GYO, 7).Value
                For GYO_machine = 2 To sheet3_row
                    If Sheets(Sheet3).Cells(GYO_machine, 3).Value = machine Then
                        machine_name = Sheets(Sheet3).Cells(GYO_machine, 2).Value
                    End If
                Next GYO_machine
                    
                For d = GYO + 1 To sheet2_row
                    If Sheets(Sheet2).Cells(d, 5).Value = 2 And Sheets(Sheet2).Cells(d, 1).Value = machine Then
                            pr = Sheets(Sheet2).Cells(d, 6).Value
                            For f = 2 To sheet4_row
                                If Sheets(Sheet4).Cells(f, 3).Value = pr Then
                                    pr = Sheets(Sheet4).Cells(f, 2).Value
                                End If
                            Next f
                    ElseIf Sheets(Sheet2).Cells(d, 2).Value = "end" And Sheets(Sheet2).Cells(d, 7).Value = product Then
                            Exit For
                    End If
                Next d
                
                For c = 6 To 50
                    If Sheets(Sheet1).Cells(c, 2).Value = product Then
                        Sheets(Sheet1).Cells(c + 1, p).Value = "0"
                        info = machine_name + " , " + pr
                        If PRO = False Then
                            Sheets(Sheet1).Cells(c, p).VerticalAlignment = xlBottom
                            Sheets(Sheet1).Cells(c, p).Value = info
                            PRO = True
                         Else
                            Sheets(Sheet1).Cells(c, p).VerticalAlignment = xlTop
                            Sheets(Sheet1).Cells(c, p).Value = info
                            PRO = False
                        End If
                        Exit For
                    ElseIf c = 50 Then
                        For e = 6 To 50
                            If Sheets(Sheet1).Cells(e, 2).Value = "" And e Mod 2 = 0 Then
                                Sheets(Sheet1).Cells(e, 2).Value = product
                                Sheets(Sheet1).Cells(e + 1, p).Value = "0"
                                info = machine_name + " , " + pr
                                If PRO = False Then
                                    Sheets(Sheet1).Cells(e, p).VerticalAlignment = xlBottom
                                    Sheets(Sheet1).Cells(e, p).Value = info
                                    PRO = True
                                Else
                                    Sheets(Sheet1).Cells(e, p).VerticalAlignment = xlTop
                                    Sheets(Sheet1).Cells(e, p).Value = info
                                    PRO = False
                                End If
                                Exit For
                            End If
                        Next e
                    End If
                Next c

                info = ""
                machine_name = ""
                pr = ""
                   
            Else
                timestamp = Sheets(Sheet2).Cells(GYO, 4).Value
                p = (Val(Left(timestamp, 2)) - 6) * 12 + 12
                If Mid(timestamp, 2, 1) = ":" Then
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 3, 2)) / 5, 0)
                Else
                    p = p + Application.WorksheetFunction.RoundDown(Val(Mid(timestamp, 4, 2)) / 5, 0)
                End If
                product = Sheets(Sheet2).Cells(GYO, 7).Value
                For GYO_machine = 6 To 50
                    If Sheets(Sheet1).Cells(GYO_machine, 2).Value = product Then
                        Sheets(Sheet1).Cells(GYO_machine + 1, p).Value = "1"
                    End If
                Next GYO_machine
            End If
        End If
    Next GYO
    
    'イナズマ線
    For GYO = 7 To 50
        For RETSU = 12 To 200
            If Sheets(Sheet1).Cells(GYO, RETSU).Value = "0" Then
                If a <> "" Then
                    Sheets(Sheet1).Range(a, Cells(GYO, RETSU)).Interior.Color = RGB(255, 0, 255)
                End If
                a = Sheets(Sheet1).Cells(GYO, RETSU).Address
            ElseIf Sheets(Sheet1).Cells(GYO, RETSU) = "1" Then
                b = Sheets(Sheet1).Cells(GYO, RETSU).Address
                If a = "" Then
                    Sheets(Sheet1).Range(b).Interior.Color = RGB(255, 0, 255)
                    a = ""
                    b = ""
                Else
                    Sheets(Sheet1).Range(a, b).Interior.Color = RGB(255, 0, 255)
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
